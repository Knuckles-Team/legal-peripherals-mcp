---
name: legal-peripherals-contract-review
skill_type: skill
description: >-
  Review an inbound NDA, vendor agreement, or SaaS/MSA subscription against
  the team playbook, auto-routing to the right sub-review by agreement type
  and flagging deviations GREEN/YELLOW/RED — grounded in the commercial
  domain ontology's NDAAgreement/VendorAgreement/MSAAgreement classes and
  cross-linked to compliance Attestations when the contract touches
  classified data. Use when reviewing any inbound commercial
  contract. Do NOT use for tracking amendment history or renewal deadlines
  (legal-peripherals-contract-lifecycle) or for routing a flagged finding to
  an approver (legal-peripherals-contract-escalation).
license: MIT
tags: [legal-peripherals, commercial, contract-review, nda, msa, saas, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---

# Legal Peripherals — Contract Review (NDA / Vendor / SaaS-MSA)

Grounded in `domain_commercial.ttl`'s `:Contract` hierarchy
(`:NDAAgreement`, `:VendorAgreement`, `:MSAAgreement`) and its
`:requiresAttestation` cross-link into the compliance suite.

## When to use
- Any inbound NDA, vendor agreement, or SaaS subscription/MSA needs a
  playbook review before signature.
- Fast triage of inbound NDAs into GREEN / YELLOW / RED so lawyer time only
  goes to the ones that need it.

## When NOT to use
- Tracking a contract's amendment history or renewal/cancel-by deadline →
  `legal-peripherals-contract-lifecycle`.
- Routing a flagged finding to the right approver, or a stakeholder summary →
  `legal-peripherals-contract-escalation`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL`
for `legal_compliance_lookup` when the contract touches classified data
(PHI/PII/PCI/FinancialData).

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `dataclass_lookup` | If the contract handles PHI/PII/PCI/FinancialData, resolve the Regulation(s) + required Attestation it triggers |
| `legal_compliance_lookup` | `regulation_detail` | Pull the specific Obligation (e.g. HIPAA's BAA obligation) the Attestation satisfies |

## Recipe
1. **Identify the type** from the document's title/structure — NDA, vendor
   agreement, or SaaS/MSA — and route to that review's focus:
   - **NDA**: mutual vs. one-way, term, residuals clause, injunctive-relief
     carve-out.
   - **Vendor agreement**: liability cap, indemnification, IP assignment,
     data-handling terms, termination-for-convenience.
   - **SaaS/MSA**: auto-renewal mechanics, price-escalation caps, SLA/uptime
     commitment, data-processing terms, subprocessor list.
2. **Data-classification check** — if the agreement will process PHI, PII,
   PCI, or financial data, resolve what that triggers:
   ```
   legal_compliance_lookup(action="dataclass_lookup", data_class="PHI")
   ```
   A PHI-handling vendor agreement needs a signed BAA before go-live — mirror
   `domain_commercial.ttl`'s `:ExamplePHIVendorAgreement` example
   (`:classifiedAs :PHI`, `:governedBy :HIPAA`,
   `:requiresAttestation :HIPAABusinessAssociateAgreement`).
3. **Rate GREEN/YELLOW/RED** against the team's risk posture and produce the
   deviation list — each deviation typed as a `:ContractReviewFinding`
   (`domain_commercial.ttl`) `:deviatesFromClause` the playbook clause it
   departs from.

## KG grounding
Every reviewed Contract is typed (`:NDAAgreement`/`:VendorAgreement`/
`:MSAAgreement`), and a data-classified Contract resolves straight to the
Regulation + Attestation it must satisfy — the same join a compliance gate
performs, so "which of our vendor agreements still need a signed BAA" is a
graph query.

## Gotchas
- Never assert an Attestation exists — check whether the signed BAA/DPA is
  actually on file; the ontology models what's REQUIRED, not what's DONE.
- GREEN/YELLOW/RED is a triage aid, not a substitute for attorney sign-off on
  RED-rated (or any escalated) findings.

## Related
- `legal-peripherals-contract-lifecycle` — amendment history + renewal tracking.
- `legal-peripherals-contract-escalation` — routing + stakeholder summary.
- `legal-peripherals-privacy-agreement-review` — a DPA specifically.
