# Maintaining the public portfolio

`data/public-portfolio.json` is the only editorial input. It is a curated public
projection of three approved code repositories, never their technical authority.
Templates and `scripts/art.py` define presentation. Generated files must not be
edited by hand. Python 3.10+ and its standard library are sufficient; CI uses 3.12.
There are no build-time network calls, package installs or credentials.

```sh
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 scripts/build.py --check
python3 scripts/audit.py
python3 scripts/verify_sources.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory site
```

The last verification command makes anonymous, read-only requests to public
GitHub metadata and exact revision URLs. It separates two questions:

- **Mandatory snapshot verification:** the manifest passes the repository/path
  allowlist, current repository identity/public visibility/MIT metadata match,
  the exact pinned commit resolves to that SHA, and every pinned evidence file
  is accessible and nonempty. Missing or changed metadata, a missing/mismatched
  commit, unavailable/empty evidence or an allowlist violation returns exit 1.
  Rate limiting or network failure during these checks also returns exit 1;
  unavailable evidence is not proof and cannot pass the gate.
- **Advisory upstream observation:** after verifying the snapshot, compare the
  default-branch head with the pin. Output `snapshot_status: VERIFIED` independently
  of `upstream_status`: `VERIFIED` means the head equals the pin; `DRIFT_FOUND`
  means it differs; `UNKNOWN` with `main_sha: null` means the branch observation
  was unavailable or malformed. Drift and unknown observations are reported in
  JSON and stderr but do not invalidate a verified snapshot or change the pin.

Exit 0 means every mandatory snapshot check passed, not that every upstream head
is unchanged. CI uses this same contract. An upstream warning calls for a focused
source/copy review; it does not automatically adopt new code or approve publication.
A human must verify that the copy matches the cited snapshot. Never use upstream
`DRIFT_FOUND` or `UNKNOWN` as a substitute for missing pinned evidence.

The builder creates `README.md`, `assets/*.svg` and the complete `site/` directory.
It uses no time, random seed, machine path or Git working-tree state in output.
`--check` is read only and detects missing, changed and stale generated files.
Generation overwrites only named outputs and never deletes files; remove stale
generated files deliberately after reviewing the failing check.

## Exporting to the website repository

After profile review, use an isolated checkout of the exact website repository:

```sh
python3 scripts/build.py --check
python3 scripts/build.py --pages-dir /path/to/justgithubaccount.github.io
python3 scripts/audit.py --site-only --root /path/to/justgithubaccount.github.io
```

This copies exactly the generated website bytes; it neither pushes nor deploys.
The website repository has no second manifest or content templates. Its validation
script is a byte-identical copy of `scripts/audit.py`; copy updates explicitly.
`build-info.json` records the canonical manifest digest, generator-input digest
and per-file hashes. Compare the export to the reviewed profile commit before
opening its separate Draft PR. Those hashes detect byte drift; they are not
signatures or operator approval. Record the exact profile source commit in the
website PR description after that commit exists remotely.

## Publication gate

The checked-in manifest is `RELEASE_APPROVED` as an operator-authorized
**release-review candidate**, following acceptance of V1 content and design.
This switches the generated HTML to `index, follow`, `robots.txt` to `Allow: /`
and the Profile README link to the intended root Pages URL. It does **not**
create a deployment, prove the root URL is live or authorize a merge.

The generator's `DRAFT` mode remains supported and tested separately: it emits
`noindex, nofollow`, `Disallow: /` and a publication-pending README link.
Canonical/sitemap URLs in either mode identify the intended site, not its
runtime status. Continue using the local HTTP preview before publication.

Merge, Pages configuration/reactivation, actual publication and final public
content/rights/source checks require **separate explicit operator release
authorization**, followed by live root-URL and rendered GitHub profile checks.
There is deliberately no Pages deploy workflow, privileged cross-repository token,
merge automation or runtime dependency. Enabling Pages and merging remain
separate operator decisions. Verify the final live root URL before recording
publication state at its owner.

Do not add clients, performance numbers, prices, offers, contacts, logos or new
source repositories without their own evidence and explicit publication review.
The generic focus section describes the public code; it is not a sellable offer.

## Visual QA recipe

Serve `site/` locally and inspect widths 320, 390, 768, 1024 and 1440px. Verify
anchor navigation, all three evidence disclosures, keyboard focus and the text
overview. Scroll through the whole page so lazy images load before full-page
screenshots. Check the README through GitHub's Markdown renderer, then view it
at mobile and desktop widths on both light and dark surrounds. A local GitHub
Markdown preview does not prove the special profile or GitHub image proxy is live.

The website intentionally uses the dark art direction in either OS theme. SVGs
have their own opaque backgrounds and system fonts; no web fonts, external
resources, scripts, raster payloads or vendor emblems are used.
