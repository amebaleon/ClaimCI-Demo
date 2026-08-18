# ClaimCI-Demo no-manifest pilot fixtures

## Purpose

ClaimCI-Demo will hold five tiny, passive evidence catalogs that exercise the
merged ClaimCI zero-configuration path without `research.yaml`. A future pilot
PR materializes exactly one catalog into supported evidence paths and uses the
scenario's documented title. The hosted service receives no ClaimCI-specific
manifest and executes no repository code.

## Repository shape and isolation boundary

Permanent fixture bytes live under inert ordinal names:

```text
pilot-fixtures/
  README.md
  scenarios.json
  templates/
    complete-supported/*.fixture
    not-supported/*.fixture
    insufficient-evidence/*.fixture
    mapping-needed/*.fixture
    partial/*.fixture
```

The `.fixture` names contain no result/config/dataset classification token and
have no supported evidence suffix. Current ClaimCI Discovery therefore cannot
treat dormant catalogs as artifacts. Their original data format is declared
in the catalog, but ClaimCI does not inspect the template bytes.

`pilot-fixtures/active/` is absent from `main`. A short-lived E2E branch copies
the selected scenario's template bytes, without parsing or transformation, to
the exact supported paths in that scenario's `materialization` list. It also
adds an inert `activation.txt` carrying a scenario ID and non-secret run ID.
The PR must contain exactly one active materialization and use the exact title
in `scenarios.json`. The active directory is never merged to main.

This topology is required by current ClaimCI: with a single PR-title claim,
unmatched result candidates remain eligible for that claim. Keeping multiple
supported result packs permanently discoverable would therefore create
cross-scenario mapping ambiguity. Isolation is achieved in Demo data, without
special-casing or weakening ClaimCI Core.

## Hosted workflow cutover

The legacy `.github/workflows/claimci.yml` invokes the external manifest Audit
whose default input is root `research.yaml`. Both are removed. Future pilot
activation PRs rely solely on the installed hosted ClaimCI GitHub App. The
advisory `.claimci/review.yaml` policy remains repository data for the hosted
path; no replacement Actions workflow or secret is introduced.

## Claim and scenario contracts

Every exact PR title contains both an explicit metric baseline-to-candidate
pair and an explicit unitless `improved by at least N` clause. Consequently
every discovered `AuditClaimSpec.minimum_absolute_improvement` is non-null
before planning evaluates mappings or missing evidence.

| Scenario | Metric | Baseline | Candidate | Public state | Deterministic result |
| --- | --- | ---: | ---: | --- | --- |
| complete-supported | accuracy | 0.60 | 0.70 | COMPLETE | SUPPORTED |
| not-supported | f1 | 0.50 | 0.70 | COMPLETE | NOT_SUPPORTED |
| insufficient-evidence | precision | 0.50 | 0.65 | COMPLETE | INSUFFICIENT_EVIDENCE |
| mapping-needed | recall | 0.55 | 0.70 | MAPPING_NEEDED | none before approval |
| partial | auc | 0.60 | 0.75 | PARTIAL | none |

The supported scenario has balanced three-run evidence, equal declared compute
proxies, aligned evaluation records, and no exact train/eval overlap. The
not-supported scenario differs only in its 3.0x candidate declared compute
proxy. The insufficient-evidence scenario has one candidate run and no
invalidating finding. The mapping-needed scenario has exactly two equally
ranked candidate-results paths. The partial scenario intentionally omits only
candidate eval evidence.

Research Review is advisory and runs only after a real deterministic Audit for
the three completed states. It does not run before mapping or for the partial
state and cannot create or replace deterministic authority.

## Passive formats and trust

- Results materialize as supported CSV or JSON run evidence.
- Configs materialize as supported YAML or TOML values.
- Train/eval datasets materialize as UTF-8 JSONL and are passed byte-for-byte
  to the existing deterministic Audit.
- The catalog maps inert source blobs to exact destination paths; validation
  proves source and active bytes are identical.
- No download, generated dataset identity, row reinterpretation, selector
  execution, repository import, or customer-code execution is permitted.
- `research.yaml` remains absent everywhere.

## Validation

A committed standard-library unittest requires an exact current ClaimCI core
checkout. For each catalog entry it copies the Demo repository to temporary
base/head roots, materializes only the selected pack into the head, supplies
the exact PR title, then runs:

1. `discover_repository()`;
2. registered adapters for relevant passive artifact candidates;
3. `planning_request_from_discovery()`;
4. `plan_ephemeral_audit()`;
5. `run_unified_analysis()` where deterministic execution is possible.

Assertions cover exact byte copies; one discovered claim; non-null threshold;
no dormant template artifact; active-only mappings/evidence; all three real
deterministic verdicts; advisory-only Review; the exact two candidate-results
choices for MAPPING_NEEDED; candidate eval as the sole PARTIAL cause; no
manifest/workflow fallback; and empty materialization scratch cleanup.

## Non-goals

- No permanent scenario branches or activated evidence on main.
- No ClaimCI or ClaimCI-Web change or demo special case.
- No hosted service implementation, deployment, or GitHub App configuration.
- No automatic mapping approval or fabricated missing evidence.
- This Draft PR does not merge itself.
