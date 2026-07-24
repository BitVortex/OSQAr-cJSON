Implementation and build boundary
=================================

Source identity
---------------

The component source is an unmodified git submodule pinned to
``c859b25da02955fef659d658b8f324b5cde87be3`` (upstream cJSON ``v1.7.19``).
The Unity test framework is pinned independently. A qualification result is
valid only for these exact git objects and the configuration identified in its
evidence provenance.

The qualification claim includes ``cJSON.c`` and ``cJSON.h``. The runner also
compiles ``cJSON_Utils.c`` and executes its upstream tests as regression context,
but this does not silently extend the claim to the utilities API.

One-command frontend
--------------------

From a checkout with initialized submodules:

.. code-block:: console

   ./build-and-test.sh all --source-revision "$(git rev-parse HEAD:cjson-source)"

The shell frontend delegates to ``tools/qualification.py``. The runner creates
a clean configuration-specific build directory, checks every subprocess return
code, validates every generated report, and writes provenance next to evidence.
The command is unsuccessful if a required tool is absent or any required gate
is incomplete.

For focused regeneration, replace ``all`` with ``test``, ``sanitizer``,
``coverage``, ``complexity``, ``warnings``, ``static-analysis``, or
``reproducible``. ``--source-revision`` selects the revision recorded in
provenance and must match ``HEAD:cjson-source`` in a Git checkout. The compiler
can be selected through ``CC`` or ``--cc``; the archiver is selected through
``AR``. Missing tools, malformed output, or an incomplete expected inventory
fail the selected activity.

Qualification configuration identity
------------------------------------

The configuration hash is the SHA-256 of the runner's canonical, static
``CONFIGURATION`` mapping. It covers the schema number, component manifest path
and digest, component source names, expected Unity executable names and case
count, the build-only non-finite-number test adaptation, warning flags,
sanitizer selection, and coverage/complexity thresholds. It does not hash the
runner source, supplemental scenario source, full test-input contents, every
compiler/linker option, or the documentation tree. Tool executable versions and
the git source revision are recorded separately in activity history.

Consequently, the configuration SHA-256 is one evidence binding, not a digest
of the complete repository or execution environment. Exact-tree review, the
component source manifest, generated evidence provenance, and the controlled
candidate policy provide the additional bindings needed to detect drift outside
the static mapping.

No generated evidence or archive is accepted from an earlier revision merely
because its filename matches.

Exported-source identity
------------------------

``assurance/component-source-manifest.json`` records the SHA-256 digest of each
of 229 files from the pinned cJSON source tree together with the expected git
object. The runner verifies every listed entry before using an exported source
tree, including when ``.git`` metadata is unavailable. A missing or altered
listed file is rejected. The verifier does not enumerate the source directory
and therefore does not reject additional unlisted files; this manifest is not a
closed-world archive inventory. It binds the declared inputs to the component
revision but does not extend the in-scope qualification claim beyond
``cJSON.c`` and ``cJSON.h``.

Blocked-candidate integration
-----------------------------

The current baseline intentionally has an expected non-zero exit status from
the native ``all`` command and from both OSQAr qualification-profile commands.
``assurance/candidate-integration-policy.json`` records the only blocked outcome
that CI may integrate: the seven native activity results, exact coverage values,
complete QF-01 and QF-02 finding inventories, required framework failures, and
all 47 traceability violations. It also fixes
``qualification_claimed`` and ``publication_authorized`` to false.

After fresh native, framework, and traceability reports have been generated, CI
executes the separate fail-closed policy checker:

.. code-block:: console

   python tools/verify_candidate_integration.py \
     --root . \
     --policy assurance/candidate-integration-policy.json \
     --framework-report _build/evidence/framework-validation.json \
     --traceability-report _build/evidence/traceability-qualification-v1.json

The checker fails closed if any activity result, metric, finding, deviation, or
violation differs from policy. Its ``PASS`` means only that the documented
blocked candidate is internally consistent enough to integrate for continued
work; it cannot promote evidence, authorize publication, or establish component
qualification.

Integration boundary
--------------------

The integrator shall use a compiler and C library suitable for its target,
repeat applicable verification for that target configuration, and verify all
AoU decisions. The Linux/GCC execution in this repository is reference evidence
for the recorded environment; it is not evidence for another compiler, ABI,
operating system, processor, or runtime resource budget.
