# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Added tool suite toggles (`SOSTOOL`, `EINTOOL`, `STATUTETOOL`) to allow dynamic FastMCP tool registration.
- Added IRS filing off-hours override toggle (`BYPASS_IRS_FILING_HOURS`) for local testing.
- Documented new environment variables in `.env.example`.

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
