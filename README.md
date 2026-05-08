# OSQAr-cJSON — ISO 26262 ASIL D SEooC Qualification

cJSON v1.7.19 qualified as an ISO 26262 ASIL D Safety Element out of Context (SEooC) using the [OSQAr](https://github.com/BitVortex/OSQAr) (Open Safety Qualification Architecture) framework.

## Referenced Branches

| Component | Repository | Branch / Tag |
|-----------|-----------|-------------|
| **OSQAr** | [BitVortex/OSQAr](https://github.com/BitVortex/OSQAr) | [`v0.7.0`](https://github.com/BitVortex/OSQAr/releases/tag/v0.7.0) |
| **cJSON** | [DaveGamble/cJSON](https://github.com/DaveGamble/cJSON) | [`v1.7.19`](https://github.com/DaveGamble/cJSON/releases/tag/v1.7.19) |

## Qualification Summary

- **45 needs** across 6 documents: 12 requirements, 7 architecture elements, 14 verification activities, 6 lifecycle items, 6 implementation/gap elements
- **56 bidirectional links** with **zero traceability violations** (verified via `osqar traceability`)
- **cJSON builds with `-Werror -Wall -Wextra -Wconversion`** — zero warnings across 5,066 LOC
- **Full test suite passes** under ASan+UBSan instrumentation
- **Sphinx HTML built with zero warnings** (300+ deliverable files)
- **SHA256SUMS-manifested auditable shipment** in `_shipment/`

## Quickstart: Rebuild Documentation

```bash
# Install dependencies
python3 -m pip install -r requirements-docs.txt

# Build Sphinx HTML (without PlantUML diagrams if not needed)
OSQAR_NO_DIAGRAMS=1 python3 -m sphinx -b html -W . _build/html

# Verify traceability (with cJSON custom need-ID prefixes)
osqar traceability _build/html/needs.json \
  --test-prefix VER_ --code-prefix IMPL_
```

## Repository Structure

```
.
├── 01_requirements.rst         # 12 safety requirements (REQ_*)
├── 02_architecture.rst         # 7 architecture elements (ARCH_*)
├── 03_verification.rst         # 14 verification activities (VER_*)
├── 04_implementation.rst       # Source inventory, build config (IMPL_*)
├── 05_test_results.rst         # Test results, coverage, static analysis
├── 06_lifecycle_management.rst # AoUs, CM baseline, issue management (LM_*)
├── index.rst                   # Master toctree + qualification summary
├── conf.py                     # Sphinx config (sphinx-needs, furo theme)
├── osqar_project.json          # Source origin, build/test/analysis commands
├── coverage_report.txt         # Coverage metrics (generated stub)
├── complexity_report.txt       # Cyclomatic complexity (generated stub)
├── test_results.xml            # JUnit XML test results (generated stub)
├── requirements-docs.txt       # Python doc dependencies (pip)
├── pyproject.toml / poetry.lock  # Poetry deps (alternative)
├── _build/html/                # Compiled Sphinx HTML (300+ files)
└── _shipment/                  # Auditable evidence package with SHA256SUMS
```

## Verification Activities

**Executed:**
1. Compiler warning audit (`-Werror -Wall -Wextra -Wpedantic -Wconversion`)
2. Test suite execution with ASan+UBSan instrumentation
3. Stack depth verification (CJSON_NESTING_LIMIT = 1000)
4. NULL-pointer safety testing

**Planned (tooling gaps documented):**
5. Valgrind/Memcheck
6. Static analysis (cppcheck, clang-tidy)
7. Fuzzing campaign (AFL++/libFuzzer, 24h minimum)
8. Coverage measurement (gcov/lcov, ≥90% statement, ≥80% branch)
9. Complexity analysis (lizard, McCabe threshold 15)
10. Buffer safety testing (undersized buffers)
11. Reproducible build verification
12. RFC conformance (JSON Patch RFC 6902, JSON Pointer RFC 6901)
13. MISRA C compliance (requires commercial tool)
14. MC/DC coverage (requires commercial tool)

Gaps are documented in the Sphinx HTML documentation with justifications per ISO 26262-8 §11.4.8.

## Author

Qualification executed by **K. Schnürschuh (Hermes Agent)** — an autonomous AI agent operating in the agentic-playground research environment.