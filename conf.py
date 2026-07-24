"""Sphinx configuration for the bounded cJSON qualification attempt."""

from pathlib import Path
import json
import os
import sys

sys.path.insert(0, str(Path(__file__).parent))

project = "OSQAr-cJSON Qualification Attempt"
author = "OSQAr-cJSON contributors"
release = "1.7.19-0.10.2"

extensions = [
    "sphinx_needs",
    "sphinxcontrib.test_reports",
    "sphinx_data_viewer",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    ".venv",
    "Thumbs.db",
    ".DS_Store",
    "cjson-source",
    "unity",
]
html_theme = "furo"
html_static_path = ["_static"]
html_title = "OSQAr-cJSON — bounded qualification attempt"

needs_types = [
    {"directive": "req", "title": "Requirement", "prefix": "REQ_", "color": "#BFD8D2", "style": "node"},
    {"directive": "arch", "title": "Architecture", "prefix": "ARCH_", "color": "#FEDCD2", "style": "node"},
    {"directive": "impl", "title": "Implementation", "prefix": "IMPL_", "color": "#DF744A", "style": "node"},
    {"directive": "ver", "title": "Verification", "prefix": "VER_", "color": "#DCB239", "style": "node"},
    {"directive": "result", "title": "Result", "prefix": "RESULT_", "color": "#D6E5FA", "style": "node"},
    {"directive": "evidence", "title": "Evidence", "prefix": "EVID_", "color": "#B7E4C7", "style": "node"},
    {"directive": "lifecycle", "title": "Lifecycle", "prefix": "LM_", "color": "#E8DAEF", "style": "node"},
    {"directive": "safety_case", "title": "Safety-case", "prefix": "SC_", "color": "#FADBD8", "style": "node"},
]

needs_fields = {
    name: {
        "description": f"OSQAr qualification field: {name}",
        "schema": {"type": "string"},
        "nullable": True,
        "default": "",
    }
    for name in [
        "kind",
        "evidence_state",
        "acceptance_activity",
        "source_revision",
        "configuration_sha256",
        "owner",
        "gate_effect",
    ]
}
needs_links = {
    "allocated_to": {"incoming": "allocated from", "outgoing": "allocated to"},
    "allocated_to_api": {"incoming": "API allocation from", "outgoing": "allocated to API"},
    "realized_by": {"incoming": "realizes", "outgoing": "realized by"},
    "verified_by": {"incoming": "verifies", "outgoing": "verified by"},
    "produces": {"incoming": "produced by", "outgoing": "produces"},
    "evidenced_by": {"incoming": "evidence for", "outgoing": "evidenced by"},
    "supported_by": {"incoming": "supports", "outgoing": "supported by"},
    "references": {"incoming": "referenced by", "outgoing": "references"},
    "constrains": {"incoming": "constrained by", "outgoing": "constrains"},
    "applies_to": {"incoming": "deviation applies", "outgoing": "applies to"},
}

needs_id_required = True
needs_id_regex = r"^[A-Z][A-Z0-9_]{2,}$"
needs_build_json = True
needs_reproducible_json = True
needs_warnings_always_warn = True
needs_warnings = {
    "missing_status": "not status",
    "invalid_status": "status not in ['active', 'passed', 'passed-with-deviation', 'approved', 'supported', 'accepted', 'open', 'blocked', 'planned']",
}

nitpicky = True
smartquotes = False

# Evidence and rendered outputs are intentionally reproducible and must not embed
# the local checkout path or the wall-clock build time.
html_last_updated_fmt = None
os.environ.setdefault("SOURCE_DATE_EPOCH", "0")


def _normalize_osqar_relations(app, exception):
    """Write the v0.10.2 directed relation object without empty link fields.

    Sphinx-Needs exports every configured link as a top-level empty list on
    every need. OSQAr v0.10.2 correctly rejects relations that are not allowed
    for a source type, but it interprets those empty compatibility fields as
    authored relations. Normalizing only the exported JSON preserves the
    Sphinx graph while giving OSQAr the declared, non-empty directed edges.
    """
    if exception is not None or app.builder.name != "html":
        return
    output = Path(app.outdir) / "needs.json"
    if not output.is_file():
        return
    data = json.loads(output.read_text(encoding="utf-8"))
    version = data.get("current_version")
    versions = data.get("versions", {})
    needs = versions.get(version, {}).get("needs", {})
    relation_names = tuple(needs_links)
    for need in needs.values():
        declared = {
            name: need[name]
            for name in relation_names
            if isinstance(need.get(name), list) and need[name]
        }
        need["relations"] = declared
        for name in relation_names:
            need.pop(name, None)
            need.pop(f"{name}_back", None)
    output.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def setup(app):
    app.connect("build-finished", _normalize_osqar_relations, priority=999)
