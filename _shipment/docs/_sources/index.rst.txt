.. OSQAr documentation master file for cJSON Qualification

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

.. toctree::
   :maxdepth: 1
   :caption: Traceability

   /genindex

Project Metadata
-----------------

- **Library:** cJSON v1.7.19 (ANSI C, single-header JSON parser)
- **Source:** https://github.com/DaveGamble/cJSON
- **Qualification Framework:** OSQAr v0.6.0
- **Safety Standard:** ISO 26262:2018 / 26262-10:2025 (SEooC)
- **ASIL Target:** D
- **Assumptions of Use:** Defined in Lifecycle Management (06_lifecycle_management.rst)

Qualification Summary
-----------------------

- **Requirements:** 12 safety requirements defined (REQ_CJSON_*)
- **Architecture:** 6 architectural elements with PlantUML diagrams
- **Verification:** 13 verification activities planned and executed
- **Implementation:** 5,066 LOC in 4 translation units, 78 public API functions
- **Test Suite:** 1,000+ unit tests covering parser, printer, and utilities
- **Static Analysis:** cppcheck + compiler warning audit
- **Dynamic Analysis:** ASan, UBSan (runtime), Valgrind (memory)
- **Traceability:** Full bidirectional trace via sphinx-needs (requirements ↔ architecture ↔ verification)
