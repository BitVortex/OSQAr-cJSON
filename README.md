# OSQAr-cJSON — bounded software-component qualification attempt

[![Qualification CI](https://github.com/BitVortex/OSQAr-cJSON/actions/workflows/qualification.yml/badge.svg)](https://github.com/BitVortex/OSQAr-cJSON/actions/workflows/qualification.yml)
[![OSQAr](https://img.shields.io/badge/OSQAr-v0.10.2-blue)](https://github.com/BitVortex/OSQAr/releases/tag/v0.10.2)
[![cJSON](https://img.shields.io/badge/cJSON-v1.7.19-green)](https://github.com/DaveGamble/cJSON/releases/tag/v1.7.19)

> **RESEARCH ARTIFACT — CURRENT DECISION: BLOCK**
>
> This repository applies OSQAr v0.10.2 to a bounded qualification attempt for
> cJSON v1.7.19. It is not a certification, ISO 26262 compliance statement,
> ASIL allocation, or claim that cJSON is qualified for an automotive item.
> Item-specific suitability, tool confidence, assumptions of use, anomaly
> disposition, and independent qualification verification remain unresolved.

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

## Reproduce the candidate evidence

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

A technical activity can pass while the overall qualification decision remains
BLOCK. OSQAr framework or typed-traceability PASS means only that the declared
machine-checkable profile rules passed for the supplied immutable inputs. It
does not establish semantic adequacy, ISO 26262 compliance, certification, or
item-specific safety.

No archive may be represented as a qualified component package while a required
activity, manifest check, controlled gap, or independent exact-tree review is
BLOCK.

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
