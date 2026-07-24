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

**BLOCKED.** A fresh candidate execution passed the upstream and supplemental
scenario runs, sanitizer execution, coverage thresholds, compiler warning audit,
and reproducibility comparison. It failed the configured complexity and Cppcheck
gates. OSQAr qualification-profile validation consequently returned ``FAIL``;
the generated evidence also remains unapproved pending independent exact-tree
review. The exact finding inventory and required dispositions are recorded in
``assurance/reviews/qualification-gate-disposition.md``. No shipment, release
manifest, tag, or publication may be produced from this state.
