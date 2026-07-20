# Legal Peripherals Dsar Response

Walk through a Data Subject Access Request (or deletion/portability/ correction request) and draft the response — verify identity, locate data system-by-system, and meet the statutory deadline — grounded in the privacy domain ontology's DataSubjectRequest class cross-linked to GDPR's 30-day / CCPA's 45-day response clocks. Use whenever a data-subject rights request comes in. Do NOT use for a DPA review (legal-peripherals-privacy-agreement-review) or a PIA (legal-peripherals-privacy-impact-assessment).

# Legal Peripherals — DSAR Response

Grounded in
`domain_privacy.ttl`'s `:DataSubjectRequest` (`:requestType`,
`:requestDeadline`, `:concernsDataSubject`) and the
`:DSARFulfillmentControl` both `:GDPR` and `:CCPA` require.

## When to use
- Any access, deletion, portability, or correction request from a data
  subject/consumer needs verification, location, and a drafted response
  within the statutory window.

## When NOT to use
- Reviewing a DPA → `legal-peripherals-privacy-agreement-review`.
- Generating a PIA/DPIA or triaging whether one is needed →
  `legal-peripherals-privacy-impact-assessment`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL`
for `legal_compliance_lookup` to confirm the applicable deadline.

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `regulation_detail` | Confirm the DSARFulfillmentControl + which Regulation(s) (GDPR/CCPA) govern this request |

## Recipe
1. **Identify the applicable regime.** If the requester is an EU/EEA data
   subject → GDPR (generally 30 days, extendable). If a California consumer
   → CCPA (45 days, extendable once). Both regimes are declared in
   `domain_privacy.ttl`:
   ```
   legal_compliance_lookup(action="regulation_detail", regulation="GDPR")
   legal_compliance_lookup(action="regulation_detail", regulation="CCPA")
   ```
2. **Verify identity** using a documented, proportionate method — never
   request MORE identifying information than needed to fulfill the request.
3. **Locate data system-by-system** — walk every system that could hold the
   requester's PII, not just the primary CRM/database.
4. **Draft the response** matching the request type (`access` = data export;
   `deletion` = confirm scope and any legal-hold exceptions; `portability` =
   structured machine-readable export; `correction` = confirm the specific
   field(s) updated).
5. Type the request as a `:DataSubjectRequest` with `:requestDeadline` set
   from step 1's clock, and `:concernsDataSubject` the requester.

## KG grounding
Every DSAR is a typed node with a deadline — composable with
`legal-peripherals-compliance-watch`'s cross-domain deadline sweep so "every
DSAR due this week across every regime" is one query, not per-regime
tracking.

## Gotchas
- A deletion request may have legitimate exceptions (legal hold, ongoing
  contract necessity, legal-obligation retention) — verify before honoring
  automatically; document the exception if invoked, never silently ignore
  the request.
- Don't over-collect identity-verification data — that itself creates a new
  privacy risk.

## Related
- `legal-peripherals-privacy-agreement-review` — the processor/controller DPA side.
- `legal-peripherals-privacy-impact-assessment` — is a PIA/DPIA needed for the underlying processing?
- `legal-peripherals-compliance-watch` — cross-domain deadline sweep.
