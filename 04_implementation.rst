Implementation — cJSON Qualification
======================================

.. need:: Qualified Source Baseline — cJSON v1.7.19
   :id: IMPL_SOURCE
   :status: active
   :tags: implementation;source
   :links: REQ_CJSON_PARSE_VALID;ARCH_MODULE_BOUNDARY

   The qualified cJSON source is taken from the upstream release v1.7.19
   (commit tagged in DaveGamble/cJSON). The source consists of two
   translation units:

   - **cJSON.c** (~3190 LOC): core parser, printer, and object model
   - **cJSON_Utils.c** (~1480 LOC): JSON Patch, JSON Pointer, Sort, and
     Merge utilities

   Public headers: ``cJSON.h`` and ``cJSON_Utils.h``.

.. need:: The qualified build uses a specified C99-compliant toolchain with fixed compiler version, flags, and standard library. All compiler warnings are treated as errors (-Werror) with an audited warning flag set.
   :id: IMPL_BUILD
   :status: active
   :tags: implementation;build
   :links: REQ_CJSON_REPRODUCIBLE

.. need:: The cJSON library is delivered as a compiled static library (libcjson.a) and shared object (libcjson.so) with exported symbol visibility restricted to the CJSON_PUBLIC API.
   :id: IMPL_DELIVERABLE
   :status: active
   :tags: implementation;delivery
   :links: ARCH_MODULE_BOUNDARY

.. need:: Third-party dependencies: cJSON has zero external library dependencies beyond the C standard library (C99). The test suite depends on the Unity test framework (bundled in tests/unity/) and CMake build system.
   :id: IMPL_DEPENDENCIES
   :status: active
   :tags: implementation;dependencies

Source inventory
----------------

.. list-table:: cJSON Source Files
   :header-rows: 1

   * - File
     - LOC
     - Purpose
   * - cJSON.c
     - 3191
     - Core parser, printer, object model
   * - cJSON.h
     - 306
     - Public API declarations, type definitions
   * - cJSON_Utils.c
     - 1481
     - JSON Patch, JSON Pointer, sort, merge
   * - cJSON_Utils.h
     - 88
     - Utils API declarations
   * - **Total**
     - **5066**
     - 

Public API surface: 78 CJSON_PUBLIC functions across core + utils, covering:

- Parsing (6 functions: Parse, ParseWithLength, ParseWithOpts, ParseWithLengthOpts, ParseWithLength, Version)
- Printing (4 functions: Print, PrintUnformatted, PrintBuffered, PrintPreallocated)
- Object creation (13 functions: CreateNull, CreateTrue, CreateFalse, CreateBool, CreateNumber, CreateString, CreateRaw, CreateArray, CreateObject, CreateStringReference, CreateObjectReference, CreateArrayReference, CreateIntArray)
- Item management (8 functions: AddItemToArray, AddItemToObject, AddItemReferenceToArray, AddItemReferenceToObject, InsertItemInArray, DeleteItemFromArray, DeleteItemFromObject, ReplaceItemInArray, ReplaceItemViaPointer, DetachItemFromArray, DetachItemViaPointer)
- Accessors (20 functions: GetArraySize, GetArrayItem, GetObjectItem, GetObjectItemCaseSensitive, HasObjectItem, GetErrorPtr, GetStringValue, GetNumberValue, and type-check functions)
- Utilities (functions for Patch, Pointer, Sort, Merge, CaseSensitive comparison via cJSON_Utils)

Compiler warning flags for qualified build:

.. code-block:: text

   -Wall -Wextra -Werror -Wpedantic -Wconversion
   -Wsign-conversion -Wdouble-promotion -Wfloat-equal
   -Wnull-dereference -Wformat=2 -Wstrict-prototypes
   -Wmissing-prototypes -Wdeclaration-after-statement
   -std=c99
