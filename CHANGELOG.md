# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Added tool suite toggles (`SOSTOOL`, `EINTOOL`, `STATUTETOOL`) to allow dynamic FastMCP tool registration.
- Added IRS filing off-hours override toggle (`BYPASS_IRS_FILING_HOURS`) for local testing.
- Documented new environment variables in `.env.example`.
- **Legal practice-area domain suite**: 6 native OWL/RDF domain ontology modules
  (`domain_regulatory.ttl`, `domain_employment.ttl`, `domain_commercial.ttl`,
  `domain_privacy.ttl`, `domain_corporate.ttl`, `domain_litigation.ttl`) modeling
  the regulatory, employment, commercial, privacy, corporate, and litigation
  practice areas, cross-linked into the existing FLSA/HIPAA/LLC compliance
  modules and declaring GDPR + CCPA as new `:Regulation` individuals. New
  KG-native `legal_compliance_lookup` action-routed MCP tool (`COMPLIANCETOOL`)
  querying the bundled ontology suite directly. 18 new SKILL.md skills across
  those practice areas, including two cross-domain skills
  (`legal-peripherals-compliance-watch`, `legal-peripherals-entity-compliance-tracker`)
  that provide a single KG-native deadline sweep and close the loop on this
  package's existing entity-formation tools
  (CONCEPT:LP-OS.governance.legal-domain-suite, CONCEPT:LP-OS.governance.legal-compliance-kb).

### Changed
- `sos_entity_lookup` now queries a real company-registry backend (OpenCorporates, `us_<state>` jurisdictions) via `OPENCORPORATES_API_TOKEN` — supporting name search and direct fetch by `entity_id` (company number) — returning genuine fields with a verifiable `opencorporates_url` (CONCEPT:LEGAL-001).

### Security
- Stopped fabricating Secretary-of-State records: `sos_entity_lookup` no longer invents "Active / Good Standing" statuses, file numbers, or registered agents (including the simulated 46-state fallback crawler). Without a configured API token the lookup honestly reports unavailable and fabricates no record; request failures surface a truthful error (CONCEPT:LEGAL-001).

## [0.15.0] - 2026-05-25
### Added
- Initial implementation of the Legal Peripherals MCP Server.
- Secretary of State crawlers for TX, DE, WY, NV, and fallbacks for all 50 states.
- Form SS-4 EIN drafting and off-hours filing scheduler.
- Statute catalog and charter templates lookup.
- FastMCP dynamic action-routed tools.
