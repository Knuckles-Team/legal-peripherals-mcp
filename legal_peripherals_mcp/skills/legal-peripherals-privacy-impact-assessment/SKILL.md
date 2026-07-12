---
name: legal-peripherals-privacy-impact-assessment
skill_type: skill
description: >-
  Triage whether a new processing activity needs a PIA, a mandatory GDPR
  DPIA, or can proceed as-is, then generate the assessment in house format —
  grounded in the privacy domain ontology's ProcessingActivity and
  PrivacyImpactAssessment classes (the latter a subclass of the compliance
  suite's Assessment). Use when a new feature/
  product/processing activity needs privacy review before launch. Do NOT use
  for a DSAR (legal-peripherals-dsar-response) or a DPA review
  (legal-peripherals-privacy-agreement-review).
license: MIT
tags: [legal-peripherals, privacy, pia, dpia, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---

# Legal Peripherals — Privacy Impact Assessment (PIA / DPIA)

Grounded in `domain_privacy.ttl`'s `:ProcessingActivity`
(`:processesDataClass`) and `:PrivacyImpactAssessment` (declared
`rdfs:subClassOf` the compliance suite's `:Assessment`,
`:assessesActivity`).

## When to use
- A new feature, product, or processing activity needs a privacy
  determination before launch: no review needed, a PIA, or a mandatory GDPR
  DPIA.
- Generating the actual assessment document in house format once triage says
  one is needed.

## When NOT to use
- A data-subject rights request → `legal-peripherals-dsar-response`.
- Reviewing a DPA with a vendor/processor → `legal-peripherals-privacy-agreement-review`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL`
for `legal_compliance_lookup`.

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `dataclass_lookup` | Which Regulation(s) does this activity's data classification trigger? |
| `legal_compliance_lookup` | `regulation_detail` | Pull GDPR's DPIA obligation specifically, to test the mandatory-DPIA threshold |

## Recipe
1. **Classify the data** the activity touches (PII, PHI, financial, ...) and
   resolve what regime(s) apply:
   ```
   legal_compliance_lookup(action="dataclass_lookup", data_class="PII")
   ```
2. **Triage against the DPIA threshold** — GDPR Art. 35 requires a DPIA for
   processing "likely to result in high risk" (large-scale profiling,
   systematic monitoring, special-category data at scale, new technology).
   Pull the obligation for the exact trigger language:
   ```
   legal_compliance_lookup(action="regulation_detail", regulation="GDPR")
   ```
   Below that threshold but still touching PII, a house-format PIA
   (lighter-weight) may suffice instead; genuinely low-risk activities need
   neither — say so rather than defaulting to "assessment required."
3. **Generate the assessment** — type the activity as a `:ProcessingActivity`
   `:processesDataClass` the classification(s) involved, then the assessment
   itself as a `:PrivacyImpactAssessment` `:assessesActivity` it, following
   the house PIA structure (purpose, data flows, legal basis, risk,
   mitigations, residual-risk sign-off).

## KG grounding
`:PrivacyImpactAssessment` reuses (subclasses) the compliance suite's
`:Assessment` rather than a bespoke class — so a fleet-wide "every open
Assessment across every domain" query already includes PIAs alongside HIPAA
risk assessments and AML independent tests.

## Gotchas
- Don't over-trigger DPIAs for genuinely low-risk activities — that dilutes
  the signal for the ones that truly need deep review.
- A PIA/DPIA is a point-in-time assessment — a materially changed processing
  activity needs a new (or updated) one, not a stale reference to the
  original.

## Related
- `legal-peripherals-dsar-response` — the data-subject-rights side.
- `legal-peripherals-privacy-agreement-review` — the DPA/vendor side.
- `legal-peripherals-privacy-gap-monitor` — ongoing drift monitoring.
