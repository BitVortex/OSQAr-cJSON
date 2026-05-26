Verification — cJSON Qualification
====================================

.. need:: Execute the full cJSON test suite (unit tests for parser, printer, utilities, RFC conformance) and confirm all tests pass with zero failures.
   :id: VER_CJSON_TEST_SUITE
   :status: active
   :tags: verification;test;ASIL_D
   :links: REQ_CJSON_PARSE_VALID;REQ_CJSON_PRINT_VALID;REQ_CJSON_UTILS_RFC

.. need:: Run Valgrind/Memcheck on the test suite to verify absence of memory leaks, use-after-free, uninitialized reads, and invalid memory accesses.
   :id: VER_CJSON_VALGRIND
   :status: active
   :tags: verification;memory;valgrind;ASIL_D
   :links: REQ_CJSON_MEMORY_SAFE;REQ_CJSON_NO_UB;REQ_CJSON_STRING_SAFE

.. need:: Run AddressSanitizer (ASan) and UndefinedBehaviorSanitizer (UBSan) instrumented test builds to detect runtime memory errors and undefined behavior.
   :id: VER_CJSON_SANITIZERS
   :status: active
   :tags: verification;safety;sanitizers;ASIL_D
   :links: REQ_CJSON_NO_UB;REQ_CJSON_MEMORY_SAFE

.. need:: Verify bounded stack usage. Confirm that CJSON_NESTING_LIMIT (default 1000) prevents unbounded recursion and that the parser returns an error for inputs exceeding the nesting limit.
   :id: VER_CJSON_STACK
   :status: active
   :tags: verification;stack;ASIL_D
   :links: REQ_CJSON_STACK_BOUNDED

.. need:: Audit integer operations in parse_number, print_number, and buffer-size computation for signed overflow and wraparound vulnerabilities. Verify with UBSan integer checks.
   :id: VER_CJSON_ARITH
   :status: active
   :tags: verification;integer;ASIL_D
   :links: REQ_CJSON_ARITH_SAFE

.. need:: Fuzz-test the cJSON parser with AFL++ or libFuzzer for a minimum of 24 CPU-hours. All crashes, hangs, and assertion failures shall be triaged and resolved.
   :id: VER_CJSON_FUZZING
   :status: active
   :tags: verification;fuzzing;ASIL_D
   :links: REQ_CJSON_PARSE_VALID;REQ_CJSON_NO_UB

.. need:: Run static analysis (cppcheck, clang-tidy) on cJSON source with MISRA-inspired checks. All warnings shall be reviewed and either resolved or justified with a deviation record.
   :id: VER_CJSON_STATIC
   :status: active
   :tags: verification;static-analysis;ASIL_D
   :links: REQ_CJSON_CODE_QUALITY;REQ_CJSON_ARITH_SAFE;REQ_CJSON_STRING_SAFE

.. need:: Verify NULL-pointer safety by constructing test cases that pass NULL to every public API function and confirming deterministic error returns.
   :id: VER_CJSON_API
   :status: active
   :tags: verification;api;ASIL_D
   :links: REQ_CJSON_NULL_PTR_SAFE

.. need:: Measure statement and branch coverage of the test suite on the cJSON source. Target: ≥ 90% statement coverage, ≥ 80% branch coverage. Document uncovered branches with safety justifications.
   :id: VER_CJSON_COVERAGE
   :status: active
   :tags: verification;coverage;ASIL_D
   :links: REQ_CJSON_CODE_QUALITY

.. need:: Verify JSON Patch and JSON Pointer conformance against RFC 6902 and RFC 6901 test vectors, including edge cases and error paths.
   :id: VER_CJSON_UTILS
   :status: active
   :tags: verification;rfc;utils;ASIL_D
   :links: REQ_CJSON_UTILS_RFC

.. need:: Measure cyclomatic complexity of all cJSON functions. Functions exceeding McCabe 15 shall be reviewed and justifications documented.
   :id: VER_CJSON_COMPLEXITY
   :status: active
   :tags: verification;complexity;ASIL_D
   :links: REQ_CJSON_CODE_QUALITY

.. need:: Verify cJSON_PrintBuffered and cJSON_PrintPreallocated do not write beyond buffer boundaries by providing undersized buffers and confirming error returns.
   :id: VER_CJSON_STRING
   :status: active
   :tags: verification;string;buffer;ASIL_D
   :links: REQ_CJSON_STRING_SAFE

.. need:: Compile cJSON with the qualified toolchain and confirm reproducible build output (identical binary across rebuilds).
   :id: VER_CJSON_REPRODUCIBLE
   :status: active
   :tags: verification;build;ASIL_D
   :links: REQ_CJSON_REPRODUCIBLE

Standards Traceability (ISO 26262-6:2018)
-----------------------------------------

Each verification activity targets specific ISO 26262-6:2018 requirements
for ASIL D software development:

.. list-table::
   :header-rows: 1

   * - Verification Activity
     - ISO 26262-6:2018 Reference
     - ASIL D Requirement
   * - VER_CJSON_TEST_SUITE
     - §9.4.4 (Test case derivation)
     - Requirements-based tests derived from software safety requirements
   * - VER_CJSON_SANITIZERS
     - §9.4.5 (Dynamic analysis)
     - Memory and undefined behavior detection via runtime instrumentation
   * - VER_CJSON_STATIC
     - §9.4.5 (Static code analysis)
     - Automated static analysis of source code, MISRA checks
   * - VER_CJSON_COVERAGE
     - §9.4.7 Table 10 (Structural coverage at unit level)
     - Statement coverage, branch coverage; MC/DC deferred (documented gap)
   * - VER_CJSON_COMPLEXITY
     - §7.4.5 Table 3 (Software architectural design principles)
     - Restricted size and complexity of software components
   * - VER_CJSON_STACK
     - §8.4.5 Table 8 (Software unit design — no recursion)
     - Bounded recursion; depth limit enforced
   * - VER_CJSON_ARITH
     - §8.4.5 Table 8 (Defensive implementation)
     - Overflow protection in arithmetic operations
   * - VER_CJSON_STRING
     - §8.4.5 Table 8 (Defensive implementation)
     - Buffer boundary checks on all string operations
   * - VER_CJSON_API
     - §6.4.1 Table 1 (Safety requirements specification)
     - NULL-pointer safety; deterministic error returns
   * - VER_CJSON_VALGRIND
     - §9.4.5 (Dynamic analysis — supplementary)
     - Additional memory safety validation beyond ASan/UBSan
   * - VER_CJSON_FUZZING
     - §9.4.5 Table 9 (Methods for verification of software units)
     - Negative testing / fault injection via fuzzing
   * - VER_CJSON_REPRODUCIBLE
     - §11.4.8 (Configuration management — reproduction)
     - Build reproducibility verification per ISO 26262-8:2018 §11.4.8
   * - VER_CJSON_UTILS
     - §9.4.4 (Test case derivation)
     - RFC conformance testing for utility functions
