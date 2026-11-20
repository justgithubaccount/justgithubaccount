"""Offline smoke checks for the standalone anonymous orbital experiment.

Run: python3 experiments/anonymous-orbits/check.py

This checks source invariants only. It is not a browser/CI/deployment acceptance.
"""
from __future__ import annotations

from pathlib import Path
import math
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SVG_NS = "{http://www.w3.org/2000/svg}"


def require(test: bool, message: str) -> None:
    if not test:
        raise AssertionError(message)


def inspect_svg(filename: str, node_class: str, expected_box: str) -> None:
    source = (ROOT / filename).read_text(encoding="utf-8")
    root = ET.fromstring(source)
    require(root.tag == f"{SVG_NS}svg", f"{filename}: invalid SVG root")
    require(root.attrib.get("viewBox") == expected_box, f"{filename}: unexpected viewBox")

    title = root.find(f"{SVG_NS}title")
    desc = root.find(f"{SVG_NS}desc")
    require(title is not None and (title.text or "").strip(), f"{filename}: missing title")
    require(desc is not None and (desc.text or "").strip(), f"{filename}: missing description")
    require(root.attrib.get("aria-labelledby") == "title desc", f"{filename}: missing accessible labels")

    css = root.find(f"{SVG_NS}style")
    require(css is not None and css.text is not None, f"{filename}: missing CSS")
    require("@keyframes " in css.text, f"{filename}: missing animation")
    require("prefers-reduced-motion:reduce" in css.text, f"{filename}: missing reduced motion")
    require("animation:none!important" in css.text, f"{filename}: reduced-motion animation not disabled")

    elements = list(root.iter())
    nodes = [
        e for e in elements
        if e.tag == f"{SVG_NS}g" and node_class in e.attrib.get("class", "").split()
    ]
    require(len(nodes) == 6, f"{filename}: expected exactly six neutral nodes")
    numbers = sorted(
        (t.text or "").strip()
        for n in nodes
        for t in n.iter(f"{SVG_NS}text")
        if t.attrib.get("class") == "node-num"
    )
    require(numbers == [f"{i:02d}" for i in range(1, 7)], f"{filename}: missing numbered nodes")

    disallowed_tags = {"script", "foreignObject", "iframe", "image", "a"}
    require(
        not any(e.tag.rsplit("}", 1)[-1] in disallowed_tags for e in elements),
        f"{filename}: disallowed interactive or external SVG element",
    )
    scan = source.replace("http://www.w3.org/2000/svg", "")
    require(not re.search(r"@import\b|https?://|javascript:|data:", scan, re.I),
            f"{filename}: external/import resource or executable URL")
    require(not any("href" in key.lower() for e in elements for key in e.attrib),
            f"{filename}: unexpected SVG link")
    # Only fragment paint references are allowed; any other CSS url() is rejected.
    url_values = re.findall(r"url\(\s*([^)]*)\)", css.text, re.I)
    require(all(v.strip(" \"'").startswith("#") for v in url_values),
            f"{filename}: external CSS resource")

    center_circle = [
        e for e in elements
        if e.tag == f"{SVG_NS}circle" and e.attrib.get("fill") == "#0b203b"
    ]
    require(len(center_circle) == 1, f"{filename}: central disk missing")
    center_radius = float(center_circle[0].attrib["r"])
    ellipses = [
        e for e in elements
        if e.tag == f"{SVG_NS}ellipse" and "orbit" in e.attrib.get("class", "").split()
    ]
    require(bool(ellipses), f"{filename}: missing orbit")
    inner_minor = min(min(float(e.attrib["rx"]), float(e.attrib["ry"])) for e in ellipses)
    # Half-diagonal of a 70x78 card is a safe conservative bound for both scenes.
    require(inner_minor - math.hypot(35, 39) > center_radius,
            f"{filename}: orbital cards can intersect the central disk")


def main() -> None:
    inspect_svg("orbit.svg", "satellite", "0 0 1200 600")
    inspect_svg("orbit-mobile.svg", "mobile-node", "0 0 600 600")
    desktop = (ROOT / "orbit.svg").read_text(encoding="utf-8")
    require(all(f"animation:{k} {t}s" in desktop
                for k, t in (("outer", 42), ("middle", 30), ("inner", 20))),
            "desktop: three independent speeds absent")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    require('content="noindex,nofollow"' in html, "HTML: not marked noindex")
    require('data="orbit.svg"' in html and 'data="orbit-mobile.svg"' in html,
            "HTML: missing responsive local SVG references")
    require("max-width:640px" in html, "HTML: missing mobile breakpoint")
    require(not re.search(r"<script\b|https?://(?!127\.0\.0\.1)|@import\b", html, re.I),
            "HTML: disallowed active or remote resource")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require("<picture>" in readme and 'srcset="./orbit-mobile.svg"' in readme
            and 'src="./orbit.svg"' in readme, "README: responsive GitHub embed missing")
    print("PASS: XML, 6+6 nodes, orbits/core separation, reduced-motion, no external assets, HTML/README preview")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ET.ParseError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
