Qualification verification plan and evidence bindings
=====================================================

All activities are required for the bounded qualification attempt. A runner
step is successful only when the subprocess exit status, parsed content,
expected inventory, policy threshold, provenance, and output schema all pass.
A generated file by itself is not evidence of success.

Verification activities
-----------------------

.. ver:: Compile and execute the exact 21-executable upstream Unity inventory;
        reconcile 162 verbose cases, process exits, summaries, and JUnit cases.
   :id: VER_UNIT
   :status: active
   :produces: RESULT_UNIT

.. ver:: Recompile component objects and every harness with ASan and UBSan,
        execute the exact Unity inventory, and reject any sanitizer diagnostic,
        non-zero exit, signal, or inventory mismatch.
   :id: VER_SANITIZER
   :status: active
   :produces: RESULT_SANITIZER

.. ver:: Recompile component objects and harnesses with coverage
        instrumentation, execute the exact inventory, create gcovr JSON/text,
        validate the source scope, and enforce the recorded line/branch policy.
   :id: VER_COVERAGE
   :status: active
   :produces: RESULT_COVERAGE

.. ver:: Execute cppcheck against the recorded source scope, parse non-empty
        XML, reject error/warning findings, and inventory every remaining
        severity in a machine-readable findings record.
   :id: VER_STATIC
   :status: active
   :produces: RESULT_STATIC

.. ver:: Compile each recorded source under C99 with the warning policy and
        ``-Werror``; any diagnostic or command failure blocks the activity.
   :id: VER_WARNINGS
   :status: active
   :produces: RESULT_WARNINGS

.. ver:: Execute lizard live, parse each function metric, enforce the recorded
        CCN/function-length policy, and inventory every exceedance.
   :id: VER_COMPLEXITY
   :status: active
   :produces: RESULT_COMPLEXITY

.. ver:: Perform two clean builds from the same recorded inputs and compare
        SHA-256 identities for each component object and static library.
   :id: VER_REPRODUCIBLE
   :status: active
   :produces: RESULT_REPRODUCIBLE

Candidate result and evidence nodes
-----------------------------------

The nodes below intentionally remain ``blocked``/``candidate`` in source. The
evidence generator must create fresh artifacts, and OSQAr v0.10.2 must establish
framework acceptance for the exact source/configuration before a controlled
release process may promote them. Authored prose cannot self-approve evidence.

.. result:: Unity inventory and JUnit reconciliation result.
   :id: RESULT_UNIT
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: test-suite
   :evidenced_by: EVID_UNIT

.. evidence:: Generated ``_build/evidence/test_results.xml`` and paired
             provenance JSON.
   :id: EVID_UNIT
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: test-suite

.. result:: Component-instrumented ASan/UBSan execution result.
   :id: RESULT_SANITIZER
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: sanitizer
   :evidenced_by: EVID_SANITIZER

.. evidence:: Generated sanitizer execution report and provenance JSON.
   :id: EVID_SANITIZER
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: sanitizer

.. result:: Structural coverage policy result.
   :id: RESULT_COVERAGE
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: coverage
   :evidenced_by: EVID_COVERAGE

.. evidence:: Generated gcovr JSON/text reports and provenance JSON.
   :id: EVID_COVERAGE
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: coverage

.. result:: Static-analysis finding-policy result.
   :id: RESULT_STATIC
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: static-analysis
   :evidenced_by: EVID_STATIC

.. evidence:: Generated cppcheck XML, controlled finding inventory, and
             provenance JSON.
   :id: EVID_STATIC
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: static-analysis

.. result:: Compiler warning-policy result.
   :id: RESULT_WARNINGS
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: warnings
   :evidenced_by: EVID_WARNINGS

.. evidence:: Generated compiler invocation/diagnostic report and provenance.
   :id: EVID_WARNINGS
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: warnings

.. result:: Complexity threshold result.
   :id: RESULT_COMPLEXITY
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: complexity
   :evidenced_by: EVID_COMPLEXITY

.. evidence:: Generated lizard report, threshold finding inventory, and
             provenance JSON.
   :id: EVID_COMPLEXITY
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: complexity

.. result:: Clean-build reproducibility result.
   :id: RESULT_REPRODUCIBLE
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: reproducible-build
   :evidenced_by: EVID_REPRODUCIBLE

.. evidence:: Generated two-build SHA-256 comparison and provenance JSON.
   :id: EVID_REPRODUCIBLE
   :status: blocked
   :evidence_state: candidate
   :acceptance_activity: reproducible-build

Verification completeness rule
------------------------------

A result may be promoted only by a controlled generation step that binds the
result to the current source revision and configuration SHA-256 and only after
all required activity records pass OSQAr v0.10.2 qualification-profile
validation. Independent verification of intended-use validity remains a
separate Clause 12 release gate.
