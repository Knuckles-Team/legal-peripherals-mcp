"""CONCEPT:LEGAL-003 Statutory rules and dynamic charter templates lookup."""
import asyncio
import os
import re

from agent_utilities.base_utilities import get_logger

logger = get_logger(__name__)

# Maximum time (seconds) for statute lookups.
STATUTE_TIMEOUT_SECONDS = int(os.getenv("STATUTE_TIMEOUT_SECONDS", "30"))

# Valid US state and territory abbreviations
_VALID_STATES = frozenset({
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "PR", "VI", "GU", "AS", "MP",
})

# Supported entity types (normalised)
VALID_ENTITY_TYPES = frozenset({"LLC", "Corporation"})

STATUTORY_DATABASE = {
    ("DE", "LLC"): {
        "voting": "Under DGCL / LLC Act, voting is based on member percentage interest (majority in interest wins) unless otherwise provided in the Operating Agreement.",
        "indemnification": "Delaware LLC Act Sec. 18-108 allows maximum freedom of contract, enabling broad indemnification of members/managers for any and all claims except willful misconduct or bad faith.",
        "capital_contributions": "Sec. 18-502 states a member is obligated to perform any promise to contribute cash, property, or services, even if unable because of death, disability, or other reason.",
        "template": "=== DELAWARE LLC OPERATING AGREEMENT TEMPLATE ===\nThis Operating Agreement is made by the members...\n1. Formation...\n2. Management: Vested in Managers/Members...\n3. Voting: Majority in Interest..."
    },
    ("DE", "Corporation"): {
        "voting": "Under DGCL Sec. 212, each stockholder is entitled to one vote for each share of capital stock held by such stockholder, unless otherwise provided in the Certificate of Incorporation.",
        "indemnification": "DGCL Sec. 145 permits broad indemnification and advancement of expenses. Mandatory indemnification applies if the director/officer is successful on the merits.",
        "capital_contributions": "DGCL Sec. 152/153 requires the board to determine value of capital contributions, and shares must be fully paid and non-assessable.",
        "template": "=== DELAWARE CERTIFICATE OF INCORPORATION TEMPLATE ===\n1. Name...\n2. Registered Agent...\n3. Purpose...\n4. Authorized Capital Stock: [Number of Shares] at [Par Value]..."
    },
    ("TX", "LLC"): {
        "voting": "Under Texas Business Organizations Code (BOC) Sec. 101.354, decisions are made by a majority of the members' percentage interests unless the company agreement provides otherwise.",
        "indemnification": "BOC Sec. 101.402 permits broad indemnification and advancement of expenses for managers/members.",
        "capital_contributions": "BOC Sec. 101.151 states a promise to make a capital contribution is not enforceable unless it is in writing and signed by the member.",
        "template": "=== TEXAS LLC COMPANY AGREEMENT TEMPLATE ===\nThis Company Agreement...\n1. Formation...\n2. Management: Manager-Managed / Member-Managed...\n3. Voting: Majority of Percentage Interests..."
    },
    ("TX", "Corporation"): {
        "voting": "Under BOC Sec. 21.358, each outstanding share is entitled to one vote on each matter submitted to a vote at a meeting of shareholders.",
        "indemnification": "BOC Chapter 8 allows and regulates indemnification and advancement of expenses for directors and officers.",
        "capital_contributions": "BOC Sec. 21.157 states the board of directors determines the adequacy of consideration received for shares.",
        "template": "=== TEXAS CERTIFICATE OF FORMATION TEMPLATE ===\n1. Entity Name...\n2. Registered Agent & Office...\n3. Board of Directors...\n4. Authorized Shares: [Number of Shares]..."
    },
    ("WY", "LLC"): {
        "voting": "Wyoming LLC Act Sec. 17-29-407: each member has equal vote regardless of ownership percentage unless operating agreement states otherwise.",
        "indemnification": "Wyoming LLC Act Sec. 17-29-408 permits broad indemnification. Members/managers may be indemnified for actions taken in good faith.",
        "capital_contributions": "Sec. 17-29-401 allows capital contributions of cash, property, services, or promissory notes.",
        "template": "=== WYOMING LLC OPERATING AGREEMENT TEMPLATE ===\n1. Formation under Wyoming LLC Act...\n2. Management: Member-Managed / Manager-Managed...\n3. Voting: Per capita or percentage interest per agreement..."
    },
    ("NV", "LLC"): {
        "voting": "Nevada Revised Statutes (NRS) Chapter 86: members vote by percentage interest unless operating agreement provides otherwise.",
        "indemnification": "NRS 86.411 permits indemnification of members and managers. Nevada provides strong personal liability protections.",
        "capital_contributions": "NRS 86.321 permits contributions of tangible/intangible property or services rendered.",
        "template": "=== NEVADA LLC OPERATING AGREEMENT TEMPLATE ===\n1. Formation under NRS Chapter 86...\n2. Management structure...\n3. Voting: Majority of percentage interests..."
    },
}


class StatuteLookupError(Exception):
    """Raised when a statute lookup fails validation."""


def _validate_statute_inputs(state: str, entity_type: str, topic: str) -> tuple[str, str, str]:
    """Validate and normalise statute lookup inputs.

    Raises:
        StatuteLookupError: If inputs are invalid.
    """
    state_upper = state.strip().upper()
    topic_norm = topic.strip().lower()

    if state_upper not in _VALID_STATES:
        raise StatuteLookupError(
            f"Invalid state abbreviation: '{state}'. Must be a valid US state or territory code."
        )

    type_norm = "LLC" if "llc" in entity_type.lower() else "Corporation"

    if not topic_norm:
        raise StatuteLookupError("Topic must not be empty.")
    if len(topic_norm) > 200:
        raise StatuteLookupError(
            f"Topic too long ({len(topic_norm)} chars). Max 200."
        )

    return state_upper, type_norm, topic_norm


async def handle_statute_rules(
    state: str,
    entity_type: str,
    topic: str,
    client=None,
    ctx=None,
) -> str:
    """Query state statutes and retrieve charter templates."""
    try:
        state_upper, type_norm, topic_norm = _validate_statute_inputs(state, entity_type, topic)
    except StatuteLookupError as exc:
        logger.warning("Statute validation failed: %s", exc)
        return f"Error: {exc}"

    if ctx:
        await ctx.info(
            f"Querying statutes for state={state_upper}, entity_type={type_norm}, topic={topic_norm}"
        )

    try:
        return await asyncio.wait_for(
            _do_statute_lookup(state_upper, type_norm, topic_norm),
            timeout=STATUTE_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        msg = f"Statute lookup timed out after {STATUTE_TIMEOUT_SECONDS}s for state={state_upper}."
        logger.error(msg)
        return f"Error: {msg}"
    except Exception as exc:
        msg = f"Statute lookup failed for state={state_upper}: {exc}"
        logger.exception(msg)
        return f"Error: {msg}"


async def _do_statute_lookup(state_upper: str, type_norm: str, topic_norm: str) -> str:
    """Core statute lookup logic, separated for timeout wrapping."""
    # Fetch entry
    entry = STATUTORY_DATABASE.get((state_upper, type_norm))

    if entry:
        statute_info = entry.get(
            topic_norm,
            f"Default statutory rules apply for {topic_norm} in {state_upper}.",
        )
        template_info = entry.get("template", "No default template found.")
    else:
        # Fallback for states without specific entries
        statute_info = (
            f"--- General Fallback Statute Lookup ({state_upper} {type_norm}) ---\n"
            f"Topic: {topic_norm}\n"
            f"Default Rule: Under {state_upper} state law, general default voting and corporate governance rules apply. "
            f"Consult local business organization codes for specific {topic_norm} statutory provisions."
        )
        if type_norm == "LLC":
            template_info = (
                f"=== GENERAL {state_upper} LLC OPERATING AGREEMENT ===\n"
                f"1. Name and State: {state_upper}\n"
                f"2. Statutory defaults apply for voting, allocations, and distributions."
            )
        else:
            template_info = (
                f"=== GENERAL {state_upper} ARTICLES OF INCORPORATION ===\n"
                f"1. Name and State: {state_upper}\n"
                f"2. Capital Stock authorization and registered agent designation."
            )

    return (
        f"State: {state_upper}\n"
        f"Entity Type: {type_norm}\n"
        f"Topic: {topic_norm}\n\n"
        f"--- Statutory Summary ---\n"
        f"{statute_info}\n\n"
        f"--- Recommended Template ---\n"
        f"{template_info}"
    )
