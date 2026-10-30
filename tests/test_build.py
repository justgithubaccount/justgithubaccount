"""Behavioral contracts for the public projection; run with stdlib unittest."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class BootstrapTest(unittest.TestCase):
    def test_builder_exists(self):
        self.assertTrue((ROOT / 'scripts/build.py').is_file(), 'deterministic builder is missing')


class BuildTests(unittest.TestCase):
    def setUp(self):
        if not (ROOT / 'scripts/build.py').exists():
            self.skipTest('builder not implemented yet')
        spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
        self.b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.b)
        self.data = json.loads((ROOT / 'data/public-portfolio.json').read_text())

    def test_repeatable_in_independent_directories(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            self.b.build(self.data, Path(a))
            self.b.build(self.data, Path(b))
            files = lambda p: {str(f.relative_to(p)): f.read_bytes() for f in Path(p).rglob('*') if f.is_file()}
            self.assertEqual(files(a), files(b))
            self.assertIn('site/llms.txt', files(a))

    def test_invalid_manifests_fail_before_writes(self):
        mutations = [
            lambda d: d['projects'][0].update(repository='justgithubaccount/private-project'),
            lambda d: d['projects'][0].update(revision='main'),
            lambda d: d['projects'][0]['evidence'].append('../secret'),
            lambda d: d['projects'][0]['evidence'].append('https://evil.example/'),
            lambda d: d['projects'].append(copy.deepcopy(d['projects'][0])),
            lambda d: d.update(contact='mailto:invented@example.com'),
            lambda d: d['identity'].update(intro='<script>alert(1)</script>'),
            lambda d: d['identity'].update(intro='hidden\x00value'),
            lambda d: d['identity'].update(intro='[injected](https://evil.example)'),
            lambda d: d.update(publication_state='PUBLIC'),
            lambda d: d['projects'][0].update(title='x' * 2000),
            lambda d: d['projects'][0].update(evidence=['README.md?redirect=evil']),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate), tempfile.TemporaryDirectory() as out:
                d = copy.deepcopy(self.data)
                mutate(d)
                with self.assertRaises(ValueError):
                    self.b.build(d, Path(out))
                self.assertEqual(list(Path(out).iterdir()), [])

    def test_vector_assets_are_safe_and_described(self):
        files = self.b.render(self.data)
        svgs = [v for k, v in files.items() if k.endswith('.svg')]
        self.assertGreaterEqual(len(svgs), 5)
        for svg in svgs:
            root = ET.fromstring(svg)
            self.assertIn('viewBox', root.attrib)
            self.assertIsNotNone(root.find('{http://www.w3.org/2000/svg}title'))
            self.assertIsNotNone(root.find('{http://www.w3.org/2000/svg}desc'))
            self.assertFalse(any(x in svg for x in ('<image', 'foreignObject', '<script', 'base64', 'href=', '@font-face')))

    def test_draft_does_not_claim_a_live_website(self):
        files = self.b.render(self.data)
        self.assertIn('noindex, nofollow', files['site/index.html'])
        self.assertIn('Disallow: /', files['site/robots.txt'])
        self.assertNotIn('](https://justgithubaccount.github.io/)', files['README.md'])
        self.assertIn('publication pending', files['README.md'])

    def test_release_approval_switches_indexing_without_claiming_publication(self):
        d = copy.deepcopy(self.data)
        d['publication_state'] = 'RELEASE_APPROVED'
        files = self.b.render(d)
        self.assertIn('index, follow', files['site/index.html'])
        self.assertIn('Allow: /', files['site/robots.txt'])
        self.assertIn('](https://justgithubaccount.github.io/)', files['README.md'])

    def test_check_is_readonly_and_detects_missing_modified_and_stale_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.b.build(self.data, out)
            self.assertEqual(self.b.check(self.data, out), [])
            target = out / 'site/index.html'
            target.write_text('tampered')
            (out / 'assets/hero.svg').unlink()
            (out / 'site/stale.txt').write_text('obsolete')
            errors = self.b.check(self.data, out)
            self.assertIn('site/index.html', errors)
            self.assertIn('assets/hero.svg', errors)
            self.assertIn('site/stale.txt', errors)
            self.assertEqual(target.read_text(), 'tampered')

    def test_pages_export_matches_and_has_no_second_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.b.export_pages(self.data, Path(tmp))
            for name, body in self.b.render(self.data).items():
                if name.startswith('site/'):
                    self.assertEqual((Path(tmp) / name[5:]).read_text(), body)
            self.assertFalse((Path(tmp) / 'data/public-portfolio.json').exists())

    def test_structured_data_has_only_evidenced_projects(self):
        files = self.b.render(self.data)
        data = json.loads(files['site/structured-data.json'])
        projects = data['@graph'][1]['hasPart']
        self.assertEqual(len(projects), 3)
        self.assertTrue(all(p['@type'] == 'SoftwareSourceCode' for p in projects))
        self.assertNotIn('Offer', json.dumps(data))
        self.assertNotIn('aggregateRating', json.dumps(data))


if __name__ == '__main__':
    unittest.main()
