#!/usr/bin/env python3
"""Verify pinned public snapshots; report upstream drift separately, anonymously."""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

from build import ROOT, validate


def fetch(url):
    request = Request(url, headers={'User-Agent': 'public-portfolio-source-check/1', 'Accept': 'application/vnd.github+json'})
    with urlopen(request, timeout=30) as response:
        return response.read()


def commit_sha(url):
    payload = json.loads(fetch(url))
    sha = payload.get('sha') if isinstance(payload, dict) else None
    if not isinstance(sha, str) or not re.fullmatch('[0-9a-f]{40}', sha):
        raise ValueError('Invalid commit response: ' + url)
    return sha


def verify(data):
    validate(data)
    results = []
    for p in data['projects']:
        prefix = 'https://api.github.com/repos/' + p['repository']
        meta = json.loads(fetch(prefix))
        if (not isinstance(meta, dict) or meta.get('full_name') != p['repository']
                or meta.get('private') is not False
                or not isinstance(meta.get('license'), dict)
                or meta['license'].get('spdx_id') != p['license']):
            raise ValueError('Source visibility, identity or rights drift: ' + p['repository'])
        # Mandatory evidence: the exact public commit and every approved file.
        if commit_sha(prefix + '/commits/' + p['revision']) != p['revision']:
            raise ValueError('Pinned commit mismatch: ' + p['repository'])
        for path in p['evidence']:
            body = fetch('https://raw.githubusercontent.com/' + p['repository'] + '/' + p['revision'] + '/' + path)
            if not body:
                raise ValueError('Empty source evidence: ' + path)
        result = {'repository': p['repository'], 'pinned_sha': p['revision'],
                  'visibility': 'PUBLIC', 'snapshot_status': 'VERIFIED'}
        # Advisory observation: a branch may move without invalidating its snapshot.
        try:
            branch = meta.get('default_branch')
            if not isinstance(branch, str) or not branch:
                raise ValueError('Default branch unavailable')
            current = commit_sha(prefix + '/commits/' + branch)
            result.update(main_sha=current, upstream_status='VERIFIED' if current == p['revision'] else 'DRIFT_FOUND')
        except (ValueError, OSError, URLError) as exc:
            result.update(main_sha=None, upstream_status='UNKNOWN', upstream_error=str(exc))
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'data/public-portfolio.json')
    args = parser.parse_args()
    try:
        results = verify(json.loads(args.manifest.read_text()))
        print(json.dumps(results, indent=2))
        for result in results:
            if result['upstream_status'] != 'VERIFIED':
                print('Upstream ' + result['upstream_status'] + ': ' + result['repository']
                      + '; pinned snapshot VERIFIED', file=sys.stderr)
        return 0  # Mandatory snapshot verification raises on failure; drift is advisory.
    except (ValueError, OSError, URLError) as exc:
        print('Source snapshot verification failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
