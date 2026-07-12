---
name: legal-peripherals-privacy-agreement-review
skill_type: skill
description: >-
  Review a Data Processing Agreement, auto-detecting whether the org is
  processor or controller and applying the right half of the playbook,
  grounded in the privacy domain ontology's DataProcessingAgreement class
  (subclass of Contract) and cross-linked to GDPR/CCPA. Use when reviewing an
  inbound or outbound DPA. Do NOT use for a DSAR
  (legal-peripherals-dsar-response), a PIA/DPIA
  (legal-peripherals-privacy-impact-assessment), or a general commercial
  contract review (legal-peripherals-contract-review).
license: MIT
tags: [legal-peripherals, privacy, dpa, gdpr, ccpa, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---

# Legal Peripherals — Data Processing Agreement Review

Grounded in
`domain_privacy.ttl`'s `:DataProcessingAgreement` (subclass of
`domain_commercial.ttl`'s `:Contract`; `:processorRole` = `controller` or
`processor`) and cross-linked to the `:GDPR`/`:CCPA` `:Regulation`
individuals this module declares.

## When to use
- Review an inbound or outbound DPA against the org's playbook.

## When NOT to use
- A Data Subject Access Request → `legal-peripherals-dsar-response`.
- A Privacy Impact Assessment / DPIA → `legal-peripherals-privacy-impact-assessment`.
- A general (non-privacy) commercial contract → `legal-peripherals-contract-review`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL`
for `legal_compliance_lookup`.

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `regulation_detail` | Pull GDPR's/CCPA's Obligation set the DPA must reflect |

## Recipe
1. **Auto-detect role** from the agreement's structure (who determines
   purposes/means of processing = controller; who processes on the other's
   behalf = processor) and apply the corresponding half of the playbook —
   controller-side DPAs emphasize instructions/audit-rights language;
   processor-side emphasize subprocessor flow-down and breach-notification
   timing.
2. **Ground the review** in the actual Obligation set:
   ```
   legal_compliance_lookup(action="regulation_detail", regulation="GDPR")
   ```
   Confirm the DPA's breach-notification clause meets (or beats) the
   72-hour `:BreachNotification72HourControl`; confirm subprocessor and
   data-subject-rights-assistance clauses are present.
3. Flag deviations the way `legal-peripherals-contract-review` does
   (GREEN/YELLOW/RED), typing the DPA as a `:DataProcessingAgreement`.

## KG grounding
The DPA is a `:Contract` subclass, so it inherits everything
`domain_commercial.ttl` models (amendment history, renewal deadlines,
escalation routing) while its `:processorRole` and GDPR/CCPA cross-link are
privacy-specific.

## Gotchas
- Controller vs. processor auto-detection is a heuristic — when the
  agreement is ambiguous (joint controllership, sub-processing chains),
  flag for review rather than force a single role.
- CCPA uses "business"/"service provider" terminology, not
  controller/processor — map correctly, don't conflate the two frameworks'
  vocabularies.

## Related
- `legal-peripherals-dsar-response` — the data-subject-rights side.
- `legal-peripherals-privacy-impact-assessment` — PIA/DPIA generation + triage.
- `legal-peripherals-contract-review` — general commercial contract review.
