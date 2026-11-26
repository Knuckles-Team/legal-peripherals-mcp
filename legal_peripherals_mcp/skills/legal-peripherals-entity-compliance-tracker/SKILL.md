---
name: legal-peripherals-entity-compliance-tracker
skill_type: skill
description: >-
  Track a formed entity's ongoing compliance deadlines (annual or biennial report, registered agent, operating agreement) and run a health audit. Use after an entity was looked up or formed. Do NOT use for the lookup or EIN filing (entity-lookup, ein-filing) or cross-domain sweeps (compliance-watch).
license: MIT
tags: [legal-peripherals, corporate, entity-compliance, llc, sos, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Entity Compliance Tracker

Scope: Track a formed business entity's ongoing compliance deadlines (annual/ biennial report, registered-agent maintenance, operating-agreement currency) and run a health audit, grounded in the corporate domain ontology's EntityComplianceDeadline cross-linked to the LLC compliance module's LLCAnnualReportRequirement — the same entity this package's Secretary-of-State and EIN tools already formed. Use for post-formation compliance tracking of an entity looked up via `legal-peripherals-entity-lookup`. Do NOT use for the initial formation lookup/filing itself (legal-peripherals-entity-lookup, legal-peripherals-ein-filing) or cross-domain deadline sweeps spanning other practice areas (legal-peripherals-compliance-watch).

Tracks a formed entity's ongoing compliance, closing the loop this package's
SOS/EIN entity-formation tools opened:
`domain_corporate.ttl`'s `:EntityComplianceDeadline` (`:tracksRequirement`,
`:deadlineFor`, `:nextDueDate`) tracks a **specific Company's** instance of
`compliance_llc.ttl`'s `:LLCAnnualReportRequirement` — the general
requirement the entity-formation tools' ontology already declares.

## When to use
- After forming (or looking up) an entity with `legal-peripherals-entity-lookup`
  / `legal-peripherals-ein-filing`, initialize ongoing compliance tracking
  for it: next annual/biennial report due date, registered-agent status,
  operating-agreement currency.
- Report upcoming deadlines, update status once filed, or run a health audit
  across the org's tracked entities.

## When NOT to use
- The initial SOS lookup or EIN filing itself → `legal-peripherals-entity-lookup`
  / `legal-peripherals-ein-filing`.
- A cross-domain sweep spanning non-entity deadlines too →
  `legal-peripherals-compliance-watch`.
- Corporate governance documents (board resolutions, written consents) → out
  of scope here; see `domain_corporate.ttl`'s `:BoardResolution`/
  `:WrittenConsent` for the ontology shape, no dedicated skill ships yet.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL`
for the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`). Entity lookups themselves use `SOSTOOL`/
`EINTOOL`/`STATUTETOOL` (see `legal-peripherals-entity-lookup`).

## Steps

1. Pull the LLC requirement set with `legal_get_regulation`(regulation="LLCFormationGovernance"). Verify it returns `LLCAnnualReportRequirement`, registered-agent, and operating-agreement controls.
2. Confirm the state's report cadence and fee with `lookup_statute_rules`(state, entity_type, topic). Verify the cadence is read from the result rather than assumed annual.
3. Create an `:EntityComplianceDeadline` with `:tracksRequirement`, `:deadlineFor` the `:Company`, and `:nextDueDate`. Verify the date follows the state's cadence.
4. Run a health audit by re-checking each tracked entity with `sos_entity_lookup`(state, entity_name). Verify the status is freshly returned as active or good standing.
5. Report deadlines sorted by `:nextDueDate`, flagging past-due items as dissolution risk. Verify each flagged entity cites `:LLCAdministrativeDissolutionPenalty`.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `sos_entity_lookup` reports not configured | `OPENCORPORATES_API_TOKEN` is not set | Set the token in the server environment and repeat the lookup before reporting standing |
| Entity not found in registry | Wrong state or name | Search again with the correct `state` and a shorter `entity_name`, or fetch by `entity_id` |
| Cadence unknown for the state | `lookup_statute_rules` returned a general fallback | Mark the due date unconfirmed and cite the state's primary source |

## Tools & actions
| Tool | Arguments | Purpose |
|------|--------|---------|
| `legal_get_regulation` | `regulation` | Pull `LLCFormationGovernance`'s full Obligation/Control/ReportingRequirement set |
| `sos_entity_lookup` (existing) | — | Confirm current registry status before reporting "good standing" |
| `lookup_statute_rules` (existing) | — | Confirm the specific state's report cadence/fee |
| `legal_ingest_sos_entities` (existing) | — | Re-verify + re-ingest the entity's current SOS record |

## Recipe
1. Pull the general LLC compliance requirement set:
   ```
   legal_get_regulation(regulation="LLCFormationGovernance")
   ```
   This returns `LLCAnnualReportObligation` → `LLCAnnualReportFilingControl`
   → `LLCAnnualReportRequirement`, plus `LLCRegisteredAgentControl` and
   `LLCOperatingAgreementControl`.
2. For a specific `:Company` (a `:BusinessEntity` the SOS tool already
   ingested), create an `:EntityComplianceDeadline` `:tracksRequirement`
   `:LLCAnnualReportRequirement`, `:deadlineFor` the `:Company`, with
   `:nextDueDate` computed from the state's actual cadence (confirm via
   `lookup_statute_rules` — cadence/fee vary by jurisdiction, don't assume
   annual).
3. **Health audit:** for every tracked entity, re-run `sos_entity_lookup`
   to confirm current registry status is still "active"/"good standing" —
   never report standing without a fresh check.
4. Report upcoming deadlines, sorted by `nextDueDate`, flagging anything
   past due as administrative-dissolution risk
   (`:LLCAdministrativeDissolutionPenalty`).

## KG grounding
`:EntityComplianceDeadline` is the per-Company instantiation of the
GENERAL `:LLCAnnualReportRequirement` compliance_llc.ttl already declares —
the same pattern `legal-peripherals-compliance-watch` generalizes across
every domain. Because the underlying `:BusinessEntity` was ingested by the
existing `legal_ingest_sos_entities` tool, the deadline attaches to a real,
already-KG-resident node.

## Gotchas
- Report cadence AND fee are state-specific — never assume "annual"; some
  states are biennial, and the fee/deadline can shift by statute (check via
  `lookup_statute_rules`, don't hardcode).
- "Good standing" is a live registry fact, not a cached one — re-check via
  `sos_entity_lookup` before asserting it in a health-audit report.

## Related
- `legal-peripherals-entity-lookup` / `legal-peripherals-ein-filing` /
  `legal-peripherals-statute-lookup` — the existing formation tools this closes the loop on.
- `legal-peripherals-compliance-watch` — cross-domain deadline sweep.
