# ClaimCI-Demo no-manifest pilot fixtures implementation plan

**Goal:** Keep five passive scenario templates on main while allowing a
short-lived E2E PR to materialize exactly one current-Core-compatible evidence
pack under `pilot-fixtures/active/`.

**Architecture:** `scenarios.json` maps inert ordinal `.fixture` blobs to exact
supported active paths. The committed unittest performs byte-preserving
materialization in a temporary head, supplies the scenario's exact PR title,
and drives real ClaimCI Discovery, adapters, planner, Audit, and advisory
Review. Root `research.yaml` and the legacy manifest workflow are removed.

**Pinned ClaimCI Core:** `c54beaf5cd06d57425eeed383942bf44392ede6f`

**Spec:** `docs/superpowers/specs/2026-08-18-claimci-demo-no-manifest-pilot-fixtures-design.md`

## Constraints

- Work only on `codex/no-manifest-pilot-fixtures` in the isolated Demo worktree.
- Do not modify ClaimCI, ClaimCI-Web, or their Git state.
- Keep `.claimci/review.yaml`; remove only the manifest-based Actions workflow.
- Keep active evidence absent from main and create no permanent scenario branch.
- Every title must expose the numeric pair and unitless absolute threshold.
- Execute no repository content and invent no authority or evidence.
- Do not merge the Draft PR.

## Task 1: RED catalog contract

- [x] Write `tests/test_pilot_fixtures.py` against the pinned real core.
- [x] Verify the original manifest layout fails the no-manifest contract.
- [x] Extend the test for active-only byte materialization and verify it fails
  while the legacy workflow remains.

## Task 2: Inert templates and hosted cutover

- [x] Move all five evidence packs byte-for-byte to ordinal `.fixture` names
  under `pilot-fixtures/templates/<scenario>/`.
- [x] Replace `scenarios.json` with schema v2 materialization records.
- [x] Remove root `research.yaml`, legacy root evidence, and
  `.github/workflows/claimci.yml`.
- [x] Preserve `.claimci/review.yaml` and document hosted GitHub App activation.
- [x] Make the focused real-core test green for all five states.
- [x] Mutation-check threshold, ambiguity, missing candidate eval, and template
  byte-equality assertions, then restore green.
- [x] Commit the scoped fixture implementation.

## Task 3: Verification and Draft PR

- [x] Run the focused fixture test against the exact current core SHA.
- [x] Run the complete ClaimCI core suite and compileall with caches outside the
  core checkout; confirm that checkout remains clean.
- [x] Run Demo unittest discovery, JSON validation, passive-file/scope checks,
  `git diff --check origin/main...HEAD`, and status checks.
- [x] Record commands, outcomes, verdicts, mapping choices, missing evidence,
  byte identity, workflow cutover, and scratch cleanup under
  `docs/verification/no-manifest-pilot-fixtures.md`.
- [x] Commit the verification record on the scoped feature branch.
- [x] Push the branch and open one Draft PR.
- [ ] Read back URL, head/base refs, Draft flag, changed files, checks, and
  mergeability. Do not merge.
