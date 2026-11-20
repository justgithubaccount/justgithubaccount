# Anonymous orbital SVG experiment (study 002)

Task: [ANON_ORBIT_SVG_DEMO_V1](https://github.com/justgithubaccount/justgithubaccount/issues/6)

Standalone, original, non-identifying visual experiment. It is not part of the generated public profile, Pages export or production site.

## Preview

Open `index.html` directly, or serve the directory locally:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory experiments/anonymous-orbits
```

Then visit `http://127.0.0.1:8765/`. Desktop selects `orbit.svg` and viewport widths below 641px select the square `orbit-mobile.svg` composition.

## Behavior

- Desktop: six neutral numbered nodes on three separate elliptical tracks, with opposite pairs and independent 42 / 30 / 20 second orbit durations. Each node is moved by explicit SVG-coordinate CSS transforms along the visible ellipse, preventing unexpected motion-path origin shifts.
- Mobile: square composition with six evenly separated nodes, a common 30-second period, and a readable center.
- Both variants provide accessible SVG titles/descriptions and a static non-overlapping arrangement under `prefers-reduced-motion: reduce`.
- HTML has `noindex,nofollow`. All assets are local. No JavaScript, remote dependencies, scripts, analytics or tracking.
- The artwork is original; the external orbital reference is a conceptual reference only, with no copied assets.

## Delivery status

Draft PR is a review artifact, **not a deployment**. Browser and manual QA are separate from CI and operator acceptance. Do not merge, deploy, or connect it to public surfaces without explicit operator authorization.

Implementation stays isolated under `experiments/anonymous-orbits/`.