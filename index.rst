.. OSQAr documentation master file for cJSON Qualification

.. attention:: **RESEARCH ARTIFACT — NO WARRANTY**

   This is an **active research repository** for agentic qualification of
   open-source software for cyber-physical systems. All artifacts herein
   are produced by autonomous AI agents. **Information may be inconsistent,
   outdated, incomplete, or just plain wrong.** No warranty is provided and
   no liability is assumed. Do not use in production safety systems without
   independent expert review.

OSQAr Qualification — cJSON v1.7.19 SEooC (ISO 26262 ASIL D)
==============================================================

**Case Study:** Application of the OSQAr Qualification Architecture to cJSON as an ISO 26262 ASIL D Safety Element out of Context.

.. toctree::
   :maxdepth: 2
   :caption: Qualification Artifacts

   01_requirements
   02_architecture
   03_verification
   04_implementation
   05_test_results
   06_lifecycle_management
   07_safety_case

.. toctree::
   :maxdepth: 1
   :caption: Traceability

   /genindex

Project Metadata
-----------------

- **Library:** cJSON v1.7.19 (ANSI C, single-header JSON parser)
- **Source:** https://github.com/DaveGamble/cJSON
- **Qualification Framework:** OSQAr v0.8.0
- **Safety Standard:** ISO 26262:2018 / 26262-10:2025 (SEooC)
- **ASIL Target:** D
- **Assumptions of Use:** Defined in Lifecycle Management (06_lifecycle_management.rst)

Qualification Summary
-----------------------

- **Requirements:** 12 safety requirements defined (REQ_CJSON_*)
- **Architecture:** 7 architectural elements with PlantUML diagrams
- **Verification:** 14 verification activities planned and executed
- **Implementation:** 5,066 LOC in 4 translation units, 78 public API functions
- **Safety Case:** GSN argument with 4 safety goals and evidence links (see 07_safety_case)
- **Test Suite:** 1,000+ unit tests covering parser, printer, and utilities
- **Static Analysis:** cppcheck + compiler warning audit
- **Dynamic Analysis:** ASan, UBSan (runtime), Valgrind (planned)
- **Traceability:** Full bidirectional trace via sphinx-needs (requirements ↔ architecture ↔ verification)
- **Baseline:** v1.0 requirement baseline snapshot archived
- **Impact Analysis:** Transitive closure on traceability links for change management
