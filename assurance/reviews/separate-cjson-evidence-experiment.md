# Separate blocked cJSON evidence experiment

**Disposition:** BLOCK

**Approved:** false

**Authority granted:** false

**Domain Owner:** Jan Toennemann

## Purpose

This record links a separate, public research experiment without importing or rebinding its artifacts into this repository. The experiment is published as [cJSON draft pull request #1](https://github.com/critx-jt/cJSON/pull/1) at exact head `30b79ee4a2a87a3a2761fb220468ab9792ce6bb3`.

The linked tree is a newly derived public research successor. It is distinct from this repository's candidate and from any future acceptance candidate. No review result transfers between those trees.

## Boundary preserved here

This repository remains bound to its existing cJSON v1.7.19 component object `c859b25da02955fef659d658b8f324b5cde87be3` and existing core-only qualification boundary. This record does not change the component source, submodule binding, manifests, policies, requirements, evidence runner, expected findings, or release disposition.

The linked experiment instead starts from public cJSON commit `fb16e5cf358798aabb049655975cde8427101056`, an unreleased post-v1.7.19 snapshot, and studies a core-plus-Utils evidence boundary. Its catalogs, descriptors, source locators, probes, tests, and provenance therefore do not describe this repository's candidate and must not be used here without a separately frozen migration and review.

## Experiment status

The linked draft publishes research-only qualification-evidence infrastructure while keeping the four protected implementation files byte-identical to its own public baseline. Its status remains **BLOCK**, with `approved=false` and `authority_granted=false`.

Known unresolved limitations include:

- coordinated rebinding of the semantic catalog and its validator oracle;
- coordinated rebinding of the helper catalog and its validator map;
- a raw-value contradiction in the projected `cJSON_GetStringValue` semantics;
- historical patch-digest non-reproducibility; and
- a historical semantic-review result whose raw disposition was `BLOCK` but whose terminal protocol was invalid.

The draft's structural checks and publication-integrity review passed for its exact head. Those results do not establish qualification, compliance, certification, safety, SEooC, release, component-use, or item-use authority.

## Consequence for OSQAr-cJSON

This is an informational tracking record only. It neither closes nor supersedes this repository's existing qualification gaps. The qualification and qualified-component publication decision in [`qualification-gate-disposition.md`](qualification-gate-disposition.md) remains **BLOCK**.

Any future adoption must begin from an explicitly selected baseline and scope, remove or control the known semantic-oracle weaknesses, freeze a new exact tree, and obtain fresh independent reviews. The linked draft must not be merged, tagged, released, or cited as qualified evidence on the strength of this record.
