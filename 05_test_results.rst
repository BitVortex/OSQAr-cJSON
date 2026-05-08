Test Results — cJSON Qualification
====================================

.. note:: Test results are populated from the CI build pipeline. The table below reflects the most recent execution of the test suite with AddressSanitizer and UndefinedBehaviorSanitizer enabled.

.. need:: The cJSON test suite verifies parsing, printing, and utility functions. Results are captured in JUnit XML format.
   :id: TEST_REPORT_MAIN
   :status: active
   :tags: test-report
   :links: VER_CJSON_TEST_SUITE

Test execution summary:

.. list-table:: Test Suite Results
   :header-rows: 1

   * - Configuration
     - Tests
     - Passed
     - Failed
     - Sanitizers
   * - Release (c99, -O2)
     - {test_count}
     - {test_pass}
     - {test_fail}
     - —
   * - Debug + ASan/UBSan
     - {test_count}
     - {test_pass}
     - {test_fail}
     - ASan + UBSan
   * - Valgrind/Memcheck
     - {test_count}
     - {test_pass}
     - {test_fail}
     - Memcheck

.. note:: The cJSON test suite is based on the Unity test framework (bundled). Tests cover: parsing valid/invalid JSON, printing formatted/unformatted, object/array manipulation, JSON Patch/JSON Pointer operations, edge cases (deep nesting, large numbers, Unicode escapes, empty objects/arrays).

Coverage Summary
-----------------

.. include:: coverage_report.txt

Static Analysis Summary
-----------------------

.. include:: complexity_report.txt
