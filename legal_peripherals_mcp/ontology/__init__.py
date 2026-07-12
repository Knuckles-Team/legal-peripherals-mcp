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
  comment for the pattern to follow when adding more (GDPR, SOX, PCI-DSS,
  FedRAMP/NIST, GLBA, ...).
"""
