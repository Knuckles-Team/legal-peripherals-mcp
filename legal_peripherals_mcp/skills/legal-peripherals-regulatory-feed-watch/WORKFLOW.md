# Legal Peripherals Regulatory Feed Watch

Check for new/changed regulatory guidance and open NPRM comment periods against the regulations tracked in the compliance ontology suite, and report what's material. Use when the user says "check the feeds", "what's new in regulation X", or an NPRM comment window needs tracking. Do NOT use for gap remediation (legal-peripherals-regulatory-gap-tracker) or entity-specific filing deadlines (legal-peripherals-entity-compliance-tracker).

# Legal Peripherals — Regulatory Feed Watch

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

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `list_domains` | Inventory every ontology module (incl. `domain_regulatory.ttl`'s change-notice/guidance vocabulary) |
| `legal_compliance_lookup` | `regulation_detail` | Materiality check: does this Regulation apply to your Sector/DataClassification? |
| `legal_compliance_lookup` | `sector_lookup` / `dataclass_lookup` | Narrow to only the Regulations that matter to your practice profile |

## Recipes
See what regulatory-domain vocabulary is available (change notices, agency
guidance, enforcement actions):
```
legal_compliance_lookup(action="list_domains")
```
Materiality-filter: only regulations touching your sector matter:
```
legal_compliance_lookup(action="sector_lookup", sector="Medical")
```
Then, for anything the org's real feed connector surfaces as changed, resolve
which Obligations it affects:
```
legal_compliance_lookup(action="regulation_detail", regulation="HIPAA")
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
