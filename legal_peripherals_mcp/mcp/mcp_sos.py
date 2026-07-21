"""CONCEPT:LP-OS.governance.legal Secretary of State (SOS) business-entity lookup.

Backed by the OpenCorporates API (https://api.opencorporates.com) — a real,
documented company-registry aggregator covering US state Secretary-of-State
filings via ``us_<state>`` jurisdiction codes. Lookups require an API token
(``OPENCORPORATES_API_TOKEN``); without one the tool reports that no data source
is configured and returns NO fabricated record.
"""

import asyncio
import os

import requests
from agent_utilities.base_utilities import get_logger, to_boolean

logger = get_logger(__name__)

# Maximum time (seconds) for any SOS lookup before timeout.
SOS_TIMEOUT_SECONDS = int(os.getenv("SOS_TIMEOUT_SECONDS", "30"))

# OpenCorporates API base (overridable for self-hosted/proxy deployments).
OPENCORPORATES_BASE_URL = os.getenv(
    "OPENCORPORATES_BASE_URL", "https://api.opencorporates.com/v0.4"
).rstrip("/")

# Valid US state and territory abbreviations
_VALID_STATES = frozenset(
    {
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "DC",
        "PR",
        "VI",
        "GU",
        "AS",
        "MP",
    }
)


class SOSLookupError(Exception):
    """Raised when a Secretary of State entity lookup fails."""


def _maybe_ingest_entities(companies: list[dict]) -> None:
    """Default-on authoritative native ingestion of SOS company records.

    Pushes each looked-up business entity into the epistemic-graph as a
    ``:BusinessEntity`` node. Disable with ``LEGAL_KG_INGEST=false``. When enabled,
    native ingestion failures propagate.
    """
    if not companies or not to_boolean(os.getenv("LEGAL_KG_INGEST", "true")):
        return
    from legal_peripherals_mcp.kg_ingest import ingest_sos_entities

    ingest_sos_entities(companies)


def _validate_inputs(state: str, entity_name: str) -> tuple[str, str]:
    """Validate and normalise SOS lookup inputs.

    Raises:
        SOSLookupError: If inputs are invalid.
    """
    state_upper = state.strip().upper()
    entity_name_clean = entity_name.strip()

    if state_upper not in _VALID_STATES:
        raise SOSLookupError(
            f"Invalid state abbreviation: '{state}'. Must be a valid US state or territory code."
        )
    if not entity_name_clean:
        raise SOSLookupError("Entity name must not be empty.")
    if len(entity_name_clean) > 500:
        raise SOSLookupError(
            f"Entity name too long ({len(entity_name_clean)} chars). Max 500."
        )

    return state_upper, entity_name_clean


async def handle_sos_lookup(
    state: str,
    entity_name: str,
    entity_id: str | None = None,
    client=None,
    ctx=None,
) -> str:
    """Perform Secretary of State entity lookup with specific state scrapers and a general 50-state fallback."""
    try:
        state_upper, entity_name_clean = _validate_inputs(state, entity_name)
    except SOSLookupError as exc:
        logger.warning("Operation failed: error_type=%s", type(exc).__name__)
        return "Error: invalid entity lookup parameters"

    if ctx:
        await ctx.info("Initiating configured entity lookup")

    try:
        return await asyncio.wait_for(
            _do_lookup(state_upper, entity_name_clean, entity_id, ctx),
            timeout=SOS_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("Entity lookup timed out")
        return "Error: entity lookup timed out"
    except Exception as exc:
        logger.error("Entity lookup failed: error_type=%s", type(exc).__name__)
        return "Error: entity lookup failed"


def _jurisdiction_code(state_upper: str) -> str:
    """Map a US state/territory code to an OpenCorporates jurisdiction code."""
    return f"us_{state_upper.lower()}"


def _format_company(state_upper: str, company: dict) -> str:
    """Render a single OpenCorporates company record as a readable summary."""
    fields = [
        ("Entity Name", company.get("name")),
        ("Jurisdiction", company.get("jurisdiction_code")),
        ("Company Number", company.get("company_number")),
        ("Entity Type", company.get("company_type")),
        ("Status", company.get("current_status")),
        ("Incorporation Date", company.get("incorporation_date")),
        ("Dissolution Date", company.get("dissolution_date")),
        ("Registered Address", company.get("registered_address_in_full")),
        ("Source", company.get("opencorporates_url")),
    ]
    body = "\n".join(f"{label}: {value}" for label, value in fields if value)
    return (
        f"--- Secretary of State Lookup ({state_upper}) — via OpenCorporates ---\n"
        f"{body}"
    )


def _http_get(url: str, params: dict) -> dict:
    """Blocking GET helper run off the event loop via ``asyncio.to_thread``."""
    resp = requests.get(url, params=params, timeout=SOS_TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp.json()


async def _do_lookup(
    state_upper: str,
    entity_name_clean: str,
    entity_id: str | None,
    ctx=None,
) -> str:
    """Core lookup logic, separated for timeout wrapping.

    Performs a real OpenCorporates query for the state's jurisdiction. Returns an
    honest "not configured" notice (and no fabricated record) when no API token is
    available; raises :class:`SOSLookupError` on a failed request so the caller can
    surface a truthful error.
    """
    token = os.getenv("OPENCORPORATES_API_TOKEN", "").strip()
    if not token:
        return (
            f"SOS lookup unavailable for {state_upper}: no business-registry data "
            f"source is configured. Set OPENCORPORATES_API_TOKEN to enable real "
            f"Secretary-of-State entity lookups "
            f"(https://opencorporates.com/api_accounts/new). No record was returned "
            f"because none was fabricated."
        )

    jurisdiction = _jurisdiction_code(state_upper)
    if ctx:
        await ctx.info(
            f"Querying OpenCorporates jurisdiction={jurisdiction} for "
            f"entity={entity_name_clean!r} id={entity_id!r}"
        )

    try:
        # A specific company number → direct fetch; otherwise a name search.
        if entity_id:
            data = await asyncio.to_thread(
                _http_get,
                f"{OPENCORPORATES_BASE_URL}/companies/{jurisdiction}/{entity_id}",
                {"api_token": token},
            )
            company = (data.get("results") or {}).get("company")
            if not company:
                return (
                    f"No Secretary-of-State record found in {state_upper} for "
                    f"company number {entity_id}."
                )
            _maybe_ingest_entities([company])
            return _format_company(state_upper, company)

        data = await asyncio.to_thread(
            _http_get,
            f"{OPENCORPORATES_BASE_URL}/companies/search",
            {
                "q": entity_name_clean,
                "jurisdiction_code": jurisdiction,
                "api_token": token,
            },
        )
    except requests.RequestException as exc:
        raise SOSLookupError(
            f"OpenCorporates request failed for {state_upper}: {type(exc).__name__}"
        ) from exc

    companies = (data.get("results") or {}).get("companies") or []
    if not companies:
        return (
            f"No Secretary-of-State record found for '{entity_name_clean}' in "
            f"{state_upper}."
        )

    # Each search hit is wrapped as {"company": {...}}.
    hits = [
        hit["company"]
        for hit in companies
        if isinstance(hit, dict) and hit.get("company")
    ]
    _maybe_ingest_entities(hits)
    rendered = [_format_company(state_upper, company) for company in hits]
    header = (
        f"Found {len(rendered)} Secretary-of-State match(es) for "
        f"'{entity_name_clean}' in {state_upper}:\n\n"
    )
    return header + "\n\n".join(rendered)
