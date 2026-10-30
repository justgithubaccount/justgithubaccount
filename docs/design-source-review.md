# Visual source review

Inspected all eight original PNG files in
`justgithubaccount/intro-justgithubaccount/consept/`, source commit
`c2c8b19fd010d8a52b4c2b276a30a032cb4e6fc7`. This is a style review, not a claim
that the historical manifesto, old emblems or generated imagery are licensed for
reuse in commercial materials. None of those images is included in this export.

| Actual source | Observed visual language | Original vector interpretation |
| --- | --- | --- |
| `self-vol-1.png` | Near-black navy; blue/violet/pink light; central DNA-like double helix rising from a circular stone opening; small cell/molecule forms; diffuse speckled texture | New parametric two-strand braid, connecting ribs and restrained star field; circular base; no reproduced cell symbols or stone texture |
| `self-vol-2.png` | Cyan/teal organic coil on dark petrol; amber underside; molecular diagrams, rings and small waveforms | Thin cyan connections and orbital ellipses; amber is omitted to keep the primary violet system coherent |
| `self-vol-3-meta-contact.png` | Deep blue/violet clouds, a vast tilted circular structure, tiny human silhouette, a helix and purple particles; strong difference in scale | Tilted intersecting orbital paths and a large isolated hero illustration; no copied spacecraft, figure, clouds or implied product UI |
| `obsidian.png` | Floating rectangular note panels, thin cyan/violet luminous edges, a network of small linked nodes, perspective and shallow-focus depth | Newly drawn connected panels with restrained edge gradients; real text remains in semantic HTML rather than perspective artwork |
| `logo-ver-01.png` | Circular dark frame, central helix with branching flame-like tendrils, surrounding science/cell motifs | Branching curves around the braid; no adopted emblem |
| `logo-ver-02.png` | Single helix inside a dark oval/circular stone aperture; violet/pink upward light | Quiet elliptical base and vertical center of gravity |
| `logo-ver-03.png` | Centered helix, star particles and orbital/scientific symbols inside a circular border | Orbital field and fixed sparse dots; symbols omitted |
| `logo-ver-04.png` | Sharper blue/violet outlines, helix with side branches, scientific ornaments, circular segmented frame | Crisp vector strokes, concentric framing and a new simple two-orbit favicon; no tracing or old logo reuse |

The biological concepts and logo variants contain no usable typography system.
The note image has white sans-serif headings and smaller pale text; it does not
establish a specific font family. The implementation uses local Arial/Helvetica
fallbacks, large plain headings, subdued secondary text and monospace technology
labels. No font or third-party brand identity is inferred from the PNGs.

## Reusable rules

- Opaque navy `#080c1c` grounds every SVG, preserving contrast on GitHub light and
  dark backgrounds. Near-white `#f1f2ff` carries primary text; secondary copy uses
  `#bdc3df`. Violet `#c4b6ff` and cyan `#96dbf5` carry navigation and connections.
- Use one vertical braid as the identity composition, not a generic dashboard.
  Orbit geometry and thin connections unify hero and project surfaces.
- Keep the main headline separate from the artwork. On narrow screens, stack
  illustration and copy; keep each project description in normal document flow.
- Original SVG project cards use the same field and categories as the website,
  with larger system text for GitHub Markdown. A native `picture` source selects
  compact SVG compositions below 600px; every card has meaningful alternative
  text and a nearby normal-text explanation.
- Simplify the PNGs' heavy texture, fog, stone and cinematic glow into lightweight
  paths, circles, ellipses and gradients. No raster, remote font, animation,
  script, foreignObject or traced third-party emblem is included.

This is an original, restrained web interpretation of the observed images.
It intentionally does not reconstruct their raster scenes. Final aesthetic and
rights acceptance remains with the operator; visual QA is evidence for review.
