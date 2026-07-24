# Pre-revision baseline review for OSQAr v0.10.2

**Review subject:** `OSQAr-cJSON` commit `d73c092f5f8feb60e29a54f5d46ccb8b09127a58`  
**Component baseline:** `cjson-source` gitlink `c859b25d3b25fe44d3c99dc56dce35bdd55a8a8f` (upstream tag `v1.7.19`)  
**OSQAr target:** version `0.10.2`, source commit `4003c4046b13610328d268f7c07de3140d97bf4a`  
**Review date:** 2026-07-24  
**Review type:** full pre-revision repository and shipped-artifact review

## Review boundary

The review covered every tracked file in the baseline tree, the complete ZIP shipment inventory, the cJSON and Unity gitlinks, the documentation/needs model, the native evidence-generation pipeline, CI definitions, generated evidence, and the OSQAr v0.10.2 qualification-profile interfaces. The source component was not modified during this review.

This is a researched technical review, not an independent functional-safety assessment and not a statement that cJSON is qualified for any automotive item.

## Reproducible baseline observations

- The baseline tree contains 46 tracked entries and two submodule gitlinks.
- The tracked ZIP contains 31 regular files. It omits `cjson-source/tests/inputs/test11`, although `parse_examples` reads that path, and it contains no `OSQAR-RELEASE-MANIFEST.json`.
- The packaged `test_results.xml` declares 162 tests but contains only 21 `testcase` elements. The packaged `cppcheck_report.xml` is empty (`0` findings); it does not reconcile with the documented 91-finding static-analysis baseline.
- Executing `./build-and-test.sh all` against the frozen baseline returned exit code 0 even though cppcheck reported a broken configuration and no valid analysis. The script redirects tool failures and conditionally ignores missing/non-zero test runs.
- The baseline native run reported 162 Unity tests and 32.5% statement coverage. The ASan/UBSan path rebuilt the library without sanitizer flags and added sanitizer flags only when linking the test executables.
- A Sphinx build with OSQAr v0.10.2 exported `needs.json` but failed under `-W` because the `plantuml` directive was not registered when diagrams were disabled.
- Legacy untyped traceability passed. OSQAr v0.10.2 qualification-profile typed traceability failed with 103 violations because all directives exported as generic `need` records, typed relations were absent, safety-case kinds were absent, and authoritative OSQAr acceptance evidence was absent.
- The workflows install floating OSQAr sources or `osqar==0.9.0`; they do not pin OSQAr v0.10.2 by package hash and do not execute the qualification profile.

Raw review logs were generated from the frozen exported tree under `/tmp/osqar-cjson-baseline-review`; the repository retains this concise finding record rather than transient build output.

## Standards framing

ISO 26262-8:2018, Clause 12 is the applicable primary process framing for reuse qualification of a third-party software library:

- 12.1 defines the objective as evidence of suitability for reuse in items developed using ISO 26262 processes.
- 12.4.1 requires a component specification, compliance evidence, intended-use suitability evidence, evidence about the component development process, and a qualification plan.
- 12.4.2.1 requires unique identification, maximum target ASIL, planned activities, component/intended-use requirements, configuration, interfaces/resources, integration information, anomalous-condition reactions, and known anomalies/workarounds.
- 12.4.2.2 requires requirements coverage, normal and failure-condition coverage, and no known errors that could violate allocated safety requirements.
- 12.4.2.3 requires structural coverage measurement for an ASIL D target.
- 12.4.2.4 limits verification validity to an unchanged implementation.
- 12.4.2.5 requires qualification identity/configuration, performer, environment, verification results, and maximum ASIL.
- 12.4.3 requires independent verification of qualification results and their validity for intended use under the Part 8 Clause 9 verification process.

The baseline is principally structured as ISO 26262-6 unit verification and does not yet provide all Clause 12 work products. The revision must therefore state a bounded qualification target and preserve unresolved process/independence gaps rather than infer qualification from test execution.

## Findings and required dispositions

### BR-01 — P0 — Native pipeline is fail-open

**Evidence:** test execution uses conditional/ignored failure paths; aggregate counts are trusted; missing executables do not necessarily fail; cppcheck failure produced overall success.  
**Required correction:** fail on command exit/signal, missing or extra test executables, malformed Unity output, unexpected per-executable inventory, report inconsistency, or absent evidence. Add executable fault-seed regressions.

### BR-02 — P0 — Sanitizer evidence does not instrument the component

**Evidence:** `build_library` compiles `cJSON.c` and `cJSON_Utils.c` with release flags before sanitized tests are linked.  
**Required correction:** compile both component objects and harnesses with ASan/UBSan flags; record configuration and prove instrumentation through a deterministic sanitizer fault seed.

### BR-03 — P0 — Shipped evidence is inconsistent or missing

**Evidence:** JUnit counters do not match cases; static-analysis XML is empty despite a documented baseline; `test11` is absent from the archive; no OSQAr release manifest exists.  
**Required correction:** regenerate evidence from one immutable source revision, validate each evidence format/content threshold, verify test-input inventory, and create/verify an OSQAr v0.10.2 release manifest against the exact shipment inventory.

### BR-04 — P0 — Qualification-profile traceability is absent

**Evidence:** all needs export as `type=need`; only generic `links` exist; qualification traceability reports 103 violations.  
**Required correction:** use typed need directives and directed relations (`allocated_to`, `realized_by`, `verified_by`, `produces`, `evidenced_by`, `supported_by`) matching the v0.10.2 catalog; validate with `osqar traceability --profile qualification`.

### BR-05 — P0 — Evidence provenance and acceptance are fail-open

**Evidence:** records use prose/legacy status values; they lack complete `activity_history`, `source_revision`, and `configuration_sha256`; no authoritative `tools.osqar_evidence` acceptance block exists.  
**Required correction:** generate schema-valid evidence records, perform framework validation with the exact source revision, then update configuration provenance and record only tool-produced acceptance. Do not mark evidence approved without the required reviewer authority.

### BR-06 — P0 — Qualification claim is overbroad relative to ISO 26262-8:2018 Clause 12

**Evidence:** current prose can be read as an ASIL D qualification package, while development-process evidence, intended-use verification, known-anomaly disposition, qualification verification independence, and item/integration context are incomplete.  
**Required correction:** reframe the package as a bounded qualification attempt targeting ASIL D verification rigor. Define the API/configuration/AoU boundary and an explicit gap register. Prohibit certification/compliance/qualification claims until all Clause 12 and governance conditions are independently accepted.

### BR-07 — P1 — Assumptions of use are not operational

**Evidence:** AoU prose is not a controlled accept/verify/reject protocol and does not map integrator obligations to evidence or release identity.  
**Required correction:** provide an AoU checklist with applicability, integrator evidence, acceptance decision, and release/source/configuration binding.

### BR-08 — P1 — Source scope is internally inconsistent

**Evidence:** architecture and tests include cJSON Utils, while statements elsewhere emphasize core cJSON; the shipment does not clearly state whether the utilities API is qualified or excluded.  
**Required correction:** identify the exact source files and public API boundary. Treat excluded utilities as outside the qualification claim even when built for regression analysis.

### BR-09 — P1 — Tool-confidence treatment is incomplete

**Evidence:** the lifecycle document assigns TCL values without a reproducible determination and without separating confidence in OSQAr evidence processing from confidence in compilers, analyzers, and test tools.  
**Required correction:** replace unsupported TCL conclusions with a tool-use inventory, potential-error/detection rationale, compensating checks, version identity, and an explicit open gap where ISO 26262-8:2018 Clause 11 evidence is unavailable.

### BR-10 — P1 — CI does not enforce one immutable qualification configuration

**Evidence:** workflows use inconsistent Python versions, floating dependencies, outdated OSQAr installation, and basic traceability.  
**Required correction:** define one pinned qualification environment, run native fault-seed and evidence validators, use OSQAr v0.10.2 qualification profile, build docs, create the shipment, verify its manifest, and upload the exact checked artifact.

### BR-11 — P1 — Documentation build configuration is not fail-closed

**Evidence:** `OSQAR_NO_DIAGRAMS=1` excludes the extension but documents still contain `plantuml` directives; CI does not consistently treat warnings as errors.  
**Required correction:** make no-diagram builds parse deterministically or install/execute the rendering prerequisites; use `sphinx-build -W --keep-going`.

### BR-12 — P1 — Existing open findings are not dispositioned as controlled qualification gaps

**Evidence:** upstream anomalies, fuzzing/Valgrind/stack-analysis limitations, coverage shortfalls, and governance review dependencies exist in issues/prose but are not bound into an authoritative release decision.  
**Required correction:** maintain a release gap register with owner, evidence, disposition, and gate effect. Open safety-impacting or qualification-validity gaps must force a BLOCK outcome.

## Revision acceptance criteria

1. All BR-01 through BR-05 corrections are executable and fail-closed.
2. Documentation states the bounded intended-use/API/configuration target and carries BR-06 through BR-12 as controlled gaps where evidence remains unavailable.
3. Every generated artifact reconciles with the exact source revision and configuration hash.
4. OSQAr v0.10.2 qualification-profile validation and typed traceability are executed; any failure is preserved as a release blocker, not suppressed.
5. The shipment manifest verifies after clean extraction and rejects mutation, deletion, addition, and path-policy violations.
6. An independent exact-tree review produces APPROVE or BLOCK. BLOCK prevents publication as a qualified component package.

## Review conclusion

**BLOCK baseline shipment and any qualification claim.** The baseline can serve as source material for a revised qualification attempt, but its native pipeline, evidence provenance, typed traceability, release integrity, and Clause 12 framing are insufficient. Revision may proceed only with the above findings retained as acceptance criteria.
