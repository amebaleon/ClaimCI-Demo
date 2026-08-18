# No-manifest pilot fixture verification

## Verified scope

- Repository: `amebaleon/ClaimCI-Demo`
- Base: `origin/main` at `45ee0c4fbfe6457a809bd6b609f717da1615a80e`
- Branch: `codex/no-manifest-pilot-fixtures`
- ClaimCI Core: `c54beaf5cd06d57425eeed383942bf44392ede6f`
- Core remote `main` was read immediately before validation and matched the
  pinned checkout.

Root `research.yaml` and its legacy root evidence are absent. The manifest-
based `.github/workflows/claimci.yml` is also absent, so future activation PRs
use the hosted GitHub App path. `.claimci/review.yaml` remains byte-identical
to Demo main at SHA-256
`3d23011167406ca49138572fd2911fc302c1ac64206f5b55cee0c697ed85d76e`.

All five permanent catalogs are inert ordinal `.fixture` files. Main contains
no `pilot-fixtures/active/` directory. The test materializes one catalog at a
time by exact byte copy to the supported paths declared in `scenarios.json`.

## Real ClaimCI outcomes

The committed unittest exercised real Discovery, registered adapters for all
relevant result/config/dataset candidates,
planning, ephemeral materialization, `audit_research()`, and unified advisory
Review against a temporary base/head pair.

| Metric/scenario | Planning state | Public state | Deterministic authority | Advisory Review |
| --- | --- | --- | --- | --- |
| accuracy / complete-supported | READY | COMPLETE | SUPPORTED | present, advisory |
| f1 / not-supported | READY | COMPLETE | NOT_SUPPORTED | present, advisory |
| precision / insufficient-evidence | READY | COMPLETE | INSUFFICIENT_EVIDENCE | present, advisory |
| recall / mapping-needed | MAPPING_NEEDED | MAPPING_NEEDED | none | not run |
| auc / partial | PARTIAL | PARTIAL | none | not run |

The f1 result's only invalidating driver is
`CONFIG.COMPUTE_MISMATCH`. The precision result's authority-limiting driver is
`SEED.SINGLE_RUN` with `INSUFFICIENT` impact. The supported result has no
invalidating or insufficient driver.

Every discovered audit claim has a non-null absolute-improvement threshold.
The recall scenario asks exactly `Which file contains the candidate results?`
with only the two active recall candidate-result paths declared in the
catalog. The auc scenario has no mapping question and reports one missing
candidate `DATASET`; its candidate-train binding exists and candidate eval is
the intentionally absent active path.

All completed outcomes came from an actual `AuditResult`. The fake test
provider was called exactly once per completed scenario and only populated the
advisory interpretation. It was not called for mapping-needed or partial. Each
ephemeral Audit scratch directory was empty after completion.

## TDD and mutation evidence

The initial test failed while root `research.yaml` existed. After the active-
materialization contract was added, it failed while the legacy workflow still
existed. A real-core trace then proved that permanently discoverable result
packs cross-route under a single PR-title claim, which led to the authorized
inert-template topology rather than a ClaimCI special case.

Four temporary mutations were each verified red and then restored:

1. Removing the explicit threshold clause produced a null
   `minimum_absolute_improvement` and failed the threshold assertion.
2. Removing the candidate role token from the second recall result changed
   planning to READY and failed the required MAPPING_NEEDED assertion.
3. Materializing the omitted auc candidate eval changed planning to READY and
   failed the required PARTIAL assertion.
4. Appending a byte during materialization failed the exact template-byte
   equality assertion for all five scenarios.

The restored approved tree passed afterward.

## Commands and results

From the Demo worktree:

```powershell
$env:CLAIMCI_CORE_ROOT='C:\ClaimCI-worktrees\hosted-core-v03'
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover -s tests -v
```

Result: `Ran 1 test ... OK`; the method contains five named scenario subtests.

From the exact ClaimCI checkout:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m pytest -q -p no:cacheprovider
```

Result: `952 passed, 13 skipped in 31.30s`.

Compile validation used `python -B -m compileall -q claimci` with
`PYTHONPYCACHEPREFIX` directed to an external temporary directory. It exited
zero, and the ClaimCI checkout remained clean.

Additional passing checks:

```powershell
python -B -m json.tool pilot-fixtures\scenarios.json
git diff --check origin/main...HEAD
git status --short
```

Repository assertions also verified: no `research.yaml` or `research.yml` at
any depth; no legacy workflow; no active directory on main; only `.fixture`
files below template roots; all materialized bytes equal their source bytes;
no dormant template is issued as a Discovery artifact; and all selected plan
mapping/evidence paths are confined to `pilot-fixtures/active/`. The unchanged
`.claimci/review.yaml` may be normalized as non-selected config evidence and
does not enter the deterministic plan.

## Future activation procedure

Create a temporary branch from main, select one catalog entry, and copy every
declared template to its declared active path without changing bytes. Add the
active marker with the scenario ID and a non-secret run ID, verify the active
directory contains exactly that entry's declared paths plus the marker, and
use the exact catalog title. The PR body must not add scientific claims.

Do not add a manifest or Actions workflow, merge active evidence to main,
execute repository content, or create a permanent scenario branch.
