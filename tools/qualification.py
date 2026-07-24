#!/usr/bin/env python3
"""Fail-closed native qualification evidence runner for the pinned cJSON source."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

MIN_PYTHON = (3, 11)
COMPONENT_MANIFEST = Path("assurance/component-source-manifest.json")
COMPONENT_MANIFEST_SHA256 = "df3f33d816e673610406cc98d85fbffc206eaf4c490525eec1a0cdaec7c91e03"
EXPECTED_TESTS = (
    "parse_examples", "parse_number", "parse_hex4", "parse_string",
    "parse_array", "parse_object", "parse_value", "print_string",
    "print_number", "print_array", "print_object", "print_value",
    "misc_tests", "parse_with_opts", "compare_tests", "cjson_add",
    "readme_examples", "minify_tests", "json_patch_tests",
    "old_utils_tests", "misc_utils_tests",
)
EXPECTED_CASES = 162
UTILS_TESTS = frozenset(("json_patch_tests", "old_utils_tests", "misc_utils_tests"))
COMPONENT_SOURCES = ("cJSON.c", "cJSON_Utils.c")
LINE_COVERAGE_MIN = 90.0
BRANCH_COVERAGE_MIN = 80.0
MAX_CCN = 15
MAX_FUNCTION_LENGTH = 100
WARNING_FLAGS = (
    "-Wall", "-Wextra", "-Werror", "-Wpedantic", "-Wconversion",
    "-Wsign-conversion", "-Wdouble-promotion", "-Wnull-dereference",
    "-Wformat=2", "-Wstrict-prototypes", "-Wmissing-prototypes",
    "-Wdeclaration-after-statement",
)
CONFIGURATION = {
    "schema": 1,
    "language": "c99",
    "component_manifest": str(COMPONENT_MANIFEST),
    "component_manifest_sha256": COMPONENT_MANIFEST_SHA256,
    "component_sources": list(COMPONENT_SOURCES),
    "test_executables": list(EXPECTED_TESTS),
    "expected_cases": EXPECTED_CASES,
    "test_adaptations": {
        "print_number_should_print_non_number":
            "replace upstream C89 TEST_IGNORE with C99 NAN/+INFINITY/-INFINITY assertions",
    },
    "warning_flags": list(WARNING_FLAGS),
    "sanitizers": ["address", "undefined"],
    "coverage_minimum_percent": {
        "line": LINE_COVERAGE_MIN,
        "branch": BRANCH_COVERAGE_MIN,
    },
    "complexity_limits": {
        "cyclomatic_complexity": MAX_CCN,
        "function_length": MAX_FUNCTION_LENGTH,
    },
}
CASE_RE = re.compile(
    r"^(?P<file>[^:\r\n]+):(?P<line>\d+):(?P<name>[^:\r\n]+):"
    r"(?P<status>PASS|FAIL|IGNORE)(?::(?P<message>.*))?$"
)
SUMMARY_RE = re.compile(
    r"^(?P<tests>\d+) Tests (?P<failures>\d+) Failures "
    r"(?P<ignored>\d+) Ignored\s*$"
)


class QualificationError(RuntimeError):
    """A gate could not produce trustworthy passing evidence."""


@dataclass(frozen=True)
class UnityCase:
    executable: str
    source: str
    line: int
    name: str
    status: str
    message: str


@dataclass(frozen=True)
class UnityRun:
    executable: str
    cases: tuple[UnityCase, ...]
    tests: int
    failures: int
    ignored: int
    returncode: int
    output: str


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def configuration_sha256() -> str:
    return hashlib.sha256(canonical_json(CONFIGURATION).encode()).hexdigest()


def parse_unity_output(executable: str, output: str, returncode: int) -> UnityRun:
    cases: list[UnityCase] = []
    summaries: list[re.Match[str]] = []
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        match = CASE_RE.match(line)
        if match:
            cases.append(UnityCase(
                executable=executable,
                source=match.group("file"),
                line=int(match.group("line")),
                name=match.group("name"),
                status=match.group("status"),
                message=(match.group("message") or "").strip(),
            ))
        summary = SUMMARY_RE.match(line)
        if summary:
            summaries.append(summary)
    if len(summaries) != 1:
        raise QualificationError(
            f"{executable}: expected exactly one Unity summary, found {len(summaries)}"
        )
    summary = summaries[0]
    tests = int(summary.group("tests"))
    failures = int(summary.group("failures"))
    ignored = int(summary.group("ignored"))
    parsed_failures = sum(case.status == "FAIL" for case in cases)
    parsed_ignored = sum(case.status == "IGNORE" for case in cases)
    if len(cases) != tests:
        raise QualificationError(
            f"{executable}: summary reports {tests} tests but parsed {len(cases)} cases"
        )
    if parsed_failures != failures or parsed_ignored != ignored:
        raise QualificationError(
            f"{executable}: Unity case statuses do not reconcile with summary"
        )
    return UnityRun(
        executable, tuple(cases), tests, failures, ignored, returncode, output
    )


def junit_tree(runs: Sequence[UnityRun], suite_name: str, elapsed: float) -> ET.ElementTree:
    cases = [case for run in runs for case in run.cases]
    failures = sum(case.status == "FAIL" for case in cases)
    skipped = sum(case.status == "IGNORE" for case in cases)
    errors = sum(run.returncode != 0 and run.failures == 0 for run in runs)
    suite = ET.Element("testsuite", {
        "name": suite_name,
        "tests": str(len(cases)),
        "failures": str(failures),
        "errors": str(errors),
        "skipped": str(skipped),
        "time": f"{elapsed:.6f}",
    })
    for case in cases:
        node = ET.SubElement(suite, "testcase", {
            "classname": f"cJSON.{case.executable}",
            "name": case.name,
            "file": case.source,
            "line": str(case.line),
        })
        if case.status == "FAIL":
            ET.SubElement(node, "failure", {"message": case.message or "Unity failure"})
        elif case.status == "IGNORE":
            ET.SubElement(node, "skipped", {"message": case.message or "Unity ignored"})
    return ET.ElementTree(suite)


class Runner:
    def __init__(self, root: Path, source_revision: str | None, cc: str) -> None:
        self.root = root.resolve()
        self.source = self.root / "cjson-source"
        self.tests = self.source / "tests"
        self.build_root = self.root / "_build" / "qualification"
        self.evidence_root = self.root / "_build" / "evidence"
        self.cc = cc
        self.ar = os.environ.get("AR", "ar")
        manifest_revision = self.verify_component_manifest()
        expected_revision = self.gitlink_revision()
        if expected_revision and expected_revision != manifest_revision:
            raise QualificationError(
                "cjson-source gitlink does not match the pinned component manifest"
            )
        if source_revision is None:
            self.source_revision = expected_revision or manifest_revision
        else:
            self.source_revision = source_revision.strip().lower()
            if self.source_revision != manifest_revision:
                raise QualificationError(
                    "--source-revision does not match the pinned component manifest"
                )
        self.history: list[dict[str, object]] = []
        self.artifacts: list[Path] = []
        self.tool_versions: dict[str, str] = {
            "python": sys.version.splitlines()[0],
        }

    def verify_component_manifest(self) -> str:
        manifest_path = self.root / COMPONENT_MANIFEST
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise QualificationError(f"cannot read component source manifest: {exc}") from exc
        digest = hashlib.sha256(canonical_json(manifest).encode()).hexdigest()
        if digest != COMPONENT_MANIFEST_SHA256:
            raise QualificationError("component source manifest does not match its pinned SHA-256")
        if not isinstance(manifest, dict) or manifest.get("schema") != 1:
            raise QualificationError("component source manifest schema is invalid")
        revision = manifest.get("revision")
        files = manifest.get("files")
        if (
            not isinstance(revision, str)
            or len(revision) != 40
            or any(character not in "0123456789abcdef" for character in revision)
            or not isinstance(files, dict)
            or not files
        ):
            raise QualificationError("component source manifest identity is invalid")
        for relative, expected_sha256 in sorted(files.items()):
            if not isinstance(relative, str) or not isinstance(expected_sha256, str):
                raise QualificationError("component source manifest entry is invalid")
            relative_path = Path(relative)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise QualificationError("component source manifest path is unsafe")
            path = self.source / relative_path
            if not path.is_file():
                raise QualificationError(f"component source manifest file is missing: {relative}")
            actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual_sha256 != expected_sha256:
                raise QualificationError(
                    f"component source file does not match pinned revision: {relative}"
                )
        return revision

    def gitlink_revision(self) -> str:
        if not (self.root / ".git").exists():
            return ""
        result = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD:cjson-source"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if result.returncode:
            raise QualificationError("cannot determine cjson-source gitlink revision")
        revision = result.stdout.strip().lower()
        if len(revision) != 40 or any(character not in "0123456789abcdef" for character in revision):
            raise QualificationError("cjson-source gitlink revision is not a 40-hex object ID")
        return revision

    def require_tool(self, name: str) -> str:
        path = shutil.which(name)
        if path is None:
            raise QualificationError(f"required tool not found: {name}")
        if name not in self.tool_versions:
            result = subprocess.run(
                [path, "--version"], text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, check=False,
            )
            version = next(iter(result.stdout.splitlines()), "").strip()
            if not version:
                raise QualificationError(f"could not obtain version for {name}")
            self.tool_versions[name] = version
        return path

    def validate_sources(self) -> tuple[str, ...]:
        required = [
            self.source / source for source in COMPONENT_SOURCES
        ] + [
            self.tests / "unity_setup.c",
            self.tests / "unity" / "src" / "unity.c",
            self.tests / "inputs",
            self.tests / "json-patch-tests" / "tests.json",
        ]
        missing = [str(path.relative_to(self.root)) for path in required if not path.exists()]
        if missing:
            raise QualificationError("missing expected input(s): " + ", ".join(missing))
        discovered = tuple(sorted(
            path.stem for path in self.tests.glob("*.c")
            if path.name not in {"common.c", "unity_setup.c"}
        ))
        expected = tuple(sorted(EXPECTED_TESTS))
        missing_tests = sorted(set(expected) - set(discovered))
        extra_tests = sorted(set(discovered) - set(expected))
        if missing_tests or extra_tests:
            raise QualificationError(
                f"test source inventory mismatch; missing={missing_tests}, extra={extra_tests}"
            )
        return discovered

    def command(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        log: Path | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                list(argv), cwd=cwd, env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                timeout=120,
            )
        except subprocess.TimeoutExpired as exc:
            raise QualificationError(
                f"{shlex.join(argv)} timed out after 120 seconds"
            ) from exc

        def portable(value: str) -> str:
            return value.replace(str(self.root), "${PROJECT_ROOT}")

        self.history.append({
            "argv": [portable(value) for value in argv],
            "cwd": str((cwd or self.root).resolve().relative_to(self.root)),
            "returncode": result.returncode,
        })
        if log is not None:
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(result.stdout, encoding="utf-8")
            self.artifacts.append(log)
        if check and result.returncode != 0:
            if result.returncode < 0:
                signame = signal.Signals(-result.returncode).name
                detail = f"terminated by signal {signame}"
            else:
                detail = f"exited {result.returncode}"
            raise QualificationError(f"{shlex.join(argv)} {detail}")
        return result

    def clean_dir(self, name: str) -> Path:
        path = self.build_root / name
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
        return path

    def evidence_dir(self, activity: str) -> Path:
        path = self.evidence_root / activity
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
        return path

    def compile_objects(self, mode: str, flags: Sequence[str]) -> tuple[Path, list[Path]]:
        cc = self.require_tool(self.cc)
        ar = self.require_tool(self.ar)
        build = self.clean_dir(mode)
        objects: list[Path] = []
        for source_name in COMPONENT_SOURCES:
            obj = build / f"{Path(source_name).stem}.o"
            self.command([
                cc, "-std=c99", *flags, "-I", str(self.source), "-c",
                str(self.source / source_name), "-o", str(obj),
            ])
            if not obj.is_file():
                raise QualificationError(f"compiler did not create {obj.name}")
            objects.append(obj)
        library = build / "libcjson.a"
        self.command([ar, "rcs", str(library), *(str(obj) for obj in objects)])
        if not library.is_file():
            raise QualificationError("archiver did not create libcjson.a")
        return build, objects

    def build_tests(
        self, mode: str, flags: Sequence[str], component_objects: Sequence[Path]
    ) -> tuple[Path, tuple[str, ...]]:
        inventory = self.validate_sources()
        cc = self.require_tool(self.cc)
        build = self.build_root / mode
        unity_obj = build / "unity.o"
        relative = lambda path: str(path.relative_to(self.root))
        self.command([
            cc, "-std=c99", *flags, "-Wno-error", "-Wno-switch-enum",
            "-fvisibility=default", "-I", relative(self.tests / "unity" / "src"),
            "-c", relative(self.tests / "unity" / "src" / "unity.c"),
            "-o", relative(unity_obj),
        ], cwd=self.root)
        for name in inventory:
            executable = build / name
            test_source = self.tests / f"{name}.c"
            if name == "print_number":
                source_text = test_source.read_text(encoding="utf-8")
                ignored = """static void print_number_should_print_non_number(void)
{
    TEST_IGNORE();
    /* FIXME: Cannot test this easily in C89! */
    /* assert_print_number(\"null\", NaN); */
    /* assert_print_number(\"null\", INFTY); */
    /* assert_print_number(\"null\", -INFTY); */
}"""
                exercised = """static void print_number_should_print_non_number(void)
{
    assert_print_number(\"null\", NAN);
    assert_print_number(\"null\", INFINITY);
    assert_print_number(\"null\", -INFINITY);
}"""
                if source_text.count(ignored) != 1:
                    raise QualificationError(
                        "print_number non-number adaptation no longer matches pinned source"
                    )
                test_source = build / "print_number.qualification.c"
                test_source.write_text(
                    "#include <math.h>\n" + source_text.replace(ignored, exercised),
                    encoding="utf-8",
                )
            # Upstream common.h intentionally includes cJSON.c so tests can
            # exercise internal functions. Utility tests additionally need the
            # separately compiled cJSON_Utils component object.
            linked_components = (
                [component_objects[1]] if name in UTILS_TESTS else []
            )
            self.command([
                cc, "-std=c99", *flags,
                "-I", relative(self.source), "-I", relative(self.tests),
                relative(test_source), relative(self.tests / "unity_setup.c"),
                *(relative(obj) for obj in linked_components), relative(unity_obj),
                "-lm", "-o", relative(executable),
            ], cwd=self.root)
        actual = tuple(sorted(
            path.name for path in build.iterdir()
            if path.is_file() and os.access(path, os.X_OK)
        ))
        expected = tuple(sorted(EXPECTED_TESTS))
        if actual != expected:
            raise QualificationError(
                f"executable inventory mismatch; expected={list(expected)}, actual={list(actual)}"
            )
        return build, inventory

    def run_qualification_scenarios(
        self,
        activity: str,
        build: Path,
        flags: Sequence[str],
        objects: Sequence[Path],
        env: dict[str, str] | None = None,
    ) -> None:
        scenario_executable = build / "component_qualification_scenarios"
        self.command([
            self.require_tool(self.cc), "-std=c99", *flags,
            "-I", str(self.source),
            str(self.root / "tests" / "component_qualification_scenarios.c"),
            *(str(obj) for obj in objects), "-lm", "-o", str(scenario_executable),
        ])
        self.command(
            [str(scenario_executable)],
            env=env,
            log=self.evidence_root / activity / "logs" / "component_qualification_scenarios.txt",
        )

    def execute_tests(
        self, activity: str, build: Path, env: dict[str, str] | None = None
    ) -> list[UnityRun]:
        evidence = self.evidence_root / activity
        runs: list[UnityRun] = []
        for name in EXPECTED_TESTS:
            executable = build / name
            if not executable.is_file() or not os.access(executable, os.X_OK):
                raise QualificationError(f"missing expected executable: {name}")
            result = self.command(
                [str(executable)], cwd=self.tests, env=env,
                log=evidence / "logs" / f"{name}.txt", check=False,
            )
            if result.returncode < 0:
                raise QualificationError(
                    f"{name}: terminated by signal {signal.Signals(-result.returncode).name}"
                )
            run = parse_unity_output(name, result.stdout, result.returncode)
            runs.append(run)
            if result.returncode != 0:
                raise QualificationError(f"{name}: exited {result.returncode}")
            if run.failures:
                raise QualificationError(
                    f"{name}: {run.failures} failures, {run.ignored} ignored"
                )
            if run.ignored:
                raise QualificationError(f"{name}: {run.ignored} ignored tests are not accepted")
        total = sum(run.tests for run in runs)
        if len(runs) != len(EXPECTED_TESTS) or total != EXPECTED_CASES:
            raise QualificationError(
                f"suite inventory mismatch: {len(runs)} executables, {total} cases"
            )
        junit = evidence / "junit.xml"
        tree = junit_tree(runs, f"cJSON-{activity}", 0.0)
        ET.indent(tree, space="  ")
        tree.write(junit, encoding="utf-8", xml_declaration=True)
        parsed = ET.parse(junit).getroot()
        if (
            len(parsed.findall("testcase")) != EXPECTED_CASES
            or int(parsed.attrib["tests"]) != EXPECTED_CASES
            or int(parsed.attrib["failures"]) != 0
            or int(parsed.attrib["errors"]) != 0
            or int(parsed.attrib["skipped"]) != sum(run.ignored for run in runs)
        ):
            raise QualificationError("generated JUnit counters do not reconcile")
        self.artifacts.append(junit)
        return runs

    def test(self) -> None:
        self.evidence_dir("test")
        flags = ["-O2"]
        build, objects = self.compile_objects("test", flags)
        self.build_tests("test", flags, objects)
        self.execute_tests("test", build)
        self.run_qualification_scenarios("test", build, flags, objects)

    def sanitizer(self) -> None:
        self.evidence_dir("sanitizer")
        flags = [
            "-O1", "-g", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-fno-common",
        ]
        build, objects = self.compile_objects("sanitizer", flags)
        self.build_tests("sanitizer", flags, objects)
        env = os.environ.copy()
        env["ASAN_OPTIONS"] = "detect_leaks=1:halt_on_error=1"
        env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        self.execute_tests("sanitizer", build, env)
        self.run_qualification_scenarios("sanitizer", build, flags, objects, env)

    def warnings(self) -> None:
        evidence = self.evidence_dir("warnings")
        cc = self.require_tool(self.cc)
        self.validate_sources()
        for source_name in COMPONENT_SOURCES:
            log = evidence / f"{Path(source_name).stem}.txt"
            self.command([
                cc, "-std=c99", *WARNING_FLAGS, "-O2", "-I", str(self.source),
                "-fsyntax-only", str(self.source / source_name),
            ], log=log)

    def coverage(self) -> None:
        evidence = self.evidence_dir("coverage")
        gcovr = self.require_tool("gcovr")
        flags = ["-O0", "-g", "--coverage", "-fprofile-abs-path"]
        build, objects = self.compile_objects("coverage", flags)
        self.build_tests("coverage", flags, objects)
        self.execute_tests("coverage", build)
        self.run_qualification_scenarios("coverage", build, flags, objects)
        json_path = evidence / "coverage.json"
        text_path = evidence / "coverage.txt"
        common = [
            gcovr, "--root", str(self.source), "--object-directory", str(build),
            "--gcov-exclude-directories", re.escape(str(self.source / "build")),
            "--filter", re.escape(str(self.source)) + r"/cJSON(_Utils)?\.c$",
            "--exclude-unreachable-branches",
        ]
        self.command([*common, "--json-pretty", "--output", str(json_path)])
        self.command([
            *common, "--txt-metric", "branch", "--txt", "--output", str(text_path)
        ])
        if not json_path.is_file() or not text_path.is_file():
            raise QualificationError("gcovr did not create JSON and text reports")
        self.artifacts.extend([json_path, text_path])
        data = json.loads(json_path.read_text(encoding="utf-8"))
        files = data.get("files")
        if not isinstance(files, list) or not files:
            raise QualificationError("gcovr JSON contains no source files")
        scoped = {
            Path(item.get("file", "")).name: item
            for item in files
            if Path(item.get("file", "")).name in COMPONENT_SOURCES
        }
        if set(scoped) != set(COMPONENT_SOURCES):
            raise QualificationError(
                f"coverage source scope mismatch: {sorted(scoped)}"
            )
        line_total = line_hit = branch_total = branch_hit = 0
        for item in scoped.values():
            for line in item.get("lines", []):
                if "count" in line:
                    line_total += 1
                    line_hit += int(line["count"] > 0)
                for branch in line.get("branches", []):
                    branch_total += 1
                    branch_hit += int(branch.get("count", 0) > 0)
        if not line_total or not branch_total:
            raise QualificationError("coverage has zero measurable lines or branches")
        line_pct = 100.0 * line_hit / line_total
        branch_pct = 100.0 * branch_hit / branch_total
        metrics = {
            "scope": list(COMPONENT_SOURCES),
            "line": {"covered": line_hit, "total": line_total, "percent": line_pct,
                     "minimum_percent": LINE_COVERAGE_MIN},
            "branch": {"covered": branch_hit, "total": branch_total,
                       "percent": branch_pct, "minimum_percent": BRANCH_COVERAGE_MIN},
        }
        metrics_path = evidence / "metrics.json"
        metrics_path.write_text(canonical_json(metrics) + "\n", encoding="utf-8")
        self.artifacts.append(metrics_path)
        if line_pct < LINE_COVERAGE_MIN or branch_pct < BRANCH_COVERAGE_MIN:
            raise QualificationError(
                f"coverage below thresholds: line={line_pct:.2f}%, "
                f"branch={branch_pct:.2f}%"
            )

    def complexity(self) -> None:
        evidence = self.evidence_dir("complexity")
        lizard = self.require_tool("lizard")
        sources = list(COMPONENT_SOURCES)
        raw = evidence / "lizard.txt"
        self.command(
            [lizard, "-l", "c", *sources], cwd=self.source, log=raw, check=False
        )
        result = self.command(
            [lizard, "--csv", "-l", "c", *sources], cwd=self.source, check=False
        )
        csv_path = evidence / "lizard.csv"
        csv_path.write_text(result.stdout, encoding="utf-8")
        self.artifacts.append(csv_path)
        rows = list(csv.reader(result.stdout.splitlines()))
        findings: list[dict[str, object]] = []
        for row in rows:
            if not row:
                continue
            if len(row) < 10:
                raise QualificationError("lizard CSV is not parseable")
            try:
                ccn, length = int(row[1]), int(row[4])
            except ValueError as exc:
                raise QualificationError("lizard CSV contains invalid metrics") from exc
            if ccn > MAX_CCN or length > MAX_FUNCTION_LENGTH:
                findings.append({
                    "function": row[7], "source": row[6],
                    "cyclomatic_complexity": ccn, "function_length": length,
                })
        metrics = evidence / "metrics.json"
        metrics.write_text(canonical_json({
            "limits": CONFIGURATION["complexity_limits"],
            "functions": len(rows),
            "violations": findings,
        }) + "\n", encoding="utf-8")
        self.artifacts.append(metrics)
        if findings:
            raise QualificationError(f"complexity limits exceeded by {len(findings)} functions")

    def static_analysis(self) -> None:
        evidence = self.evidence_dir("static-analysis")
        cppcheck = self.require_tool("cppcheck")
        xml_path = evidence / "cppcheck.xml"
        result = self.command([
            cppcheck, "--enable=all", "--inconclusive", "--std=c99",
            "--suppress=missingIncludeSystem", "-I", ".",
            *COMPONENT_SOURCES, "--xml",
        ], cwd=self.source, check=False)
        xml_path.write_text(result.stdout, encoding="utf-8")
        self.artifacts.append(xml_path)
        if not result.stdout.strip():
            raise QualificationError("cppcheck produced empty XML")
        try:
            root = ET.fromstring(result.stdout)
        except ET.ParseError as exc:
            raise QualificationError("cppcheck XML is not parseable") from exc
        errors = root.find("errors")
        if errors is None:
            raise QualificationError("cppcheck XML has no errors inventory")
        findings = []
        blocking = []
        for node in errors.findall("error"):
            item = dict(node.attrib)
            item["locations"] = [dict(loc.attrib) for loc in node.findall("location")]
            findings.append(item)
            if item.get("severity") in {"error", "warning"}:
                blocking.append(item)
        inventory = evidence / "findings.json"
        inventory.write_text(canonical_json({
            "nonblocking_findings": [
                item for item in findings if item.get("severity") not in {"error", "warning"}
            ],
            "blocking_findings": blocking,
        }) + "\n", encoding="utf-8")
        self.artifacts.append(inventory)
        if result.returncode != 0:
            raise QualificationError(f"cppcheck exited {result.returncode}")
        if blocking:
            raise QualificationError(
                f"cppcheck reported {len(blocking)} error/warning findings"
            )

    def reproducible(self) -> None:
        evidence = self.evidence_dir("reproducible")
        self.validate_sources()
        cc = self.require_tool(self.cc)
        ar = self.require_tool(self.ar)
        comparisons: dict[str, dict[str, str | bool]] = {}
        parent = self.clean_dir("reproducible")
        dirs = [parent / "build-1", parent / "build-2"]
        for directory in dirs:
            # Each build starts from a newly created, empty output directory.
            directory.mkdir()
            objects = []
            for source_name in COMPONENT_SOURCES:
                obj = directory / f"{Path(source_name).stem}.o"
                self.command([
                    cc, "-std=c99", *WARNING_FLAGS, "-O2",
                    "-ffile-prefix-map=" + str(directory) + "=.",
                    "-I", str(self.source), "-c", str(self.source / source_name),
                    "-o", str(obj),
                ], env={**os.environ, "SOURCE_DATE_EPOCH": "0"})
                objects.append(obj)
            self.command([
                ar, "rcsD", str(directory / "libcjson.a"),
                *(str(obj) for obj in objects),
            ], env={**os.environ, "SOURCE_DATE_EPOCH": "0"})
        for name in ("cJSON.o", "cJSON_Utils.o", "libcjson.a"):
            hashes = [
                hashlib.sha256((directory / name).read_bytes()).hexdigest()
                for directory in dirs
            ]
            comparisons[name] = {
                "build_1_sha256": hashes[0],
                "build_2_sha256": hashes[1],
                "match": hashes[0] == hashes[1],
            }
        report = evidence / "comparison.json"
        report.write_text(canonical_json({"artifacts": comparisons}) + "\n", encoding="utf-8")
        self.artifacts.append(report)
        if not all(bool(item["match"]) for item in comparisons.values()):
            raise QualificationError("reproducible build artifact mismatch")

    def finalize(self, activity: str, result: str, message: str = "") -> None:
        activity_dir = self.evidence_root / activity
        activity_dir.mkdir(parents=True, exist_ok=True)
        result_path = activity_dir / "result.json"
        result_path.write_text(canonical_json({
            "activity": activity, "result": result, "message": message,
        }) + "\n", encoding="utf-8")
        if result_path not in self.artifacts:
            self.artifacts.append(result_path)

        junit_path = activity_dir / "result.junit.xml"
        suite = ET.Element("testsuite", {
            "name": f"cJSON-{activity}-gate",
            "tests": "1",
            "failures": "0" if result == "passed" else "1",
            "errors": "0",
            "skipped": "0",
            "time": "0.000000",
        })
        case = ET.SubElement(suite, "testcase", {
            "classname": "cJSON.qualification",
            "name": activity,
        })
        if result != "passed":
            ET.SubElement(case, "failure", {"message": message or "activity failed"})
        junit_tree_result = ET.ElementTree(suite)
        ET.indent(junit_tree_result, space="  ")
        junit_tree_result.write(junit_path, encoding="utf-8", xml_declaration=True)
        self.artifacts.append(junit_path)

        artifacts = sorted({
            path.resolve() for path in self.artifacts
            if path.exists() and activity_dir.resolve() in path.resolve().parents
            and not path.name.endswith(".provenance.json")
        })
        activity_history = ["planned", "ready", "running"]
        activity_history.append("completed" if result == "passed" else "failed")
        provenance_base = {
            "schema": 1,
            "source_revision": self.source_revision,
            "component_manifest_sha256": COMPONENT_MANIFEST_SHA256,
            "configuration_sha256": configuration_sha256(),
            "configuration": CONFIGURATION,
            "tool_versions": dict(sorted(self.tool_versions.items())),
            "activity_history": activity_history,
            "command_history": self.history,
            "result": result,
        }
        for artifact in artifacts:
            provenance = {
                **provenance_base,
                "artifact": str(artifact.relative_to(self.root)),
                "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            }
            sidecar = artifact.with_name(artifact.name + ".provenance.json")
            sidecar.write_text(canonical_json(provenance) + "\n", encoding="utf-8")

    def run_activity(self, activity: str) -> None:
        actions = {
            "test": self.test,
            "sanitizer": self.sanitizer,
            "coverage": self.coverage,
            "complexity": self.complexity,
            "warnings": self.warnings,
            "static-analysis": self.static_analysis,
            "reproducible": self.reproducible,
        }
        self.history = []
        self.artifacts = []
        try:
            actions[activity]()
        except (QualificationError, OSError, ValueError, json.JSONDecodeError) as exc:
            self.finalize(activity, "failed", str(exc))
            raise QualificationError(f"{activity}: {exc}") from exc
        self.finalize(activity, "passed")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", nargs="?", default="all",
        choices=("all", "test", "sanitizer", "coverage", "complexity",
                 "warnings", "static-analysis", "reproducible"),
    )
    parser.add_argument("--source-revision", help="revision recorded in provenance")
    parser.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    if sys.version_info < MIN_PYTHON:
        print("qualification.py requires Python 3.11+", file=sys.stderr)
        return 2
    args = parse_args(argv or sys.argv[1:])
    runner = Runner(Path(__file__).resolve().parents[1], args.source_revision, args.cc)
    activities = (
        ("test", "sanitizer", "coverage", "complexity", "warnings",
         "static-analysis", "reproducible")
        if args.command == "all" else (args.command,)
    )
    failures = []
    for activity in activities:
        print(f"=== {activity} ===", flush=True)
        try:
            runner.run_activity(activity)
        except QualificationError as exc:
            failures.append(str(exc))
            print(f"FAIL: {exc}", file=sys.stderr, flush=True)
            if args.command != "all":
                return 1
        else:
            print(f"PASS: {activity}", flush=True)
    if failures:
        print("Qualification evidence run failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
