#!/usr/bin/env python3
"""
CONCEPT:LP-OS.config.legal Generalized Interactive Legal Holding Company Structuring Flow.
Supports forming holding companies from scratch, shifting existing LLCs into trusts,
and linking pre-existing trusts and LLCs with dynamic statutory default lookups,
Secretary of State availability checks, Form SS-4 EIN drafting, and Assignment of Interest prep.
"""

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime

# Ensure parent directory is in sys.path for direct imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from legal_peripherals_mcp.mcp.mcp_ein import handle_ein_draft
from legal_peripherals_mcp.mcp.mcp_sos import handle_sos_lookup
from legal_peripherals_mcp.mcp.mcp_statute import handle_statute_rules

# Color codes for stunning visual experience
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
========================================================================
             UNIVERSAL DYNAMIC LEGAL AUTOMATION SUITE
       Universal Holding Company Structuring & Migration Flow
========================================================================{RESET}"""


def get_input(prompt: str, default: str) -> str:
    """Helper to prompt for user input with a styled default value."""
    try:
        val = input(
            f"{BOLD}{BLUE}?{RESET} {prompt} [{YELLOW}{default}{RESET}]: "
        ).strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print(f"\n{RED}Process interrupted by user. Exiting.{RESET}")
        sys.exit(1)


def print_section(title: str):
    print(f"\n{BOLD}{MAGENTA}--- {title} ---{RESET}\n")


@dataclass
class StructuringInputs:
    """The user-facing fields gathered for a structuring run, one path's worth."""

    trust_name: str
    trustee_name: str
    trustee_address: str
    llc_name: str
    state: str
    purpose: str
    current_owner_name: str


@dataclass
class StatuteRules:
    """The three statute-rules lookups a structuring run drafts documents from."""

    operating: str
    indemnity: str
    capital: str


@dataclass
class TrustDraftFiles:
    """Paths to whichever Phase 3 trust documents this path drafted (else None)."""

    trust_file: str | None = None
    sovereign_trust_file: str | None = None
    commodity_registry_file: str | None = None
    dividend_resolution_file: str | None = None


@dataclass
class OwnershipDraftFiles:
    """Paths to whichever Phase 5 ownership documents this path drafted (else None)."""

    assignment_file: str | None = None
    amended_operating_agreement_file: str | None = None
    operating_agreement_file: str | None = None


def _summary_text(rules_text: str) -> str:
    """Pull just the '--- Statutory Summary ---' section out of a rules response."""
    return (
        rules_text.split("--- Statutory Summary ---")[-1]
        .split("--- Recommended Template ---")[0]
        .strip()
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Orchestrate Trust & LLC holding company creation or migration workflow."
    )
    parser.add_argument(
        "--path",
        type=int,
        choices=[1, 2, 3, 4],
        help="Workflow Path (1: Scratch, 2: Migrate LLC to New Trust, 3: Link Existing LLC & Trust, 4: Sovereign Fiduciary Community Trust)",
    )
    parser.add_argument("--trust-name", type=str, help="Name of the Trust")
    parser.add_argument("--trustee-name", type=str, help="Name of the Trustee")
    parser.add_argument("--trustee-address", type=str, help="Address of the Trustee")
    parser.add_argument("--llc-name", type=str, help="Name of the LLC")
    parser.add_argument(
        "--state", type=str, help="State jurisdiction (e.g. DE, WY, TX)"
    )
    parser.add_argument("--purpose", type=str, help="Business purpose")
    parser.add_argument(
        "--current-owner-name",
        type=str,
        help="Current owner of existing LLC (for migration/linking/managing directors)",
    )
    parser.add_argument(
        "--non-interactive", action="store_true", help="Run without prompt interaction"
    )
    return parser


def _select_path(args: argparse.Namespace) -> int:
    """Prompt for (or take from ``args``) the workflow path, 1 through 4."""
    if not args.path and not args.non_interactive:
        print(
            f"{BOLD}{YELLOW}Please select a holding company workflow path to begin:{RESET}"
        )
        print(
            f"  [{CYAN}1{RESET}] {BOLD}Brand New Holding Structure{RESET} (Form a new Trust and a new LLC under it)"
        )
        print(
            f"  [{CYAN}2{RESET}] {BOLD}Migrate Existing LLC{RESET} (Establish a new Trust and shift your existing LLC into it)"
        )
        print(
            f"  [{CYAN}3{RESET}] {BOLD}Link Existing Entities{RESET} (Shift an existing LLC into an existing Trust)"
        )
        print(
            f"  [{CYAN}4{RESET}] {BOLD}Sovereign Fiduciary Community Trust & Pool{RESET} (Assert Common-Law sovereignty, appoint Managing Directors, pool commodity assets)"
        )
        print()
        path_selection = get_input("Enter selection (1, 2, 3, or 4)", "1")
        try:
            return int(path_selection)
        except ValueError:
            return 1
    return args.path or 1


_SOVEREIGN_PATH_DEFAULTS = {
    "llc_name": "Sovereign Commodity Pool",
    "state": "WY",
    "purpose": "Sovereign asset protection, physical gold/silver pooling and community dividends",
    "trust_name": "The Sovereign Peoples Trust",
    "trustee_name": "Sovereign Representative Fiduciary",
    "trustee_address": "Common Law Jurisdiction, USA",
    "current_owner_name": "Sovereign Representative, Co-Fiduciary A, Co-Fiduciary B",
}

_STANDARD_PATH_DEFAULTS = {
    "llc_name": "Liberty Holdings LLC",
    "state": "DE",
    "purpose": "Holding company and wealth preservation",
    "trust_name": "The Liberty Family Trust",
    "trustee_name": "Sovereign Representative",
    "trustee_address": "1209 North Orange Street, Wilmington, DE 19801",
    "current_owner_name": "Sovereign Representative",
}


def _resolve(value: str | None, default: str) -> str:
    return value or default


def _non_interactive_inputs(args: argparse.Namespace, path: int) -> StructuringInputs:
    """The non-interactive fallback defaults, per path (1-3 share one default set)."""
    defaults = _SOVEREIGN_PATH_DEFAULTS if path == 4 else _STANDARD_PATH_DEFAULTS
    return StructuringInputs(
        trust_name=_resolve(args.trust_name, defaults["trust_name"]),
        trustee_name=_resolve(args.trustee_name, defaults["trustee_name"]),
        trustee_address=_resolve(args.trustee_address, defaults["trustee_address"]),
        llc_name=_resolve(args.llc_name, defaults["llc_name"]),
        state=_resolve(args.state, defaults["state"]).strip().upper(),
        purpose=_resolve(args.purpose, defaults["purpose"]),
        current_owner_name=_resolve(
            args.current_owner_name, defaults["current_owner_name"]
        ),
    )


def _interactive_inputs_path1(args: argparse.Namespace) -> StructuringInputs:
    """Path 1: brand-new Trust + brand-new LLC."""
    print(
        f"{YELLOW}Preparing to draft a brand new Trust and a brand new LLC...{RESET}\n"
    )
    trust_name = get_input(
        "Enter Trust Name", args.trust_name or "The Liberty Family Trust"
    )
    trustee_name = get_input(
        "Enter Trustee Name", args.trustee_name or "Sovereign Representative"
    )
    trustee_address = get_input(
        "Enter Trustee Address",
        args.trustee_address or "1209 North Orange Street, Wilmington, DE 19801",
    )
    llc_name = get_input(
        "Enter Brand New LLC Name", args.llc_name or "Liberty Holdings LLC"
    )
    state = (
        get_input("Enter LLC Jurisdiction State (e.g. DE, WY, TX)", args.state or "DE")
        .strip()
        .upper()
    )
    purpose = get_input(
        "Enter LLC Business Purpose",
        args.purpose or "Holding company and wealth preservation",
    )
    current_owner_name = trustee_name
    return StructuringInputs(
        trust_name=trust_name,
        trustee_name=trustee_name,
        trustee_address=trustee_address,
        llc_name=llc_name,
        state=state,
        purpose=purpose,
        current_owner_name=current_owner_name,
    )


def _interactive_inputs_path2(args: argparse.Namespace) -> StructuringInputs:
    """Path 2: migrate an existing LLC into a newly formed Trust."""
    print(
        f"{YELLOW}Preparing to migrate an existing LLC into a newly formed Trust...{RESET}\n"
    )
    llc_name = get_input(
        "Enter Existing LLC Name", args.llc_name or "Liberty Holdings LLC"
    )
    state = (
        get_input("Enter Existing LLC State (e.g. DE, WY, TX)", args.state or "DE")
        .strip()
        .upper()
    )
    current_owner_name = get_input(
        "Enter Current LLC Owner/Member Legal Name",
        args.current_owner_name or "Sovereign Representative",
    )
    trust_name = get_input(
        "Enter New Trust Name to establish",
        args.trust_name or "The Liberty Family Trust",
    )
    trustee_name = get_input(
        "Enter Trustee Name", args.trustee_name or "Sovereign Representative"
    )
    trustee_address = get_input(
        "Enter Trustee Address",
        args.trustee_address or "1209 North Orange Street, Wilmington, DE 19801",
    )
    purpose = get_input(
        "Enter Purpose of the Holding Structure",
        args.purpose or "Holding company and wealth preservation",
    )
    return StructuringInputs(
        trust_name=trust_name,
        trustee_name=trustee_name,
        trustee_address=trustee_address,
        llc_name=llc_name,
        state=state,
        purpose=purpose,
        current_owner_name=current_owner_name,
    )


def _interactive_inputs_path3(args: argparse.Namespace) -> StructuringInputs:
    """Path 3: link an existing LLC and a pre-existing Trust."""
    print(
        f"{YELLOW}Preparing to link an existing LLC and a pre-existing Trust...{RESET}\n"
    )
    llc_name = get_input(
        "Enter Existing LLC Name", args.llc_name or "Liberty Holdings LLC"
    )
    state = (
        get_input("Enter Existing LLC State (e.g. DE, WY, TX)", args.state or "DE")
        .strip()
        .upper()
    )
    current_owner_name = get_input(
        "Enter Current LLC Owner/Member Legal Name",
        args.current_owner_name or "Sovereign Representative",
    )
    trust_name = get_input(
        "Enter Pre-existing Trust Name",
        args.trust_name or "The Liberty Family Trust",
    )
    trustee_name = get_input(
        "Enter Trustee Name", args.trustee_name or "Sovereign Representative"
    )
    trustee_address = get_input(
        "Enter Trustee Address",
        args.trustee_address or "1209 North Orange Street, Wilmington, DE 19801",
    )
    purpose = get_input(
        "Enter Business Purpose",
        args.purpose or "Holding company and wealth preservation",
    )
    return StructuringInputs(
        trust_name=trust_name,
        trustee_name=trustee_name,
        trustee_address=trustee_address,
        llc_name=llc_name,
        state=state,
        purpose=purpose,
        current_owner_name=current_owner_name,
    )


def _interactive_inputs_path4(args: argparse.Namespace) -> StructuringInputs:
    """Path 4: Sovereign Fiduciary Community Trust & Commodity Pool."""
    print(
        f"{YELLOW}Preparing to establish a Sovereign Fiduciary Community Trust & Commodity Pool...{RESET}\n"
    )
    trust_name = get_input(
        "Enter Sovereign Trust Name",
        args.trust_name or "The Sovereign Peoples Trust",
    )
    trustee_name = get_input(
        "Enter Sovereign Trustee Name",
        args.trustee_name or "Sovereign Representative Fiduciary",
    )
    trustee_address = get_input(
        "Enter Trustee Address/Coordinates",
        args.trustee_address or "Common Law Jurisdiction, USA",
    )
    current_owner_name = get_input(
        "Enter Board of Managing Directors/Community Members (comma-separated list)",
        args.current_owner_name
        or "Sovereign Representative, Co-Fiduciary A, Co-Fiduciary B",
    )
    llc_name = get_input(
        "Enter Commodity Asset Pool / LLC Name",
        args.llc_name or "Sovereign Commodity Pool",
    )
    state = (
        get_input(
            "Enter Common-law Jurisdiction State (e.g. DE, WY, TX)",
            args.state or "WY",
        )
        .strip()
        .upper()
    )
    purpose = get_input(
        "Enter Trust Purpose",
        args.purpose
        or "Sovereign asset protection, physical gold/silver pooling and community dividends",
    )
    return StructuringInputs(
        trust_name=trust_name,
        trustee_name=trustee_name,
        trustee_address=trustee_address,
        llc_name=llc_name,
        state=state,
        purpose=purpose,
        current_owner_name=current_owner_name,
    )


_INTERACTIVE_INPUT_BUILDERS = {
    1: _interactive_inputs_path1,
    2: _interactive_inputs_path2,
    3: _interactive_inputs_path3,
    4: _interactive_inputs_path4,
}


def _gather_inputs(args: argparse.Namespace, path: int) -> StructuringInputs:
    """Gather the structuring fields, non-interactively or via the path's prompts."""
    if args.non_interactive:
        return _non_interactive_inputs(args, path)
    return _INTERACTIVE_INPUT_BUILDERS[path](args)


async def _run_sos_check(path: int, inputs: StructuringInputs) -> str:
    """Phase 1: Secretary of State registration/availability check (bypassed on path 4)."""
    print_section("PHASE 1: LLC Secretary of State (SOS) Registration Check")
    if path == 4:
        print(
            f"{YELLOW}Sovereign Representative Fiduciary Trust asserts non-statutory status under Article I, Section 10 (Contract Clause) of the Constitution.{RESET}"
        )
        print(
            f"{BLUE}Bypassing public Secretary of State (SOS) filing requirement for Common Law entities...{RESET}"
        )
        sos_result = "Non-Statutory/Common Law Trust: Not registered with the Secretary of State (asserts private Contract Clause protection under U.S. Const. art. I, § 10)."
        print(f"{GREEN}SOS Response:{RESET}\n{sos_result}\n")
        return sos_result

    if path == 1:
        print(
            f"{BLUE}Checking LLC name availability for new entity '{inputs.llc_name}' in state={inputs.state}...{RESET}"
        )
    else:
        print(
            f"{BLUE}Confirming active registration / status for existing LLC '{inputs.llc_name}' in state={inputs.state}...{RESET}"
        )
    sos_result = await handle_sos_lookup(state=inputs.state, entity_name=inputs.llc_name)
    print(f"{GREEN}SOS Response:{RESET}\n{sos_result}\n")
    return sos_result


async def _fetch_statute_rules(state: str) -> StatuteRules:
    """Phase 2: fetch the voting, indemnification, and capital-contribution defaults."""
    print_section(f"PHASE 2: Statutory Defaults for State of {state}")
    print(f"{BLUE}Retrieving operating agreement template and default laws...{RESET}")

    operating_rules = await handle_statute_rules(
        state=state, entity_type="LLC", topic="voting"
    )
    indemnity_rules = await handle_statute_rules(
        state=state, entity_type="LLC", topic="indemnification"
    )
    capital_rules = await handle_statute_rules(
        state=state, entity_type="LLC", topic="capital_contributions"
    )

    print(
        f"{GREEN}Voting, Indemnification, and Capital Contribution Rules Successfully Parsed!{RESET}\n"
    )
    return StatuteRules(
        operating=operating_rules, indemnity=indemnity_rules, capital=capital_rules
    )


def _draft_sovereign_trust_documents(
    inputs: StructuringInputs, drafts_dir: str
) -> tuple[str, str, str]:
    """Path 4's Phase 3: sovereign trust indenture, commodity registry, dividend resolution."""
    print_section("PHASE 3: Sovereign Trust Indenture & Commodity Pool Formulation")
    print(
        f"{BLUE}Drafting Constitutional Common-Law Trust Indenture for '{inputs.trust_name}'...{RESET}"
    )

    directors_list = [d.strip() for d in inputs.current_owner_name.split(",")]
    directors_formatted = "\n   - ".join(directors_list)

    sovereign_trust_indenture = f"""========================================================================
                      CONSTITUTIONAL TRUST INDENTURE
                                   OF
                     {inputs.trust_name}
========================================================================

1. DECLARATION OF SOVEREIGNTY:
   We, the Sovereign People, in accordance with the Natural Law and the
   principles of individual liberty, hereby declare our absolute sovereignty.
   This Trust is established as a private, non-statutory, constitutional
   Common-Law trust asserting all natural rights and protections guaranteed
   under the United States Constitution.

2. BOARD OF MANAGING DIRECTORS / TRUSTEES:
   The Board of Managing Directors shall govern and administer the Trust
   assets with equal fiduciary and managerial authority.
   The initial appointed Board of Managing Directors / Trustees are:
   - {directors_formatted}

   Primary Sovereign Representative: {inputs.trustee_name}
   Primary Coordinates: {inputs.trustee_address}

3. CONTRACT CLAUSE PROTECTION:
   This Indenture is a private contract protected against impairment by any
   state or legislative act pursuant to Article I, Section 10 of the
   Constitution of the United States: "No State shall... pass any Law impairing
   the Obligation of Contracts."

4. TRUST ASSETS:
   The trust assets shall include the physical holdings of the community and
   100% ownership of {inputs.llc_name} (Commodity Pool & Local Credit Registry).

5. EXECUTION & SOVEREIGN ATTESTATION:
   Dated: {datetime.now().strftime("%Y-%m-%d")}

   ___________________________            ___________________________
   Sovereign Trustee:                     Co-Trustee / Director:
   {inputs.trustee_name}
"""
    sovereign_trust_file = os.path.join(drafts_dir, "sovereign_trust_indenture.txt")
    with open(sovereign_trust_file, "w") as f:
        f.write(sovereign_trust_indenture)
    print(
        f"{GREEN}Drafted Sovereign Trust Indenture saved to: {sovereign_trust_file}{RESET}"
    )

    print(
        f"{BLUE}Drafting Commodity Asset Pool Registry for '{inputs.llc_name}'...{RESET}"
    )
    commodity_registry = f"""========================================================================
                     COMMODITY ASSET POOL REGISTRY
                                   OF
                     {inputs.llc_name}
========================================================================

1. ESTABLISHMENT OF COMMODITY POOL:
   Pursuant to the Constitutional Trust Indenture of {inputs.trust_name}, there is
   hereby established a private Commodity Asset Pool to defend community wealth
   against inflationary fiat currency depreciation.

2. CAPITAL POOLING & CONVERSION TO METALS:
   - All community funds and capital contributed to the Pool shall be converted into
     physical gold and silver bullion.
   - Allocation Ratio:
     * 50.0% Physical Gold Bullion (held in secure vaults)
     * 50.0% Physical Silver Bullion (held in secure vaults)

3. LOCAL ECONOMIC CREDIT PROTOCOL:
   - To facilitate community trade, the Pool issues local fractionally backed
     credits, denominated in "Sovereign Liberty Credits" (SLC).
   - Each SLC is backed 100% by the physical gold/silver reserves stored in
     the vault at a fixed exchange rate.
   - Members can redeem SLC for physical bullion coordinates upon demand.

4. CURRENT POOL STANDINGS:
   Reserves: Physical Gold Bullion & Physical Silver Bullion
   Assigned Asset Managers:
   - {inputs.trustee_name} (Primary Custodian)
   - {inputs.current_owner_name} (Co-Custodian Board)
"""
    commodity_registry_file = os.path.join(
        drafts_dir, "commodity_asset_pool_registry.txt"
    )
    with open(commodity_registry_file, "w") as f:
        f.write(commodity_registry)
    print(
        f"{GREEN}Drafted Commodity Asset Pool Registry saved to: {commodity_registry_file}{RESET}"
    )

    print(f"{BLUE}Drafting Board of Managing Directors Dividend Resolution...{RESET}")
    directors_sigs = "\n\n   ___________________________   ".join(
        [f"{d.strip()} (Managing Director)" for d in directors_list]
    )
    dividend_resolution = f"""========================================================================
                BOARD OF MANAGING DIRECTORS DIVIDEND RESOLUTION
                                   OF
                     {inputs.trust_name}
========================================================================

WHEREAS, the Board of Managing Directors of {inputs.trust_name} has reviewed the
performance, growth, and appreciation of the Physical Gold & Silver reserves
managed under the {inputs.llc_name}; and

WHEREAS, it is the primary purpose of this Sovereign Community Trust to return
the real economic yields of pooled asset growth directly to the Sovereign Members;

NOW, THEREFORE, BE IT RESOLVED BY THE BOARD OF MANAGING DIRECTORS:

1. DIVIDEND APPROVAL:
   A dividend distribution is hereby approved for the current fiscal period.

2. ALLOCATION IN COMMODITY UNITS:
   - The total distribution shall be allocated in Physical Gold/Silver ounces
     or their equivalent Sovereign Liberty Credits (SLC).
   - Distribution Rate: 0.10 oz Silver (or equivalent SLC) per Member Credit Unit.

3. DIRECT PAYMENTS:
   - Fiduciary Custodian {inputs.trustee_name} is authorized and directed to execute
     the transfer of bullion values directly to the secure community wallets.

SO RESOLVED AND ATTESTED BY THE BOARD OF MANAGING DIRECTORS:
{directors_sigs}

Dated: {datetime.now().strftime("%Y-%m-%d")}
"""
    dividend_resolution_file = os.path.join(
        drafts_dir, "managing_directors_dividend_resolution.txt"
    )
    with open(dividend_resolution_file, "w") as f:
        f.write(dividend_resolution)
    print(
        f"{GREEN}Drafted Dividend Resolution saved to: {dividend_resolution_file}{RESET}"
    )

    return sovereign_trust_file, commodity_registry_file, dividend_resolution_file


def _draft_new_trust_agreement(inputs: StructuringInputs, drafts_dir: str) -> str:
    """Paths 1/2's Phase 3: draft a brand-new Trust Agreement."""
    print_section("PHASE 3: Trust Agreement Formulation")
    print(f"{BLUE}Drafting brand-new Trust Agreement for '{inputs.trust_name}'...{RESET}")

    trust_agreement = f"""========================================================================
                      TRUST AGREEMENT
========================================================================

1. PARTIES:
   This Trust Agreement is established by the Grantor for the benefit of
   the designated beneficiaries, with:
   Trustee: {inputs.trustee_name}
   Trust Address: {inputs.trustee_address}

2. TRUST NAME:
   The trust established hereunder shall be known as:
   {inputs.trust_name}

3. TRUST ASSETS & PURPOSE:
   The primary asset of this Trust is the 100% membership interest of
   {inputs.llc_name}, a limited liability company formed under the laws of the State of {inputs.state}.
   The Purpose is: {inputs.purpose}.

4. GOVERNING LAW:
   This Trust shall be governed by, construed, and enforced in accordance
   with the laws of the State of {inputs.state}.

5. SIGNATURES:
   Dated: {datetime.now().strftime("%Y-%m-%d")}

   ___________________________            ___________________________
   Grantor                                Trustee: {inputs.trustee_name}
"""
    trust_file = os.path.join(drafts_dir, "trust_agreement.txt")
    with open(trust_file, "w") as f:
        f.write(trust_agreement)
    print(f"{GREEN}Drafted Trust Agreement saved successfully.{RESET}")
    return trust_file


def _run_trust_drafting_phase(
    path: int, inputs: StructuringInputs, drafts_dir: str
) -> TrustDraftFiles:
    """Phase 3 dispatcher: sovereign docs (path 4), a new Trust Agreement (1/2), or skip (3)."""
    if path == 4:
        sovereign_trust_file, commodity_registry_file, dividend_resolution_file = (
            _draft_sovereign_trust_documents(inputs, drafts_dir)
        )
        return TrustDraftFiles(
            sovereign_trust_file=sovereign_trust_file,
            commodity_registry_file=commodity_registry_file,
            dividend_resolution_file=dividend_resolution_file,
        )
    if path in (1, 2):
        return TrustDraftFiles(trust_file=_draft_new_trust_agreement(inputs, drafts_dir))
    print_section("PHASE 3: Trust Agreement (Skipped)")
    print(
        f"{YELLOW}Trust already established. Skipping Trust Agreement drafting.{RESET}"
    )
    return TrustDraftFiles()


async def _draft_ein_application(
    path: int, inputs: StructuringInputs, drafts_dir: str
) -> str | None:
    """Phase 4: draft IRS Form SS-4 for paths 1/2/4; skipped for path 3."""
    if path not in (1, 2, 4):
        print_section("PHASE 4: IRS Form SS-4 EIN (Skipped)")
        print(
            f"{YELLOW}Existing entities are fully registered with active tax identifiers. Skipping EIN prep.{RESET}"
        )
        return None

    print_section("PHASE 4: IRS Form SS-4 EIN Drafting & Scheduling")

    if path == 4:
        print(
            f"{BLUE}Preparing EIN application for Sovereign Trust {inputs.trust_name}...{RESET}"
        )
        ein_result = await handle_ein_draft(
            legal_name=inputs.trust_name,
            trade_name="",
            responsible_party_ssn="XXX-XX-XXXX",
            responsible_party_name=inputs.trustee_name,
            business_type="Common Law Trust",
            mailing_address=inputs.trustee_address,
            county_state=f"USA, {inputs.state}",
            reason_for_applying="To open a banking/financial account for the non-statutory Trust",
        )
    else:
        print(
            f"{BLUE}Preparing EIN application for {inputs.llc_name} owned by {inputs.trust_name}...{RESET}"
        )
        ein_result = await handle_ein_draft(
            legal_name=inputs.llc_name,
            trade_name="",
            responsible_party_ssn="XXX-XX-XXXX",
            responsible_party_name=inputs.trustee_name,
            business_type="LLC",
            mailing_address=inputs.trustee_address,
            county_state=f"USA, {inputs.state}",
            reason_for_applying="Started new business (Solely owned by Trust)",
        )

    print(f"{GREEN}EIN Draft & Schedule Response:{RESET}\n{ein_result}\n")

    ein_file = os.path.join(drafts_dir, "ein_ss4_draft.txt")
    with open(ein_file, "w") as f:
        f.write(ein_result)
    print(f"{GREEN}Drafted IRS EIN SS-4 saved successfully.{RESET}")
    return ein_file


def _draft_ownership_transition_documents(
    inputs: StructuringInputs, drafts_dir: str, rules: StatuteRules
) -> tuple[str, str]:
    """Paths 2/3's Phase 5: Assignment of Interest + Amended Operating Agreement + guide."""
    print_section("PHASE 5: Ownership Assignment & Amended Operating Agreement")
    print(
        f"{BLUE}Generating Assignment of Membership Interest (shifting ownership)...{RESET}"
    )

    assignment_agreement = f"""========================================================================
                  ASSIGNMENT OF MEMBERSHIP INTEREST
========================================================================

1. TRANSFER OF INTEREST:
   This Assignment of Membership Interest (the "Assignment") is made and entered into
   by and between:
   Assignor: {inputs.current_owner_name} (Current 100% Owner/Member)
   Assignee: {inputs.trust_name} (Trust established with Trustee {inputs.trustee_name})

2. ASSIGNMENT AND TRANSFER:
   For good and valuable consideration, the receipt and sufficiency of which are
   hereby acknowledged, Assignor hereby transfers, assigns, and conveys to Assignee
   100% of the membership interest, capital interests, and governance rights in:
   Entity Name: {inputs.llc_name} (formed under State of {inputs.state})

3. ACCEPTANCE AND GOVERNING LAW:
   Assignee hereby accepts the transfer of the Assigned Interest and agrees to
   be bound by all the terms, obligations, and covenants of the Company's Operating Agreement.
   This Assignment is governed by the laws of the State of {inputs.state}.

4. EXECUTION:
   Dated: {datetime.now().strftime("%Y-%m-%d")}

   ___________________________            ___________________________
   Assignor: {inputs.current_owner_name}              Assignee: {inputs.trust_name}
                                          By: {inputs.trustee_name}, Trustee
"""
    assignment_file = os.path.join(
        drafts_dir, "assignment_of_membership_interest.txt"
    )
    with open(assignment_file, "w") as f:
        f.write(assignment_agreement)
    print(
        f"{GREEN}Drafted Assignment of Membership Interest saved to: {assignment_file}{RESET}"
    )

    print(
        f"{BLUE}Drafting Amended LLC Operating Agreement incorporating Trust sole membership...{RESET}"
    )

    amended_operating_agreement = f"""========================================================================
             AMENDED & RESTATED LIMITED LIABILITY COMPANY OPERATING AGREEMENT
                                OF
                       {inputs.llc_name}
========================================================================

1. FORMATION & AMENDMENT:
   This Amended and Restated Operating Agreement is adopted to reflect the shift in
   membership ownership of {inputs.llc_name} to {inputs.trust_name}.

2. NEW SOLE MEMBER:
   The SOLE MEMBER of this Limited Liability Company is:
   {inputs.trust_name} (formed with Trustee {inputs.trustee_name})

3. OPERATIONAL STATUTE AMENDMENTS:
   - voting: {_summary_text(rules.operating)}
   - capital contributions: {_summary_text(rules.capital)}
   - indemnification: {_summary_text(rules.indemnity)}

4. SIGNED:
   Assignee Member: {inputs.trust_name}
   By: ___________________________ ({inputs.trustee_name}, Trustee)
   Dated: {datetime.now().strftime("%Y-%m-%d")}
"""
    amended_operating_agreement_file = os.path.join(
        drafts_dir, "amended_operating_agreement.txt"
    )
    with open(amended_operating_agreement_file, "w") as f:
        f.write(amended_operating_agreement)
    print(
        f"{GREEN}Drafted Amended Operating Agreement saved to: {amended_operating_agreement_file}{RESET}"
    )

    # Write Transition / Filing Instructions Guide
    print(f"{BLUE}Drafting Transition / Filing Instructions Guide...{RESET}")
    transition_guide = f"""========================================================================
                      TRANSITION & FILING GUIDE
========================================================================

You have successfully drafted the necessary legal documents to shift ownership of your
existing LLC ({inputs.llc_name}) to your Trust ({inputs.trust_name}). Follow these step-by-step
filing guidelines to complete the transfer:

Step 1: Execute Legal Documents
- Assignor ({inputs.current_owner_name}) and Trustee ({inputs.trustee_name}) must sign and date the
  Assignment of Membership Interest.
- The Trustee must sign the Amended & Restated Operating Agreement.
- File both documents securely with your corporate records.

Step 2: Secretary of State Filing (if applicable)
- In the State of {inputs.state}, verify if the state requires reporting members or managers.
- If member lists are filed publicly, submit an Amendment of Certificate/Articles to
  designate {inputs.trust_name} as the sole managing member.

Step 3: Update Bank / Financial Institution Accounts
- Present the signed Assignment of Membership Interest and Amended Operating Agreement
  to your bank representatives to update signing authorities and account ownership to
  the Trust name.

Step 4: Notify the IRS (Form 8822-B)
- Since the LLC is now solely owned by the Trust, file Form 8822-B (Change of Address or
  Responsible Party) with the IRS if there has been a change in the active responsible party
  or primary mailing coordinates.
"""
    transition_file = os.path.join(drafts_dir, "transition_guide.txt")
    with open(transition_file, "w") as f:
        f.write(transition_guide)
    print(f"{GREEN}Transition Guide saved successfully.{RESET}")

    return assignment_file, amended_operating_agreement_file


def _draft_sole_member_operating_agreement(
    inputs: StructuringInputs, drafts_dir: str, rules: StatuteRules
) -> str:
    """Path 1's Phase 5: standard sole-member LLC Operating Agreement."""
    print_section("PHASE 5: LLC Operating Agreement Formulation")
    print(
        f"{BLUE}Generating standard Sole-Member Operating Agreement for {inputs.llc_name}...{RESET}"
    )

    template_header = "=== OPERATING AGREEMENT ==="
    if "--- Recommended Template ---" in rules.operating:
        template_header = rules.operating.split("--- Recommended Template ---")[
            -1
        ].strip()

    llc_operating_agreement = f"""========================================================================
              LIMITED LIABILITY COMPANY OPERATING AGREEMENT
                                OF
                       {inputs.llc_name}
========================================================================

1. FORMATION:
   This Limited Liability Company is formed pursuant to the LLC Act of the
   State of {inputs.state}.

2. SOLE MEMBER:
   The SOLE MEMBER of this Limited Liability Company is:
   {inputs.trust_name} (formed with Trustee {inputs.trustee_name})

3. CAPITAL CONTRIBUTIONS & PERCENTAGE INTEREST:
   The Trust holds a 100% membership interest in {inputs.llc_name}.
   {_summary_text(rules.capital)}

4. MANAGEMENT & VOTING:
   Management of the Company is vested solely in the Member.
   {_summary_text(rules.operating)}

5. INDEMNIFICATION:
   {_summary_text(rules.indemnity)}

6. TEMPLATE REFERENCE:
{template_header}

7. EXECUTED BY MEMBER:
   Member: {inputs.trust_name}
   By: ___________________________ ({inputs.trustee_name}, Trustee)
   Dated: {datetime.now().strftime("%Y-%m-%d")}
"""
    operating_agreement_file = os.path.join(
        drafts_dir, "llc_operating_agreement.txt"
    )
    with open(operating_agreement_file, "w") as f:
        f.write(llc_operating_agreement)
    print(
        f"{GREEN}Drafted Operating Agreement saved to: {operating_agreement_file}{RESET}"
    )
    return operating_agreement_file


def _run_ownership_phase(
    path: int, inputs: StructuringInputs, drafts_dir: str, rules: StatuteRules
) -> OwnershipDraftFiles:
    """Phase 5 dispatcher: bypass (path 4), ownership transition (2/3), or sole-member (1)."""
    if path == 4:
        print_section("PHASE 5: Sovereign Operating Protocols (Bypassed)")
        print(
            f"{YELLOW}Sovereign trust governs the pool via Indenture & Commodity Pool Registry. Bypassing LLC operating agreement.{RESET}"
        )
        return OwnershipDraftFiles()
    if path in (2, 3):
        assignment_file, amended_file = _draft_ownership_transition_documents(
            inputs, drafts_dir, rules
        )
        return OwnershipDraftFiles(
            assignment_file=assignment_file,
            amended_operating_agreement_file=amended_file,
        )
    return OwnershipDraftFiles(
        operating_agreement_file=_draft_sole_member_operating_agreement(
            inputs, drafts_dir, rules
        )
    )


def _diagram_for_new_structure(inputs: StructuringInputs) -> tuple[str, str]:
    diagram_type = "BRAND NEW STRUCTURE (Trust owned Sole-Member LLC)"
    diagram_flow = f"""
               +-------------------------------------------+
               |                 GRANTOR                   |
               +-------------------------------------------+
                                     |
                                     v (Establishes)
               +-------------------------------------------+
               |          {inputs.trust_name:32} |
               |  (Trustee: {inputs.trustee_name:31}) |
               +-------------------------------------------+
                                     |
                                     v (Owns 100% of Member Interest)
               +-------------------------------------------+
               |          {inputs.llc_name:32} |
               |  (State: {inputs.state:34}) |
               +-------------------------------------------+
                                     |
                                     v (Asset / Holding Operations)
                        [Real Estate / IP / Capital]
"""
    return diagram_type, diagram_flow


def _diagram_for_ownership_transition(inputs: StructuringInputs) -> tuple[str, str]:
    diagram_type = "MIGRATED OWNERSHIP (Assignment of Interest to Trust)"
    diagram_flow = f"""
               +-------------------------------------------+
               |      Assignor: {inputs.current_owner_name:26} |
               +-------------------------------------------+
                      |                               |
                      | (Assigns Interest)            | (Establishes)
                      v                               v
               +-------------------------------------------+
               |      Assignee: {inputs.trust_name:26} |
               |  (Trustee: {inputs.trustee_name:31}) |
               +-------------------------------------------+
                                     |
                                     v (Now Owns 100% of Member Interest)
               +-------------------------------------------+
               |          {inputs.llc_name:32} |
               |  (State: {inputs.state:34}) |
               +-------------------------------------------+
"""
    return diagram_type, diagram_flow


def _diagram_for_sovereign_pool(inputs: StructuringInputs) -> tuple[str, str]:
    diagram_type = "SOVEREIGN COMMUNITY TRUST & COMMODITY POOL"
    directors_joined = ", ".join(
        [d.strip() for d in inputs.current_owner_name.split(",")]
    )
    if len(directors_joined) > 40:
        directors_joined = directors_joined[:37] + "..."
    diagram_flow = f"""
               +-------------------------------------------+
               |        SOVEREIGN COMMUNITY MEMBERS        |
               |  ({directors_joined:40})  |
               +-------------------------------------------+
                                     |
                                     v (Elect / Form)
               +-------------------------------------------+
               |          {inputs.trust_name:32} |
               |  (Trustee/Rep: {inputs.trustee_name:27}) |
               |  (Contract Clause: Art. I, Sec. 10)       |
               +-------------------------------------------+
                                     |
                                     v (Manages / Pools Reserves)
               +-------------------------------------------+
               |          {inputs.llc_name:32} |
               |  (50.0% Gold Bullion / 50.0% Silver)       |
               |  (Backs Sovereign Liberty Credits)        |
               +-------------------------------------------+
                                     |
                                     v (Distributes)
                    [Commodity Dividend Resolution]
"""
    return diagram_type, diagram_flow


def _build_structure_diagram(path: int, inputs: StructuringInputs) -> tuple[str, str]:
    if path == 1:
        return _diagram_for_new_structure(inputs)
    if path in (2, 3):
        return _diagram_for_ownership_transition(inputs)
    return _diagram_for_sovereign_pool(inputs)


def _write_structure_diagram(
    path: int, inputs: StructuringInputs, drafts_dir: str
) -> str:
    """Phase 6: render + save the holding structure diagram for this path."""
    print_section("PHASE 6: Holding Structure Visualization")

    diagram_type, diagram_flow = _build_structure_diagram(path, inputs)

    diagram = f"""========================================================================
                      STRUCTURE VISUALIZER
Path type: {diagram_type}
========================================================================
{diagram_flow}"""
    print(diagram)

    diagram_file = os.path.join(drafts_dir, "structure_diagram.txt")
    with open(diagram_file, "w") as f:
        f.write(diagram)
    print(f"{GREEN}Structure Diagram saved successfully.{RESET}")
    return diagram_file


def _write_summary(
    path: int,
    inputs: StructuringInputs,
    drafts_dir: str,
    trust_files: TrustDraftFiles,
    ein_file: str | None,
    ownership_files: OwnershipDraftFiles,
    diagram_file: str,
) -> None:
    """Save the run's summary metadata (every generated file path + the chosen fields)."""
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "path_selected": path,
        "trust_name": inputs.trust_name,
        "trustee_name": inputs.trustee_name,
        "trustee_address": inputs.trustee_address,
        "llc_name": inputs.llc_name,
        "jurisdiction_state": inputs.state,
        "business_purpose": inputs.purpose,
        "files_generated": {
            "trust_agreement": trust_files.trust_file,
            "sovereign_trust_indenture": trust_files.sovereign_trust_file,
            "commodity_asset_pool_registry": trust_files.commodity_registry_file,
            "managing_directors_dividend_resolution": trust_files.dividend_resolution_file,
            "llc_operating_agreement": ownership_files.operating_agreement_file,
            "ein_ss4_draft": ein_file,
            "assignment_of_membership_interest": ownership_files.assignment_file,
            "amended_operating_agreement": ownership_files.amended_operating_agreement_file,
            "structure_diagram": diagram_file,
        },
    }

    summary_file = os.path.join(drafts_dir, "structuring_summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"{GREEN}Summary metadata saved successfully.{RESET}")


async def main():
    args = _build_arg_parser().parse_args()

    print(BANNER)

    path = _select_path(args)
    print_section(f"Selected Path: Path {path}")

    inputs = _gather_inputs(args, path)

    # Create drafts directory
    drafts_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "drafts"
    )
    os.makedirs(drafts_dir, exist_ok=True)

    await _run_sos_check(path, inputs)
    rules = await _fetch_statute_rules(inputs.state)

    trust_files = _run_trust_drafting_phase(path, inputs, drafts_dir)
    ein_file = await _draft_ein_application(path, inputs, drafts_dir)
    ownership_files = _run_ownership_phase(path, inputs, drafts_dir, rules)
    diagram_file = _write_structure_diagram(path, inputs, drafts_dir)

    _write_summary(
        path, inputs, drafts_dir, trust_files, ein_file, ownership_files, diagram_file
    )

    print(
        f"\n{BOLD}{GREEN}🎉 SUCCESS! Generalized holding company structuring flow completed successfully!{RESET}\n"
    )


if __name__ == "__main__":
    asyncio.run(main())
