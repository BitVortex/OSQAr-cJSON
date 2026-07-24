# Qualification gate disposition record

**Candidate component:** cJSON v1.7.19, git object `c859b25da02955fef659d658b8f324b5cde87be3`

**Policy configuration:** qualification runner schema 1; line coverage >= 90%, branch coverage >= 80%, cyclomatic complexity <= 15, function length <= 100 lines, zero compiler warnings, and zero Cppcheck error/warning findings.

**Candidate integration decision:** MERGE WITH DOCUMENTED DEVIATIONS

**Qualification and publication decision:** BLOCK

This record inventories the findings produced by the fail-closed native evidence runner. QF-01 and QF-02 are accepted only as deviations from the research candidate's stated goals so that the blocked candidate can be merged for continued work. They are not accepted as evidence of qualification and do not establish qualification, compliance, certification, or release readiness. The machine-readable decision and exact expected failure inventory are in `assurance/candidate-integration-policy.json`.

## Passing mechanical gates

The current candidate run passed the following mechanical gates:

- 162/162 upstream Unity cases across 21 executables, with zero failures or ignored cases;
- 30 supplemental qualification scenarios, including deterministic allocation-failure injection, with zero failures;
- ASan and UBSan execution of both component objects, all Unity harnesses, and the supplemental scenarios;
- line coverage 90.44% and branch coverage 80.26% over `cJSON.c` and `cJSON_Utils.c`;
- strong C99 compiler warning audit with `-Werror`;
- two clean deterministic builds with exact SHA-256 agreement for `cJSON.o`, `cJSON_Utils.o`, and `libcjson.a`.

The generated evidence and adjacent provenance sidecars are under `_build/evidence/` and are intentionally not committed. A pinned 229-file component-source manifest binds archive/export executions to the declared cJSON git object even when Git metadata is absent; the runner regression suite includes 14 tests, including altered-export rejection and controlled fault seeds.

The 90.44% line and 80.26% branch measurements satisfy only the repository's mechanical minimums. Modified condition/decision coverage (MC/DC) was not measured, uncovered code and requirements-linked completeness have not been independently dispositioned, and the measurements do not demonstrate adequacy for an ASIL D software-component qualification argument. Coverage is therefore explicitly below the evidential standard needed to argue qualification, notwithstanding the mechanical activity result.

## Blocking finding QF-01: complexity thresholds

Lizard measured 154 functions. Fifteen functions exceed cyclomatic complexity 15, function length 100 lines, or both:

- `cJSON.c`: `parse_number`, `utf16_literal_to_utf8`, `parse_string`, `print_string_ptr`, `parse_value`, `print_value`, `parse_object`, `print_object`, `cJSON_Duplicate_rec`, and `cJSON_Compare`;
- `cJSON_Utils.c`: `compare_pointers`, `sort_list`, `compare_json`, `apply_patch`, and `create_patches`.

The largest observations are CCN 37 and 230 lines for `apply_patch`. The complete values are in `_build/evidence/complexity/metrics.json`. The runner correctly returns nonzero; no threshold was relaxed.

**Candidate disposition:** QF-01 is accepted only for merging this blocked research candidate. Qualification acceptance still requires refactoring and rerunning the evidence, or an independently reviewed intended-use argument with explicit, finding-specific risk controls.

## Blocking finding QF-02: Cppcheck findings

Cppcheck 2.17.1 produced 17 error/warning findings:

- 14 `nullPointerRedundantCheck` warnings in parser paths;
- one `ctunullpointer` warning at `cJSON.c:821`;
- one `invalidFunctionArg` error associated with the platform-dependent fallback definition of `NAN`;
- one `uselessAssignmentPtrArg` warning for `object = NULL` after deallocation in `cJSON_free`.

The complete path information and the 88 nonblocking style/information findings are inventoried in `_build/evidence/static-analysis/findings.json`. Compiler and sanitizer success do not by themselves close these static-analysis findings. The runner correctly returns nonzero; no warning was suppressed.

**Candidate disposition:** QF-02 is accepted only for merging this blocked research candidate. Qualification acceptance still requires eliminating the findings in the controlled component baseline, or independently establishing and approving exact finding-specific deviations. A blanket tool suppression is not acceptable.

## Release consequence

`./build-and-test.sh all` returns 1 because QF-01 and QF-02 remain open. CI may pass only when that blocked outcome, the exact known failure inventory, and the non-qualification policy all match; such a green run means **candidate integration accepted**, not **qualification passed**. OSQAr qualification-profile acceptance, shipment preparation, release-manifest generation, tagging, and publication remain blocked.

Unapproved evidence and ISO 26262-8:2018, 12.4.3 independent verification of the qualification result are tracked in [GitHub issue #21](https://github.com/BitVortex/OSQAr-cJSON/issues/21). This candidate may be merged with that reference, but the issue must not be closed by the merge itself.
