#!/usr/bin/env python3
"""Accept a truthfully blocked candidate for integration without claiming qualification."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXPECTED_SCHEMA = "osqar-cjson.candidate-integration-policy.v1"
KNOWN_FAILURE_MESSAGES = {
    "complexity": "complexity limits exceeded by 15 functions",
    "static-analysis": "cppcheck reported 17 error/warning findings",
}
EXPECTED_ACTIVITY_RESULTS = {
    "test": "passed",
    "sanitizer": "passed",
    "coverage": "passed",
    "complexity": "failed",
    "warnings": "passed",
    "static-analysis": "failed",
    "reproducible": "passed",
}


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def verify(
    root: Path,
    policy_path: Path,
    framework_path: Path,
    traceability_path: Path,
) -> list[str]:
    errors: list[str] = []
    policy = load_object(policy_path, "candidate integration policy")
    framework = load_object(framework_path, "framework report")
    traceability = load_object(traceability_path, "traceability report")

    if policy.get("schema") != EXPECTED_SCHEMA:
        errors.append("candidate integration policy schema is invalid")
    if policy.get("decision") != "merge-candidate-with-known-limitations":
        errors.append("candidate integration decision is not explicit")
    if policy.get("qualification_claimed") is not False:
        errors.append("candidate integration policy must not claim qualification")
    if policy.get("publication_authorized") is not False:
        errors.append("candidate integration policy must not authorize publication")
    issue = policy.get("follow_up_issue")
    if issue != "https://github.com/BitVortex/OSQAr-cJSON/issues/21":
        errors.append("candidate integration policy must bind follow-up issue 21")

    coverage = policy.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage limitation record is missing")
    else:
        if coverage.get("line_percent") != 90.44:
            errors.append("line coverage observation is not 90.44%")
        if coverage.get("branch_percent") != 80.26:
            errors.append("branch coverage observation is not 80.26%")
        if coverage.get("mc_dc_measured") is not False:
            errors.append("coverage record must state that MC/DC was not measured")
        if coverage.get("adequate_for_qualification_argument") is not False:
            errors.append("coverage record must not claim adequacy for qualification")

    deviations = policy.get("integration_deviations")
    expected_deviation_ids = {"QF-01", "QF-02"}
    if not isinstance(deviations, list) or {
        item.get("id") for item in deviations if isinstance(item, dict)
    } != expected_deviation_ids or len(deviations) != 2:
        errors.append("candidate integration deviations must be exactly QF-01 and QF-02")
    else:
        for item in deviations:
            deviation_id = item["id"]
            if (
                item.get("disposition")
                != "accepted only for integration of the blocked research candidate"
                or item.get("qualification_effect")
                != "unresolved; does not support qualification acceptance"
            ):
                errors.append(
                    f"{deviation_id} deviation is not limited to candidate integration"
                )

    expected_results = policy.get("expected_activity_results")
    if expected_results != EXPECTED_ACTIVITY_RESULTS:
        errors.append("expected activity result map differs from the bounded candidate")
    else:
        evidence_root = root / "_build" / "evidence"
        try:
            actual_activities = {
                entry.name for entry in evidence_root.iterdir() if entry.is_dir()
            }
        except OSError as exc:
            errors.append(f"cannot inventory native activities: {exc}")
            actual_activities = set()
        if actual_activities != set(EXPECTED_ACTIVITY_RESULTS):
            errors.append("native activity inventory differs from the bounded candidate")

        for activity, expected in sorted(EXPECTED_ACTIVITY_RESULTS.items()):
            result_path = evidence_root / activity / "result.json"
            try:
                result = load_object(result_path, f"{activity} result")
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if result.get("activity") != activity or result.get("result") != expected:
                errors.append(f"{activity} result does not match candidate policy")
            expected_message = KNOWN_FAILURE_MESSAGES.get(activity)
            if expected_message and result.get("message") != expected_message:
                errors.append(f"{activity} failure inventory changed")

        try:
            coverage_metrics = load_object(
                evidence_root / "coverage" / "metrics.json", "native coverage metrics"
            )
            line = coverage_metrics.get("line")
            branch = coverage_metrics.get("branch")
            if (
                not isinstance(line, dict)
                or not isinstance(branch, dict)
                or line.get("percent") != 90.43863972400197
                or branch.get("percent") != 80.2593659942363
            ):
                errors.append("native coverage metrics differ from the documented candidate")
        except ValueError as exc:
            errors.append(str(exc))

        try:
            complexity_metrics = load_object(
                evidence_root / "complexity" / "metrics.json",
                "QF-01 native finding inventory",
            )
            complexity_findings = complexity_metrics.get("violations")
            if (
                complexity_metrics.get("functions") != 154
                or not isinstance(complexity_findings, list)
                or len(complexity_findings) != 15
                or not all(isinstance(item, dict) for item in complexity_findings)
                or max(
                    item.get("cyclomatic_complexity", -1)
                    for item in complexity_findings
                )
                != 37
                or max(item.get("function_length", -1) for item in complexity_findings)
                != 230
            ):
                errors.append("QF-01 native finding inventory differs")
        except (TypeError, ValueError) as exc:
            errors.append(f"QF-01 native finding inventory differs: {exc}")

        try:
            static_metrics = load_object(
                evidence_root / "static-analysis" / "findings.json",
                "QF-02 native finding inventory",
            )
            static_findings = static_metrics.get("blocking_findings")
            if not isinstance(static_findings, list) or len(static_findings) != 17:
                errors.append("QF-02 native finding inventory differs")
        except ValueError as exc:
            errors.append(str(exc))

    required_failures = policy.get("required_framework_failures")
    actual_failures = framework.get("failures")
    if (
        framework.get("status") != "FAIL"
        or framework.get("acceptance_claimed") is not False
    ):
        errors.append("framework report must remain a non-accepting FAIL")
    if not isinstance(required_failures, list) or not all(
        isinstance(item, str) and item for item in required_failures
    ):
        errors.append("required framework failure inventory is invalid")
    elif actual_failures != required_failures:
        errors.append("framework failure inventory differs from the documented candidate policy")

    violations = traceability.get("violations")
    expected_count = policy.get("expected_traceability_violation_count")
    expected_violations = policy.get("expected_traceability_violations")
    if traceability.get("status") != "FAIL":
        errors.append("qualification traceability report must remain FAIL")
    if not isinstance(violations, list) or not all(isinstance(item, str) for item in violations):
        errors.append("traceability violation inventory is invalid")
    else:
        if expected_count is not None:
            if not isinstance(expected_count, int) or isinstance(expected_count, bool):
                errors.append("expected traceability violation count is invalid")
            elif len(violations) != expected_count:
                errors.append("traceability violation count differs from the candidate policy")
        if not isinstance(expected_violations, list) or not all(
            isinstance(item, str) and item for item in expected_violations
        ):
            errors.append("expected traceability violation inventory is invalid")
        elif violations != expected_violations:
            errors.append("traceability violation inventory differs from the candidate policy")

    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--framework-report", type=Path, required=True)
    parser.add_argument("--traceability-report", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        errors = verify(
            args.root.resolve(),
            args.policy.resolve(),
            args.framework_report.resolve(),
            args.traceability_report.resolve(),
        )
    except ValueError as exc:
        errors = [str(exc)]
    if errors:
        print("candidate integration policy: FAIL", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("candidate integration policy: PASS")
    print("qualification status: BLOCKED; no qualification or publication claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
