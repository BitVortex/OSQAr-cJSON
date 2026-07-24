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

Review tracking status
----------------------

Issue #21 was closed as not planned when the blocked research candidate was
integrated. Its acceptance criteria were not completed: the evidence was not
approved and no independent Clause 12 qualification approval was recorded. The
`issue record <https://github.com/BitVortex/OSQAr-cJSON/issues/21>`_ remains in
the candidate policy as a historical follow-up reference; issue closure is not
evidence that its qualification gates passed. A future qualification attempt
must open a new exact-tree review issue and bind its decision to that immutable
tree.

Measured baseline
-----------------

The controlled candidate policy and disposition record fix the current measured
outcome as follows:

- all 162 upstream Unity cases across 21 executables pass with no ignored case;
- all 30 assurance-owned supplemental scenarios pass;
- ASan/UBSan execution, the compiler warning audit, and the two-build
  reproducibility comparison pass;
- line coverage is 90.44% and branch coverage is 80.26%; these meet the local
  mechanical thresholds, but MC/DC is not measured and coverage adequacy for the
  qualification argument remains explicitly unaccepted;
- 15 of 154 functions exceed the complexity or function-length policy, with
  observed maxima of CCN 37 and 230 lines (QF-01); and
- 17 Cppcheck error/warning findings remain open (QF-02).

The CI policy expects ``test``, ``sanitizer``, ``coverage``, ``warnings``, and
``reproducible`` to pass, and ``complexity`` and ``static-analysis`` to fail.
Any different result is rejected rather than treated as automatically better:
the exact evidence and policy must first be reviewed and updated together.

Outstanding verification work
-----------------------------

The current runner does not complete Valgrind/Memcheck analysis, sustained
fuzzing, MISRA C assessment with a suitable checker, MC/DC measurement, or an
independent RFC-conformance validation. These activities are tracked in GitHub
issues `#5 <https://github.com/BitVortex/OSQAr-cJSON/issues/5>`_ through
`#9 <https://github.com/BitVortex/OSQAr-cJSON/issues/9>`_. Evidence approval,
finding-specific dispositions, tool-confidence justification, intended-use and
assumptions-of-use confirmation, anomaly disposition, and independent
verification of the immutable final result also remain open. Until the
applicable work is completed and accepted, the result remains BLOCK regardless
of locally passing mechanical activities.
