# Public source and copy review

All content describes code, not running services, paid deliveries or customers.
The three source repositories were anonymously accessible on 2026-10-30 and
reported MIT licensing. Exact source links are generated from the manifest.

| Project | Source revision proposed for this V1 | Evidence supporting the description |
| --- | --- | --- |
| GitOps platform | `8f4f31226fd591ad027750fd65e66385db58cb55` | README plus development and smoke Kustomize roots: Argo CD desired state and environment boundaries |
| Cloud infrastructure | `cb7c88f84e9f796e4725fc0a218fe68e3785a72e` | README, Terraform configuration and smoke workflow: provisioning, bootstrap and bounded lifecycle |
| Python application | `899ba6434745390c44c6965a0ebe48f3515a7170` | README, API routes and provider client: project history, provider errors and telemetry |

The earlier brief referenced `c8b9b68cb5b800b247c0ee8b1cc1e7770c9b57d1`,
`e62d0caa9a848b2b4fe52db339ea7f3338b3af3e` and
`9a10e779a5940213ca3d75de2495dc1e27f06f21` respectively. Current main revisions
have changed materially. That difference is **DRIFT_FOUND against the earlier
snapshot**, not silently substituted approval. This local draft proposes the
newer inspected snapshots for source/content review. It does not widen the
three-repository allowlist or authorize publication.

The authorized source refresh on 2026-10-30 replaces the infrastructure pin
`7e0bca62bc4a0f69f314769bac3964acda275de7` with the verified public main revision
`cb7c88f84e9f796e4725fc0a218fe68e3785a72e`. The one-commit comparison updates
operator contracts, tooling and documentation. The cited Terraform configuration
and smoke workflow are unchanged; the updated README still supports provisioning,
Argo CD bootstrap and bounded cleanup. The portfolio description is unchanged.

## FastAPI upstream review — 2026-10-30

The public FastAPI default branch advanced from the pinned
`899ba6434745390c44c6965a0ebe48f3515a7170` to
`c42b365e44cfa8c3869cb347cc9f5188fffd0e62`.
The [one-commit comparison](https://github.com/justgithubaccount/app-poly-gitops-fastapi/compare/899ba6434745390c44c6965a0ebe48f3515a7170...c42b365e44cfa8c3869cb347cc9f5188fffd0e62)
changes tooling/dependencies and removes an unused `ProjectMemory` import,
instance and helper. README clarifies that SQLModel is the project/history store
and that behavior integrations are optional scaffolding. This is upstream
`DRIFT_FOUND`, while the pinned commit and all its cited files remain verifiable.

The cited files were inspected at both exact revisions:

| Existing public draft claim | Evidence after comparison |
| --- | --- |
| Project-scoped conversations and stored transcripts | `app/api.py` still creates/lists projects, stores successful replies in `ChatHistoryDB` and reads project history through SQLModel |
| Provider failures handled separately from successful history | The provider call precedes history writes; `LLMProviderError` returns HTTP 502. `app/core/llm_client.py` is byte-identical and still rejects failed/malformed provider replies |
| OpenTelemetry instrumentation | API counters and available trace/span IDs remain; the unchanged provider client retains traces and metrics |

The draft claims remain accurate for the pinned snapshot and are not contradicted
by this upstream change. No pin, commercial copy, visuals or generated output is
changed, and no running service, Notion-backed storage or customer result is
claimed. This code comparison does not establish runtime or upstream CI health.

## Verification and publication boundaries

The public first name comes from the existing intro README at
`c2c8b19fd010d8a52b4c2b276a30a032cb4e6fc7`. No family name, email, social handle,
customer identity or marketplace link is inferred. The headline is editorial
positioning; the engineering-focus section summarizes the linked code, not a
commercial offer. Contact and current sellable service packages are omitted.

Source visibility, license, exact pinned commit and evidence availability are
mandatory checks in `scripts/verify_sources.py`. Upstream movement is reported
separately as `DRIFT_FOUND`; an unavailable branch observation is `UNKNOWN`,
without erasing verified pinned evidence. Neither automatically updates a pin.
Description accuracy also requires human review. A source-check PASS does not
establish source CI health, runtime availability, rights to legacy imagery,
customer acceptance, publication, attention, inquiries or revenue.
