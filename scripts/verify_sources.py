#!/usr/bin/env python3
"""Reverify only the three approved public sources, anonymously, without credentials."""
import argparse
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

from build import ROOT, validate


def fetch(url):
    request = Request(url, headers={'User-Agent': 'public-portfolio-source-check/1', 'Accept': 'application/vnd.github+json'})
    with urlopen(request, timeout=30) as response:
        return response.read()


def verify(data):
    validate(data)
    results = []
    for p in data['projects']:
        prefix = 'https://api.github.com/repos/' + p['repository']
        meta = json.loads(fetch(prefix))
        if meta['full_name'] != p['repository'] or meta['private'] or meta['license']['spdx_id'] != p['license']:
            raise ValueError('Source visibility, identity or rights drift: ' + p['repository'])
        current = json.loads(fetch(prefix + '/commits/' + meta['default_branch']))['sha']
        state = 'VERIFIED' if current == p['revision'] else 'DRIFT_FOUND'
        for path in p['evidence']:
            body = fetch('https://raw.githubusercontent.com/' + p['repository'] + '/' + p['revision'] + '/' + path)
            if not body:
                raise ValueError('Empty source evidence: ' + path)
        results.append({'repository': p['repository'], 'pinned_sha': p['revision'], 'main_sha': current, 'visibility': 'PUBLIC', 'status': state})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'data/public-portfolio.json')
    args = parser.parse_args()
    try:
        results = verify(json.loads(args.manifest.read_text()))
        print(json.dumps(results, indent=2))
        return 0 if all(r['status'] == 'VERIFIED' for r in results) else 1
    except (ValueError, OSError, URLError) as exc:
        print('Source verification UNKNOWN: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
