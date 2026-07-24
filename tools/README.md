# Native qualification evidence runner

`./build-and-test.sh` is the one-command frontend. It requires Python 3.11 or
newer and an initialized `cjson-source` submodule at the repository's pinned
revision. The runner never initializes, updates, or modifies the submodule.

Commands:

```text
./build-and-test.sh all
./build-and-test.sh test
./build-and-test.sh sanitizer
./build-and-test.sh coverage
./build-and-test.sh complexity
./build-and-test.sh warnings
./build-and-test.sh static-analysis
./build-and-test.sh reproducible
```

Use `--source-revision REVISION` to record the controlled cJSON gitlink object;
otherwise the runner derives `HEAD:cjson-source`. In a Git checkout, an explicit
revision must match that gitlink. `CC`/`--cc` and `AR` select the compiler and
archiver.

Dependencies are a C99 compiler (GCC by default), `ar`, `gcovr`, `lizard`, and
`cppcheck`. Sanitizer execution also requires compiler/runtime support for
AddressSanitizer and UndefinedBehaviorSanitizer. Missing tools and malformed or
empty tool output fail closed. Running the automated runner tests additionally
requires `pytest`.

The fixed suite inventory is 21 upstream Unity executables and 162 cases.
Discovery rejects missing or additional top-level Unity test sources (while
excluding support sources `common.c` and `unity_setup.c`), and execution rejects
missing or additional binaries. Both component sources (`cJSON.c` and
`cJSON_Utils.c`) and all harnesses are instrumented for sanitizer and coverage
runs.

Enforced thresholds are:

- line coverage: at least 90%
- branch coverage: at least 80%
- cyclomatic complexity: at most 15 per function
- function length: at most 100 lines per function
- compiler warnings: none under the configured strong C99 flags with `-Werror`
- cppcheck `error` and `warning` findings: none

Generated evidence is written below `_build/evidence/<command>/` and remains
ignored by Git. Every report, log, JUnit file, and result file has an adjacent
`.provenance.json` sidecar containing its SHA-256, the source revision,
configuration SHA-256 and full configuration, tool versions, activity history,
and final result. JUnit contains one testcase per Unity case and reconciled
suite counters. The runner also executes 30 assurance-owned supplemental scenarios
covering malformed inputs, API edge cases, and deterministic allocation-failure
injection; these remain separate from the fixed upstream Unity inventory. The
pinned upstream suite contains one C89-era `TEST_IGNORE`
for non-finite numbers. The runner creates a build-directory-only C99 adaptation
that executes that case with `NAN`, positive infinity, and negative infinity;
the pinned submodule remains unchanged and ignored cases are rejected.

Run the runner tests with `python3 -m pytest -q`. The focused tests include real
temporary repository-copy fault seeds for a forced Unity assertion failure, an
aborting test process, a missing expected input/executable, and an injected
component memory error detected by the sanitizer. Faults are applied only to
temporary copies; the pinned submodule working tree is never edited.
