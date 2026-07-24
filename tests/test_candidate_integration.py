from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "verify_candidate_integration.py"
POLICY = ROOT / "assurance" / "candidate-integration-policy.json"
GSN = ROOT / "_static" / "gsn_safety_case.puml"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def candidate_fixture(
    tmp_path: Path,
    traceability_violations: list[str] | None = None,
    coverage_percent: float = 90.43863972400197,
    complexity_count: int = 15,
    static_finding_count: int = 17,
) -> tuple[Path, Path, Path]:
    evidence = tmp_path / "_build" / "evidence"
    expected_results = {
        "test": ("passed", ""),
        "sanitizer": ("passed", ""),
        "coverage": ("passed", ""),
        "complexity": ("failed", "complexity limits exceeded by 15 functions"),
        "warnings": ("passed", ""),
        "static-analysis": ("failed", "cppcheck reported 17 error/warning findings"),
        "reproducible": ("passed", ""),
    }
    for activity, (result, message) in expected_results.items():
        payload = {"activity": activity, "result": result}
        if message:
            payload["message"] = message
        write_json(evidence / activity / "result.json", payload)
    write_json(
        evidence / "coverage" / "metrics.json",
        {
            "line": {"percent": coverage_percent},
            "branch": {"percent": 80.2593659942363},
        },
    )
    write_json(
        evidence / "complexity" / "metrics.json",
        {
            "functions": 154,
            "violations": [
                {"cyclomatic_complexity": 37, "function_length": 230},
                *(
                    {"cyclomatic_complexity": 16, "function_length": 101}
                    for _ in range(complexity_count - 1)
                ),
            ],
        },
    )
    write_json(
        evidence / "static-analysis" / "findings.json",
        {"blocking_findings": [{"id": index} for index in range(static_finding_count)]},
    )

    framework_failures = [
        "activity complexity: finding QF-01 is undispositioned (open)",
        "activity static-analysis: finding QF-02 is undispositioned (open)",
        "activity test-suite: evidence is not approved (validated)",
        "gap independent-exact-tree-review: required gap remains open",
    ]
    framework = tmp_path / "framework.json"
    write_json(
        framework,
        {
            "status": "FAIL",
            "acceptance_claimed": False,
            "failures": framework_failures,
        },
    )
    trace = tmp_path / "trace.json"
    default_violations = [
        *(f"framework acceptance failed: {item}" for item in framework_failures),
        "EVID_UNIT: evidence is not accepted",
    ]
    write_json(
        trace,
        {
            "status": "FAIL",
            "violations": traceability_violations or default_violations,
        },
    )
    return evidence, framework, trace


def policy() -> dict[str, object]:
    return {
        "schema": "osqar-cjson.candidate-integration-policy.v1",
        "decision": "merge-candidate-with-known-limitations",
        "qualification_claimed": False,
        "publication_authorized": False,
        "follow_up_issue": "https://github.com/BitVortex/OSQAr-cJSON/issues/21",
        "coverage": {
            "line_percent": 90.44,
            "branch_percent": 80.26,
            "mc_dc_measured": False,
            "adequate_for_qualification_argument": False,
        },
        "integration_deviations": [
            {
                "id": "QF-01",
                "disposition": "accepted only for integration of the blocked research candidate",
                "qualification_effect": "unresolved; does not support qualification acceptance",
            },
            {
                "id": "QF-02",
                "disposition": "accepted only for integration of the blocked research candidate",
                "qualification_effect": "unresolved; does not support qualification acceptance",
            },
        ],
        "expected_activity_results": {
            "test": "passed",
            "sanitizer": "passed",
            "coverage": "passed",
            "complexity": "failed",
            "warnings": "passed",
            "static-analysis": "failed",
            "reproducible": "passed",
        },
        "required_framework_failures": [
            "activity complexity: finding QF-01 is undispositioned (open)",
            "activity static-analysis: finding QF-02 is undispositioned (open)",
            "activity test-suite: evidence is not approved (validated)",
            "gap independent-exact-tree-review: required gap remains open",
        ],
        "expected_traceability_violation_count": 5,
        "expected_traceability_violations": [
            "framework acceptance failed: activity complexity: finding QF-01 is undispositioned (open)",
            "framework acceptance failed: activity static-analysis: finding QF-02 is undispositioned (open)",
            "framework acceptance failed: activity test-suite: evidence is not approved (validated)",
            "framework acceptance failed: gap independent-exact-tree-review: required gap remains open",
            "EVID_UNIT: evidence is not accepted",
        ],
    }


def invoke(
    tmp_path: Path,
    policy_value: dict[str, object],
    traceability_violations: list[str] | None = None,
    coverage_percent: float = 90.43863972400197,
    complexity_count: int = 15,
    static_finding_count: int = 17,
) -> subprocess.CompletedProcess[str]:
    _, framework, trace = candidate_fixture(
        tmp_path,
        traceability_violations,
        coverage_percent,
        complexity_count,
        static_finding_count,
    )
    policy_path = tmp_path / "policy.json"
    write_json(policy_path, policy_value)
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(tmp_path),
            "--policy",
            str(policy_path),
            "--framework-report",
            str(framework),
            "--traceability-report",
            str(trace),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_checked_in_policy_records_nonqualification_limitations() -> None:
    value = json.loads(POLICY.read_text())
    assert value["qualification_claimed"] is False
    assert value["publication_authorized"] is False
    assert value["follow_up_issue"].endswith("/issues/21")
    assert value["coverage"] == {
        "line_percent": 90.44,
        "branch_percent": 80.26,
        "mc_dc_measured": False,
        "adequate_for_qualification_argument": False,
    }
    assert value["expected_traceability_violation_count"] == 47
    assert len(value["expected_traceability_violations"]) == 47
    assert {item["id"] for item in value["integration_deviations"]} == {
        "QF-01",
        "QF-02",
    }


def test_ci_requires_exact_documented_block_before_passing() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert 'test "${NATIVE_RC}" -eq 1' in workflow
    assert 'test "${FRAMEWORK_RC}" -eq 1' in workflow
    assert 'test "${TRACEABILITY_RC}" -eq 1' in workflow
    assert "tools/verify_candidate_integration.py" in workflow
    assert "assurance/candidate-integration-policy.json" in workflow


def test_shipped_gsn_does_not_claim_the_blocked_proposition() -> None:
    gsn = GSN.read_text()
    assert "QUALIFICATION AND PUBLICATION: BLOCK" in gsn
    assert "sufficiently safe" not in gsn
    assert "All safety requirements are verified" not in gsn
    assert "does not invoke undefined behavior for any" not in gsn
    assert "free from memory errors" not in gsn
    assert "correctly parses all valid JSON" not in gsn


def test_documented_blocked_candidate_is_accepted_for_integration(tmp_path: Path) -> None:
    result = invoke(tmp_path, policy())
    assert result.returncode == 0, result.stdout
    assert "candidate integration policy: PASS" in result.stdout


def test_changed_unapproved_evidence_inventory_is_rejected(tmp_path: Path) -> None:
    expected = policy()["expected_traceability_violations"]
    assert isinstance(expected, list)
    violations = list(expected)
    violations[-1] = "EVID_TAMPER: evidence is not accepted"
    result = invoke(tmp_path, policy(), violations)
    assert result.returncode == 1
    assert "traceability violation inventory differs" in result.stdout


def test_deviation_cannot_be_promoted_to_qualification_acceptance(tmp_path: Path) -> None:
    value = policy()
    deviations = value["integration_deviations"]
    assert isinstance(deviations, list)
    deviations[0]["qualification_effect"] = "accepted for qualification"
    result = invoke(tmp_path, value)
    assert result.returncode == 1
    assert "QF-01 deviation is not limited to candidate integration" in result.stdout


def test_unexpected_native_activity_is_rejected(tmp_path: Path) -> None:
    candidate_fixture(tmp_path)
    write_json(
        tmp_path / "_build" / "evidence" / "unexpected" / "result.json",
        {"activity": "unexpected", "result": "passed"},
    )
    result = invoke(tmp_path, policy())
    assert result.returncode == 1
    assert "native activity inventory differs" in result.stdout


def test_changed_native_coverage_metrics_are_rejected(tmp_path: Path) -> None:
    result = invoke(tmp_path, policy(), coverage_percent=100.0)
    assert result.returncode == 1
    assert "native coverage metrics differ" in result.stdout


def test_changed_qf_finding_inventories_are_rejected(tmp_path: Path) -> None:
    complexity = invoke(tmp_path, policy(), complexity_count=14)
    assert complexity.returncode == 1
    assert "QF-01 native finding inventory differs" in complexity.stdout

    static_analysis = invoke(tmp_path, policy(), static_finding_count=16)
    assert static_analysis.returncode == 1
    assert "QF-02 native finding inventory differs" in static_analysis.stdout
