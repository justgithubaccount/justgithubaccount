"""Negative tests exercise the publication checks against changed export bytes."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import audit
import build


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data/public-portfolio.json').read_text())

    def test_public_urls_are_exact_not_prefixes(self):
        for url in ['https://github.com/justgithubaccount/app-poly-gitops-k8s',
                    'https://github.com/justgithubaccount/app-poly-gitops-fastapi/blob/' + 'a' * 40 + '/app/api.py']:
            self.assertTrue(audit.public_url(url))
        for url in ['https://github.com.evil.example/justgithubaccount/app-poly-gitops-k8s',
                    'https://github.com/justgithubaccount/private-repo',
                    'https://github.com/justgithubaccount/app-poly-gitops-k8s-extra',
                    'https://github.com/justgithubaccount/app-poly-gitops-k8s/blob/main/README.md',
                    'https://github.com/justgithubaccount/app-poly-gitops-k8s/blob/' + 'a' * 40 + '/secret.txt']:
            self.assertFalse(audit.public_url(url))

    def test_export_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            build.export_pages(self.data, Path(tmp))
            audit.audit_site(Path(tmp))
            (Path(tmp) / 'index.html').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'digest drift'):
                audit.audit_site(Path(tmp))

    def test_unsafe_html_even_with_updated_digest_is_rejected(self):
        mutations = [
            ('href="#work"', 'href="https://evil.example"'),
            ('href="#work"', 'href="#missing-anchor"'),
            ('<body>', '<body onload="alert(1)">'),
            ('<body>', '<body><script>alert(1)</script>'),
            ('<body>', '<body><iframe src="https://evil.example"></iframe>'),
            ('<body>', '<body><p>Vast-CX-Suit internal</p>'),
            ('<body>', '<body><p>invented@example.com</p>'),
            ('<body>', '<body><p>192.168.1.1</p>'),
            ('href="styles.css"', 'href="../outside.css"'),
            ('<main id="main">', '<main id="work">'),
        ]
        for before, after in mutations:
            with self.subTest(after=after), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                build.export_pages(self.data, out)
                target = out / 'index.html'
                target.write_text(target.read_text().replace(before, after, 1))
                info = json.loads((out / 'build-info.json').read_text())
                info['files']['index.html'] = hashlib.sha256(target.read_bytes()).hexdigest()
                (out / 'build-info.json').write_text(json.dumps(info))
                with self.assertRaises(ValueError):
                    audit.audit_site(out)

    def test_svg_rejects_raster_script_and_remote_resources(self):
        base = build.render(self.data)['assets/hero.svg']
        for extra in ['<image href="data:image/png;base64,AAAA"/>', '<script/>', '<foreignObject/>', '<path onclick="x()"/>', '<path fill="url(https://evil.example)"/>']:
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / 'x.svg'
                target.write_text(base.replace('</svg>', extra + '</svg>'))
                with self.assertRaises(ValueError):
                    audit.audit_svg(target)


if __name__ == '__main__':
    unittest.main()
