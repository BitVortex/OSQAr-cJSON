Goal Structuring Notation — cJSON Safety Case
================================================

.. _gsn_overview:

.. plantuml:: _static/gsn_safety_case.puml
   :caption: GSN Safety Case — cJSON v1.7.19 SEooC (ISO 26262-10:2025)
   :align: center

The following safety case is structured using the Goal Structuring Notation (GSN)
and targets ISO 26262-10:2025 SEooC qualification of cJSON v1.7.19 for ASIL D
integration. Goals are linked to their supporting strategies, sub-goals, and
solutions (evidence). Context elements capture the Assumptions of Use from
`Lifecycle Management <06_lifecycle_management>`_.

Top-Level Goal
--------------

.. sc:: cJSON v1.7.19 is sufficiently safe to be integrated as a Safety Element out of Context (SEooC) into an ASIL D automotive system, subject to the Assumptions of Use defined in LM_AOU_CONTEXT through LM_AOU_TOOLCHAIN.
   :id: SC_CJSON_SAFE
   :status: active
   :tags: safety-case;top-level
   :links: LM_AOU_CONTEXT;LM_AOU_INPUTS;LM_AOU_THREADING;LM_AOU_ERROR;LM_AOU_TOOLCHAIN

Parsing Safety
--------------

.. sc:: cJSON correctly parses all valid JSON (RFC 8259) and deterministically rejects all malformed inputs.
   :id: SC_PARSE_SAFETY
   :status: active
   :tags: safety-case;parsing
   :links: REQ_CJSON_PARSE_VALID;VER_CJSON_TEST_SUITE;VER_CJSON_FUZZING;SC_CJSON_SAFE

.. sc:: **Solution:** 162 Unity tests covering parsing edge cases, including malformed JSON, deep nesting, and boundary conditions. The test suite passes under standard and ASan+UBSan instrumented builds. Evidence: :need:`VER_CJSON_TEST_SUITE`. Fuzzing campaign planned: :need:`VER_CJSON_FUZZING`.
   :id: SC_PARSE_EVIDENCE
   :status: active
   :tags: safety-case;evidence;parsing
   :links: SC_PARSE_SAFETY

Memory Safety
-------------

.. sc:: cJSON is free from memory errors (heap corruption, use-after-free, double-free, buffer overrun, uninitialized reads).
   :id: SC_MEMORY_SAFETY
   :status: active
   :tags: safety-case;memory
   :links: REQ_CJSON_MEMORY_SAFE;VER_CJSON_SANITIZERS;VER_CJSON_VALGRIND;SC_CJSON_SAFE

.. sc:: **Solution:** ASan+UBSan instrumentation on full test suite returns CLEAN — no heap out-of-bounds, use-after-free, or stack buffer overflow. ASan's LeakSanitizer detects memory leaks. A Valgrind/Memcheck gap is documented with ASan mitigation (see `Gap Documentation <_static/gaps>`_). Evidence: :need:`VER_CJSON_SANITIZERS`, :need:`VER_CJSON_VALGRIND`.
   :id: SC_MEMORY_EVIDENCE
   :status: active
   :tags: safety-case;evidence;memory
   :links: SC_MEMORY_SAFETY

Undefined Behavior Freedom
--------------------------

.. sc:: cJSON does not invoke undefined behavior for any input, including integer overflow, NULL dereference, and malformed data.
   :id: SC_NO_UB
   :status: active
   :tags: safety-case;ub
   :links: REQ_CJSON_NO_UB;VER_CJSON_SANITIZERS;VER_CJSON_ARITH;VER_CJSON_API;SC_CJSON_SAFE

.. sc:: **Solution:** UBSan integer+pointer checks return CLEAN on full test suite. Arithmetic audit (VER_CJSON_ARITH) confirms no signed overflow in parse_number/print_number. NULL-pointer safety verified by dedicated test cases (VER_CJSON_API). Compiler warning audit with -Werror -Wconversion — zero warnings. Evidence: :need:`VER_CJSON_SANITIZERS`, :need:`VER_CJSON_ARITH`, :need:`VER_CJSON_API`, :need:`IMPL_BUILD`.
   :id: SC_UB_EVIDENCE
   :status: active
   :tags: safety-case;evidence;ub
   :links: SC_NO_UB

Verification Completeness
-------------------------

.. sc:: All safety requirements are verified with adequate coverage and documented evidence suitable for ISO 26262-8 audit.
   :id: SC_VERIFICATION_COMPLETE
   :status: active
   :tags: safety-case;verification
   :links: REQ_CJSON_TRACEABILITY;VER_CJSON_COVERAGE;VER_CJSON_COMPLEXITY;SC_CJSON_SAFE

.. sc:: **Solution:** Statement coverage 88.1% (1,788/2,029 lines), function coverage 98.7% (149/151). All uncovered branches are in error-recovery paths (malloc failure, depth limit) justified via :need:`VER_CJSON_COVERAGE`. Static analysis (cppcheck —all —inconclusive) produces reviewed report. Complexity analysis: one function (parse_string, CC=18) exceeds McCabe 15 with documented justification. Evidence: :need:`VER_CJSON_COVERAGE`, :need:`VER_CJSON_COMPLEXITY`, :need:`VER_CJSON_STATIC`.
   :id: SC_VERIFICATION_EVIDENCE
   :status: active
   :tags: safety-case;evidence;coverage
   :links: SC_VERIFICATION_COMPLETE

Context
-------

.. sc:: **SEooC Assumptions of Use (ISO 26262-10:2025 §6.4.3):** (1) cJSON is integrated as a stateless library with caller-owned state and a qualified memory allocator provided by the integrator via cJSON_InitHooks. (2) JSON inputs do not exceed CJSON_NESTING_LIMIT (1000) depth; max string length is bounded by available memory; inputs originate from a trusted or integrity-checked source. (3) Single-threaded use or external synchronization by integrator. (4) All cJSON return values are checked by integrator; NULL/cJSON_False indicate errors. (5) Qualification build is reproduced with audited toolchain and compiler flags. See :need:`LM_AOU_CONTEXT`, :need:`LM_AOU_INPUTS`, :need:`LM_AOU_THREADING`, :need:`LM_AOU_ERROR`, :need:`LM_AOU_TOOLCHAIN`.
   :id: SC_AOU_CONTEXT
   :status: active
   :tags: safety-case;context;aou
   :links: SC_CJSON_SAFE
