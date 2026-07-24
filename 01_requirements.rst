Software component qualification specification
==============================================

Purpose and claim boundary
--------------------------

This repository records a **bounded qualification attempt** for reuse of the
identified cJSON component. It is not a certification, compliance statement, or
claim that cJSON is qualified for an automotive item. An integrator remains
responsible for item-specific safety analysis, allocation, integration,
verification, tool confidence, and acceptance of every assumption of use.

The process framing is ISO 26262-8:2018, Clause 12 (qualification of software
components). Unit and integration verification techniques from ISO
26262-6:2018, Clauses 9 and 10 support the evidence but do not replace the Part
8 Clause 12 intended-use and qualification-verification obligations.

Identified component and configuration
--------------------------------------

**Component identity:** upstream cJSON tag ``v1.7.19`` at git object
``c859b25d3b25fe44d3c99dc56dce35bdd55a8a8f``.

**In-scope implementation:** ``cjson-source/cJSON.c`` and
``cjson-source/cJSON.h`` with ``ENABLE_LOCALES`` not defined and the default
allocator hooks unless the integrator verifies a replacement allocator.

**In-scope API classes:** parsing, printing, tree construction/access,
deallocation, duplication/comparison, minification, allocator hooks, and error
pointer access declared by ``cJSON.h``.

**Explicitly outside the qualification claim:** ``cJSON_Utils.c`` and
``cJSON_Utils.h``; CMake/package integration; platform-specific shared-library
loading; locale-enabled number conversion; custom allocator behavior;
concurrent use of mutable trees; and any item-specific timing, stack, or memory
budget. The utilities are still built and exercised as regression context so
that their presence cannot silently corrupt the in-scope library build.

**Maximum target:** ASIL D verification rigor is targeted. This label is a
verification target only; it is not an ASIL allocation or qualification result.

Component requirements
----------------------

.. req:: The delivered component and evidence shall identify the exact upstream
         source object, in-scope files, build configuration, and qualification
         configuration hash.
   :id: REQ_COMPONENT_IDENTITY
   :status: active
   :allocated_to: ARCH_BUILD_BOUNDARY
   :allocated_to_api: IMPL_CORE_SOURCE
   :verified_by: VER_REPRODUCIBLE

.. req:: For a valid, bounded JSON input and sufficient resources, the parsing
         APIs shall return a tree representing the accepted input without
         reading outside the supplied buffer.
   :id: REQ_PARSE_VALID
   :status: active
   :allocated_to: ARCH_PARSER
   :allocated_to_api: IMPL_PARSE_API
   :verified_by: VER_UNIT, VER_SANITIZER

.. req:: For an in-scope cJSON tree and sufficient resources, the printing APIs
         shall emit a syntactically valid representation or report allocation
         failure through their documented return value.
   :id: REQ_PRINT_VALID
   :status: active
   :allocated_to: ARCH_PRINTER
   :allocated_to_api: IMPL_PRINT_API
   :verified_by: VER_UNIT, VER_SANITIZER

.. req:: Invalid, truncated, deeply nested, or unsupported input shall produce
         a documented failure result without undefined behavior in the
         exercised qualification configuration.
   :id: REQ_INPUT_FAILURE
   :status: active
   :allocated_to: ARCH_ERROR_CONTRACT
   :allocated_to_api: IMPL_PARSE_API, IMPL_DIAGNOSTIC_API
   :verified_by: VER_UNIT, VER_SANITIZER

.. req:: Component-owned dynamic memory shall be allocated and released through
         one compatible allocator family, and deletion shall release the full
         owned subtree without double free in the exercised configuration.
   :id: REQ_MEMORY_OWNERSHIP
   :status: active
   :allocated_to: ARCH_MEMORY
   :allocated_to_api: IMPL_MEMORY_API
   :verified_by: VER_UNIT, VER_SANITIZER

.. req:: Size and numeric conversions exercised by the bounded test suite shall
         not wrap into an unsafe allocation or cause undefined behavior.
   :id: REQ_NUMERIC_SAFETY
   :status: active
   :allocated_to: ARCH_PARSER, ARCH_PRINTER
   :allocated_to_api: IMPL_PARSE_API, IMPL_PRINT_API
   :verified_by: VER_UNIT, VER_SANITIZER, VER_STATIC

.. req:: Mutable cJSON trees and the global error pointer shall not be accessed
         concurrently unless the integrator supplies and verifies external
         synchronization; read-only access after publication is permitted only
         under the integrator's concurrency analysis.
   :id: REQ_CONCURRENCY_BOUNDARY
   :status: active
   :allocated_to: ARCH_ERROR_CONTRACT, ARCH_MEMORY
   :allocated_to_api: IMPL_DIAGNOSTIC_API, IMPL_MEMORY_API
   :verified_by: VER_STATIC, VER_UNIT

.. req:: The in-scope source shall compile as C99 with the recorded compiler
         configuration and without compiler diagnostics promoted by the
         qualification warning policy.
   :id: REQ_BUILD_DIAGNOSTICS
   :status: active
   :allocated_to: ARCH_BUILD_BOUNDARY
   :allocated_to_api: IMPL_CORE_SOURCE
   :verified_by: VER_WARNINGS

.. req:: The in-scope source shall be evaluated against the recorded static
         analysis and complexity policies; every finding or threshold
         exceedance shall be represented in a machine-readable result.
   :id: REQ_ANALYSIS_ACCOUNTABILITY
   :status: active
   :allocated_to: ARCH_BUILD_BOUNDARY
   :allocated_to_api: IMPL_CORE_SOURCE
   :verified_by: VER_STATIC, VER_COMPLEXITY

.. req:: The qualification test suite shall provide requirements-linked unit,
         failure-condition, sanitizer, and structural-coverage evidence whose
         counters reconcile with the executed inventory.
   :id: REQ_VERIFICATION_EVIDENCE
   :status: active
   :allocated_to: ARCH_BUILD_BOUNDARY
   :allocated_to_api: IMPL_CORE_SOURCE
   :verified_by: VER_UNIT, VER_SANITIZER, VER_COVERAGE

.. req:: Repeated clean builds with the same recorded inputs shall produce
         byte-identical in-scope objects and static library in the qualification
         environment.
   :id: REQ_REPRODUCIBLE_BUILD
   :status: active
   :allocated_to: ARCH_BUILD_BOUNDARY
   :allocated_to_api: IMPL_CORE_SOURCE
   :verified_by: VER_REPRODUCIBLE

Acceptance limitations
----------------------

Passing these requirements demonstrates only that the recorded activities
completed for the identified source and configuration. Suitability for an
intended automotive use is blocked until the Clause 12 gap register and AoU
protocol in :doc:`06_lifecycle_management` are independently accepted.
