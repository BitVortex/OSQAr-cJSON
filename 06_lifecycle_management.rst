Lifecycle Management — cJSON Qualification
===========================================

.. need:: The cJSON SEooC qualification lifecycle follows ISO 26262-10 Clause 6 (SEooC development). The lifecycle encompasses four phases: (1) Assumption of Use definition, (2) Safety Requirements derivation from assumptions, (3) Verification and Validation against requirements, (4) Integration validation in target context.
   :id: LM_LIFECYCLE
   :status: active
   :tags: lifecycle

Assumptions of Use (AoU)
-------------------------

.. need:: **AoU-1 (Integration Context):** cJSON is integrated as a stateless library in an ASIL D ECU context. All state is caller-owned (cJSON* pointers). The integrator provides a qualified memory allocator via cJSON_InitHooks.
   :id: LM_AOU_CONTEXT
   :status: active
   :tags: lifecycle;aou;ASIL_D
   :links: SC_CJSON_SAFE

.. need:: **AoU-2 (Input Constraints):** JSON inputs processed through cJSON shall not exceed CJSON_NESTING_LIMIT (1000) depth. Maximum single string length is bounded by available memory. Inputs originate from a trusted or integrity-checked source (validated at system level before reaching cJSON).
   :id: LM_AOU_INPUTS
   :status: active
   :tags: lifecycle;aou;ASIL_D
   :links: SC_CJSON_SAFE

.. need:: **AoU-3 (Threading Model):** cJSON is not thread-safe and shall be used from a single thread of control or externally synchronized by the integrator.
   :id: LM_AOU_THREADING
   :status: active
   :tags: lifecycle;aou;ASIL_D
   :links: SC_CJSON_SAFE

.. need:: **AoU-4 (Error Handling):** The integrator shall check all cJSON return values for error indicators (NULL from parse/create functions, cJSON_False from boolean returns). Unchecked error paths are the integrator's responsibility.
   :id: LM_AOU_ERROR
   :status: active
   :tags: lifecycle;aou;ASIL_D
   :links: SC_CJSON_SAFE

.. need:: **AoU-5 (Toolchain):** The integrator shall reproduce the qualification build with the audited toolchain version and compiler flags. Binary equivalence or semantic equivalence shall be demonstrated.
   :id: LM_AOU_TOOLCHAIN
   :status: active
   :tags: lifecycle;aou;ASIL_D
   :links: SC_CJSON_SAFE

Configuration Management
-------------------------

.. need:: The cJSON SEooC qualification baseline is v1.7.19 (identified by git tag and SHA256 of the source archive). All artifacts (requirements, architecture, verification reports, builds) are version-controlled under the OSQAr project.
   :id: LM_CM_BASELINE
   :status: active
   :tags: lifecycle;cm

Issue Management
-----------------

.. need:: All deviations from requirements, static analysis false positives, and coverage gaps shall be documented as issue records with safety justifications, reviewer sign-off, and traceability to affected requirements.
   :id: LM_ISSUES
   :status: active
   :tags: lifecycle;issues

Shipment Content
-----------------

The qualification shipment contains:
1. Requirements document (this project)
2. Architecture document with PlantUML diagrams
3. Verification plan and results
4. Implementation description and source inventory
5. Test suite and execution report (JUnit XML)
6. Static analysis report
7. Code coverage report
8. Complexity analysis report
9. Sanitizer / Valgrind execution logs
10. Fuzzing campaign summary (if executed)
11. Compiler warning audit
12. SHA256SUMS manifest for integrity verification

Tool Confidence Level (TCL) Assessment
--------------------------------------

Per ISO 26262-8:2018 §11.4 (Software tool qualification), each tool used
in the qualification process is classified by Tool Impact (TI) and Tool
Error Detection (TD) to determine the required Tool Confidence Level (TCL).

.. list-table:: Tool Qualification Assessment
   :header-rows: 1

   * - Tool
     - Version
     - Purpose
     - TI
     - TD
     - TCL
     - Qualification Method
   * - gcc
     - 11.4.0 (Ubuntu 22.04)
     - Compiler, linker
     - TI2
     - TD3
     - TCL3
     - Increased confidence from use (10⁹+ field hours)
   * - gcov / lcov
     - 1.16
     - Code coverage measurement
     - TI1
     - TD1
     - TCL1
     - No qualification required
   * - cppcheck
     - 2.14.0
     - Static analysis
     - TI1
     - TD2
     - TCL2
     - Tool validation against known defect corpus
   * - lizard
     - 1.17.10
     - Cyclomatic complexity
     - TI1
     - TD1
     - TCL1
     - No qualification required
   * - Valgrind/Memcheck
     - 3.22.0
     - Dynamic memory analysis
     - TI1
     - TD1
     - TCL1
     - No qualification required
   * - ASan / UBSan
     - (compiler-builtin)
     - Runtime sanitizers
     - TI1
     - TD1
     - TCL1
     - No qualification required
   * - plantuml
     - 1.2024.6
     - Diagram generation
     - TI1
     - TD1
     - TCL1
     - No qualification required
   * - gsn2x
     - 4.3.1
     - GSN diagram rendering
     - TI1
     - TD1
     - TCL1
     - No qualification required
   * - Sphinx
     - ≥7.4
     - Documentation generation
     - TI1
     - TD2
     - TCL2
     - Tool validation (CI regression suite)
   * - Unity (test framework)
     - (bundled v2.5.2)
     - Unit test harness
     - TI1
     - TD1
     - TCL1
     - No qualification required

.. need:: Tool confidence levels are assessed per ISO 26262-8:2018 §11.4.
   The compiler (gcc) is classified TCL3 (TI2 + TD3) due to its potential
   to introduce errors into the safety-related software. The qualification
   argument relies on increased confidence from use across 10⁹+ field
   hours in automotive and safety-critical contexts. All verification
   tools are TCL1 or TCL2, requiring no formal qualification beyond
   documented validation. A TCL3 qualification report for the compiler
   is deferred to a future qualification cycle.
   :id: LM_TOOL_TCL
   :status: active
   :tags: lifecycle;tool-qualification;ASIL_D
   :links: REQ_CJSON_TRACEABILITY
