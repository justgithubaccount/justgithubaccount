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
            ('<body>', '<body><style>@import "https://evil.example/style.css";</style>'),
            ('<body>', '<body><meta http-equiv="refresh" content="0;url=https://evil.example"/>'),
            ('<img src=', '<img srcset="https://evil.example/image.svg 2x" src='),
            ('<body>', '<body><a href="#work" ping="https://evil.example/log">work</a>'),
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

    def test_svg_rejects_stylesheet_processing_instructions_and_paint_bypasses(self):
        base = build.render(self.data)['assets/hero.svg']
        mutations = [
            '<?xml-stylesheet type="text/css" href="https://evil.example/style.css"?>' + base,
            base.replace('fill="url(#glow)"', 'fill="URL(//evil.example/image.svg#paint)"'),
            base.replace('fill="url(#glow)"', 'fill="u\\72l(//evil.example/image.svg#paint)"'),
            base.replace('role="img"', 'role="img" xml:base="//evil.example/"'),
        ]
        for svg in mutations:
            with self.subTest(svg=svg[:80]), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / 'x.svg'
                target.write_text(svg)
                with self.assertRaises(ValueError):
                    audit.audit_svg(target)

    def test_inventory_cannot_admit_unchecked_files_or_drop_required_metadata(self):
        for mutation in ('added-html', 'omitted-file', 'missing-manifest-hash', 'invalid-generator-hash'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                build.export_pages(self.data, out)
                info = json.loads((out / 'build-info.json').read_text())
                if mutation == 'added-html':
                    payload = '<script src="https://evil.example/script.js"></script>'
                    (out / 'extra.html').write_text(payload)
                    info['files']['extra.html'] = hashlib.sha256(payload.encode()).hexdigest()
                elif mutation == 'omitted-file':
                    del info['files']['llms.txt']
                elif mutation == 'missing-manifest-hash':
                    del info['manifest_sha256']
                else:
                    info['generator_sha256'] = 'not-a-digest'
                (out / 'build-info.json').write_text(json.dumps(info))
                with self.assertRaises(ValueError):
                    audit.audit_site(out)

    def test_stylesheet_rejects_escaped_import_and_string_image_resources(self):
        for css in ['@\\69mport "https://evil.example/style.css";',
                    'body{background-image:image-set("https://evil.example/image.png" 1x)}',
                    '@import "//evil.example/style.css";']:
            with self.subTest(css=css), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                build.export_pages(self.data, out)
                target = out / 'styles.css'
                target.write_text(css + target.read_text())
                info = json.loads((out / 'build-info.json').read_text())
                info['files']['styles.css'] = hashlib.sha256(target.read_bytes()).hexdigest()
                (out / 'build-info.json').write_text(json.dumps(info))
                with self.assertRaises(ValueError):
                    audit.audit_site(out)


    def mutate_export(self, mutate):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            build.export_pages(self.data, out)
            mutate(out)
            info = json.loads((out / 'build-info.json').read_text())
            for name in info['files']:
                info['files'][name] = hashlib.sha256((out / name).read_bytes()).hexdigest()
            (out / 'build-info.json').write_text(json.dumps(info))
            with self.assertRaises(ValueError):
                audit.audit_site(out)

    def test_only_one_exact_local_script_tag_is_allowed(self):
        tag = '<script src="assets/orbital.js" defer></script>'
        replacements = [
            '', tag + tag,
            '<script src="https://evil.example/orbital.js" defer></script>',
            '<script src="//evil.example/orbital.js" defer></script>',
            '<script src="assets/orbital.js?extra" defer></script>',
            '<script src="assets/../assets/orbital.js" defer></script>',
            '<script src="assets/%6frbital.js" defer></script>',
            '<script src="assets/orbital.js" defer async></script>',
            '<script src="assets/orbital.js" defer onload="alert(1)"></script>',
            '<script src="assets/orbital.js" defer>alert(1)</script>',
            '<script type="module" src="assets/orbital.js"></script>',
            '<script src="assets/orbital.js" src="assets/orbital.js" defer></script>',
        ]
        for replacement in replacements:
            with self.subTest(replacement=replacement):
                def mutate(out):
                    p = out / 'index.html'
                    self.assertIn(tag, p.read_text())
                    p.write_text(p.read_text().replace(tag, replacement))
                self.mutate_export(mutate)

    def test_script_tampering_is_rejected_even_with_rehashed_inventory(self):
        def mutate(out):
            p = out / 'assets/orbital.js'
            p.write_text(p.read_text() + '\nfetch("https://evil.example");')
        self.mutate_export(mutate)

    def test_inline_svg_uses_the_same_static_guard(self):
        payloads = [
            '<script>alert(1)</script>', '<foreignObject/>',
            '<path onclick="alert(1)"/>', '<path fill="url(#missing)"/>',
            '<path fill="url(https://evil.example)"/>',
            '<path style="fill:red"/>', '<path id="work"/>',
            '<?xml-stylesheet href="https://evil.example"?>',
            '<g aria-labelledby="missing"/>', '<image href="data:image/png;base64,AAAA"/>',
            '<animate attributeName="opacity"/>', '<path/><svg></svg>',
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                def mutate(out):
                    p = out / 'index.html'
                    p.write_text(p.read_text().replace('</svg>', payload + '</svg>', 1))
                self.mutate_export(mutate)

    def test_unexpected_script_file_is_rejected(self):
        self.mutate_export(lambda out: (out / 'assets/extra.js').write_text('alert(1)'))


if __name__ == '__main__':
    unittest.main()
