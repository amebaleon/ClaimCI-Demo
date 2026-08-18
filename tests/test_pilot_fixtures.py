from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


EXPECTED_CORE_SHA = "c54beaf5cd06d57425eeed383942bf44392ede6f"
EXPECTED_SCENARIOS = {
    "complete-supported": ("complete", "SUPPORTED"),
    "not-supported": ("complete", "NOT_SUPPORTED"),
    "insufficient-evidence": ("complete", "INSUFFICIENT_EVIDENCE"),
    "mapping-needed": ("mapping_needed", None),
    "partial": ("partial", None),
}
FORMAT_SUFFIXES = {
    "csv": ".csv",
    "json": ".json",
    "jsonl": ".jsonl",
    "toml": ".toml",
    "yaml": ".yaml",
}
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REVIEW_POLICY_SHA256 = (
    "3d23011167406ca49138572fd2911fc302c1ac64206f5b55cee0c697ed85d76e"
)


def _claimci_root() -> Path:
    raw = os.environ.get("CLAIMCI_CORE_ROOT")
    if not raw:
        raise RuntimeError("CLAIMCI_CORE_ROOT must name the pinned ClaimCI checkout")
    root = Path(raw).resolve()
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != EXPECTED_CORE_SHA:
        raise RuntimeError(
            f"ClaimCI checkout must be {EXPECTED_CORE_SHA}, found {head}"
        )
    return root


CORE_ROOT = _claimci_root()
sys.path.insert(0, str(CORE_ROOT))

from claimci.analysis import (  # noqa: E402
    AnalysisAuthority,
    AnalysisState,
    ArtifactKind,
    ExperimentRole,
    GitCommitSha,
    MaterializationLimits,
    PassiveArtifact,
    PlanningState,
    RepositoryIdentity,
    RuntimeExecutionContext,
    planning_request_from_discovery,
    plan_ephemeral_audit,
    run_unified_analysis,
)
from claimci.analysis.adapters import extract_registered_artifact  # noqa: E402
from claimci.analysis.discovery import discover_repository  # noqa: E402
from claimci.models import Verdict  # noqa: E402
from claimci.review import ProviderUsage, ReviewConfig  # noqa: E402
from claimci.review.provider import (  # noqa: E402
    ProviderResponse,
    StructuredRequest,
)


REPOSITORY = RepositoryIdentity("amebaleon", "ClaimCI-Demo")
HEAD_SHA = GitCommitSha("d" * 40)


class _AdvisoryProvider:
    def __init__(self) -> None:
        self.calls: list[StructuredRequest] = []

    def extract_claims(self, request: StructuredRequest) -> ProviderResponse:
        raise AssertionError("fixture validation must use deterministic claim discovery")

    def synthesize_review(self, request: StructuredRequest) -> ProviderResponse:
        self.calls.append(request)
        return ProviderResponse(
            json.dumps(
                {
                    "summary": "The deterministic Audit remains authoritative.",
                    "interpretations": [
                        "The supplied evidence has been interpreted without a verdict."
                    ],
                    "missing_evidence": [],
                    "confidence": 0.8,
                }
            ),
            "fixture-provider",
            "fixture-model",
            usage=ProviderUsage(input_tokens=10, output_tokens=5, total_tokens=15),
        )


def _copy_repository(destination: Path) -> None:
    shutil.copytree(
        REPOSITORY_ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )


def _load_catalog() -> dict[str, object]:
    path = REPOSITORY_ROOT / "pilot-fixtures" / "scenarios.json"
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError("scenario catalog root must be an object")
    return value


def _materialize_scenario(
    head: Path,
    scenario_id: str,
    scenario: dict[str, object],
) -> tuple[str, ...]:
    raw_materialization = scenario["materialization"]
    if not isinstance(raw_materialization, list) or not raw_materialization:
        raise AssertionError("scenario materialization must be a non-empty list")
    written: list[str] = []
    for raw in raw_materialization:
        if not isinstance(raw, dict) or set(raw) != {"template", "path", "format"}:
            raise AssertionError("materialization entries must use the exact schema")
        template = Path(str(raw["template"]))
        destination = Path(str(raw["path"]))
        format_name = str(raw["format"])
        if format_name not in FORMAT_SUFFIXES:
            raise AssertionError(f"unsupported fixture format {format_name!r}")
        if template.parent != Path("pilot-fixtures/templates") / scenario_id:
            raise AssertionError("template must be confined to its scenario catalog")
        if template.suffix != ".fixture":
            raise AssertionError("dormant templates must use the inert .fixture suffix")
        if destination.parent != Path("pilot-fixtures/active"):
            raise AssertionError("materialized evidence must use pilot-fixtures/active")
        if destination.suffix != FORMAT_SUFFIXES[format_name]:
            raise AssertionError("materialized extension must match its declared format")
        source = head / template
        target = head / destination
        if not source.is_file() or target.exists():
            raise AssertionError("materialization source/destination state is invalid")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if source.read_bytes() != target.read_bytes():
            raise AssertionError("materialization must preserve exact template bytes")
        written.append(destination.as_posix())

    marker = Path(str(scenario["activation_marker"]))
    if marker.parent != Path("pilot-fixtures/active") or marker.name != "activation.txt":
        raise AssertionError("activation marker must be confined to the active directory")
    marker_target = head / marker
    marker_target.write_text(
        f"scenario={scenario_id}\nrun=local-validation\n",
        encoding="utf-8",
        newline="\n",
    )
    written.append(marker.as_posix())
    return tuple(sorted(written))


class PilotFixtureTests(unittest.TestCase):
    maxDiff = None

    def test_catalog_runs_five_isolated_real_claimci_scenarios(self) -> None:
        manifests = tuple(
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for name in ("research.yaml", "research.yml")
            for path in REPOSITORY_ROOT.rglob(name)
        )
        self.assertEqual(manifests, ())
        self.assertFalse((REPOSITORY_ROOT / "pilot-fixtures" / "active").exists())
        self.assertFalse(
            (REPOSITORY_ROOT / ".github" / "workflows" / "claimci.yml").exists()
        )
        self.assertTrue((REPOSITORY_ROOT / ".claimci" / "review.yaml").is_file())
        self.assertEqual(
            hashlib.sha256(
                (REPOSITORY_ROOT / ".claimci" / "review.yaml").read_bytes()
            ).hexdigest(),
            REVIEW_POLICY_SHA256,
        )

        catalog = _load_catalog()
        self.assertEqual(
            set(catalog), {"schema_version", "claimci_core_sha", "scenarios"}
        )
        self.assertEqual(catalog["schema_version"], 2)
        self.assertEqual(catalog["claimci_core_sha"], EXPECTED_CORE_SHA)
        scenarios = catalog["scenarios"]
        self.assertIsInstance(scenarios, dict)
        assert isinstance(scenarios, dict)
        self.assertEqual(set(scenarios), set(EXPECTED_SCENARIOS))

        for scenario_id, (public_state, verdict) in EXPECTED_SCENARIOS.items():
            with self.subTest(scenario=scenario_id):
                raw = scenarios[scenario_id]
                self.assertIsInstance(raw, dict)
                assert isinstance(raw, dict)
                self._validate_scenario(
                    scenario_id,
                    raw,
                    expected_public_state=public_state,
                    expected_verdict=verdict,
                )

    def _validate_scenario(
        self,
        scenario_id: str,
        scenario: dict[str, object],
        *,
        expected_public_state: str,
        expected_verdict: str | None,
    ) -> None:
        required = {
            "metric",
            "pr_title",
            "template_path",
            "activation_marker",
            "materialization",
            "expected_public_state",
            "expected_deterministic_verdict",
            "expected_advisory_state",
            "expected_minimum_absolute_improvement",
        }
        optional = {
            "expected_mapping_prompt",
            "expected_mapping_choices",
            "intentionally_missing_path",
        }
        self.assertEqual(set(scenario) - optional, required)
        self.assertFalse(set(scenario) - required - optional)
        self.assertEqual(scenario["expected_public_state"], expected_public_state)
        self.assertEqual(scenario["expected_deterministic_verdict"], expected_verdict)
        self.assertEqual(
            scenario["expected_advisory_state"],
            "ADVISORY_COMPLETE" if expected_public_state == "complete" else "NOT_RUN",
        )

        template_path = Path(str(scenario["template_path"]))
        marker_path = Path(str(scenario["activation_marker"]))
        self.assertEqual(template_path, Path("pilot-fixtures/templates") / scenario_id)
        self.assertTrue((REPOSITORY_ROOT / template_path).is_dir())
        self.assertEqual(marker_path.parent, Path("pilot-fixtures/active"))
        self.assertEqual(marker_path.name, "activation.txt")
        self.assertFalse((REPOSITORY_ROOT / marker_path).exists())
        self.assertTrue(
            all(path.suffix == ".fixture" for path in (REPOSITORY_ROOT / template_path).iterdir())
        )

        with tempfile.TemporaryDirectory(prefix=f"claimci-{scenario_id}-") as raw_tmp:
            temporary = Path(raw_tmp)
            base = temporary / "base"
            head = temporary / "head"
            scratch = temporary / "scratch"
            _copy_repository(base)
            _copy_repository(head)
            scratch.mkdir()
            changed_paths = _materialize_scenario(head, scenario_id, scenario)
            self.assertEqual(
                set(changed_paths),
                {
                    str(item["path"])
                    for item in scenario["materialization"]
                }
                | {marker_path.as_posix()},
            )
            self.assertEqual(
                {
                    path.relative_to(head).as_posix()
                    for path in (head / "pilot-fixtures" / "active").iterdir()
                    if path.is_file()
                },
                set(changed_paths),
            )

            discovery = discover_repository(
                head,
                repository=REPOSITORY,
                head_sha=HEAD_SHA,
                pr_number=17,
                base_root=base,
                pr_title=str(scenario["pr_title"]),
            )
            self.assertEqual(len(discovery.claims), 1)
            claim = discovery.claims[0]
            self.assertEqual(claim.metric, scenario["metric"])

            mapped_paths = {
                str(binding.path)
                for mapping in discovery.mapping_candidates
                for binding in mapping.bindings
            }
            if discovery.mapping_question is not None:
                mapped_paths.update(
                    str(binding.path)
                    for choice in discovery.mapping_question.choices
                    for binding in choice.bindings
                )
            self.assertTrue(mapped_paths)
            self.assertTrue(
                all(path.startswith("pilot-fixtures/active/") for path in mapped_paths)
            )
            self.assertFalse(
                any(
                    str(artifact.path).startswith("pilot-fixtures/templates/")
                    for artifact in discovery.artifacts
                )
            )

            evidence = []
            for artifact in discovery.artifacts:
                if str(artifact.path) not in mapped_paths:
                    continue
                if artifact.kind not in {
                    ArtifactKind.RESULTS,
                    ArtifactKind.CONFIG,
                    ArtifactKind.DATASET,
                }:
                    continue
                passive = PassiveArtifact(
                    artifact,
                    (head / Path(str(artifact.path))).read_bytes(),
                )
                extracted = extract_registered_artifact(passive)
                self.assertIsNotNone(extracted, str(artifact.path))
                evidence.append(extracted)

            request = planning_request_from_discovery(
                discovery,
                claim_id=claim.reference.claim_id,
                normalized_evidence=tuple(evidence),
            )
            threshold = request.audit_claim.minimum_absolute_improvement
            self.assertIsNotNone(threshold)
            self.assertEqual(
                threshold,
                scenario["expected_minimum_absolute_improvement"],
            )
            prefix = "pilot-fixtures/active/"
            self.assertTrue(request.artifacts)
            self.assertFalse(
                any(
                    str(item.path).startswith("pilot-fixtures/templates/")
                    for item in request.artifacts
                )
            )
            self.assertTrue(
                all(
                    str(item.artifact.path).startswith(prefix)
                    for item in request.normalized_evidence
                )
            )
            self.assertTrue(
                all(
                    str(binding.path).startswith(prefix)
                    for mapping in request.mapping_candidates
                    for binding in mapping.bindings
                )
            )

            planning = plan_ephemeral_audit(request)
            provider = _AdvisoryProvider()
            runtime = RuntimeExecutionContext(
                repository=REPOSITORY,
                checkout_root=head,
                head_sha=HEAD_SHA,
                scratch_root=scratch,
                limits=MaterializationLimits(
                    max_file_bytes=1_000_000,
                    max_total_bytes=5_000_000,
                ),
            )
            result = run_unified_analysis(
                request,
                runtime,
                ReviewConfig(enabled=True),
                provider=provider,
            )

            if expected_public_state == "complete":
                self.assertEqual(planning.state, PlanningState.READY)
                self.assertEqual(result.state, AnalysisState.COMPLETE)
                self.assertEqual(result.authoritative_verdict, Verdict(expected_verdict))
                self.assertIsNotNone(result.research_interpretation)
                assert result.research_interpretation is not None
                self.assertEqual(
                    result.research_interpretation.authority,
                    AnalysisAuthority.ADVISORY,
                )
                self.assertEqual(len(provider.calls), 1)
            elif expected_public_state == "mapping_needed":
                self.assertEqual(planning.state, PlanningState.MAPPING_NEEDED)
                self.assertEqual(result.state, AnalysisState.MAPPING_NEEDED)
                self.assertIsNotNone(planning.mapping_question)
                assert planning.mapping_question is not None
                self.assertEqual(
                    planning.mapping_question.prompt,
                    scenario["expected_mapping_prompt"],
                )
                self.assertEqual(
                    tuple(choice.label for choice in planning.mapping_question.choices),
                    tuple(scenario["expected_mapping_choices"]),
                )
                self.assertEqual(len(planning.mapping_question.choices), 2)
                self.assertIsNone(result.authoritative_verdict)
                self.assertIsNone(result.research_interpretation)
                self.assertEqual(provider.calls, [])
            else:
                self.assertEqual(planning.state, PlanningState.PARTIAL)
                self.assertEqual(result.state, AnalysisState.PARTIAL)
                self.assertIsNone(planning.mapping_question)
                self.assertIsNone(result.authoritative_verdict)
                self.assertIsNone(result.research_interpretation)
                self.assertEqual(provider.calls, [])
                self.assertEqual(len(planning.missing_evidence), 1)
                missing = planning.missing_evidence[0]
                self.assertEqual(missing.kind, ArtifactKind.DATASET)
                self.assertEqual(missing.role, ExperimentRole.CANDIDATE)
                candidate_dataset_bindings = tuple(
                    binding
                    for mapping in request.mapping_candidates
                    for binding in mapping.bindings
                    if binding.kind is ArtifactKind.DATASET
                    and binding.role is ExperimentRole.CANDIDATE
                )
                self.assertEqual(
                    {binding.dataset_split.value for binding in candidate_dataset_bindings},
                    {"train"},
                )
                self.assertFalse(
                    (head / str(scenario["intentionally_missing_path"])).exists()
                )

            self.assertEqual(tuple(scratch.iterdir()), ())


if __name__ == "__main__":
    unittest.main()
