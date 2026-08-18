# ClaimCI-Demo no-manifest pilot fixtures

## Purpose

ClaimCI-Demo will hold five tiny, passive evidence catalogs that exercise the
merged ClaimCI zero-configuration path without `research.yaml`. A future pilot
run activates exactly one catalog through a scenario-local marker change and
the scenario's documented pull-request title. The hosted service must discover
the claim and evidence from ordinary repository data; it receives no
ClaimCI-specific manifest and executes no repository code.

## Repository shape

The repository keeps its existing GitHub workflow and advisory Review policy.
The root `research.yaml` and the legacy root evidence files are removed so they
cannot silently restore the advanced-manifest path or collide with the new
catalog.

Permanent fixtures live under:

```text
pilot-fixtures/
  README.md
  scenarios.json
  complete-supported/
  not-supported/
  insufficient-evidence/
  mapping-needed/
  partial/
```

Each scenario directory contains an `activation.txt` marker with the inert
value `inactive`. To run a hosted E2E, create a short-lived branch from main,
change only that scenario's marker to a unique non-secret token, and open a PR
using the exact title in `scenarios.json`. The marker is passive data and has no
semantic role in the Audit.

`scenarios.json` is the machine-readable catalog for exact titles, expected
states, deterministic verdicts, mapping prompts, missing evidence, and fixture
paths. The Markdown guide refers to this catalog without embedding lines that
look like additional scientific claims. That keeps catalog maintenance PRs
from accidentally activating scenarios.

## Scenario contracts

All metrics are unique across the catalog. Every relevant artifact filename
contains its metric plus explicit baseline/candidate tokens; JSONL dataset
paths also contain train/eval tokens. ClaimCI can therefore scope each PR claim
to one catalog even though all five coexist on main.

| Scenario | Metric | Baseline value | Candidate value | Expected public state | Deterministic result |
| --- | --- | ---: | ---: | --- | --- |
| complete-supported | accuracy | 0.60 | 0.70 | COMPLETE | SUPPORTED |
| not-supported | f1 | 0.50 | 0.70 | COMPLETE | NOT_SUPPORTED |
| insufficient-evidence | precision | 0.50 | 0.65 | COMPLETE | INSUFFICIENT_EVIDENCE |
| mapping-needed | recall | 0.55 | 0.70 | MAPPING_NEEDED | none before approval |
| partial | auc | 0.60 | 0.75 | PARTIAL | none |

### COMPLETE / SUPPORTED

The accuracy catalog has three baseline runs and three candidate runs, equal
declared compute proxies, aligned evaluation records, and no exact canonical
train/eval overlap. The supplied values match the PR claim. The real Audit is
expected to return `SUPPORTED`; Research Review is present only as advisory
interpretation.

### COMPLETE / NOT_SUPPORTED

The f1 catalog has balanced run evidence, aligned clean datasets, and a claimed
increase, but the candidate's declared compute proxy is three times the
baseline proxy. The real Audit is expected to return `NOT_SUPPORTED` while the
Research Review remains advisory and cannot replace that verdict.

### COMPLETE / INSUFFICIENT_EVIDENCE

The precision catalog is otherwise fair and clean, but supplies only one
candidate run. With no invalidating finding, the real Audit is expected to
return `INSUFFICIENT_EVIDENCE`. This remains a deterministic completed result,
not `PARTIAL` and not `UNAVAILABLE`.

### MAPPING_NEEDED

The recall catalog provides every required artifact slot but two equally
ranked candidate result files. ClaimCI must ask the bounded candidate-results
question before deterministic execution. No deterministic verdict or advisory
interpretation exists until a user choice is reconstructed and explicitly
approved through `RepoMapping.approve()` by the hosted runner.

### PARTIAL

The auc catalog intentionally omits candidate evaluation data. No available
choice can complete the required native Audit inputs, so ClaimCI must report a
typed missing-evidence `PARTIAL` result rather than offer an unhelpful mapping
question.

## Passive formats

- Results use supported CSV and JSON shapes with literal run/seed/metric data.
- Configs use supported YAML and TOML scalar/mapping shapes.
- Train and evaluation data use UTF-8 JSONL and are passed byte-for-byte to the
  existing deterministic Audit.
- No fixture downloads data, imports repository modules, invokes scripts,
  evaluates selectors from untrusted text, or relies on generated identity.

The fixtures are deliberately small. Dataset records carry stable literal IDs;
evaluation alignment and exact overlap are intentional and documented.

## Validation

A committed standard-library unittest exercises the catalog against a caller-
provided checkout of the exact current ClaimCI core. It simulates each future
PR by copying the repository to a temporary head, changing one marker, and
supplying the catalog title as trusted PR metadata. The test then runs:

1. `discover_repository()` with a real base/head pair;
2. registered passive adapter extraction;
3. `planning_request_from_discovery()`;
4. `plan_ephemeral_audit()`;
5. `run_unified_analysis()` where the state permits deterministic execution.

The assertions require one discovered claim, claim-scoped artifact and mapping
paths, the exact expected planning/public state, real deterministic verdicts,
advisory-only Review output, a bounded two-choice mapping question, typed
missing evidence, no `research.yaml`, and empty scratch cleanup. The fake Review
provider exists only in the test process; it cannot create deterministic
authority.

## Non-goals

- No permanent scenario branches or scenario PRs are created in this change.
- No ClaimCI or ClaimCI-Web code is changed or special-cased.
- No hosted service, GitHub App, provider, workflow, or deployment is changed.
- No mapping is auto-approved and no missing evidence is fabricated.
- This PR does not merge itself.
