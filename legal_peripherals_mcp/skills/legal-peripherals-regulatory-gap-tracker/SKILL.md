---
name: legal-peripherals-regulatory-gap-tracker
skill_type: skill
description: >-
  Track open compliance gaps between current policy/practice and the regulatory obligations declared in the compliance ontology suite, and produce a remediation plan. Use when the user asks "what gaps are open", wants a gap tracker or remediation status, or wants to close a gap against a named regulation/obligation.
license: MIT
tags: [legal-peripherals, regulatory, compliance-gap, ontology, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Regulatory Gap Tracker

Scope: Track open compliance gaps between current policy/practice and the regulatory obligations declared in the compliance ontology suite, and produce a remediation plan. Use when the user asks "what gaps are open", wants a gap tracker or remediation status, or wants to close a gap against a named regulation/obligation. Do NOT use for the live regulatory-feed sweep (legal-peripherals-regulatory-feed-watch) or for drafting the actual redlined policy text (legal-peripherals-policy-redraft).

KG-native gap tracking against the `legal_peripherals_mcp` compliance ontology
suite (`compliance.ttl` + per-framework modules + `domain_regulatory.ttl`'s
`:ComplianceGapRemediation`). Rather than tracking gaps in a hand-maintained
file per practice, this skill resolves the authoritative obligation/control
list straight from the ontology — so "what's open" is always consistent with
what the compliance-gate suite actually declares.

## When to use
- "What gaps are open" / "gap tracker" / "remediation status".
- Before closing a gap: confirm which Control(s) still need to be satisfied
  for a given Regulation.
- Building a remediation plan (`:ComplianceGapRemediation`) that references
  the exact `:ComplianceRequirement`/`:Control` it closes.

## When NOT to use
- Sweeping regulatory feeds for what's NEW → `legal-peripherals-regulatory-feed-watch`.
- Drafting the actual policy redline text → `legal-peripherals-policy-redraft`.
- A specific entity's LLC filing deadlines → `legal-peripherals-entity-compliance-tracker`.

## Prerequisites & environment
Connect via the `mcp-client` skill against **`legal-peripherals-mcp`**.

| Variable | Required | Notes |
|----------|----------|-------|
| `COMPLIANCETOOL` | optional | `True` (default) enables the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`) |

the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`) degrades honestly (a clear error, no fabrication) if
`rdflib` isn't installed — install `legal-peripherals-mcp[ontology]`.

## Steps

1. Pick the regulation by its local id. Verify the id is exact, since `regulation` is case-sensitive.
2. List its requirements with `legal_get_regulation`(regulation="HIPAA"). Verify obligations and required controls are returned.
3. For services spanning data classes, call `legal_gate_requirements`(data_classes="PHI,PII"). Verify `required_controls` is non-empty.
4. Diff the required controls against documented policy and practice. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify each missing control is listed as an open gap.
5. Record each remediation as a `:ComplianceGapRemediation` with `:remediatesGap` to the `:ComplianceRequirement`. Verify it links back via `:trackedByAssessment`.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `legal_get_regulation` returns no regulation | Free-text label used instead of local id | List ids with `legal_list_regulations` and use the exact one |
| Compliance tools return an error | `rdflib` not installed | Install `legal-peripherals-mcp[ontology]` |
| Org-specific gaps not persisted | Bundled ontology is static | Persist remediation records with `legal_ingest_filing_file` |

## Tools & actions
| Tool | Arguments | Purpose |
|------|--------|---------|
| `legal_get_regulation` | `regulation` | List every Obligation + required Control for a Regulation |
| `legal_gate_requirements` | `data_classes` | Given a set of data classifications, resolve every applicable Regulation + required Control (the compliance-gate join) |

### Key parameters
- `regulation` — a Regulation's local id (e.g. `HIPAA`, `FLSA`, `GDPR`, `CCPA`, `LLCFormationGovernance`).
- `data_classes` — comma-separated `:DataClassification` labels/ids (e.g. `PHI,PII`).

## Recipes
List every obligation + control HIPAA imposes, to see what "closed" looks like:
```
legal_get_regulation(regulation="HIPAA")
```
Resolve the full control set a service handling PHI+PII must satisfy (the gap
surface for a compliance gate):
```
legal_gate_requirements(data_classes="PHI,PII")
```
Then diff the returned `required_controls` against what the team's actual
policy/practice currently documents — every missing control is an open gap;
record the remediation as a `:ComplianceGapRemediation` (`domain_regulatory.ttl`)
`:remediatesGap`-linked to the specific `:ComplianceRequirement`.

## KG grounding
Every gap traced by this skill resolves to a real ontology triple
(`:Obligation`/`:Control`/`:ComplianceRequirement`) — never a free-text
assertion. `:ComplianceGapRemediation` (new in `domain_regulatory.ttl`) is the
class a remediation record should be typed as, `:trackedByAssessment` linking
it back to the `:Assessment` that surfaced it.

## Gotchas
- the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`) is read-only over the *bundled* ontology suite —
  it does not track a live per-org gap register (that lives in the KG once
  ingested, not in this static suite). Use `legal_ingest_filing_file` /
  the engine's write path to persist a specific org's remediation record.
- `regulation` is case-sensitive and must be the ontology's local id, not the
  free-text label (use `list_regulations` first if unsure).

## Related
- `legal-peripherals-regulatory-feed-watch` — what's new since the last check.
- `legal-peripherals-policy-redraft` — draft the actual policy fix.
- `legal-peripherals-entity-compliance-tracker` — per-entity filing deadlines.
