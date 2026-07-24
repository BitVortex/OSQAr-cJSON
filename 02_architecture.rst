Architecture and implementation allocation
==========================================

The architecture describes the boundary used by this qualification attempt. It
is not a replacement for an item-level software architecture.

Architecture elements
---------------------

.. arch:: Parser control flow consumes a bounded byte sequence through the
          internal parse buffer and constructs a cJSON tree. The nesting limit,
          buffer length, allocation results, and parse-end contract bound this
          path.
   :id: ARCH_PARSER
   :status: active
   :realized_by: IMPL_PARSE_API, IMPL_CORE_SOURCE

.. arch:: Printer control flow traverses an in-scope cJSON tree and writes to a
          dynamically grown or caller-provided buffer according to the selected
          printing API.
   :id: ARCH_PRINTER
   :status: active
   :realized_by: IMPL_PRINT_API, IMPL_CORE_SOURCE

.. arch:: Memory ownership is represented by tree links, value buffers, the
          reference flags, and the configured allocation hooks. Ownership is
          transferred only through documented API operations.
   :id: ARCH_MEMORY
   :status: active
   :realized_by: IMPL_MEMORY_API, IMPL_CORE_SOURCE

.. arch:: Failure and diagnostics are communicated through NULL/false return
          values and the parser error pointer. The latter is shared state and is
          therefore part of the concurrency restriction.
   :id: ARCH_ERROR_CONTRACT
   :status: active
   :realized_by: IMPL_DIAGNOSTIC_API, IMPL_CORE_SOURCE

.. arch:: The qualification build boundary fixes the source object, language
          mode, preprocessor configuration, compiler/linker options, test input
          inventory, tool versions, and evidence configuration hash.
   :id: ARCH_BUILD_BOUNDARY
   :status: active
   :realized_by: IMPL_CORE_SOURCE

Implementation elements
-----------------------

.. impl:: Parsing API class from ``cJSON.h``: ``cJSON_Parse*`` entry points and
         parse-result access through the returned tree.
   :id: IMPL_PARSE_API
   :kind: api
   :status: active

.. impl:: Printing API class from ``cJSON.h``: allocated, preallocated,
         formatted, and unformatted printing entry points.
   :id: IMPL_PRINT_API
   :kind: api
   :status: active

.. impl:: Ownership API class from ``cJSON.h``: hooks, create/add/detach/delete,
         duplicate, compare, and reference operations.
   :id: IMPL_MEMORY_API
   :kind: api
   :status: active

.. impl:: Diagnostic API class from ``cJSON.h``: error-pointer and type/query
         operations. The global error pointer is not a thread-local interface.
   :id: IMPL_DIAGNOSTIC_API
   :kind: api
   :status: active

.. impl:: The in-scope implementation is the unmodified upstream
         ``cJSON.c``/``cJSON.h`` pair at the identified git object. The
         qualification configuration does not define ``ENABLE_LOCALES``.
   :id: IMPL_CORE_SOURCE
   :kind: code
   :status: active

Control and data boundaries
---------------------------

The parser and printer have no operating-system or network interface. External
interactions are limited to input buffers, returned trees/buffers, C library
numeric/string operations, and configured allocation hooks. Resource bounds
and execution timing are platform- and input-dependent and remain integrator
obligations.
