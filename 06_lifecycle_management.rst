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
   :tags: lifecycle;aou

.. need:: **AoU-2 (Input Constraints):** JSON inputs processed through cJSON shall not exceed CJSON_NESTING_LIMIT (1000) depth. Maximum single string length is bounded by available memory. Inputs originate from a trusted or integrity-checked source (validated at system level before reaching cJSON).
   :id: LM_AOU_INPUTS
   :status: active
   :tags: lifecycle;aou

.. need:: **AoU-3 (Threading Model):** cJSON is not thread-safe and shall be used from a single thread of control or externally synchronized by the integrator.
   :id: LM_AOU_THREADING
   :status: active
   :tags: lifecycle;aou

.. need:: **AoU-4 (Error Handling):** The integrator shall check all cJSON return values for error indicators (NULL from parse/create functions, cJSON_False from boolean returns). Unchecked error paths are the integrator's responsibility.
   :id: LM_AOU_ERROR
   :status: active
   :tags: lifecycle;aou

.. need:: **AoU-5 (Toolchain):** The integrator shall reproduce the qualification build with the audited toolchain version and compiler flags. Binary equivalence or semantic equivalence shall be demonstrated.
   :id: LM_AOU_TOOLCHAIN
   :status: active
   :tags: lifecycle;aou

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
