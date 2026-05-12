Architecture — cJSON Qualification
====================================

.. need:: The cJSON parser implements a recursive-descent algorithm operating on a UTF-8 byte stream. Control flow passes through tokenizer, value parser, and object/array constructors.
   :id: ARCH_PARSER_FLOW
   :status: active
   :tags: architecture;parsing
   :links: REQ_CJSON_PARSE_VALID;REQ_CJSON_NO_UB;REQ_CJSON_STACK_BOUNDED

.. need:: The cJSON printer traverses an in-memory cJSON object graph, emitting formatted or unformatted JSON text through a bounded output buffer.
   :id: ARCH_PRINTER_FLOW
   :status: active
   :tags: architecture;printing
   :links: REQ_CJSON_PRINT_VALID;REQ_CJSON_ARITH_SAFE

.. need:: Memory management uses the standard C malloc/free allocator by default, with an optional hook mechanism (cJSON_InitHooks) that allows integration with a safety-qualified memory allocator.
   :id: ARCH_MEMORY_MODEL
   :status: active
   :tags: architecture;memory
   :links: REQ_CJSON_MEMORY_SAFE

.. need:: The cJSON data model is a tagged union (cJSON struct) supporting six value types: null, boolean, number, string, array, object. Arrays are linked lists of cJSON items; objects are linked lists of cJSON items with associated string keys.
   :id: ARCH_DATA_MODEL
   :status: active
   :tags: architecture;datamodel

.. need:: The cJSON module boundary is defined by cJSON.h. All public API functions are marked CJSON_PUBLIC. Internal helpers (parse_, print_, ensure_, etc.) are static and not part of the external interface. The cJSON_Utils extension provides JSON Patch and JSON Pointer operations on top of the core API.
   :id: ARCH_MODULE_BOUNDARY
   :status: active
   :tags: architecture;interface
   :links: REQ_CJSON_NULL_PTR_SAFE

Component Architecture (PlantUML)
------------------------------------

.. container:: gsn-figure

   .. plantuml:: _static/cjson_component_architecture.puml
      :alt: cJSON v1.7.19 Component Architecture Diagram
      :align: center

.. need:: Component decomposition: The cJSON core (cJSON.c) contains the Parser (recursive-descent JSON tokenizer and value constructor), Printer (tree-walk JSON serializer to buffer), Memory Management (malloc/free with optional hook replacement), and Object Model (tagged-union cJSON struct with linked-list children for arrays/objects). The cJSON Utils (cJSON_Utils.c) builds on the core with JSON Patch (RFC 6902), JSON Pointer (RFC 6901), and Sort/Merge utilities. All components interface with the C standard library for string and memory operations.
   :id: ARCH_COMPONENT_DECOMPOSITION
   :status: active
   :tags: architecture;decomposition
   :links: REQ_CJSON_PARSE_VALID;ARCH_PARSER_FLOW

Parser Flow (PlantUML)
-----------------------

.. container:: gsn-figure

   .. plantuml:: _static/cjson_parser_flow.puml
      :alt: cJSON Parser Flow Sequence Diagram
      :align: center

Data Model (PlantUML)
----------------------

.. container:: gsn-figure

   .. plantuml:: _static/cjson_data_model.puml
      :alt: cJSON Data Model Class Diagram
      :align: center

Safety Architecture — Freedom from Interference
------------------------------------------------

.. need:: FFI measures: cJSON has no global state (all state is in caller-owned cJSON* objects). Memory allocation hooks enable replacement with a qualified allocator. The API uses bounded stack depth (CJSON_NESTING_LIMIT=1000). No thread synchronization is performed inside the library. Integrator responsibilities: provide a qualified allocator via cJSON_InitHooks, validate all inputs before API calls, check all return values for error indicators, handle error paths at the integration boundary, and ensure inputs respect nesting limits.
   :id: ARCH_FFI_MEASURES
   :status: active
   :tags: architecture;ffi;safety
   :links: REQ_CJSON_STACK_BOUNDED;REQ_CJSON_MEMORY_SAFE
