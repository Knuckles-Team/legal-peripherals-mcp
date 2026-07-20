# Concept Registry — Legal Peripherals MCP

> **Prefix**: `CONCEPT:LEGAL-*`
> **Bridge**: `CONCEPT:AU-ECO.messaging.native-backend-abstraction` (Unified Toolkit Ingestion)

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:LP-OS.governance.legal` | Secretary of State Crawlers | Dynamic business entity lookup & verifications across 50 states |
| `CONCEPT:LP-OS.governance.legal-2` | IRS EIN & Off-Hours Filing | SS-4 PDF drafting and scheduling compliance operations |
| `CONCEPT:LP-OS.identity.legal` | Statutes & Charter Templates | LLC/corporate filing guidelines and dynamic template lookups |
| `CONCEPT:LP-OS.governance.compliance-ontology-suite` | Regulatory/Legal Compliance Ontology Suite | Shared compliance upper ontology (Regulation/Obligation/Control/ComplianceRequirement/Penalty/Sector/ReportingRequirement/ComplianceGate/Assessment/Attestation/RegulatoryAuthority) plus per-framework modules (HIPAA, BSA/AML+SARs, OCC, Dodd-Frank, CFPB, FLSA, Taxation, LLC formation/governance), federated into epistemic-graph via the ontology provider and cross-linked to the shared infra/asset ontology by data classification |
| `CONCEPT:LP-OS.governance.legal-domain-suite` | Legal Practice-Area Domain Ontology Suite | `domain_regulatory.ttl` / `domain_employment.ttl` / `domain_commercial.ttl` / `domain_privacy.ttl` / `domain_corporate.ttl` / `domain_litigation.ttl` — one broader artifact/process module per legal practice area, each importing compliance.ttl + legal.ttl and cross-linked into existing FLSA/HIPAA/LLC individuals rather than floating disconnected; declares GDPR + CCPA as new :Regulation individuals |
| `CONCEPT:LP-OS.governance.legal-compliance-kb` | Compliance Ontology Lookup Tool | `legal_compliance_lookup` action-routed MCP tool (`compliance_kb.py` + `mcp/mcp_compliance.py`) answering structured queries against the bundled ontology suite — no external API, no fabrication, honest degrade without `rdflib` (`[ontology]` extra) |
