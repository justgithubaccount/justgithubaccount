# Public source and copy review

All content describes code, not running services, paid deliveries or customers.
The three source repositories were anonymously accessible on 2026-10-30 and
reported MIT licensing. Exact source links are generated from the manifest.

| Project | Source revision proposed for this V1 | Evidence supporting the description |
| --- | --- | --- |
| GitOps platform | `8f4f31226fd591ad027750fd65e66385db58cb55` | README plus development and smoke Kustomize roots: Argo CD desired state and environment boundaries |
| Cloud infrastructure | `7e0bca62bc4a0f69f314769bac3964acda275de7` | README, Terraform configuration and smoke workflow: provisioning, bootstrap and bounded lifecycle |
| Python application | `899ba6434745390c44c6965a0ebe48f3515a7170` | README, API routes and provider client: project history, provider errors and telemetry |

The earlier brief referenced `c8b9b68cb5b800b247c0ee8b1cc1e7770c9b57d1`,
`e62d0caa9a848b2b4fe52db339ea7f3338b3af3e` and
`9a10e779a5940213ca3d75de2495dc1e27f06f21` respectively. Current main revisions
have changed materially. That difference is **DRIFT_FOUND against the earlier
snapshot**, not silently substituted approval. This local draft proposes the
newer inspected snapshots for source/content review. It does not widen the
three-repository allowlist or authorize publication.

The public first name comes from the existing intro README at
`c2c8b19fd010d8a52b4c2b276a30a032cb4e6fc7`. No family name, email, social handle,
customer identity or marketplace link is inferred. The headline is editorial
positioning; the engineering-focus section summarizes the linked code, not a
commercial offer. Contact and current sellable service packages are omitted.

Source visibility and revision are verified by `scripts/verify_sources.py`;
description accuracy also requires human review. A source-check PASS does not
establish source CI health, runtime availability, rights to legacy imagery,
customer acceptance, publication, attention, inquiries or revenue.
