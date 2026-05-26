#!/usr/bin/env python3
"""
CONCEPT:LEGAL-004 Generalized Interactive Legal Holding Company Structuring Flow.
Supports forming holding companies from scratch, shifting existing LLCs into trusts,
and linking pre-existing trusts and LLCs with dynamic statutory default lookups,
Secretary of State availability checks, Form SS-4 EIN drafting, and Assignment of Interest prep.
"""

import asyncio
import os
import sys
import argparse
import json
from datetime import datetime

# Ensure parent directory is in sys.path for direct imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from legal_peripherals_mcp.mcp.mcp_sos import handle_sos_lookup
from legal_peripherals_mcp.mcp.mcp_statute import handle_statute_rules
from legal_peripherals_mcp.mcp.mcp_ein import handle_ein_draft

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
        val = input(f"{BOLD}{BLUE}?{RESET} {prompt} [{YELLOW}{default}{RESET}]: ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print(f"\n{RED}Process interrupted by user. Exiting.{RESET}")
        sys.exit(1)

def print_section(title: str):
    print(f"\n{BOLD}{MAGENTA}--- {title} ---{RESET}\n")

async def main():
    parser = argparse.ArgumentParser(description="Orchestrate Trust & LLC holding company creation or migration workflow.")
    parser.add_argument("--path", type=int, choices=[1, 2, 3, 4], help="Workflow Path (1: Scratch, 2: Migrate LLC to New Trust, 3: Link Existing LLC & Trust, 4: Sovereign Fiduciary Community Trust)")
    parser.add_argument("--trust-name", type=str, help="Name of the Trust")
    parser.add_argument("--trustee-name", type=str, help="Name of the Trustee")
    parser.add_argument("--trustee-address", type=str, help="Address of the Trustee")
    parser.add_argument("--llc-name", type=str, help="Name of the LLC")
    parser.add_argument("--state", type=str, help="State jurisdiction (e.g. DE, WY, TX)")
    parser.add_argument("--purpose", type=str, help="Business purpose")
    parser.add_argument("--current-owner-name", type=str, help="Current owner of existing LLC (for migration/linking/managing directors)")
    parser.add_argument("--non-interactive", action="store_true", help="Run without prompt interaction")
    
    args = parser.parse_args()

    print(BANNER)

    # Path selection
    if not args.path and not args.non_interactive:
        print(f"{BOLD}{YELLOW}Please select a holding company workflow path to begin:{RESET}")
        print(f"  [{CYAN}1{RESET}] {BOLD}Brand New Holding Structure{RESET} (Form a new Trust and a new LLC under it)")
        print(f"  [{CYAN}2{RESET}] {BOLD}Migrate Existing LLC{RESET} (Establish a new Trust and shift your existing LLC into it)")
        print(f"  [{CYAN}3{RESET}] {BOLD}Link Existing Entities{RESET} (Shift an existing LLC into an existing Trust)")
        print(f"  [{CYAN}4{RESET}] {BOLD}Sovereign Fiduciary Community Trust & Pool{RESET} (Assert Common-Law sovereignty, appoint Managing Directors, pool commodity assets)")
        print()
        path_selection = get_input("Enter selection (1, 2, 3, or 4)", "1")
        try:
            path = int(path_selection)
        except ValueError:
            path = 1
    else:
        path = args.path or 1

    print_section(f"Selected Path: Path {path}")

    # Gather inputs depending on path selection
    if args.non_interactive:
        llc_name = args.llc_name or ("Sovereign Commodity Pool" if path == 4 else "Liberty Holdings LLC")
        state = (args.state or ("WY" if path == 4 else "DE")).strip().upper()
        purpose = args.purpose or ("Sovereign asset protection, physical gold/silver pooling and community dividends" if path == 4 else "Holding company and wealth preservation")
        trust_name = args.trust_name or ("The Sovereign Peoples Trust" if path == 4 else "The Liberty Family Trust")
        trustee_name = args.trustee_name or ("Sovereign Representative Fiduciary" if path == 4 else "Sovereign Representative")
        trustee_address = args.trustee_address or ("Common Law Jurisdiction, USA" if path == 4 else "1209 North Orange Street, Wilmington, DE 19801")
        current_owner_name = args.current_owner_name or ("Sovereign Representative, Co-Fiduciary A, Co-Fiduciary B" if path == 4 else "Sovereign Representative")
    else:
        # Prompt based on path selection
        if path == 1:
            print(f"{YELLOW}Preparing to draft a brand new Trust and a brand new LLC...{RESET}\n")
            trust_name = get_input("Enter Trust Name", args.trust_name or "The Liberty Family Trust")
            trustee_name = get_input("Enter Trustee Name", args.trustee_name or "Sovereign Representative")
            trustee_address = get_input("Enter Trustee Address", args.trustee_address or "1209 North Orange Street, Wilmington, DE 19801")
            llc_name = get_input("Enter Brand New LLC Name", args.llc_name or "Liberty Holdings LLC")
            state = get_input("Enter LLC Jurisdiction State (e.g. DE, WY, TX)", args.state or "DE").strip().upper()
            purpose = get_input("Enter LLC Business Purpose", args.purpose or "Holding company and wealth preservation")
            current_owner_name = trustee_name
        elif path == 2:
            print(f"{YELLOW}Preparing to migrate an existing LLC into a newly formed Trust...{RESET}\n")
            llc_name = get_input("Enter Existing LLC Name", args.llc_name or "Liberty Holdings LLC")
            state = get_input("Enter Existing LLC State (e.g. DE, WY, TX)", args.state or "DE").strip().upper()
            current_owner_name = get_input("Enter Current LLC Owner/Member Legal Name", args.current_owner_name or "Sovereign Representative")
            trust_name = get_input("Enter New Trust Name to establish", args.trust_name or "The Liberty Family Trust")
            trustee_name = get_input("Enter Trustee Name", args.trustee_name or "Sovereign Representative")
            trustee_address = get_input("Enter Trustee Address", args.trustee_address or "1209 North Orange Street, Wilmington, DE 19801")
            purpose = get_input("Enter Purpose of the Holding Structure", args.purpose or "Holding company and wealth preservation")
        elif path == 3:
            print(f"{YELLOW}Preparing to link an existing LLC and a pre-existing Trust...{RESET}\n")
            llc_name = get_input("Enter Existing LLC Name", args.llc_name or "Liberty Holdings LLC")
            state = get_input("Enter Existing LLC State (e.g. DE, WY, TX)", args.state or "DE").strip().upper()
            current_owner_name = get_input("Enter Current LLC Owner/Member Legal Name", args.current_owner_name or "Sovereign Representative")
            trust_name = get_input("Enter Pre-existing Trust Name", args.trust_name or "The Liberty Family Trust")
            trustee_name = get_input("Enter Trustee Name", args.trustee_name or "Sovereign Representative")
            trustee_address = get_input("Enter Trustee Address", args.trustee_address or "1209 North Orange Street, Wilmington, DE 19801")
            purpose = get_input("Enter Business Purpose", args.purpose or "Holding company and wealth preservation")
        else: # path == 4
            print(f"{YELLOW}Preparing to establish a Sovereign Fiduciary Community Trust & Commodity Pool...{RESET}\n")
            trust_name = get_input("Enter Sovereign Trust Name", args.trust_name or "The Sovereign Peoples Trust")
            trustee_name = get_input("Enter Sovereign Trustee Name", args.trustee_name or "Sovereign Representative Fiduciary")
            trustee_address = get_input("Enter Trustee Address/Coordinates", args.trustee_address or "Common Law Jurisdiction, USA")
            current_owner_name = get_input("Enter Board of Managing Directors/Community Members (comma-separated list)", args.current_owner_name or "Sovereign Representative, Co-Fiduciary A, Co-Fiduciary B")
            llc_name = get_input("Enter Commodity Asset Pool / LLC Name", args.llc_name or "Sovereign Commodity Pool")
            state = get_input("Enter Common-law Jurisdiction State (e.g. DE, WY, TX)", args.state or "WY").strip().upper()
            purpose = get_input("Enter Trust Purpose", args.purpose or "Sovereign asset protection, physical gold/silver pooling and community dividends")

    # Create drafts directory
    drafts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "drafts")
    os.makedirs(drafts_dir, exist_ok=True)

    # 1. Secretary of State Good-Standing / Availability Search
    print_section("PHASE 1: LLC Secretary of State (SOS) Registration Check")
    if path == 4:
        print(f"{YELLOW}Sovereign Representative Fiduciary Trust asserts non-statutory status under Article I, Section 10 (Contract Clause) of the Constitution.{RESET}")
        print(f"{BLUE}Bypassing public Secretary of State (SOS) filing requirement for Common Law entities...{RESET}")
        sos_result = "Non-Statutory/Common Law Trust: Not registered with the Secretary of State (asserts private Contract Clause protection under U.S. Const. art. I, § 10)."
        print(f"{GREEN}SOS Response:{RESET}\n{sos_result}\n")
    else:
        if path == 1:
            print(f"{BLUE}Checking LLC name availability for new entity '{llc_name}' in state={state}...{RESET}")
        else:
            print(f"{BLUE}Confirming active registration / status for existing LLC '{llc_name}' in state={state}...{RESET}")
        sos_result = await handle_sos_lookup(state=state, entity_name=llc_name)
        print(f"{GREEN}SOS Response:{RESET}\n{sos_result}\n")

    # 2. Statutory Rules & Template Auditing
    print_section(f"PHASE 2: Statutory Defaults for State of {state}")
    print(f"{BLUE}Retrieving operating agreement template and default laws...{RESET}")
    
    operating_rules = await handle_statute_rules(state=state, entity_type="LLC", topic="voting")
    indemnity_rules = await handle_statute_rules(state=state, entity_type="LLC", topic="indemnification")
    capital_rules = await handle_statute_rules(state=state, entity_type="LLC", topic="capital_contributions")

    print(f"{GREEN}Voting, Indemnification, and Capital Contribution Rules Successfully Parsed!{RESET}\n")

    # 3. Draft Trust Agreement / Indenture
    trust_file = None
    sovereign_trust_file = None
    commodity_registry_file = None
    dividend_resolution_file = None

    if path == 4:
        print_section("PHASE 3: Sovereign Trust Indenture & Commodity Pool Formulation")
        print(f"{BLUE}Drafting Constitutional Common-Law Trust Indenture for '{trust_name}'...{RESET}")
        
        directors_list = [d.strip() for d in current_owner_name.split(",")]
        directors_formatted = "\n   - ".join(directors_list)
        
        sovereign_trust_indenture = f"""========================================================================
                      CONSTITUTIONAL TRUST INDENTURE
                                   OF
                     {trust_name}
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

   Primary Sovereign Representative: {trustee_name}
   Primary Coordinates: {trustee_address}

3. CONTRACT CLAUSE PROTECTION:
   This Indenture is a private contract protected against impairment by any
   state or legislative act pursuant to Article I, Section 10 of the
   Constitution of the United States: "No State shall... pass any Law impairing
   the Obligation of Contracts."

4. TRUST ASSETS:
   The trust assets shall include the physical holdings of the community and
   100% ownership of {llc_name} (Commodity Pool & Local Credit Registry).

5. EXECUTION & SOVEREIGN ATTESTATION:
   Dated: {datetime.now().strftime('%Y-%m-%d')}

   ___________________________            ___________________________
   Sovereign Trustee:                     Co-Trustee / Director:
   {trustee_name}
"""
        sovereign_trust_file = os.path.join(drafts_dir, "sovereign_trust_indenture.txt")
        with open(sovereign_trust_file, "w") as f:
            f.write(sovereign_trust_indenture)
        print(f"{GREEN}Drafted Sovereign Trust Indenture saved to: {sovereign_trust_file}{RESET}")
        
        print(f"{BLUE}Drafting Commodity Asset Pool Registry for '{llc_name}'...{RESET}")
        commodity_registry = f"""========================================================================
                     COMMODITY ASSET POOL REGISTRY
                                   OF
                     {llc_name}
========================================================================

1. ESTABLISHMENT OF COMMODITY POOL:
   Pursuant to the Constitutional Trust Indenture of {trust_name}, there is
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
   - {trustee_name} (Primary Custodian)
   - {current_owner_name} (Co-Custodian Board)
"""
        commodity_registry_file = os.path.join(drafts_dir, "commodity_asset_pool_registry.txt")
        with open(commodity_registry_file, "w") as f:
            f.write(commodity_registry)
        print(f"{GREEN}Drafted Commodity Asset Pool Registry saved to: {commodity_registry_file}{RESET}")
        
        print(f"{BLUE}Drafting Board of Managing Directors Dividend Resolution...{RESET}")
        directors_sigs = "\n\n   ___________________________   ".join([f"{d.strip()} (Managing Director)" for d in directors_list])
        dividend_resolution = f"""========================================================================
                BOARD OF MANAGING DIRECTORS DIVIDEND RESOLUTION
                                   OF
                     {trust_name}
========================================================================

WHEREAS, the Board of Managing Directors of {trust_name} has reviewed the
performance, growth, and appreciation of the Physical Gold & Silver reserves
managed under the {llc_name}; and

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
   - Fiduciary Custodian {trustee_name} is authorized and directed to execute
     the transfer of bullion values directly to the secure community wallets.

SO RESOLVED AND ATTESTED BY THE BOARD OF MANAGING DIRECTORS:
{directors_sigs}

Dated: {datetime.now().strftime('%Y-%m-%d')}
"""
        dividend_resolution_file = os.path.join(drafts_dir, "managing_directors_dividend_resolution.txt")
        with open(dividend_resolution_file, "w") as f:
            f.write(dividend_resolution)
        print(f"{GREEN}Drafted Dividend Resolution saved to: {dividend_resolution_file}{RESET}")

    elif path in [1, 2]:
        print_section("PHASE 3: Trust Agreement Formulation")
        print(f"{BLUE}Drafting brand-new Trust Agreement for '{trust_name}'...{RESET}")
        
        trust_agreement = f"""========================================================================
                      TRUST AGREEMENT
========================================================================

1. PARTIES:
   This Trust Agreement is established by the Grantor for the benefit of
   the designated beneficiaries, with:
   Trustee: {trustee_name}
   Trust Address: {trustee_address}

2. TRUST NAME:
   The trust established hereunder shall be known as:
   {trust_name}

3. TRUST ASSETS & PURPOSE:
   The primary asset of this Trust is the 100% membership interest of
   {llc_name}, a limited liability company formed under the laws of the State of {state}.
   The Purpose is: {purpose}.

4. GOVERNING LAW:
   This Trust shall be governed by, construed, and enforced in accordance
   with the laws of the State of {state}.

5. SIGNATURES:
   Dated: {datetime.now().strftime('%Y-%m-%d')}

   ___________________________            ___________________________
   Grantor                                Trustee: {trustee_name}
"""
        trust_file = os.path.join(drafts_dir, "trust_agreement.txt")
        with open(trust_file, "w") as f:
            f.write(trust_agreement)
        print(f"{GREEN}Drafted Trust Agreement saved to: {trust_file}{RESET}")
    else:
        print_section("PHASE 3: Trust Agreement (Skipped)")
        print(f"{YELLOW}Trust already established. Skipping Trust Agreement drafting.{RESET}")

    # 4. Draft Form SS-4 EIN Preparation
    ein_file = None
    if path in [1, 2, 4]:
        print_section("PHASE 4: IRS Form SS-4 EIN Drafting & Scheduling")
        
        if path == 4:
            print(f"{BLUE}Preparing EIN application for Sovereign Trust {trust_name}...{RESET}")
            ein_result = await handle_ein_draft(
                legal_name=trust_name,
                trade_name="",
                responsible_party_ssn="XXX-XX-XXXX",
                responsible_party_name=trustee_name,
                business_type="Common Law Trust",
                mailing_address=trustee_address,
                county_state=f"USA, {state}",
                reason_for_applying="To open a banking/financial account for the non-statutory Trust"
            )
        else:
            print(f"{BLUE}Preparing EIN application for {llc_name} owned by {trust_name}...{RESET}")
            ein_result = await handle_ein_draft(
                legal_name=llc_name,
                trade_name="",
                responsible_party_ssn="XXX-XX-XXXX",
                responsible_party_name=trustee_name,
                business_type="LLC",
                mailing_address=trustee_address,
                county_state=f"USA, {state}",
                reason_for_applying="Started new business (Solely owned by Trust)"
            )
        
        print(f"{GREEN}EIN Draft & Schedule Response:{RESET}\n{ein_result}\n")

        ein_file = os.path.join(drafts_dir, "ein_ss4_draft.txt")
        with open(ein_file, "w") as f:
            f.write(ein_result)
        print(f"{GREEN}Drafted IRS EIN SS-4 saved to: {ein_file}{RESET}")
    else:
        print_section("PHASE 4: IRS Form SS-4 EIN (Skipped)")
        print(f"{YELLOW}Existing entities are fully registered with active tax identifiers. Skipping EIN prep.{RESET}")

    # 5. Draft Assignment of Membership Interest & Amended Operating Agreement
    assignment_file = None
    amended_operating_agreement_file = None
    operating_agreement_file = None

    if path == 4:
        print_section("PHASE 5: Sovereign Operating Protocols (Bypassed)")
        print(f"{YELLOW}Sovereign trust governs the pool via Indenture & Commodity Pool Registry. Bypassing LLC operating agreement.{RESET}")
    elif path in [2, 3]:
        print_section("PHASE 5: Ownership Assignment & Amended Operating Agreement")
        print(f"{BLUE}Generating Assignment of Membership Interest (shifting ownership)...{RESET}")
        
        assignment_agreement = f"""========================================================================
                  ASSIGNMENT OF MEMBERSHIP INTEREST
========================================================================

1. TRANSFER OF INTEREST:
   This Assignment of Membership Interest (the "Assignment") is made and entered into
   by and between:
   Assignor: {current_owner_name} (Current 100% Owner/Member)
   Assignee: {trust_name} (Trust established with Trustee {trustee_name})

2. ASSIGNMENT AND TRANSFER:
   For good and valuable consideration, the receipt and sufficiency of which are
   hereby acknowledged, Assignor hereby transfers, assigns, and conveys to Assignee
   100% of the membership interest, capital interests, and governance rights in:
   Entity Name: {llc_name} (formed under State of {state})

3. ACCEPTANCE AND GOVERNING LAW:
   Assignee hereby accepts the transfer of the Assigned Interest and agrees to
   be bound by all the terms, obligations, and covenants of the Company's Operating Agreement.
   This Assignment is governed by the laws of the State of {state}.

4. EXECUTION:
   Dated: {datetime.now().strftime('%Y-%m-%d')}

   ___________________________            ___________________________
   Assignor: {current_owner_name}              Assignee: {trust_name}
                                          By: {trustee_name}, Trustee
"""
        assignment_file = os.path.join(drafts_dir, "assignment_of_membership_interest.txt")
        with open(assignment_file, "w") as f:
            f.write(assignment_agreement)
        print(f"{GREEN}Drafted Assignment of Membership Interest saved to: {assignment_file}{RESET}")

        print(f"{BLUE}Drafting Amended LLC Operating Agreement incorporating Trust sole membership...{RESET}")
        
        amended_operating_agreement = f"""========================================================================
             AMENDED & RESTATED LIMITED LIABILITY COMPANY OPERATING AGREEMENT
                                OF
                       {llc_name}
========================================================================

1. FORMATION & AMENDMENT:
   This Amended and Restated Operating Agreement is adopted to reflect the shift in
   membership ownership of {llc_name} to {trust_name}.

2. NEW SOLE MEMBER:
   The SOLE MEMBER of this Limited Liability Company is:
   {trust_name} (formed with Trustee {trustee_name})

3. OPERATIONAL STATUTE AMENDMENTS:
   - voting: {operating_rules.split('--- Statutory Summary ---')[-1].split('--- Recommended Template ---')[0].strip()}
   - capital contributions: {capital_rules.split('--- Statutory Summary ---')[-1].split('--- Recommended Template ---')[0].strip()}
   - indemnification: {indemnity_rules.split('--- Statutory Summary ---')[-1].split('--- Recommended Template ---')[0].strip()}

4. SIGNED:
   Assignee Member: {trust_name}
   By: ___________________________ ({trustee_name}, Trustee)
   Dated: {datetime.now().strftime('%Y-%m-%d')}
"""
        amended_operating_agreement_file = os.path.join(drafts_dir, "amended_operating_agreement.txt")
        with open(amended_operating_agreement_file, "w") as f:
            f.write(amended_operating_agreement)
        print(f"{GREEN}Drafted Amended Operating Agreement saved to: {amended_operating_agreement_file}{RESET}")

        # Write Transition / Filing Instructions Guide
        print(f"{BLUE}Drafting Transition / Filing Instructions Guide...{RESET}")
        transition_guide = f"""========================================================================
                      TRANSITION & FILING GUIDE
========================================================================

You have successfully drafted the necessary legal documents to shift ownership of your
existing LLC ({llc_name}) to your Trust ({trust_name}). Follow these step-by-step
filing guidelines to complete the transfer:

Step 1: Execute Legal Documents
- Assignor ({current_owner_name}) and Trustee ({trustee_name}) must sign and date the
  Assignment of Membership Interest.
- The Trustee must sign the Amended & Restated Operating Agreement.
- File both documents securely with your corporate records.

Step 2: Secretary of State Filing (if applicable)
- In the State of {state}, verify if the state requires reporting members or managers.
- If member lists are filed publicly, submit an Amendment of Certificate/Articles to
  designate {trust_name} as the sole managing member.

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
        print(f"{GREEN}Transition Guide saved to: {transition_file}{RESET}")

    else:
        # Path 1 Operating Agreement
        print_section("PHASE 5: LLC Operating Agreement Formulation")
        print(f"{BLUE}Generating standard Sole-Member Operating Agreement for {llc_name}...{RESET}")
        
        template_header = "=== OPERATING AGREEMENT ==="
        if "--- Recommended Template ---" in operating_rules:
            template_header = operating_rules.split("--- Recommended Template ---")[-1].strip()

        llc_operating_agreement = f"""========================================================================
              LIMITED LIABILITY COMPANY OPERATING AGREEMENT
                                OF
                       {llc_name}
========================================================================

1. FORMATION:
   This Limited Liability Company is formed pursuant to the LLC Act of the
   State of {state}.

2. SOLE MEMBER:
   The SOLE MEMBER of this Limited Liability Company is:
   {trust_name} (formed with Trustee {trustee_name})

3. CAPITAL CONTRIBUTIONS & PERCENTAGE INTEREST:
   The Trust holds a 100% membership interest in {llc_name}.
   {capital_rules.split('--- Statutory Summary ---')[-1].split('--- Recommended Template ---')[0].strip()}

4. MANAGEMENT & VOTING:
   Management of the Company is vested solely in the Member.
   {operating_rules.split('--- Statutory Summary ---')[-1].split('--- Recommended Template ---')[0].strip()}

5. INDEMNIFICATION:
   {indemnity_rules.split('--- Statutory Summary ---')[-1].split('--- Recommended Template ---')[0].strip()}

6. TEMPLATE REFERENCE:
{template_header}

7. EXECUTED BY MEMBER:
   Member: {trust_name}
   By: ___________________________ ({trustee_name}, Trustee)
   Dated: {datetime.now().strftime('%Y-%m-%d')}
"""
        operating_agreement_file = os.path.join(drafts_dir, "llc_operating_agreement.txt")
        with open(operating_agreement_file, "w") as f:
            f.write(llc_operating_agreement)
        print(f"{GREEN}Drafted Operating Agreement saved to: {operating_agreement_file}{RESET}")

    # 6. Holding Structure Visualizer Diagram
    print_section("PHASE 6: Holding Structure Visualization")
    
    if path == 1:
        diagram_type = "BRAND NEW STRUCTURE (Trust owned Sole-Member LLC)"
        diagram_flow = f"""
               +-------------------------------------------+
               |                 GRANTOR                   |
               +-------------------------------------------+
                                     |
                                     v (Establishes)
               +-------------------------------------------+
               |          {trust_name:32} |
               |  (Trustee: {trustee_name:31}) |
               +-------------------------------------------+
                                     |
                                     v (Owns 100% of Member Interest)
               +-------------------------------------------+
               |          {llc_name:32} |
               |  (State: {state:34}) |
               +-------------------------------------------+
                                     |
                                     v (Asset / Holding Operations)
                        [Real Estate / IP / Capital]
"""
    elif path in [2, 3]:
        diagram_type = "MIGRATED OWNERSHIP (Assignment of Interest to Trust)"
        diagram_flow = f"""
               +-------------------------------------------+
               |      Assignor: {current_owner_name:26} |
               +-------------------------------------------+
                      |                               |
                      | (Assigns Interest)            | (Establishes)
                      v                               v
               +-------------------------------------------+
               |      Assignee: {trust_name:26} |
               |  (Trustee: {trustee_name:31}) |
               +-------------------------------------------+
                                     |
                                     v (Now Owns 100% of Member Interest)
               +-------------------------------------------+
               |          {llc_name:32} |
               |  (State: {state:34}) |
               +-------------------------------------------+
"""
    else:
        diagram_type = "SOVEREIGN COMMUNITY TRUST & COMMODITY POOL"
        directors_joined = ", ".join([d.strip() for d in current_owner_name.split(",")])
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
               |          {trust_name:32} |
               |  (Trustee/Rep: {trustee_name:27}) |
               |  (Contract Clause: Art. I, Sec. 10)       |
               +-------------------------------------------+
                                     |
                                     v (Manages / Pools Reserves)
               +-------------------------------------------+
               |          {llc_name:32} |
               |  (50.0% Gold Bullion / 50.0% Silver)       |
               |  (Backs Sovereign Liberty Credits)        |
               +-------------------------------------------+
                                     |
                                     v (Distributes)
                    [Commodity Dividend Resolution]
"""

    diagram = f"""========================================================================
                      STRUCTURE VISUALIZER
Path type: {diagram_type}
========================================================================
{diagram_flow}"""
    print(diagram)
    
    diagram_file = os.path.join(drafts_dir, "structure_diagram.txt")
    with open(diagram_file, "w") as f:
        f.write(diagram)
    print(f"{GREEN}Structure Diagram saved to: {diagram_file}{RESET}")

    # Save summary metadata
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "path_selected": path,
        "trust_name": trust_name,
        "trustee_name": trustee_name,
        "trustee_address": trustee_address,
        "llc_name": llc_name,
        "jurisdiction_state": state,
        "business_purpose": purpose,
        "files_generated": {
            "trust_agreement": trust_file,
            "sovereign_trust_indenture": sovereign_trust_file,
            "commodity_asset_pool_registry": commodity_registry_file,
            "managing_directors_dividend_resolution": dividend_resolution_file,
            "llc_operating_agreement": operating_agreement_file,
            "ein_ss4_draft": ein_file,
            "assignment_of_membership_interest": assignment_file,
            "amended_operating_agreement": amended_operating_agreement_file,
            "structure_diagram": diagram_file
        }
    }
    
    summary_file = os.path.join(drafts_dir, "structuring_summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"{GREEN}Summary metadata saved to: {summary_file}{RESET}")

    print(f"\n{BOLD}{GREEN}🎉 SUCCESS! Generalized holding company structuring flow completed successfully!{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())
