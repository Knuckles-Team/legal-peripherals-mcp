"""CONCEPT:LP-OS.governance.legal-2 Form SS-4 EIN preparer and off-hours filing scheduler."""

import asyncio
import os
import re
import zoneinfo
from datetime import datetime, timedelta

from agent_utilities.base_utilities import get_logger, to_boolean

logger = get_logger(__name__)

# Maximum time (seconds) for EIN draft operations.
EIN_TIMEOUT_SECONDS = int(os.getenv("EIN_TIMEOUT_SECONDS", "30"))

# Valid business types accepted by IRS Form SS-4.
VALID_BUSINESS_TYPES = frozenset(
    {
        "LLC",
        "Corporation",
        "S Corporation",
        "Partnership",
        "Sole Proprietor",
        "Trust",
        "Estate",
        "Non-Profit",
        "Church",
        "Government",
        "Other",
    }
)


class EINDraftError(Exception):
    """Raised when EIN form drafting fails validation."""


def _validate_ein_inputs(
    legal_name: str,
    business_type: str,
    responsible_party_ssn: str,
    max_employees: int,
) -> None:
    """Validate EIN form inputs.

    Raises:
        EINDraftError: If any input is invalid.
    """
    if not legal_name or not legal_name.strip():
        raise EINDraftError("Legal name is required and must not be empty.")
    if len(legal_name.strip()) > 500:
        raise EINDraftError(
            f"Legal name too long ({len(legal_name.strip())} chars). Max 500."
        )
    if business_type not in VALID_BUSINESS_TYPES:
        raise EINDraftError(
            f"Invalid business type: '{business_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_BUSINESS_TYPES))}."
        )
    if responsible_party_ssn and not re.match(
        r"^\d{3}-?\d{2}-?\d{4}$", responsible_party_ssn
    ):
        raise EINDraftError(
            f"Invalid SSN format: '{responsible_party_ssn}'. Expected NNN-NN-NNNN."
        )
    if max_employees < 0:
        raise EINDraftError(f"max_employees must be >= 0, got {max_employees}.")


def is_irs_active(dt: datetime) -> bool:
    """Check if the current time is within active IRS filing hours (Mon-Fri 7:00 AM - 10:00 PM EST)."""
    # Convert to US/Eastern timezone
    eastern = zoneinfo.ZoneInfo("America/New_York")
    dt_est = dt.astimezone(eastern)

    # Monday to Friday (0 to 4)
    if dt_est.weekday() > 4:
        return False

    # Hour between 7:00 AM (inclusive) and 10:00 PM (exclusive, or up to 10:00 PM)
    hour = dt_est.hour
    if 7 <= hour < 22:
        return True

    return False


def get_next_filing_time(dt: datetime) -> datetime:
    """Calculate the next active IRS filing hour timestamp."""
    eastern = zoneinfo.ZoneInfo("America/New_York")
    dt_est = dt.astimezone(eastern)

    # Start with today at 7:00 AM EST
    candidate = dt_est.replace(hour=7, minute=0, second=0, microsecond=0)

    # Loop to find the next valid weekday at 7:00 AM (bounded to 10 days max)
    for _ in range(10):
        if candidate > dt_est and candidate.weekday() <= 4:
            return candidate
        candidate += timedelta(days=1)

    # Fallback: should never reach here
    return candidate


async def handle_ein_draft(
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
    client=None,
    ctx=None,
) -> str:
    """Draft IRS Form SS-4 and schedule filing based on IRS operational hours."""
    # Input validation
    try:
        _validate_ein_inputs(
            legal_name, business_type, responsible_party_ssn, max_employees
        )
    except EINDraftError as exc:
        logger.warning("EIN draft validation failed: %s", exc)
        return f"Error: {exc}"

    try:
        return await asyncio.wait_for(
            _do_ein_draft(
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
                ctx=ctx,
            ),
            timeout=EIN_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        msg = f"EIN draft timed out after {EIN_TIMEOUT_SECONDS}s for '{legal_name}'."
        logger.error(msg)
        return f"Error: {msg}"
    except Exception as exc:
        msg = f"EIN draft failed for '{legal_name}': {exc}"
        logger.exception(msg)
        return f"Error: {msg}"


async def _do_ein_draft(
    legal_name: str,
    trade_name: str,
    responsible_party_ssn: str,
    responsible_party_name: str,
    business_type: str,
    mailing_address: str,
    county_state: str,
    reason_for_applying: str,
    first_date_wages_paid: str,
    max_employees: int,
    closing_month_tax_year: str,
    ctx=None,
) -> str:
    """Core EIN draft logic, separated for timeout wrapping."""
    now = datetime.now(zoneinfo.ZoneInfo("UTC"))
    active = is_irs_active(now)

    bypass = to_boolean(os.getenv("BYPASS_IRS_FILING_HOURS", "False"))
    if bypass:
        active = True

    if ctx:
        await ctx.info(
            f"Form SS-4 drafting request for {legal_name}. Active hours check: {active} (bypass: {bypass})"
        )

    # Mask SSN in output for security
    ssn_display = (
        f"***-**-{responsible_party_ssn[-4:]}"
        if responsible_party_ssn and len(responsible_party_ssn) >= 4
        else "N/A"
    )

    # Generate draft content
    draft_pdf_info = (
        f"=== Form SS-4 Draft (Application for Employer Identification Number) ===\n"
        f"Document Type: SS-4 draft\n"
        f"1. Legal Name: {legal_name}\n"
        f"2. Trade Name: {trade_name or 'N/A'}\n"
        f"3. Responsible Party: {responsible_party_name} (SSN: {ssn_display})\n"
        f"4. Type of Entity: {business_type}\n"
        f"5. Mailing Address: {mailing_address}\n"
        f"6. County and State: {county_state}\n"
        f"7. Reason for Applying: {reason_for_applying}\n"
        f"8. First Date Wages Paid: {first_date_wages_paid or 'N/A'}\n"
        f"9. Max Employees: {max_employees}\n"
        f"10. Closing Month of Tax Year: {closing_month_tax_year}\n"
    )

    if active:
        status_msg = (
            f"Filing Status: FILING IMMEDIATELY\n"
            f"Filing Timestamp: {now.astimezone(zoneinfo.ZoneInfo('America/New_York')).isoformat()}\n"
            f"Filing Mode: Active Hours Direct Electronic Submit."
        )
    else:
        next_time = get_next_filing_time(now)
        status_msg = (
            f"Filing Status: QUEUED FOR SCHEDULING (IRS Off-Hours Compliance)\n"
            f"Scheduled Filing Time: {next_time.isoformat()}\n"
            f"Filing Mode: Off-Hours Deferred Queue."
        )

    rendered = f"{draft_pdf_info}\n----------------------------------------\n{status_msg}"
    _maybe_ingest_ein(
        legal_name=legal_name,
        trade_name=trade_name,
        business_type=business_type,
        county_state=county_state,
        reason_for_applying=reason_for_applying,
        closing_month_tax_year=closing_month_tax_year,
        filing_status="filed" if active else "queued",
        draft_text=rendered,
    )
    return rendered


def _maybe_ingest_ein(**kwargs) -> None:
    """Default-on native ingestion of the drafted SS-4 (best-effort, no-op safe).

    Pushes the draft into the epistemic-graph as an ``:EINApplication`` node linked to
    its ``:BusinessEntity``. Disable with ``LEGAL_KG_INGEST=false``. Any failure is
    swallowed so drafting is never impacted.
    """
    if not to_boolean(os.getenv("LEGAL_KG_INGEST", "true")):
        return
    try:
        from legal_peripherals_mcp.kg_ingest import ingest_ein_application

        ingest_ein_application(kwargs.pop("legal_name"), **kwargs)
    except Exception as exc:  # noqa: BLE001 — ingestion is best-effort
        logger.debug("KG ingest of EIN application skipped: %s", exc)
