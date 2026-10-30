"""Source evidence is mandatory; movement of an upstream branch is advisory."""
import copy
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('verify_sources', ROOT / 'scripts/verify_sources.py')
sources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sources)


class SourceVerificationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data/public-portfolio.json').read_text())
        self.responses = {}
        for project in self.data['projects']:
            repo, sha = project['repository'], project['revision']
            prefix = 'https://api.github.com/repos/' + repo
            self.responses[prefix] = json.dumps({
                'full_name': repo, 'private': False, 'license': {'spdx_id': 'MIT'},
                'default_branch': 'main',
            }).encode()
            self.responses[prefix + '/commits/main'] = json.dumps({'sha': sha}).encode()
            self.responses[prefix + '/commits/' + sha] = json.dumps({'sha': sha}).encode()
            for path in project['evidence']:
                self.responses[f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'] = b'public evidence\n'
        self.project = self.data['projects'][2]
        self.prefix = 'https://api.github.com/repos/' + self.project['repository']
        self.moved_sha = 'c42b365e44cfa8c3869cb347cc9f5188fffd0e62'

    def fetch(self, url):
        # Only the external network boundary is replaced; validation and CLI run.
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        return response

    def run_cli(self, data=None):
        out, err = StringIO(), StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / 'manifest.json'
            manifest.write_text(json.dumps(self.data if data is None else data))
            with patch.object(sources, 'fetch', side_effect=self.fetch), \
                    patch.object(sys, 'argv', ['verify_sources.py', '--manifest', str(manifest)]), \
                    redirect_stdout(out), redirect_stderr(err):
                code = sources.main()
        return code, out.getvalue(), err.getvalue()

    def advance_upstream(self):
        self.responses[self.prefix + '/commits/main'] = json.dumps({'sha': self.moved_sha}).encode()

    def test_matching_main_and_verified_snapshot_are_reported_separately(self):
        code, out, _ = self.run_cli()
        self.assertEqual(code, 0)
        for result in json.loads(out):
            self.assertEqual(result['snapshot_status'], 'VERIFIED')
            self.assertEqual(result['upstream_status'], 'VERIFIED')

    def test_upstream_advance_does_not_fail_verifiable_pinned_snapshot(self):
        self.advance_upstream()
        code, out, err = self.run_cli()
        self.assertEqual(code, 0, err)
        result = json.loads(out)[2]
        self.assertEqual(result['snapshot_status'], 'VERIFIED')
        self.assertEqual(result['upstream_status'], 'DRIFT_FOUND')
        self.assertEqual(result['pinned_sha'], self.project['revision'])
        self.assertEqual(result['main_sha'], self.moved_sha)
        self.assertIn('DRIFT_FOUND', err)

    def test_unavailable_upstream_observation_does_not_erase_snapshot_proof(self):
        url = self.prefix + '/commits/main'
        self.responses[url] = HTTPError(url, 403, 'rate limited', {}, None)
        code, out, err = self.run_cli()
        self.assertEqual(code, 0, err)
        result = json.loads(out)[2]
        self.assertEqual(result['snapshot_status'], 'VERIFIED')
        self.assertEqual(result['upstream_status'], 'UNKNOWN')
        self.assertIsNone(result['main_sha'])
        self.assertIn('UNKNOWN', err)

    def test_missing_or_mismatched_pinned_commit_fails_even_if_files_exist(self):
        url = self.prefix + '/commits/' + self.project['revision']
        for response in [HTTPError(url, 404, 'not found', {}, None),
                         json.dumps({'sha': self.moved_sha}).encode(), b'{}']:
            with self.subTest(response=response):
                self.responses[url] = response
                self.assertEqual(self.run_cli()[0], 1)

    def test_missing_or_empty_evidence_still_fails_when_main_has_advanced(self):
        self.advance_upstream()
        for path in self.project['evidence']:
            url = 'https://raw.githubusercontent.com/{}/{}/{}'.format(
                self.project['repository'], self.project['revision'], path)
            for response in [b'', HTTPError(url, 404, 'not found', {}, None)]:
                with self.subTest(path=path, response=response):
                    self.responses[url] = response
                    self.assertEqual(self.run_cli()[0], 1)
            self.responses[url] = b'public evidence\n'

    def test_source_metadata_unavailable_is_a_mandatory_failure(self):
        self.responses[self.prefix] = HTTPError(self.prefix, 403, 'rate limited', {}, None)
        self.assertEqual(self.run_cli()[0], 1)

    def test_changed_or_missing_public_license_identity_metadata_fails(self):
        original = json.loads(self.responses[self.prefix])
        for mutation in [dict(private=True), dict(private=None), dict(license=None),
                         dict(license={'spdx_id': 'GPL-3.0'}),
                         dict(full_name='another-owner/another-project')]:
            with self.subTest(mutation=mutation):
                self.responses[self.prefix] = json.dumps({**original, **mutation}).encode()
                self.assertEqual(self.run_cli()[0], 1)

    def test_allowlist_violations_fail_before_fetching_unapproved_sources(self):
        for mutation in [dict(repository='justgithubaccount/unapproved'),
                         dict(evidence=['README.md', '../private', 'app/api.py']),
                         dict(revision='main'), dict(license='unreviewed')]:
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                data['projects'][2].update(mutation)
                self.assertEqual(self.run_cli(data)[0], 1)

    def test_malformed_source_metadata_fails_cleanly(self):
        for response in [b'null', b'[]', b'{}', b'not json']:
            with self.subTest(response=response):
                self.responses[self.prefix] = response
                self.assertEqual(self.run_cli()[0], 1)

    def test_malformed_upstream_response_is_unknown_not_snapshot_failure(self):
        for response in [b'{}', b'{"sha":"main"}', b'not json']:
            with self.subTest(response=response):
                self.responses[self.prefix + '/commits/main'] = response
                code, out, err = self.run_cli()
                self.assertEqual(code, 0, err)
                self.assertEqual(json.loads(out)[2]['snapshot_status'], 'VERIFIED')
                self.assertEqual(json.loads(out)[2]['upstream_status'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
