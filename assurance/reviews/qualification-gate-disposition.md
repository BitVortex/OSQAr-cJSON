# Qualification gate disposition record

**Candidate component:** cJSON v1.7.19, git object `c859b25da02955fef659d658b8f324b5cde87be3`

**Policy configuration:** qualification runner schema 1; line coverage >= 90%, branch coverage >= 80%, cyclomatic complexity <= 15, function length <= 100 lines, zero compiler warnings, and zero Cppcheck error/warning findings.

**Decision:** BLOCK

This record inventories the findings produced by the fail-closed native evidence runner. It does not approve a deviation and does not establish qualification, compliance, certification, or release readiness. Any proposed deviation requires an identified reviewer, a rationale tied to the intended use and assumptions of use, and independent review of the exact resulting tree.

## Passing mechanical gates

The current candidate run passed the following mechanical gates:

- 162/162 upstream Unity cases across 21 executables, with zero failures or ignored cases;
- 30 supplemental qualification scenarios, including deterministic allocation-failure injection, with zero failures;
- ASan and UBSan execution of both component objects, all Unity harnesses, and the supplemental scenarios;
- line coverage 90.44% and branch coverage 80.26% over `cJSON.c` and `cJSON_Utils.c`;
- strong C99 compiler warning audit with `-Werror`;
- two clean deterministic builds with exact SHA-256 agreement for `cJSON.o`, `cJSON_Utils.o`, and `libcjson.a`.

The generated evidence and adjacent provenance sidecars are under `_build/evidence/` and are intentionally not committed.

## Blocking finding QF-01: complexity thresholds

Lizard measured 154 functions. Fifteen functions exceed cyclomatic complexity 15, function length 100 lines, or both:

- `cJSON.c`: `parse_number`, `utf16_literal_to_utf8`, `parse_string`, `print_string_ptr`, `parse_value`, `print_value`, `parse_object`, `print_object`, `cJSON_Duplicate_rec`, and `cJSON_Compare`;
- `cJSON_Utils.c`: `compare_pointers`, `sort_list`, `compare_json`, `apply_patch`, and `create_patches`.

The largest observations are CCN 37 and 230 lines for `apply_patch`. The complete values are in `_build/evidence/complexity/metrics.json`. The runner correctly returns nonzero; no threshold was relaxed.

**Required disposition:** refactor and requalify the component, or obtain an independently reviewed `passed-with-deviation` disposition with an intended-use argument and explicit risk controls.

## Blocking finding QF-02: Cppcheck findings

Cppcheck 2.17.1 produced 17 error/warning findings:

- 14 `nullPointerRedundantCheck` warnings in parser paths;
- one `ctunullpointer` warning at `cJSON.c:821`;
- one `invalidFunctionArg` error associated with the platform-dependent fallback definition of `NAN`;
- one `uselessAssignmentPtrArg` warning for `object = NULL` after deallocation in `cJSON_free`.

The complete path information and the 88 nonblocking style/information findings are inventoried in `_build/evidence/static-analysis/findings.json`. Compiler and sanitizer success do not by themselves close these static-analysis findings. The runner correctly returns nonzero; no warning was suppressed.

**Required disposition:** eliminate the findings in the controlled component baseline, or independently establish and approve exact finding-specific deviations. A blanket tool suppression is not acceptable.

## Release consequence

`./build-and-test.sh all` returns 1 because QF-01 and QF-02 remain open. Therefore OSQAr qualification-profile acceptance, shipment preparation, release-manifest generation, tagging, and publication remain blocked.
