Implementation and build boundary
=================================

Source identity
---------------

The component source is an unmodified git submodule pinned to
``c859b25d3b25fe44d3c99dc56dce35bdd55a8a8f`` (upstream cJSON ``v1.7.19``).
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

   ./build-and-test.sh all --source-revision "$(git rev-parse HEAD)"

The shell frontend delegates to ``tools/qualification.py``. The runner creates
a clean configuration-specific build directory, checks every subprocess return
code, validates every generated report, and writes provenance next to evidence.
The command is unsuccessful if a required tool is absent or any required gate
is incomplete.

Qualification configuration identity
------------------------------------

The configuration hash is calculated from the controlled qualification policy
and runner inputs, not from transient output paths. It covers at least source
scope, compiler/linker flags, preprocessor definitions, test source/input
inventory, tool policy thresholds, and evidence schema version. Tool executable
versions and the git source revision are recorded separately in activity
history so that environment drift is visible.

No generated evidence or archive is accepted from an earlier revision merely
because its filename matches.

Integration boundary
--------------------

The integrator shall use a compiler and C library suitable for its target,
repeat applicable verification for that target configuration, and verify all
AoU decisions. The Linux/GCC execution in this repository is reference evidence
for the recorded environment; it is not evidence for another compiler, ABI,
operating system, processor, or runtime resource budget.
