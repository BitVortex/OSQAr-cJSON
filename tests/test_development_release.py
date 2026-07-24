from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "prepare_development_release.py"


def candidate_commit(tmp_path: Path) -> str:
    index = tmp_path / "candidate.index"
    env = os.environ.copy()
    env.update(
        {
            "GIT_INDEX_FILE": str(index),
            "GIT_AUTHOR_NAME": "OSQAr-cJSON test",
            "GIT_AUTHOR_EMAIL": "osqar-cjson-test@example.invalid",
            "GIT_COMMITTER_NAME": "OSQAr-cJSON test",
            "GIT_COMMITTER_EMAIL": "osqar-cjson-test@example.invalid",
        }
    )
    subprocess.run(["git", "read-tree", "HEAD"], cwd=ROOT, env=env, check=True)
    subprocess.run(["git", "add", "-A"], cwd=ROOT, env=env, check=True)
    tree = subprocess.check_output(
        ["git", "write-tree"], cwd=ROOT, env=env, text=True
    ).strip()
    return subprocess.check_output(
        ["git", "commit-tree", tree, "-p", "HEAD"],
        cwd=ROOT,
        env=env,
        input="test candidate\n",
        text=True,
    ).strip()


def test_tag_workflow_publishes_only_a_documented_development_prerelease() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "tags:" in workflow
    assert "'[0-9]*.[0-9]*.[0-9]*-[0-9]*.[0-9]*.[0-9]*'" in workflow
    assert "prepare_development_release.py" in workflow
    assert "release-manifest generate" in workflow
    assert "release-manifest verify" in workflow
    assert "prerelease: true" in workflow
    assert "make_latest: false" in workflow
    assert "qualification remains BLOCKED" in workflow
    assert "actions/deploy-pages@v4" in workflow


def test_docs_distinguish_development_release_from_qualification_publication() -> None:
    readme = " ".join((ROOT / "README.md").read_text().split())
    index = " ".join((ROOT / "index.rst").read_text().split())
    results = " ".join((ROOT / "05_test_results.rst").read_text().split())
    lifecycle = " ".join((ROOT / "06_lifecycle_management.rst").read_text().split())
    safety_case = " ".join((ROOT / "07_safety_case.rst").read_text().split())
    for text in (readme, index, results, lifecycle, safety_case):
        assert "pre-integration development" in text
        assert "1.7.19-0.10.2" in text
        assert "qualification remains blocked" in text.lower()
    assert "GitHub prerelease" in readme
    assert "DEVELOPMENT-RELEASE.json" in lifecycle
    assert "OSQAR-RELEASE-MANIFEST.json" in lifecycle


def test_prepare_development_release_copies_exact_tracked_inputs_and_status(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "generated-docs"
    evidence = tmp_path / "generated-evidence"
    docs.mkdir()
    evidence.mkdir()
    (docs / "index.html").write_text("docs", encoding="utf-8")
    (docs / "needs.json").write_text("{}", encoding="utf-8")
    (docs / "_static" / "scripts").mkdir(parents=True)
    (docs / "_static" / "scripts" / "furo-extensions.js").write_bytes(b"")
    (evidence / "framework-validation.json").write_text("{}", encoding="utf-8")
    (evidence / "traceability-qualification-v1.json").write_text(
        "{}", encoding="utf-8"
    )
    (evidence / "warnings").mkdir()
    (evidence / "warnings" / "cJSON.txt").write_bytes(b"")
    (evidence / "warnings" / "cJSON_Utils.txt").write_bytes(b"")
    output = tmp_path / "bundle"
    revision = candidate_commit(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(ROOT),
            "--output",
            str(output),
            "--docs",
            str(docs),
            "--evidence",
            str(evidence),
            "--release-version",
            "1.7.19-0.10.2",
            "--release-revision",
            revision,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout
    status = json.loads((output / "DEVELOPMENT-RELEASE.json").read_text())
    assert status["release_version"] == "1.7.19-0.10.2"
    assert status["release_revision"] == revision
    assert status["release_channel"] == "pre-integration-development"
    assert status["github_prerelease"] is True
    assert status["qualification_status"] == "BLOCKED"
    assert status["qualification_claimed"] is False
    assert status["qualification_publication_authorized"] is False
    assert status["release_manifest_exclusions"] == [
        "documentation/_static/scripts/furo-extensions.js",
        "evidence/warnings/cJSON.txt",
        "evidence/warnings/cJSON_Utils.txt",
    ]
    exported_files = [
        path for path in (output / "repository").rglob("*") if path.is_file()
    ]
    assert status["tracked_file_count"] == len(exported_files)
    assert (output / "repository" / "tools" / "qualification.py").is_file()
    assert (output / "repository" / "cjson-source" / "cJSON.c").is_file()
    assert (output / "documentation" / "index.html").read_text() == "docs"
    assert (
        output / "evidence" / "traceability-qualification-v1.json"
    ).is_file()


def test_prepare_development_release_rejects_unapproved_version(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    evidence = tmp_path / "evidence"
    docs.mkdir()
    evidence.mkdir()
    (docs / "index.html").write_text("docs", encoding="utf-8")
    (docs / "needs.json").write_text("{}", encoding="utf-8")
    (evidence / "framework-validation.json").write_text("{}", encoding="utf-8")
    (evidence / "traceability-qualification-v1.json").write_text(
        "{}", encoding="utf-8"
    )
    revision = candidate_commit(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(ROOT),
            "--output",
            str(tmp_path / "bundle"),
            "--docs",
            str(docs),
            "--evidence",
            str(evidence),
            "--release-version",
            "1.7.19-0.10.3",
            "--release-revision",
            revision,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode != 0
    assert "not authorized" in result.stdout
