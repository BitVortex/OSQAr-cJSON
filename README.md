# OSQAr-cJSON — ISO 26262 ASIL D SEooC Qualification

[![CI](https://github.com/BitVortex/OSQAr-cJSON/actions/workflows/ci.yml/badge.svg)](https://github.com/BitVortex/OSQAr-cJSON/actions/workflows/ci.yml)
[![OSQAr](https://img.shields.io/badge/OSQAr-v0.7.0-blue)](https://github.com/BitVortex/OSQAr/releases/tag/v0.7.0)
[![cJSON](https://img.shields.io/badge/cJSON-v1.7.19-green)](https://github.com/DaveGamble/cJSON/releases/tag/v1.7.19)
[![Release](https://img.shields.io/badge/release-1.7.19--0.7.0-orange)](https://github.com/BitVortex/OSQAr-cJSON/releases/tag/1.7.19-0.7.0)

> ⚠️ **RESEARCH REPOSITORY — NO WARRANTY**  
> This is an **active research repository** for agentic qualification of open-source software for cyber-physical systems. The OSQAr framework and all qualification artifacts herein are produced by autonomous AI agents in a research setting. **Information may be inconsistent, outdated, incomplete, or just plain wrong.** No warranty, express or implied, is provided. No liability is assumed for any use of this material in safety-critical contexts. This qualification has **not** been reviewed or approved by any accredited certification body. Do **not** use in production safety systems without independent expert review.

---

cJSON v1.7.19 qualified as an ISO 26262 ASIL D Safety Element out of Context (SEooC) using the [OSQAr](https://github.com/BitVortex/OSQAr) (Open Safety Qualification Architecture) framework.

## Referenced Components

| Component | Repository | Pinned Version |
|-----------|-----------|---------------|
| **OSQAr** | [BitVortex/OSQAr](https://github.com/BitVortex/OSQAr) | [`v0.7.0`](https://github.com/BitVortex/OSQAr/releases/tag/v0.7.0) |
| **cJSON** | [DaveGamble/cJSON](https://github.com/DaveGamble/cJSON) | [`v1.7.19`](https://github.com/DaveGamble/cJSON/releases/tag/v1.7.19) |

## Releases

Tagged releases follow the format **`cjson_version-osqar_version`** (e.g., `1.7.19-0.7.0`). Each release is a CI-generated auditable shipment containing:

| Asset | Description |
|-------|------------|
| `osqar_cjson_shipment.zip` | Full evidence bundle: Sphinx HTML docs, `needs.json`, `traceability_report.json`, `SHA256SUMS`, test results, coverage, complexity, sanitizer logs, cJSON source baseline |
| `osqar_cjson_shipment.zip.sha256` | SHA-256 of the shipment ZIP for downstream integrity verification |

**[Latest release →](https://github.com/BitVortex/OSQAr-cJSON/releases/latest)**

## Qualification Summary

- **45 needs** across 6 documents: 12 requirements, 7 architecture elements, 14 verification activities, 6 lifecycle items
- **56 bidirectional links**, **zero traceability violations** — verified via `osqar traceability --test-prefix VER_ --code-prefix IMPL_`
- **cJSON builds with `-Werror -Wall -Wextra -Wconversion`** — zero warnings across 5,066 LOC
- **Test suite passes** under ASan+UBSan instrumentation — clean
- **Sphinx HTML** built with PlantUML architecture diagrams, zero warnings
- **CI pipeline** on every push and tag: build → test → sanitize → coverage → docs → traceability → shipment → release

## Quickstart

### Clone and build

```bash
git clone --recurse-submodules https://github.com/BitVortex/OSQAr-cJSON.git
cd OSQAr-cJSON
./build-and-test.sh all
```

### Rebuild documentation

```bash
python3 -m pip install -r requirements-docs.txt

# With PlantUML diagrams
python3 -m sphinx -b html -W . _build/html

# Without diagrams (offline)
OSQAR_NO_DIAGRAMS=1 python3 -m sphinx -b html . _build/html

# Verify traceability (custom need-ID prefixes)
osqar traceability _build/html/needs.json \
  --test-prefix VER_ --code-prefix IMPL_
```

## Repository Structure

```
.
├── 01_requirements.rst            # 12 safety requirements (REQ_*)
├── 02_architecture.rst            # 7 architecture elements + 3 PlantUML diagrams (ARCH_*)
├── 03_verification.rst            # 14 verification activities (VER_*)
├── 04_implementation.rst          # Source inventory, build config (IMPL_*)
├── 05_test_results.rst            # Test results, coverage, static analysis
├── 06_lifecycle_management.rst    # AoUs, CM baseline, issue management (LM_*)
├── index.rst                      # Master toctree + qualification summary
├── conf.py                        # Sphinx config (_NO_DIAGRAMS guard, PlantUML detection)
├── osqar_project.json             # Commands + verification.gaps + verification.run
├── build-and-test.sh              # Qualification build & test pipeline
├── cjson-source/                  # cJSON v1.7.19 (git submodule, pinned commit)
├── _static/                       # PlantUML sources (.puml), gap docs, custom CSS
├── .github/workflows/ci.yml       # CI pipeline: build → test → docs → shipment → release
├── _build/                        # CI-generated: Sphinx HTML, needs.json
└── _shipment/                     # CI-generated: evidence bundle + SHA256SUMS
```

## Verification Activities

### Executed in CI pipeline

| # | Activity | Status |
|---|----------|--------|
| 1 | Compiler warning audit (`-Werror`) | ✅ Zero warnings |
| 2 | Test suite (1,000+ tests) | ✅ PASS |
| 3 | ASan+UBSan instrumentation | ✅ Clean |
| 4 | Stack depth verification (nesting limit 1000) | ✅ Enforced |
| 5 | NULL-pointer safety (all 78 API functions) | ✅ Deterministic |
| 6 | Coverage measurement (gcov, ≥90% stmt, ≥80% branch) | ✅ 91.7% / 83.3% |
| 7 | Complexity analysis (lizard, McCabe ≤15) | ✅ One justified exception |
| 8 | Static analysis (cppcheck) | ✅ In pipeline |

### Planned — tracked as GitHub issues

| # | Activity | Issue |
|---|----------|-------|
| 9 | Valgrind/Memcheck | [#5](https://github.com/BitVortex/OSQAr-cJSON/issues/5) |
| 10 | Fuzzing campaign (AFL++/libFuzzer, 24h) | [#6](https://github.com/BitVortex/OSQAr-cJSON/issues/6) |
| 11 | MISRA C:2012 compliance | [#7](https://github.com/BitVortex/OSQAr-cJSON/issues/7) — commercial tool |
| 12 | MC/DC coverage (ASIL D) | [#8](https://github.com/BitVortex/OSQAr-cJSON/issues/8) — commercial tool |
| 13 | RFC conformance (independent validator) | [#9](https://github.com/BitVortex/OSQAr-cJSON/issues/9) |
| 14 | Reproducible build verification | [#10](https://github.com/BitVortex/OSQAr-cJSON/issues/10) |

Gaps are documented with structured status/reason/mitigation in `osqar_project.json` → `verification.gaps` (OSQAr v0.7.0 feature) and rendered in the Sphinx HTML documentation per ISO 26262-8 §11.4.8.
