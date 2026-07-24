from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "verify_candidate_integration.py"
POLICY = ROOT / "assurance" / "candidate-integration-policy.json"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def candidate_fixture(
    tmp_path: Path,
    traceability_violations: list[str] | None = None,
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
) -> subprocess.CompletedProcess[str]:
    _, framework, trace = candidate_fixture(tmp_path, traceability_violations)
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
