"""Main FastMCP server and tool registration."""

import asyncio
import sys
from typing import Any

from agent_utilities.core.config import load_config
from agent_utilities.mcp.server_factory import create_mcp_server
from agent_utilities.mcp.verbose_tools import register_tool_surface
from fastmcp.utilities.logging import get_logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from legal_peripherals_mcp.api_client import Api
from legal_peripherals_mcp.auth import get_client
from legal_peripherals_mcp.mcp.mcp_compliance import handle_compliance_lookup
from legal_peripherals_mcp.mcp.mcp_ein import handle_ein_draft
from legal_peripherals_mcp.mcp.mcp_sos import handle_sos_lookup
from legal_peripherals_mcp.mcp.mcp_statute import handle_statute_rules

__version__ = "2.0.0"
logger = get_logger(name="legal_peripherals_mcp")


def register_sos_tools(mcp: Any) -> None:
    """Register the Secretary of State entity-lookup tool (tag: sos)."""

    @mcp.tool()
    async def sos_entity_lookup(
        state: str, entity_name: str, entity_id: str | None = None, ctx: Any = None
    ) -> str:
        """Perform Secretary of State entity lookup across 50 states (scrapers for TX, DE, WY, NV, resilient fallback for others)."""
        client = get_client()
        return await handle_sos_lookup(
            state, entity_name, entity_id, client=client, ctx=ctx
        )


def register_ein_tools(mcp: Any) -> None:
    """Register the IRS EIN drafting/filing tool (tag: ein)."""

    @mcp.tool()
    async def draft_ein_form(
        legal_name: str,
        trade_name: str = "",
        responsible_party_ssn: str = "",
        responsible_party_name: str = "",
        business_type: str = "LLC",
        mailing_address: str = "",
        county_state: str = "",
        reason_for_applying: str = "Started new business",
        first_date_wages_paid: str = "",
        max_employees: int = 0,
        closing_month_tax_year: str = "December",
        ctx: Any = None,
    ) -> str:
        """Draft IRS Form SS-4 and schedule EIN filing with off-hours compliance (Mon-Fri 7:00 AM - 10:00 PM EST)."""
        client = get_client()
        return await handle_ein_draft(
            legal_name=legal_name,
            trade_name=trade_name,
            responsible_party_ssn=responsible_party_ssn,
            responsible_party_name=responsible_party_name,
            business_type=business_type,
            mailing_address=mailing_address,
            county_state=county_state,
            reason_for_applying=reason_for_applying,
            first_date_wages_paid=first_date_wages_paid,
            max_employees=max_employees,
            closing_month_tax_year=closing_month_tax_year,
            client=client,
            ctx=ctx,
        )


def register_statute_tools(mcp: Any) -> None:
    """Register the state statute / charter-template lookup tool (tag: statute)."""

    @mcp.tool()
    async def lookup_statute_rules(
        state: str, entity_type: str, topic: str, ctx: Any = None
    ) -> str:
        """Query state statutory default rules and retrieve corporate/LLC charter templates."""
        client = get_client()
        return await handle_statute_rules(
            state=state,
            entity_type=entity_type,
            topic=topic,
            client=client,
            ctx=ctx,
        )


def register_ingest_tools(mcp: Any) -> None:
    """Register Wire-First native KG ingestion tools (tag: ingest)."""

    @mcp.tool()
    async def legal_ingest_sos_entities(
        state: str,
        entity_name: str,
        limit: int = 10,
        ctx: Any = None,
    ) -> dict:
        """Look up Secretary-of-State business entities and ingest them into the KG.

        Lists real OpenCorporates company records for ``state`` + ``entity_name`` and
        pushes them into epistemic-graph as typed ``:BusinessEntity`` (+ ``:Jurisdiction``
        / ``:incorporatedIn``) nodes via the fast engine client. Best-effort: returns
        ``{"ingested": None}`` when no engine or no OPENCORPORATES_API_TOKEN is set.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from legal_peripherals_mcp.kg_ingest import (
            ingest_sos_entities,
            search_companies,
        )

        entities = await asyncio.to_thread(
            search_companies, state, entity_name, limit=limit
        )
        if ctx:
            await ctx.info(f"Fetched {len(entities)} SOS entities for ingestion")
        result = ingest_sos_entities(entities)
        return {"listed": len(entities), "entities": entities, "ingested": result}

    @mcp.tool()
    async def legal_ingest_filing_file(
        file_path: str,
        filing_type: str = "legal_document",
        name: str = "",
        ctx: Any = None,
    ) -> dict:
        """Store a drafted filing file (e.g. drafts/*.txt) as a blob + :MediaAsset in the KG.

        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        CONCEPT:AU-KG.ingest.list-durable-media.
        """
        from legal_peripherals_mcp.kg_media import ingest_filing_file

        result = await asyncio.to_thread(
            ingest_filing_file, file_path, filing_type=filing_type, name=name
        )
        return {"file": file_path, "ingested": result}


def register_compliance_tools(mcp: Any) -> None:
    """Register the action-routed compliance-ontology lookup tool (tag: compliance)."""

    @mcp.tool()
    async def legal_compliance_lookup(
        action: str,
        regulation: str = "",
        sector: str = "",
        data_class: str = "",
        data_classes: str = "",
        ctx: Any = None,
    ) -> dict:
        """Query the bundled compliance + domain ontology suite (KG-native, no external API).

        Actions: ``list_domains``, ``list_regulations`` (optional ``sector``/
        ``data_class``), ``regulation_detail`` (needs ``regulation``), ``sector_lookup``
        (needs ``sector``), ``dataclass_lookup`` (needs ``data_class``),
        ``gate_requirements`` (needs comma-separated ``data_classes``, e.g. "PHI,PII")
        — resolves the applicable Regulation(s) and required Control(s) the way a
        ComplianceGate would for a governed entity carrying those data classifications.
        """
        return await handle_compliance_lookup(
            action=action,
            regulation=regulation,
            sector=sector,
            data_class=data_class,
            data_classes=data_classes,
            ctx=ctx,
        )


def get_mcp_instance() -> Any:
    load_config()
    args, mcp, middlewares = create_mcp_server(
        name="Legal Peripherals MCP",
        version=__version__,
        instructions="Legal Peripherals MCP Server - Automate state registrations and filing compliance.",
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    registered_tags = register_tool_surface(
        mcp,
        client_cls=Api,
        get_client=get_client,
        service="legal-peripherals-mcp",
        tools_module=sys.modules[__name__],
    )
    logger.info("Registered condensed tool surfaces: count=%d", len(registered_tags))

    for mw in middlewares:
        mcp.add_middleware(mw)
    return mcp, args, middlewares


def mcp_server() -> None:
    mcp, args, _middlewares = get_mcp_instance()
    print(f"Legal Peripherals MCP v{__version__}", file=sys.stderr)
    if args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    mcp_server()
