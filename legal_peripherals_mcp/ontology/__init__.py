"""Legal Peripherals ontology contribution (CONCEPT:AU-KG.ontology.package-federation-migration).

Data-only subpackage: it carries every ``*.ttl`` module below, which the
agent-utilities hub federates in via the ``agent_utilities.ontology_providers``
entry-point (the hub loader globs every ``*.ttl`` in this directory — dropping a
new file here is enough, no code change needed). It holds no business logic and
no heavy imports so the hub can resolve it cheaply.

Modules carried:

- ``legal.ttl`` (``http://knuckles.team/kg/legal``) — the package's general legal
  domain ontology (statutes, case law, contracts, trusts, IP, business entities).
- ``compliance.ttl`` (``http://knuckles.team/kg/legal-compliance``,
  CONCEPT:LP-OS.governance.compliance-ontology-suite) — the regulatory/legal
  compliance upper ontology: Regulation/Obligation/Control/ComplianceRequirement/
  Penalty/Sector/ReportingRequirement/ComplianceGate/Assessment/Attestation/
  RegulatoryAuthority, cross-linked to the shared infra/asset ontology via
  ``:governedBy`` / ``:classifiedAs`` / ``:appliesToDataClass`` so a service or
  asset's data classification resolves the regulation(s) that govern it.
- ``compliance_hipaa.ttl``, ``compliance_bsa_aml.ttl``, ``compliance_occ.ttl``,
  ``compliance_dodd_frank.ttl``, ``compliance_cfpb.ttl``, ``compliance_flsa.ttl``,
  ``compliance_taxation.ttl``, ``compliance_llc.ttl`` — one module per regulatory
  framework, each importing ``compliance.ttl``. See ``compliance.ttl``'s header
  comment for the pattern to follow when adding more (SOX, PCI-DSS, FedRAMP/NIST,
  GLBA, ...).
- ``domain_regulatory.ttl``, ``domain_employment.ttl``, ``domain_commercial.ttl``,
  ``domain_privacy.ttl``, ``domain_corporate.ttl``, ``domain_litigation.ttl`` —
  legal practice-area domain suite (CONCEPT:LP-OS.governance.legal-domain-suite):
  one broader domain module per legal practice area, each importing
  ``compliance.ttl`` + ``legal.ttl``. Unlike the single-Regulation
  ``compliance_<framework>.ttl`` modules above, these carry a domain's *artifact*
  and *process* vocabulary — regulatory-change/enforcement lifecycle, employment
  contracts/investigations/leave, commercial contract types/renewals/escalation,
  privacy DSARs/DPAs/PIAs (declaring GDPR + CCPA as :Regulation individuals),
  corporate governance/diligence/entity-compliance, and litigation
  matters/holds/claim charts — cross-linked into the existing compliance modules
  (e.g. domain_employment.ttl's WorkerClassificationAssessment triggers
  compliance_flsa.ttl's Obligations; domain_commercial.ttl's Contract resolves to
  compliance_hipaa.ttl's BAA Attestation via DataClassification;
  domain_corporate.ttl tracks compliance_llc.ttl's LLCAnnualReportRequirement).
  Queryable through the ``legal_compliance_lookup`` MCP tool
  (``legal_peripherals_mcp/compliance_kb.py``).
"""
