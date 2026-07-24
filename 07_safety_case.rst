Qualification argument and decision
===================================

Top-level proposition
---------------------

The proposition under evaluation is:

   The exact cJSON ``v1.7.19`` core source identified in
   :doc:`01_requirements` is suitable for reuse under the bounded API,
   configuration, and assumptions of use, with verification rigor targeting
   ASIL D.

**Current decision: BLOCK — proposition not established.**

Argument structure
------------------

A future positive decision would require all of the following independent
branches to be accepted for the same immutable source/configuration/release
identity:

1. the software-component specification and intended-use boundary are complete;
2. each component requirement is allocated and covered by adequate normal and
   failure-condition verification;
3. structural coverage and uncovered-code dispositions demonstrate test
   completeness for the target rigor;
4. no known anomaly or analysis finding can violate an allocated safety
   requirement under the intended use;
5. the component development-process evidence required by ISO 26262-8:2018,
   12.4.1 is available and accepted;
6. integration instructions and every AoU decision are accepted for the target
   item/environment;
7. tool-confidence and evidence-integrity controls are accepted;
8. ISO 26262-8:2018, 12.4.3 verification confirms both the qualification results
   and their validity for intended use; and
9. the exact release inventory and manifest pass independent exact-tree review.

Why the current decision is BLOCK
---------------------------------

The technical activities were regenerated for this revision, but complexity
and static-analysis findings remain open and all candidate result/evidence
nodes remain unapproved. More importantly, the
controlled gaps for development-process evidence, intended-use validity,
coverage adequacy, anomaly disposition, tool confidence, and independent
qualification verification are open. Automated test success cannot close these
gaps.

Interpretation rule
-------------------

OSQAr framework or typed-traceability ``PASS`` means only that the declared
machine-checkable profile rules passed for the supplied project. It does not
mean that this proposition is accepted, that ISO 26262 compliance has been
assessed, or that cJSON is qualified for an automotive use. Conversely, any
framework, traceability, evidence, manifest, or independent-review failure is a
qualification-release BLOCK.

Release ``1.7.19-0.10.2`` is a separately controlled pre-integration development
prerelease. It may reproduce and disclose the reviewed blocked state for ongoing
engineering, but qualification remains blocked. The prerelease is not evidence
for the top-level proposition and must not be presented as a qualified component
package.
