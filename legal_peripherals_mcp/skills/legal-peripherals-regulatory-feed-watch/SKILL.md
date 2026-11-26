---
name: legal-peripherals-regulatory-feed-watch
skill_type: skill
description: >-
  Check for new/changed regulatory guidance and open NPRM comment periods against the regulations tracked in the compliance ontology suite, and report what's material. Use when the user says "check the feeds", "what's new in regulation X", or an NPRM comment window needs tracking.
license: MIT
tags: [legal-peripherals, regulatory, feed-watch, nprm, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Regulatory Feed Watch

Scope: Check for new/changed regulatory guidance and open NPRM comment periods against the regulations tracked in the compliance ontology suite, and report what's material. Use when the user says "check the feeds", "what's new in regulation X", or an NPRM comment window needs tracking. Do NOT use for gap remediation (legal-peripherals-regulatory-gap-tracker) or entity-specific filing deadlines (legal-peripherals-entity-compliance-tracker).

A KG-grounded feed check: every tracked Regulation's current
obligation/control/reporting-requirement set, plus the illustrative
`:RegulatoryChangeNotice`/`:AgencyGuidance` individuals in
`domain_regulatory.ttl` that model the NPRM/guidance lifecycle. A live
Federal Register / agency-RSS feed still needs a connector adapted per
deployment; this skill's grounding is KG-native and composes with **any**
connector the fleet later wires in via `source_connector` — the ontology
shape (`:RegulatoryChangeNotice :amendsRegulation`, `:commentDeadline`) is
already there to receive it.

## When to use
- "Check the feeds" / "what's new since the last check".
- An NPRM has an open comment period and you need the deadline + which
  Regulation/Obligation it would amend.
- Materiality triage: does this change touch a Regulation your org actually
  tracks (has a Sector/DataClassification match)?

## When NOT to use
- Closing a known gap → `legal-peripherals-regulatory-gap-tracker`.
- Drafting the policy redline in response → `legal-peripherals-policy-redraft`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`. Same `COMPLIANCETOOL`
toggle as the other compliance skills; no external feed API is required for
the KG-native lookup (a live feed connector, if wired, is a separate
`source_connector` concern — see Gotchas).

## Steps

1. List the available vocabulary with `legal_list_compliance_domains`. Verify `domain_regulatory.ttl` appears among the modules.
2. Narrow to the org's practice with `legal_lookup_sector`(sector="Medical"). Verify the returned regulations match the sector.
3. For each changed item reported by a live feed connector, call `legal_get_regulation`(regulation="HIPAA") with the affected regulation. Verify the affected obligations are listed.
4. Report the open comment deadline and the regulation it amends via `:RegulatoryChangeNotice`. Verify the report separates ontology facts from live feed data.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No live changes reported | No feed connector wired | State that only the ontology is searched and wire a connector via `source_connector` |
| Sector lookup empty | Sector label not recognized | Retry with a label returned by `legal_list_compliance_domains` |
| Compliance tools missing | `COMPLIANCETOOL` disabled or `rdflib` missing | Enable `COMPLIANCETOOL` and install `legal-peripherals-mcp[ontology]` |

## Tools & actions
| Tool | Arguments | Purpose |
|------|--------|---------|
| `legal_list_compliance_domains` | - | Inventory every ontology module (incl. `domain_regulatory.ttl`'s change-notice/guidance vocabulary) |
| `legal_get_regulation` | `regulation` | Materiality check: does this Regulation apply to your Sector/DataClassification? |
| the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`) | `sector_lookup` / `dataclass_lookup` | Narrow to only the Regulations that matter to your practice profile |

## Recipes
See what regulatory-domain vocabulary is available (change notices, agency
guidance, enforcement actions):
```
legal_list_compliance_domains()
```
Materiality-filter: only regulations touching your sector matter:
```
legal_lookup_sector(sector="Medical")
```
Then, for anything the org's real feed connector surfaces as changed, resolve
which Obligations it affects:
```
legal_get_regulation(regulation="HIPAA")
```

## KG grounding
`domain_regulatory.ttl` models the change lifecycle with
`:RegulatoryChangeNotice` (`:amendsRegulation`, `:commentDeadline`,
`:issuedByAuthority`) and `:AgencyGuidance` — typed nodes a real feed
connector's ingest can populate instead of a flat per-practice markdown log,
so "what's new" composes with `graph_query` across every tracked Regulation
at once instead of a set of siloed single-purpose watchers.

## Gotchas
- This skill's KG-native lookup answers "what does the ontology say", not
  "what changed on the Federal Register today" — a live feed still needs a
  real connector (RSS/Federal Register API) wired via `source_connector`;
  the illustrative `:HIPAAOmnibusRuleNotice`/`:FLSAOvertimeRuleGuidance`
  individuals in `domain_regulatory.ttl` show the target shape, not live data.
- Materiality threshold is a practice-specific judgment call — this skill
  surfaces the ontology facts; the threshold decision is the agent's/user's.

## Related
- `legal-peripherals-regulatory-gap-tracker` — close a known gap.
- `legal-peripherals-policy-redraft` — draft the fix.
- `legal-peripherals-compliance-watch` — cross-domain deadline/requirement watch.
