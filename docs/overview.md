# Architectural Overview

The Legal Peripherals MCP package leverages FastMCP to expose three core domains to LLM agents:

1. **Secretary of State (SOS) Crawlers**:
   - Uses Playwright to query state business registry pages dynamically.
   - Provides pre-configured crawling pipelines for TX, DE, NV, and WY.
   - Gracefully falls back to simulated/mocked search structures for all 50 states to guarantee 100% state coverage.

2. **EIN (Form SS-4) & Scheduling**:
   - Drafts the IRS Form SS-4 fields as structured outputs.
   - Automatically detects current IRS working hours (Mon-Fri, 7am - 10pm EST).
   - Schedules/queues submissions during off-hours, providing tracking IDs.

3. **Statute Catalog**:
   - Contains precise corporate / LLC statutes across all 50 US states.
   - Maps standard organizational charter templates for drafting company filings.
