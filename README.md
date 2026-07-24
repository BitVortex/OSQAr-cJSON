# OSQAr-cJSON — bounded software-component qualification attempt

[![Qualification CI](https://github.com/BitVortex/OSQAr-cJSON/actions/workflows/ci.yml/badge.svg)](https://github.com/BitVortex/OSQAr-cJSON/actions/workflows/ci.yml)
[![OSQAr](https://img.shields.io/badge/OSQAr-v0.10.2-blue)](https://github.com/BitVortex/OSQAr/releases/tag/v0.10.2)
[![cJSON](https://img.shields.io/badge/cJSON-v1.7.19-green)](https://github.com/DaveGamble/cJSON/releases/tag/v1.7.19)

> **WORK IN PROGRESS — QUALIFICATION: BLOCKED; DEVELOPMENT PRERELEASE AVAILABLE**
>
> The `main` branch contains an actively developed, bounded qualification attempt
> for cJSON v1.7.19 using OSQAr v0.10.2. It is not a certification, an ISO 26262
> compliance statement, an ASIL allocation, or a claim that cJSON is qualified
> for an automotive item. The merged baseline is intended to support continued
> qualification work while its documented gaps remain visible and fail closed.

## Current qualification gaps

- **QF-01 — complexity:** 15 of 154 measured functions exceed the configured
  cyclomatic-complexity limit, function-length limit, or both; the observed
  maxima are CCN 37 and 230 lines.
- **QF-02 — static analysis:** 17 Cppcheck error/warning findings remain open.
- **Coverage adequacy:** measured coverage is 90.44% line and 80.26% branch.
  These values meet local mechanical thresholds, but MC/DC has not been measured
  and uncovered code has not received an independently approved disposition.
- **Outstanding verification activities:** Valgrind/Memcheck, sustained fuzzing,
  MISRA C assessment with a suitable checker, MC/DC measurement, and independent
  RFC-conformance validation remain incomplete; see open issues
  [#5](https://github.com/BitVortex/OSQAr-cJSON/issues/5) through
  [#9](https://github.com/BitVortex/OSQAr-cJSON/issues/9).
- **Qualification assurance:** evidence approval, finding-specific deviation
  approval, tool-confidence justification, intended-use and assumptions-of-use
  confirmation, anomaly disposition, and independent verification of the final
  qualification result remain incomplete.

CI is intentionally green only when it reproduces this exact documented blocked
state. The candidate policy permits release `1.7.19-0.10.2` only as a GitHub
prerelease for pre-integration development. Qualification remains blocked, and
the prerelease must not be represented as a qualified component package.

## Development release boundary

Tag `1.7.19-0.10.2` publishes the exact tagged repository sources, pinned
cJSON source, rendered documentation, and generated blocked-state evidence in a
release-manifest bundle. `DEVELOPMENT-RELEASE.json` labels the release channel
and blocked qualification status; `OSQAR-RELEASE-MANIFEST.json` binds the
bundle inventory except for three explicitly listed zero-length renderer/warning
files, while the adjacent archive checksum binds the complete ZIP. This
publication supports development and pre-integration
work only. It does not approve evidence or establish qualification, compliance,
certification, an ASIL allocation, or item-specific suitability.

## Scope

The primary process framing is **ISO 26262-8:2018, Clause 12** (qualification of
software components). ISO 26262-6 verification techniques support the evidence
but do not replace the Part 8 intended-use and qualification-verification
obligations.

- **Component baseline:** cJSON tag `v1.7.19`, git object
  `c859b25da02955fef659d658b8f324b5cde87be3`.
- **In-scope implementation:** `cJSON.c` and `cJSON.h`, with the configuration
  stated in `01_requirements.rst`.
- **Outside the claim:** cJSON Utils, packaging/CMake integration,
  locale-enabled behavior, custom allocator behavior, concurrency of mutable
  trees, and item-specific resource/timing properties.
- **Target:** ASIL D verification rigor. This is a target for the evidence
  workflow, not an achieved qualification status.

The utilities source and tests are still built as regression context; that does
not silently extend the claim boundary.

## What changed for OSQAr v0.10.2

- fail-closed native test/evidence execution;
- component-instrumented ASan/UBSan builds;
- exact Unity executable/case inventory with reconciled JUnit;
- live, parsed coverage, complexity, compiler-warning, static-analysis, and
  reproducibility evidence;
- source/configuration-bound activity provenance;
- typed directed traceability (`allocated_to`, `realized_by`, `verified_by`,
  `produces`, and `evidenced_by`);
- qualification-profile framework and traceability gates;
- an operational assumptions-of-use protocol and controlled Clause 12 gaps;
- hash-locked Python qualification dependencies; and
- an exact-inventory `OSQAR-RELEASE-MANIFEST.json` for candidate shipments.

The full pre-revision findings are retained in
[`assurance/reviews/pre-v0.10.2-baseline-review.md`](assurance/reviews/pre-v0.10.2-baseline-review.md).

## Reproduce the current evidence

Prerequisites are Python 3.11+, a C99 compiler/toolchain, `ar`, and `uv` (or an
equivalent hash-verifying installer).

```bash
git clone --recurse-submodules https://github.com/BitVortex/OSQAr-cJSON.git
cd OSQAr-cJSON

uv venv --python 3.11 .venv
uv pip sync --python .venv/bin/python requirements.lock
export PATH="$PWD/.venv/bin:$PATH"

pytest -q
./build-and-test.sh all --source-revision "$(git rev-parse HEAD:cjson-source)"
sphinx-build -W --keep-going -b html . _build/html
```

Run the OSQAr gates with the source revision and configuration SHA-256 emitted
by the native runner:

```bash
osqar framework validate \
  --project osqar_project.json \
  --profile qualification \
  --source-revision "$(git rev-parse HEAD:cjson-source)" \
  --configuration-sha256 "$CONFIGURATION_SHA256" \
  --report-json _build/evidence/framework-report.json

osqar traceability _build/html/needs.json \
  --profile qualification \
  --evidence-project osqar_project.json \
  --source-revision "$(git rev-parse HEAD:cjson-source)" \
  --configuration-sha256 "$CONFIGURATION_SHA256" \
  --json-report _build/evidence/traceability-report.json
```

Do not replace a failed gate with an unvalidated file or weaken a threshold to
obtain a pass. The runner documentation is in
[`tools/README.md`](tools/README.md).

## Evidence interpretation

A technical activity or candidate-integration CI run can pass while the overall
qualification decision remains BLOCK. For the current `main` baseline, green CI
requires the native, framework, and traceability reports to reproduce the exact
documented blocked outcome in `assurance/candidate-integration-policy.json`;
it is not a qualification PASS. OSQAr framework or typed-traceability PASS means
only that the declared machine-checkable profile rules passed for the supplied
immutable inputs. It does not establish semantic adequacy, ISO 26262 compliance,
certification, or item-specific safety.

No archive may be represented as a qualified component package while a required
activity, manifest check, controlled gap, or independent exact-tree review is
BLOCK. A separately labeled pre-integration development prerelease does not alter
that decision.

## Repository map

- `01_requirements.rst` — bounded component and intended-use specification
- `02_architecture.rst` — typed architecture/API allocation
- `03_verification.rst` — required activities and candidate evidence bindings
- `04_implementation.rst` — source/build/configuration identity
- `05_test_results.rst` — evidence reconciliation and promotion rules
- `06_lifecycle_management.rst` — AoU protocol and controlled gap register
- `07_safety_case.rst` — explicit BLOCK argument and release decision
- `tools/qualification.py` — fail-closed native evidence runner
- `tests/` — parser, inventory, failure, and executable fault-seed regressions
- `requirements.lock` — hash-locked OSQAr v0.10.2 tool environment
- `assurance/reviews/` — immutable review records

## Licence and upstream source

This repository's assurance material follows its declared repository licence.
The cJSON and Unity submodules retain their respective upstream licences. No
warranty is provided; independently assess all material before safety-related
use.
