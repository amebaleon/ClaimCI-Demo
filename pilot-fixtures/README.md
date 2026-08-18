# ClaimCI hosted pilot fixtures

This catalog provides five passive, deterministic evidence packs for real
no-manifest ClaimCI pull-request tests. All template packs remain on `main` as
inert `.fixture` blobs. They are deliberately not eligible artifacts for
ClaimCI Discovery.

## Activate a scenario

1. Create a short-lived branch from current `main`.
2. Choose one scenario ID from `scenarios.json`.
3. Create `pilot-fixtures/active/` only on that branch.
4. For every entry in the selected scenario's `materialization` list, copy the
   template bytes unchanged from `template` to `path`. Do not parse, generate,
   or reinterpret the content.
5. Add `pilot-fixtures/active/activation.txt` with the selected scenario ID and
   a unique, non-secret E2E run ID.
6. Confirm that no other file exists under `pilot-fixtures/active/`.
7. Use the scenario's exact `pr_title` value as the pull-request title and keep
   the PR description free of additional scientific claims.
8. Open the PR and wait for the hosted GitHub App to publish the unified
   ClaimCI result.

Never add `research.yaml` for these runs. Do not edit template or materialized
evidence bytes. Close the temporary PR and delete its branch after the E2E; do
not merge an activated `pilot-fixtures/active/` directory into `main`.

The repository intentionally contains no legacy manifest-based ClaimCI Actions
workflow. Hosted pilot PRs rely on the installed ClaimCI GitHub App.

## Expected outcomes

| Scenario ID | Public state | Deterministic verdict | Research Review |
| --- | --- | --- | --- |
| `complete-supported` | `COMPLETE` | `SUPPORTED` | advisory, complete |
| `not-supported` | `COMPLETE` | `NOT_SUPPORTED` | advisory, complete |
| `insufficient-evidence` | `COMPLETE` | `INSUFFICIENT_EVIDENCE` | advisory, complete |
| `mapping-needed` | `MAPPING_NEEDED` | none before explicit approval | not run before mapping |
| `partial` | `PARTIAL` | none | not run |

`scenarios.json` is authoritative for exact titles, template-to-active byte
copies, thresholds, mapping choices, and intentionally missing evidence. The
templates contain only passive CSV, JSON, YAML, TOML, and JSONL data. ClaimCI
must never execute repository content.
