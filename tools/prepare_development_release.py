#!/usr/bin/env python3
"""Prepare an exact, explicitly non-qualified OSQAr-cJSON development bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

POLICY_PATH = Path("assurance/candidate-integration-policy.json")
SOURCE_MANIFEST_PATH = Path("assurance/component-source-manifest.json")
REQUIRED_DOCS = ("index.html", "needs.json")
REQUIRED_EVIDENCE = (
    "framework-validation.json",
    "traceability-qualification-v1.json",
)
RELEASE_MANIFEST_EXCLUSIONS = (
    "documentation/_static/scripts/furo-extensions.js",
    "evidence/warnings/cJSON.txt",
    "evidence/warnings/cJSON_Utils.txt",
)


class ReleasePreparationError(RuntimeError):
    """A release input does not satisfy the development-release contract."""


def run_git(root: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ReleasePreparationError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleasePreparationError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleasePreparationError(f"{label} must be a JSON object")
    return value


def checkout_exact_tree(repository: Path, revision: str, destination: Path) -> str:
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osqar-release-index-") as temporary:
        index = Path(temporary) / "index"
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(index)
        run_git(repository, "read-tree", revision, env=env)
        run_git(
            repository,
            f"--work-tree={destination}",
            "checkout-index",
            "--all",
            "--force",
            env=env,
        )
        reproduced = run_git(repository, "write-tree", env=env)
    expected = run_git(repository, "rev-parse", f"{revision}^{{tree}}")
    if reproduced != expected:
        raise ReleasePreparationError("temporary checkout did not reproduce the requested tree")
    return expected


def verify_component_source(source_root: Path, manifest_path: Path, revision: str) -> int:
    manifest = load_object(manifest_path, "component source manifest")
    if manifest.get("revision") != revision:
        raise ReleasePreparationError("component source revision differs from its manifest")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ReleasePreparationError("component source manifest file inventory is invalid")
    actual = {
        path.relative_to(source_root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    expected = set(files)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise ReleasePreparationError(
            f"component source inventory differs: missing={missing} unexpected={unexpected}"
        )
    for relative, expected_digest in sorted(files.items()):
        if not isinstance(relative, str) or not isinstance(expected_digest, str):
            raise ReleasePreparationError("component source manifest entry is invalid")
        path = source_root / relative
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected_digest:
            raise ReleasePreparationError(f"component source digest differs: {relative}")
    return len(files)


def prepare(
    root: Path,
    output: Path,
    docs: Path,
    evidence: Path,
    release_version: str,
    release_revision: str,
) -> dict[str, Any]:
    root = root.resolve()
    output = output.resolve()
    docs = docs.resolve()
    evidence = evidence.resolve()
    if output.exists():
        raise ReleasePreparationError(f"output already exists: {output}")
    for name in REQUIRED_DOCS:
        if not (docs / name).is_file():
            raise ReleasePreparationError(f"required documentation output is missing: {name}")
    for name in REQUIRED_EVIDENCE:
        if not (evidence / name).is_file():
            raise ReleasePreparationError(f"required evidence output is missing: {name}")

    resolved_revision = run_git(root, "rev-parse", f"{release_revision}^{{commit}}")
    repository_output = output / "repository"
    release_tree = checkout_exact_tree(root, resolved_revision, repository_output)

    policy = load_object(repository_output / POLICY_PATH, "candidate integration policy")
    authorization = policy.get("development_release")
    if not isinstance(authorization, dict) or authorization.get("authorized") is not True:
        raise ReleasePreparationError("development release is not authorized")
    if authorization.get("release_version") != release_version:
        raise ReleasePreparationError(f"release version {release_version!r} is not authorized")
    if authorization.get("channel") != "pre-integration-development":
        raise ReleasePreparationError("development release channel is not authorized")
    if authorization.get("github_prerelease") is not True:
        raise ReleasePreparationError("development release must be a GitHub prerelease")
    if policy.get("qualification_claimed") is not False:
        raise ReleasePreparationError("policy must not claim qualification")
    if policy.get("qualification_publication_authorized") is not False:
        raise ReleasePreparationError("policy must not authorize qualification publication")

    source_revision = run_git(root, "rev-parse", f"{resolved_revision}:cjson-source")
    source_output = repository_output / "cjson-source"
    if source_output.exists():
        shutil.rmtree(source_output)
    checkout_exact_tree(root / "cjson-source", source_revision, source_output)
    source_count = verify_component_source(
        source_output,
        repository_output / SOURCE_MANIFEST_PATH,
        source_revision,
    )

    shutil.copytree(docs, output / "documentation")
    shutil.copytree(evidence, output / "evidence")
    empty_files = sorted(
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file() and path.stat().st_size == 0
    )
    if empty_files != list(RELEASE_MANIFEST_EXCLUSIONS):
        raise ReleasePreparationError(
            "zero-length release inventory differs: "
            f"expected={list(RELEASE_MANIFEST_EXCLUSIONS)} actual={empty_files}"
        )
    tracked_count = sum(
        1
        for path in repository_output.rglob("*")
        if path.is_file() or path.is_symlink()
    )
    status: dict[str, Any] = {
        "schema": "osqar-cjson.development-release.v1",
        "release_version": release_version,
        "release_revision": resolved_revision,
        "release_tree": release_tree,
        "release_channel": "pre-integration-development",
        "github_prerelease": True,
        "component": {
            "name": "cJSON",
            "version": "1.7.19",
            "source_revision": source_revision,
            "source_manifest_file_count": source_count,
        },
        "osqar_version": "0.10.2",
        "qualification_status": "BLOCKED",
        "qualification_claimed": False,
        "qualification_publication_authorized": False,
        "release_manifest_exclusions": list(RELEASE_MANIFEST_EXCLUSIONS),
        "candidate_integration_policy": POLICY_PATH.as_posix(),
        "tracked_file_count": tracked_count,
        "notice": (
            "This prerelease supports pre-integration development. It is not a "
            "qualified component package, certification, compliance statement, "
            "or ASIL allocation. See the bundled documentation and evidence for "
            "the exact open qualification findings."
        ),
    }
    (output / "DEVELOPMENT-RELEASE.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return status


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--docs", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--release-revision", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        status = prepare(
            args.root,
            args.output,
            args.docs,
            args.evidence,
            args.release_version,
            args.release_revision,
        )
    except ReleasePreparationError as exc:
        print(f"development release preparation: FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "development release preparation: PASS "
        f"({status['tracked_file_count']} tracked files; qualification BLOCKED)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
