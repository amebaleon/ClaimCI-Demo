# ClaimCI-Demo no-manifest pilot fixtures implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the manifest-dependent ClaimCI-Demo root fixture with five permanently coexisting passive scenario catalogs that exercise current ClaimCI zero-configuration analysis through real PR metadata.

**Architecture:** One machine-readable catalog defines exact PR titles and expected outcomes. Metric-specific filenames make every fixture pack independently discoverable inside one repository; a future PR changes only the selected pack's inert marker. A standard-library unittest simulates those PRs against pinned ClaimCI core, exercises real Discovery/adapters/planner/Audit/unified Review, and proves the intended state rather than a missing threshold or cross-scenario collision.

**Tech Stack:** Git, Python 3.11+ standard library unittest, merged ClaimCI core at `c54beaf5cd06d57425eeed383942bf44392ede6f`, passive CSV/JSON/YAML/TOML/JSONL.

**Spec:** `docs/superpowers/specs/2026-08-18-claimci-demo-no-manifest-pilot-fixtures-design.md`

## Global constraints

- Work only in `C:\ClaimCI-Demo-worktrees\no-manifest-pilot-fixtures` on `codex/no-manifest-pilot-fixtures`.
- Do not modify ClaimCI, ClaimCI-Web, their worktrees, or their Git state.
- Delete root `research.yaml`; do not add another manifest anywhere.
- Do not change `.github/workflows/claimci.yml` or `.claimci/review.yaml`.
- Keep all five fixture packs permanently coexisting on main; create no permanent scenario branches.
- Every title contains an explicit metric baseline-to-candidate pair plus an explicit unitless `improved by at least N` clause.
- Every discovered `AuditClaimSpec.minimum_absolute_improvement` must be non-null.
- ClaimCI must execute no repository code; fixture directories contain passive data only.
- Only the real Audit may produce deterministic authority; fake Review output remains advisory.
- Do not merge the Draft PR.

---

### Task 1: Add the executable catalog contract first

**Files:**
- Create: `tests/test_pilot_fixtures.py`
- Create: `pilot-fixtures/scenarios.json`
- Create: `pilot-fixtures/README.md`
- Delete: `research.yaml`
- Delete: `baseline-config.yaml`
- Delete: `baseline-eval.jsonl`
- Delete: `baseline-results.json`
- Delete: `baseline-train.jsonl`
- Delete: `candidate-config.yaml`
- Delete: `candidate-eval.jsonl`
- Delete: `candidate-results.json`
- Delete: `candidate-train.jsonl`

**Interfaces:**
- Consumes: `CLAIMCI_CORE_ROOT`, an exact checkout at `c54beaf5cd06d57425eeed383942bf44392ede6f`.
- Produces: `SCENARIOS`, a five-entry JSON object whose entries carry `metric`, `pr_title`, `expected_public_state`, `expected_deterministic_verdict`, `scenario_path`, and state-specific expectations.

- [ ] **Step 1: Write the failing end-to-end unittest before any catalog or fixture data**

  Create `tests/test_pilot_fixtures.py` with literal expected scenario IDs and the following real pipeline helpers:

  ```python
  EXPECTED_CORE_SHA = "c54beaf5cd06d57425eeed383942bf44392ede6f"
  EXPECTED_SCENARIOS = {
      "complete-supported": ("complete", "SUPPORTED"),
      "not-supported": ("complete", "NOT_SUPPORTED"),
      "insufficient-evidence": ("complete", "INSUFFICIENT_EVIDENCE"),
      "mapping-needed": ("mapping_needed", None),
      "partial": ("partial", None),
  }
  ```

  The test must:

  1. require `CLAIMCI_CORE_ROOT`, verify `git rev-parse HEAD` equals the pinned SHA, and prepend that checkout to `sys.path` before importing ClaimCI;
  2. assert no file named `research.yaml` exists anywhere in the repository;
  3. load `pilot-fixtures/scenarios.json`, require exactly the five literal IDs above, and require each referenced path/marker to exist;
  4. copy the repository into temporary base/head roots excluding `.git` and `__pycache__`, mutate only the selected `activation.txt`, and pass the catalog title as `pr_title` to `discover_repository()`;
  5. require exactly one discovered metric-improvement claim and build normalized evidence only from its routed `RESULTS`, `CONFIG`, and `DATASET` artifacts using `PassiveArtifact` plus `extract_registered_artifact()`;
  6. call `planning_request_from_discovery()` and require `request.audit_claim.minimum_absolute_improvement is not None`;
  7. require every scoped artifact, evidence item, and mapping binding to begin with that scenario's directory;
  8. call `plan_ephemeral_audit()` and `run_unified_analysis()` with a temporary scratch root and a fake synthesis-only provider whose output has no verdict field.

  For `mapping-needed`, require the question prompt to equal `Which file contains the candidate results?`, require exactly two choices, and require their labels to be the two cataloged candidate result paths. For `partial`, require a non-null threshold, no mapping question, one missing `DATASET` item for the `CANDIDATE` role, an existing candidate-train binding, and no candidate-eval binding. For complete states, require `AnalysisState.COMPLETE`, the literal deterministic verdict, one advisory provider call, and an empty scratch directory.

- [ ] **Step 2: Run the test to verify RED**

  Run from the Demo worktree:

  ```powershell
  $env:CLAIMCI_CORE_ROOT='C:\ClaimCI-worktrees\hosted-core-v03'
  $env:PYTHONDONTWRITEBYTECODE='1'
  python -B -m unittest discover -s tests -p 'test_pilot_fixtures.py' -v
  ```

  Expected: FAIL because `pilot-fixtures/scenarios.json` and the scenario roots do not exist and root `research.yaml` still exists. Confirm the failure is behavioral, not an import or syntax error.

- [ ] **Step 3: Add the exact catalog and human activation guide**

  Create `pilot-fixtures/scenarios.json` with these exact titles and expectations:

  | ID | Exact `pr_title` | State | Verdict | Threshold |
  | --- | --- | --- | --- | ---: |
  | complete-supported | `accuracy improved from 0.60 to 0.70; improved by at least 0.05` | complete | SUPPORTED | 0.05 |
  | not-supported | `f1 improved from 0.50 to 0.70; improved by at least 0.10` | complete | NOT_SUPPORTED | 0.10 |
  | insufficient-evidence | `precision improved from 0.50 to 0.65; improved by at least 0.10` | complete | INSUFFICIENT_EVIDENCE | 0.10 |
  | mapping-needed | `recall improved from 0.55 to 0.70; improved by at least 0.10` | mapping_needed | null | 0.10 |
  | partial | `auc improved from 0.60 to 0.75; improved by at least 0.10` | partial | null | 0.10 |

  `pilot-fixtures/README.md` must instruct future operators to branch from main, change only the selected scenario's `activation.txt` from `inactive` to a unique non-secret token, copy the exact title from `scenarios.json`, leave the PR body free of additional scientific claims, and never add `research.yaml`. Do not repeat an exact activation title in Markdown, because changed Markdown is a claim source.

- [ ] **Step 4: Remove the manifest-dependent root fixture**

  Delete root `research.yaml` and its eight root config/results/dataset files. Preserve `.claimci/review.yaml` and `.github/workflows/claimci.yml` byte-for-byte.

---

### Task 2: Implement all five passive evidence packs

**Files:**
- Create: `pilot-fixtures/complete-supported/*`
- Create: `pilot-fixtures/not-supported/*`
- Create: `pilot-fixtures/insufficient-evidence/*`
- Create: `pilot-fixtures/mapping-needed/*`
- Create: `pilot-fixtures/partial/*`
- Test: `tests/test_pilot_fixtures.py`

**Interfaces:**
- Consumes: the exact catalog schema and validation helper from Task 1.
- Produces: metric-scoped passive files selected entirely through validated filename role/split mappings.

- [ ] **Step 1: Add COMPLETE / SUPPORTED data**

  Under `pilot-fixtures/complete-supported/`, create `activation.txt` with `inactive`; three-run baseline and candidate accuracy CSVs with means `0.60` and `0.70`; YAML configs with equal `training_steps`, `batch_size`, `epochs`, model, learning rate, train identity, and eval identity; and four JSONL datasets. Baseline and candidate eval files must contain the same two canonical records, while neither role's train data overlaps its eval data.

- [ ] **Step 2: Add COMPLETE / NOT_SUPPORTED data**

  Under `pilot-fixtures/not-supported/`, create the marker; three-run baseline and candidate f1 JSON results with means `0.50` and `0.70`; TOML configs identical except baseline `training_steps = 100` and candidate `training_steps = 300` with equal batch size; and clean aligned JSONL datasets. The sole invalidating behavior is the 3.0x declared compute proxy.

- [ ] **Step 3: Add COMPLETE / INSUFFICIENT_EVIDENCE data**

  Under `pilot-fixtures/insufficient-evidence/`, create the marker; a three-run precision baseline CSV with mean `0.50`; a one-run candidate CSV at `0.65`; equal YAML configs; and clean aligned JSONL datasets. No invalidating finding may be present, so the single candidate run is the reason for `INSUFFICIENT_EVIDENCE`.

- [ ] **Step 4: Add MAPPING_NEEDED data**

  Under `pilot-fixtures/mapping-needed/`, create the marker, one recall baseline JSON result, two equally ranked and unambiguously parseable candidate JSON result files, equal TOML configs, and all four clean aligned JSONL datasets. Both candidate result paths must carry the same metric/role tokens and artifact confidence so Discovery emits exactly the bounded two-choice candidate-results question.

- [ ] **Step 5: Add PARTIAL data**

  Under `pilot-fixtures/partial/`, create the marker; valid auc baseline/candidate CSV results; equal YAML configs; baseline train/eval JSONL and candidate train JSONL; intentionally omit candidate eval JSONL. No second plausible dataset choice may exist.

- [ ] **Step 6: Run the real-core test to verify GREEN**

  Run the same unittest command from Task 1. Expected: all five scenario subtests PASS, with real deterministic verdicts for the three complete scenarios and the exact mapping/partial causes for the other two.

- [ ] **Step 7: Mutation-check the load-bearing assertions**

  Temporarily change one title threshold field to omit the second clause and run the focused test; it must FAIL at the non-null threshold assertion. Restore it. Temporarily make the two recall candidate result paths non-ambiguous and rerun; it must FAIL at the exact two-choice question assertion. Restore it. Temporarily add the missing auc candidate eval file and rerun; it must FAIL at the candidate-eval missing assertion. Restore the approved tree and rerun GREEN.

- [ ] **Step 8: Commit the fixture implementation**

  ```powershell
  git add --all
  git diff --cached --check
  git commit -m "feat: add no-manifest pilot fixtures"
  ```

---

### Task 3: Full verification and Draft PR

**Files:**
- Create: `docs/verification/no-manifest-pilot-fixtures.md`
- Modify only if evidence requires it: `pilot-fixtures/README.md`, `pilot-fixtures/scenarios.json`, `tests/test_pilot_fixtures.py`

**Interfaces:**
- Consumes: the frozen fixture catalog and pinned real-core test.
- Produces: a reproducible verification record and one Draft PR; no merge.

- [ ] **Step 1: Run fresh fixture verification**

  Run the focused unittest with `CLAIMCI_CORE_ROOT` and `PYTHONDONTWRITEBYTECODE=1`. Record test count, exact core SHA, each planning/public state, each deterministic verdict, provider-call counts, mapping prompt/choice labels, missing evidence tuple, and scratch cleanup.

- [ ] **Step 2: Run the full current ClaimCI core suite without changing it**

  From `C:\ClaimCI-worktrees\hosted-core-v03`:

  ```powershell
  $env:PYTHONDONTWRITEBYTECODE='1'
  python -B -m pytest -q -p no:cacheprovider
  python -B -m compileall -q claimci
  git status --short
  ```

  Require the exact core checkout to remain clean at `c54beaf5cd06d57425eeed383942bf44392ede6f`.

- [ ] **Step 3: Verify Demo scope and records**

  Require:

  ```powershell
  git diff --check origin/main...HEAD
  git status --short
  git diff --name-status origin/main...HEAD
  Get-ChildItem -Recurse -Filter research.yaml
  ```

  Confirm no `research.yaml`, no changes to `.claimci/review.yaml` or `.github/workflows/claimci.yml`, no fixture code inside scenario directories, and no ClaimCI/ClaimCI-Web changes.

- [ ] **Step 4: Write and verify the milestone record**

  Add `docs/verification/no-manifest-pilot-fixtures.md` with the exact commands/results and expected future activation procedure. Avoid embedding an activation title as a Markdown claim line; point to `scenarios.json` instead. Run the focused test, `git diff --check`, and status again.

- [ ] **Step 5: Commit final records**

  ```powershell
  git add docs/verification/no-manifest-pilot-fixtures.md
  git diff --cached --check
  git commit -m "docs: record pilot fixture verification"
  ```

- [ ] **Step 6: Push and open one Draft PR**

  Push `codex/no-manifest-pilot-fixtures` to `origin` and open a Draft PR against `main`. The PR description must list all five states, core SHA, test evidence, no-manifest/no-execution guarantees, and the future marker/title activation procedure. Do not create permanent scenario branches and do not merge.

- [ ] **Step 7: Verify remote PR state**

  Read back the PR URL, head SHA, base/head refs, Draft flag, changed-file list, checks, and mergeability. Report any pending remote checks accurately without waiting indefinitely.
