OSQAr-cJSON: bounded qualification attempt
==========================================

.. important::

   This repository is a research and assurance work product for a bounded
   software-component qualification attempt. It is **not** a certification,
   compliance statement, ASIL allocation, or claim that cJSON is qualified for
   an automotive item. The current qualification decision is **BLOCK**.
   Release ``1.7.19-0.10.2`` is authorized only as a pre-integration development
   prerelease; qualification remains blocked.

The repository applies OSQAr v0.10.2 fail-closed evidence and typed-traceability
interfaces to the exact cJSON v1.7.19 core-source baseline. The primary process
framing is ISO 26262-8:2018, Clause 12. Item-specific suitability and independent
qualification verification remain mandatory.

Current repository state
------------------------

The ``main`` branch contains a blocked research candidate with a separately
controlled **candidate integration** decision. Its native evidence run passes
unit and supplemental scenarios, sanitizers, coverage, compiler warnings, and
reproducibility, but fails the configured complexity and static-analysis gates.
Framework and traceability qualification profiles therefore also fail. CI is
green only when it reproduces that exact blocked outcome and validates it against
``assurance/candidate-integration-policy.json``. Green CI is not a qualification
decision. The same policy separately permits the exact tagged
``1.7.19-0.10.2`` bundle to be published for pre-integration development while
qualification remains blocked. See :doc:`05_test_results` for the measured
results and remaining verification work.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Controlled work products

   01_requirements
   02_architecture
   03_verification
   04_implementation
   05_test_results
   06_lifecycle_management
   07_safety_case

Execution
---------

Create the documented Python 3.11 environment, install the hash-locked toolchain,
initialize the submodules, and execute the one-command frontend:

.. code-block:: console

   uv venv --python 3.11 .venv
   uv pip sync --python .venv/bin/python requirements.lock
   export PATH="$PWD/.venv/bin:$PATH"
   git submodule update --init --recursive
   ./build-and-test.sh all --source-revision "$(git rev-parse HEAD:cjson-source)"

The native runner additionally requires a C99 compiler, ``ar``, and sanitizer
runtime support. The locked environment supplies OSQAr v0.10.2, Sphinx,
Sphinx-Needs, pytest, gcovr, lizard, and Cppcheck. See :doc:`04_implementation`
for selective native commands and the candidate-integration contract.

Then run OSQAr v0.10.2 framework and traceability qualification profiles with the
same source revision and generated configuration SHA-256. On this baseline the
native, framework, and traceability qualification commands are expected to return
non-zero because controlled findings and unapproved evidence remain open. The CI
workflow accepts integration only after ``tools/verify_candidate_integration.py``
confirms that the complete generated failure inventory exactly matches the
controlled candidate policy. An unexpected pass, failure, metric, finding, or
traceability violation fails CI. Do not weaken a policy to obtain a pass.

Baseline review
---------------

The pre-revision artifact findings and acceptance criteria are retained in
``assurance/reviews/pre-v0.10.2-baseline-review.md``.
