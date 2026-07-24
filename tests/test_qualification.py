from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "qualification", ROOT / "tools" / "qualification.py"
)
assert SPEC and SPEC.loader
qualification = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = qualification
SPEC.loader.exec_module(qualification)


def copy_repository(tmp_path: Path) -> Path:
    destination = tmp_path / "repository"
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", "_build", ".pytest_cache", "__pycache__"),
    )
    return destination


def invoke(repository: Path, command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(repository / "tools" / "qualification.py"),
            command,
            "--source-revision",
            "fault-seed",
        ],
        cwd=repository,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=120,
    )


def test_parse_unity_output_reconciles_verbose_cases() -> None:
    output = "\n".join((
        "sample.c:10:first:PASS",
        "sample.c:11:second:IGNORE:not implemented",
        "",
        "2 Tests 0 Failures 1 Ignored ",
        "OK",
    ))
    run = qualification.parse_unity_output("sample", output, 0)
    assert run.tests == 2
    assert [case.status for case in run.cases] == ["PASS", "IGNORE"]


@pytest.mark.parametrize(
    "output",
    [
        "sample.c:10:first:PASS\n2 Tests 0 Failures 0 Ignored\nOK",
        "sample.c:10:first:FAIL:oops\n1 Tests 0 Failures 0 Ignored\nFAIL",
        "sample.c:10:first:PASS\n",
    ],
)
def test_parse_unity_output_rejects_unreconciled_output(output: str) -> None:
    with pytest.raises(qualification.QualificationError):
        qualification.parse_unity_output("sample", output, 0)


def test_junit_has_one_element_per_unity_case() -> None:
    cases = tuple(
        qualification.UnityCase("program", "source.c", number, f"case_{number}",
                                "PASS", "")
        for number in range(qualification.EXPECTED_CASES)
    )
    run = qualification.UnityRun(
        "program", cases, qualification.EXPECTED_CASES, 0, 0, 0, ""
    )
    root = qualification.junit_tree([run], "suite", 0.0).getroot()
    assert root.attrib["tests"] == str(qualification.EXPECTED_CASES)
    assert len(root.findall("testcase")) == qualification.EXPECTED_CASES


def test_configured_coverage_thresholds_preserve_documented_policy() -> None:
    assert qualification.LINE_COVERAGE_MIN == 90.0
    assert qualification.BRANCH_COVERAGE_MIN == 80.0


def test_forced_unity_failure_fails_closed_in_temp_copy(tmp_path: Path) -> None:
    repository = copy_repository(tmp_path)
    source = repository / "cjson-source" / "tests" / "parse_hex4.c"
    text = source.read_text(encoding="utf-8")
    marker = "static void parse_hex4_should_parse_all_combinations(void)\n{"
    assert marker in text
    source.write_text(
        text.replace(marker, marker + '\n    TEST_FAIL_MESSAGE("forced fault");', 1),
        encoding="utf-8",
    )
    result = invoke(repository, "test")
    assert result.returncode != 0
    evidence = repository / "_build" / "evidence" / "test"
    assert "parse_hex4: exited" in result.stdout
    assert json.loads((evidence / "result.json").read_text())["result"] == "failed"


def test_abort_signal_is_detected_in_temp_copy(tmp_path: Path) -> None:
    repository = copy_repository(tmp_path)
    source = repository / "cjson-source" / "tests" / "parse_hex4.c"
    text = source.read_text(encoding="utf-8")
    marker = "static void parse_hex4_should_parse_all_combinations(void)\n{"
    assert marker in text
    source.write_text(
        text.replace(marker, marker + "\n    abort();", 1),
        encoding="utf-8",
    )
    result = invoke(repository, "test")
    assert result.returncode != 0
    assert "terminated by signal SIGABRT" in result.stdout


@pytest.mark.parametrize(
    ("relative", "expected"),
    [
        (Path("cjson-source/tests/inputs"), "missing expected input"),
        (Path("cjson-source/tests/parse_hex4.c"), "test source inventory mismatch"),
    ],
)
def test_missing_expected_input_fails_in_temp_copy(
    tmp_path: Path, relative: Path, expected: str
) -> None:
    repository = copy_repository(tmp_path)
    target = repository / relative
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    result = invoke(repository, "test")
    assert result.returncode != 0
    assert expected in result.stdout


def test_missing_expected_executable_is_rejected_in_temp_copy(tmp_path: Path) -> None:
    repository = copy_repository(tmp_path)
    runner = qualification.Runner(repository, "fault-seed", os.environ.get("CC", "gcc"))
    runner.evidence_dir("test")
    build, objects = runner.compile_objects("test", ["-O2"])
    runner.build_tests("test", ["-O2"], objects)
    (build / qualification.EXPECTED_TESTS[0]).unlink()
    with pytest.raises(qualification.QualificationError, match="missing expected executable"):
        runner.execute_tests("test", build)


def test_sanitizer_detects_injected_component_memory_fault(tmp_path: Path) -> None:
    if shutil.which(os.environ.get("CC", "gcc")) is None:
        pytest.skip("C compiler unavailable")
    repository = copy_repository(tmp_path)
    source = repository / "cjson-source" / "cJSON.c"
    text = source.read_text(encoding="utf-8")
    marker = "CJSON_PUBLIC(cJSON *) cJSON_Parse(const char *value)\n{"
    assert marker in text
    injected = (
        marker
        + "\n    volatile char *qualification_fault = (volatile char*)malloc(1);"
        + "\n    qualification_fault[1] = 1;"
        + "\n    free((void*)qualification_fault);"
    )
    source.write_text(text.replace(marker, injected, 1), encoding="utf-8")
    result = invoke(repository, "sanitizer")
    assert result.returncode != 0
    logs = repository / "_build" / "evidence" / "sanitizer" / "logs"
    combined = "".join(path.read_text(errors="replace") for path in logs.glob("*.txt"))
    assert "AddressSanitizer" in combined or "runtime error:" in combined
