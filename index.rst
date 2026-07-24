OSQAr-cJSON: bounded qualification attempt
==========================================

.. important::

   This repository is a research and assurance work product for a bounded
   software-component qualification attempt. It is **not** a certification,
   compliance statement, ASIL allocation, or claim that cJSON is qualified for
   an automotive item. The current release decision is **BLOCK**.

The repository applies OSQAr v0.10.2 fail-closed evidence and typed-traceability
interfaces to the exact cJSON v1.7.19 core-source baseline. The primary process
framing is ISO 26262-8:2018, Clause 12. Item-specific suitability and independent
qualification verification remain mandatory.

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

Initialize the submodules and execute the one-command frontend:

.. code-block:: console

   git submodule update --init --recursive
   ./build-and-test.sh all --source-revision "$(git rev-parse HEAD:cjson-source)"

Then run OSQAr v0.10.2 framework and traceability qualification profiles with the
same source revision and generated configuration SHA-256. A failed activity or
open controlled gap remains a BLOCK; do not weaken a policy to obtain a pass.

Baseline review
---------------

The pre-revision artifact findings and acceptance criteria are retained in
``assurance/reviews/pre-v0.10.2-baseline-review.md``.
