Qualification execution results
===============================

Results are generated, not authored
-----------------------------------

This source file intentionally contains no pre-approved test, analysis, or
qualification result. Run the controlled qualification frontend against the
exact revision. Generated artifacts are written under ``_build/evidence`` and
must be validated before use.

The source-controlled candidate nodes in :doc:`03_verification` remain blocked
until the release process imports fresh, accepted activity records and updates
them in a reviewable exact-tree change. This prevents a documentation rebuild
from presenting old evidence as current.

Required reconciliation
-----------------------

A candidate evidence set is complete only when all of the following hold:

- the release test run contains the exact executable and case inventory, and
  JUnit suite counters equal the number of concrete ``testcase`` elements;
- sanitizer evidence proves that component objects and harnesses carried the
  recorded ASan/UBSan instrumentation;
- gcovr JSON and text agree on the exact source scope and satisfy the configured
  line/branch policy;
- compiler warning, cppcheck, and lizard outputs are non-empty, parseable, and
  reconciled with their machine-readable finding inventories;
- the reproducibility report compares two clean builds and records each digest;
- every activity carries source revision, configuration SHA-256, tool versions,
  ordered activity history, and final result;
- OSQAr v0.10.2 framework validation is invoked with
  ``--profile qualification`` and the expected source/configuration identity;
- typed traceability is invoked with ``--profile qualification`` and the same
  authoritative evidence project;
- the shipped inventory is covered by a valid
  ``OSQAR-RELEASE-MANIFEST.json`` and survives clean-extraction verification.

A tool-created file that fails any reconciliation rule is a failed activity,
not partial positive evidence.

Current release decision
------------------------

**BLOCKED until fresh execution and independent review.** See the controlled
gap register in :doc:`06_lifecycle_management`.
