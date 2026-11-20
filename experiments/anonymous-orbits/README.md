# Anonymous orbital SVG experiment

Task: [ANON_ORBIT_SVG_DEMO_V1](https://github.com/justgithubaccount/justgithubaccount/issues/6)

An original, anonymous visual experiment, isolated from the generated profile, manifest, and Pages export.

## Preview

Open `index.html` directly or serve this folder using Python's standard-library server:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory experiments/anonymous-orbits
```

Then visit `http://127.0.0.1:8765/`. No package installation or external request is required.

## Design and safety

- Pure SVG and embedded CSS; no JavaScript, personal data, project identifiers, logos, tracking, network requests or dependency on a hosted service.
- Six independent, looping orbits on three elliptical tracks; generic nodes 01–06. Orbit durations 17, 23, 29 seconds with phase offsets.
- Motion stops under `prefers-reduced-motion: reduce`; labels and center remain visible.
- `index.html` has `noindex,nofollow` and references only local `orbit.svg`.
- Static SVG opening and accessibility labels work separately from the HTML page.
- Not connected to the generator or production site. Do not treat Draft PR as published deployment.

## Verification (implementation checklist)
- [ ] Local static HTML/SVG validation.
- [ ] Reduced-motion and mobile browser screenshot QA.
- [ ] GitHub PR CI and independent visual review.
- [ ] Human visual acceptance before any subsequent integration.

Third-party concept reference: `masterkain/masterkain` animated orbital SVG (reference only; no source artwork copied).