"""Main FastMCP server and tool registration."""

import os
import sys
from typing import Any

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server, load_config
from fastmcp.utilities.logging import get_logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from legal_peripherals_mcp.auth import get_client
from legal_peripherals_mcp.mcp.mcp_ein import handle_ein_draft
from legal_peripherals_mcp.mcp.mcp_sos import handle_sos_lookup
from legal_peripherals_mcp.mcp.mcp_statute import handle_statute_rules

__version__ = "0.15.0"
logger = get_logger(name="legal_peripherals_mcp")


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

    # Tool registration
    if to_boolean(os.getenv("SOSTOOL", "True")):

        @mcp.tool()
        async def sos_entity_lookup(
            state: str, entity_name: str, entity_id: str | None = None, ctx: Any = None
        ) -> str:
            """Perform Secretary of State entity lookup across 50 states (scrapers for TX, DE, WY, NV, resilient fallback for others)."""
            client = get_client()
            return await handle_sos_lookup(
                state, entity_name, entity_id, client=client, ctx=ctx
            )

    if to_boolean(os.getenv("EINTOOL", "True")):

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

    if to_boolean(os.getenv("STATUTETOOL", "True")):

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
