Lifecycle, assumptions of use, and qualification gaps
=====================================================

Assumptions-of-use protocol
---------------------------

For each AoU below the integrator shall record: applicability; item/element and
allocated safety requirements; objective evidence; reviewer and independence;
PASS/BLOCK decision; source revision; component configuration; target
compiler/platform; and the release-manifest digest. ``Not applicable`` requires
a rationale and reviewer. Missing evidence or an unresolved decision is BLOCK.

.. lifecycle:: Inputs are bounded, available for the full call, and subject to
              item-specific size/depth/resource limits. The integrator verifies
              malformed, truncated, deeply nested, and overload behavior against
              its allocated safety requirements.
   :id: LM_AOU_INPUTS
   :kind: assumption
   :status: active
   :owner: integrator
   :gate_effect: block
   :constrains: REQ_PARSE_VALID, REQ_INPUT_FAILURE, VER_UNIT, VER_SANITIZER, VER_COVERAGE

.. lifecycle:: Mutable trees are owned by one execution context or externally
              synchronized. The global parse-error pointer is not used as a
              cross-thread diagnostic interface. The integrator verifies its
              publication and lifetime model.
   :id: LM_AOU_CONCURRENCY
   :kind: assumption
   :status: active
   :owner: integrator
   :gate_effect: block
   :constrains: REQ_CONCURRENCY_BOUNDARY, ARCH_ERROR_CONTRACT, ARCH_MEMORY, VER_STATIC

.. lifecycle:: Custom allocation hooks, if used, form a compatible allocation
              family for the complete component lifetime and meet item-specific
              failure, determinism, alignment, and concurrency requirements.
   :id: LM_AOU_ALLOCATOR
   :kind: assumption
   :status: active
   :owner: integrator
   :gate_effect: block
   :constrains: REQ_MEMORY_OWNERSHIP, ARCH_MEMORY, VER_SANITIZER

.. lifecycle:: The production compiler, C library, ABI, options, definitions,
              locale behavior, and target hardware are identified. Differences
              from the reference qualification environment are impact-analysed
              and applicable verification is repeated.
   :id: LM_AOU_TOOLCHAIN
   :kind: assumption
   :status: active
   :owner: integrator
   :gate_effect: block
   :constrains: REQ_BUILD_DIAGNOSTICS, REQ_REPRODUCIBLE_BUILD, ARCH_BUILD_BOUNDARY, VER_WARNINGS, VER_REPRODUCIBLE

.. lifecycle:: Item-specific execution-time, stack, heap, recursion-depth, and
              availability budgets are established and verified using the real
              input distribution and target environment; this repository does
              not provide those budgets.
   :id: LM_AOU_RESOURCES
   :kind: assumption
   :status: active
   :owner: integrator
   :gate_effect: block
   :constrains: REQ_INPUT_FAILURE, ARCH_PARSER, ARCH_PRINTER, VER_COVERAGE

.. lifecycle:: Only the identified ``cJSON.c``/``cJSON.h`` source and in-scope
              API classes are relied upon. Utilities, locale-enabled behavior,
              packaging, and modified source require a new or extended
              qualification specification and impact analysis.
   :id: LM_AOU_SCOPE
   :kind: assumption
   :status: active
   :owner: integrator
   :gate_effect: block
   :constrains: REQ_COMPONENT_IDENTITY, ARCH_BUILD_BOUNDARY, VER_REPRODUCIBLE

Change and baseline control
---------------------------

Every change to the source gitlink, runner, qualification policy, requirement,
AoU, accepted deviation, tool version, or generated shipment invalidates the
previous evidence baseline and exact-tree review. Such a change does not
necessarily change the configuration SHA-256: that digest changes only when the
static ``CONFIGURATION`` mapping in ``tools/qualification.py`` changes. The full
evidence workflow shall still be rerun and the new exact tree independently
reviewed. The upstream issue/anomaly state is reviewed at each release rather
than copied forward as static prose.

Tool-confidence boundary
------------------------

The compiler, linker, Python runtime, Unity, sanitizers, gcovr, lizard,
cppcheck, Sphinx/Sphinx-Needs, OSQAr, archive tools, and cryptographic digest
implementation can introduce or fail to detect errors. This repository records
versions and applies diverse checks (process status, parsers, schema checks,
counter reconciliation, fault seeds, clean rebuilds, and exact-inventory
verification). These controls are detection evidence; they are not, by
themselves, an ISO 26262-8:2018 Clause 11 tool qualification or a justified TCL
determination for an integrator's use.

Controlled Clause 12 gap register
---------------------------------

.. lifecycle:: Evidence that the upstream component development process is
              based on an appropriate national or international standard has
              not been established for this baseline.
   :id: LM_GAP_DEVELOPMENT_PROCESS
   :kind: gap
   :status: open
   :owner: component-qualification-manager
   :gate_effect: block

.. lifecycle:: Item-independent tests cannot establish suitability for a
              specific intended use. The AoU protocol requires item/integration
              evidence and an independent validity review.
   :id: LM_GAP_INTENDED_USE
   :kind: gap
   :status: open
   :owner: integrator
   :gate_effect: block

.. lifecycle:: Structural coverage in the reference environment does not by
              itself establish completeness for ASIL D requirements or the
              target production environment. Uncovered code and derived test
              adequacy require reviewed disposition.
   :id: LM_GAP_COVERAGE_ADEQUACY
   :kind: gap
   :status: open
   :owner: verification-manager
   :gate_effect: block

.. lifecycle:: Upstream known anomalies and live analysis findings require
              safety-impact classification, disposition, and regression linkage
              for the intended use.
   :id: LM_GAP_ANOMALIES
   :kind: gap
   :status: open
   :owner: component-qualification-manager
   :gate_effect: block

.. lifecycle:: Tool-confidence evaluations for the actual qualification and
              production tool uses have not received independent acceptance.
   :id: LM_GAP_TOOL_CONFIDENCE
   :kind: gap
   :status: open
   :owner: tool-qualification-manager
   :gate_effect: block

.. lifecycle:: ISO 26262-8:2018, 12.4.3 verification of the qualification result
              and its intended-use validity has not been completed by an
              independent reviewer for an immutable release tree.
   :id: LM_GAP_INDEPENDENT_VERIFICATION
   :kind: gap
   :status: open
   :owner: independent-functional-safety-reviewer
   :gate_effect: block

Release rule
------------

Any open gap with ``gate_effect=block``, failed qualification-profile activity,
manifest mismatch, or independent BLOCK decision prevents publication or use of
the archive as a qualified software component package. A blocked archive may be
retained as a clearly labeled research/review candidate. Policy version 2
authorizes ``1.7.19-0.10.2`` as a GitHub prerelease for pre-integration
development only, provided the exact documented blocked outcome, exact-tree
review, archive checksum, and closed release manifest all pass. Qualification
remains blocked.

The prerelease archive carries ``DEVELOPMENT-RELEASE.json`` with the exact tag
commit, tree, component revision, release channel, and non-qualification status.
``OSQAR-RELEASE-MANIFEST.json`` provides the closed inventory subject to its
explicit exclusions. Neither record converts failed or unapproved qualification
evidence into accepted evidence.

OSQAr release manifests reject zero-length artifacts. The manifest therefore
records explicit exclusions for the empty Furo extension stub and the two empty
compiler-warning logs. ``DEVELOPMENT-RELEASE.json`` fixes that exclusion list,
and the adjacent ZIP SHA-256 binds the complete archive including those files.
