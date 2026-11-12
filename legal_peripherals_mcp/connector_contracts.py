"""Surface contracts: tool use, links, data locations and business roles."""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

CONTRACTS = (
    ToolUseContract(
        "look-up-an-entity",
        (
            ToolStep(
                "sos_entity_lookup",
                params=("state", "entity_name", "entity_id"),
                result=("status", "entities", "source"),
                refusals=(
                    Refusal(
                        "NOT_CONFIGURED",
                        "the lookup source is not configured, no record is fabricated",
                    ),
                    Refusal(
                        "INVALID_ARGUMENT",
                        "the state, entity type, topic or data class is not one the tool documents",
                    ),
                ),
            ),
            ToolStep(
                "legal_ingest_sos_entities",
                params=("state", "entity_name", "limit"),
                result=("listed", "entities", "ingested"),
                refusals=(
                    Refusal(
                        "NOT_CONFIGURED",
                        "the lookup source is not configured, no record is fabricated",
                    ),
                    Refusal(
                        "NO_ENGINE",
                        "no knowledge-graph engine is reachable, ingested is null",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "file-for-an-ein",
        (
            ToolStep(
                "lookup_statute_rules",
                params=("state", "entity_type", "topic"),
                result=("rules", "template"),
                refusals=(
                    Refusal(
                        "INVALID_ARGUMENT",
                        "the state, entity type, topic or data class is not one the tool documents",
                    ),
                ),
            ),
            ToolStep(
                "draft_ein_form",
                params=(
                    "legal_name",
                    "trade_name",
                    "responsible_party_name",
                    "business_type",
                    "mailing_address",
                    "county_state",
                    "reason_for_applying",
                    "first_date_wages_paid",
                    "max_employees",
                    "closing_month_tax_year",
                ),
                result=("draft", "scheduled_at", "status"),
                refusals=(
                    Refusal(
                        "OUTSIDE_FILING_HOURS",
                        "the IRS online EIN window (Mon-Fri 7:00-22:00 Eastern) is closed, the filing is scheduled instead",
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the user has not confirmed every field",
                    ),
                ),
            ),
            ToolStep(
                "legal_ingest_filing_file",
                params=("file_path", "filing_type", "name"),
                result=("file", "ingested"),
                refusals=(
                    Refusal(
                        "NO_ENGINE",
                        "no knowledge-graph engine is reachable, ingested is null",
                    ),
                    Refusal("FILE_MISSING", "the file path is not a readable file"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "research-a-state-statute",
        (
            ToolStep(
                "legal_list_statute_coverage",
                result=("states", "entity_types", "topics", "specific_rules"),
            ),
            ToolStep(
                "lookup_statute_rules",
                params=("state", "entity_type", "topic"),
                result=("rules", "template"),
                refusals=(
                    Refusal(
                        "INVALID_ARGUMENT",
                        "the state, entity type, topic or data class is not one the tool documents",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "track-entity-compliance",
        (
            ToolStep(
                "sos_entity_lookup",
                params=("state", "entity_name", "entity_id"),
                result=("status", "entities"),
                refusals=(
                    Refusal(
                        "NOT_CONFIGURED",
                        "the lookup source is not configured, no record is fabricated",
                    ),
                    Refusal(
                        "INVALID_ARGUMENT",
                        "the state, entity type, topic or data class is not one the tool documents",
                    ),
                ),
            ),
            ToolStep(
                "lookup_statute_rules",
                params=("state", "entity_type", "topic"),
                result=("rules",),
                refusals=(
                    Refusal(
                        "INVALID_ARGUMENT",
                        "the state, entity type, topic or data class is not one the tool documents",
                    ),
                ),
            ),
            ToolStep(
                "legal_ingest_sos_entities",
                params=("state", "entity_name", "limit"),
                result=("listed", "ingested"),
                refusals=(
                    Refusal(
                        "NOT_CONFIGURED",
                        "the lookup source is not configured, no record is fabricated",
                    ),
                ),
            ),
            ToolStep(
                "legal_lookup_sector",
                params=("sector",),
                result=("sector", "regulations"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "ground-a-regulatory-question",
        (
            ToolStep(
                "legal_list_compliance_domains",
                result=("domains",),
            ),
            ToolStep(
                "legal_list_regulations",
                params=("sector", "data_class"),
                result=("regulations", "sector", "data_class"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_get_regulation",
                params=("regulation",),
                result=(
                    "regulation",
                    "authority",
                    "obligations",
                    "controls",
                    "penalties",
                    "reporting_requirements",
                ),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_lookup_sector",
                params=("sector",),
                result=("sector", "regulations"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_lookup_data_class",
                params=("data_class",),
                result=("data_class", "regulations", "controls"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "gate-data-classes",
        (
            ToolStep(
                "legal_lookup_data_class",
                params=("data_class",),
                result=("data_class", "regulations", "controls"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_gate_requirements",
                params=("data_classes",),
                result=("regulations", "controls"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_get_regulation",
                params=("regulation",),
                result=(
                    "regulation",
                    "authority",
                    "obligations",
                    "controls",
                    "penalties",
                    "reporting_requirements",
                ),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "review-an-employment-matter",
        (
            ToolStep(
                "legal_list_regulations",
                params=("sector", "data_class"),
                result=("regulations", "sector", "data_class"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_get_regulation",
                params=("regulation",),
                result=(
                    "regulation",
                    "authority",
                    "obligations",
                    "controls",
                    "penalties",
                    "reporting_requirements",
                ),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_lookup_sector",
                params=("sector",),
                result=("sector", "regulations"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_ingest_filing_file",
                params=("file_path", "filing_type", "name"),
                result=("file", "ingested"),
                refusals=(
                    Refusal(
                        "NO_ENGINE",
                        "no knowledge-graph engine is reachable, ingested is null",
                    ),
                    Refusal("FILE_MISSING", "the file path is not a readable file"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "review-a-commercial-contract",
        (
            ToolStep(
                "legal_list_regulations",
                params=("sector", "data_class"),
                result=("regulations", "sector", "data_class"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_get_regulation",
                params=("regulation",),
                result=(
                    "regulation",
                    "authority",
                    "obligations",
                    "controls",
                    "penalties",
                    "reporting_requirements",
                ),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
            ToolStep(
                "legal_lookup_data_class",
                params=("data_class",),
                result=("data_class", "regulations", "controls"),
                refusals=(
                    Refusal(
                        "NOT_FOUND", "the ontology suite has no entry with that name"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "record-a-filing-document",
        (
            ToolStep(
                "legal_ingest_filing_file",
                params=("file_path", "filing_type", "name"),
                result=("file", "ingested"),
                refusals=(
                    Refusal(
                        "NO_ENGINE",
                        "no knowledge-graph engine is reachable, ingested is null",
                    ),
                    Refusal("FILE_MISSING", "the file path is not a readable file"),
                ),
            ),
        ),
    ),
)

LINKS = (
    SurfaceLink(
        "look-up-an-entity",
        tools=("sos_entity_lookup", "legal_ingest_sos_entities"),
        prompts=(
            "legal-peripherals-operator",
            "legal-peripherals-formation-specialist",
        ),
        skills=("legal-peripherals-entity-lookup",),
    ),
    SurfaceLink(
        "file-for-an-ein",
        tools=("lookup_statute_rules", "draft_ein_form", "legal_ingest_filing_file"),
        prompts=(
            "legal-peripherals-operator",
            "legal-peripherals-formation-specialist",
        ),
        skills=("legal-peripherals-ein-filing",),
    ),
    SurfaceLink(
        "research-a-state-statute",
        tools=("legal_list_statute_coverage", "lookup_statute_rules"),
        prompts=(
            "legal-peripherals-operator",
            "legal-peripherals-formation-specialist",
        ),
        skills=("legal-peripherals-statute-lookup",),
    ),
    SurfaceLink(
        "track-entity-compliance",
        tools=(
            "sos_entity_lookup",
            "lookup_statute_rules",
            "legal_ingest_sos_entities",
            "legal_lookup_sector",
        ),
        prompts=(
            "legal-peripherals-operator",
            "legal-peripherals-formation-specialist",
        ),
        skills=("legal-peripherals-entity-compliance-tracker",),
    ),
    SurfaceLink(
        "ground-a-regulatory-question",
        tools=(
            "legal_list_compliance_domains",
            "legal_list_regulations",
            "legal_get_regulation",
            "legal_lookup_sector",
            "legal_lookup_data_class",
        ),
        prompts=("legal-peripherals-operator", "legal-peripherals-compliance-counsel"),
        skills=(
            "legal-peripherals-regulatory-gap-tracker",
            "legal-peripherals-regulatory-feed-watch",
            "legal-peripherals-policy-redraft",
            "legal-peripherals-compliance-watch",
            "legal-peripherals-mcp-operations",
        ),
    ),
    SurfaceLink(
        "gate-data-classes",
        tools=(
            "legal_lookup_data_class",
            "legal_gate_requirements",
            "legal_get_regulation",
        ),
        prompts=("legal-peripherals-operator", "legal-peripherals-compliance-counsel"),
        skills=(
            "legal-peripherals-privacy-agreement-review",
            "legal-peripherals-dsar-response",
            "legal-peripherals-privacy-impact-assessment",
            "legal-peripherals-privacy-gap-monitor",
        ),
    ),
    SurfaceLink(
        "review-an-employment-matter",
        tools=(
            "legal_list_regulations",
            "legal_get_regulation",
            "legal_lookup_sector",
            "legal_ingest_filing_file",
        ),
        prompts=("legal-peripherals-operator", "legal-peripherals-employment-counsel"),
        skills=(
            "legal-peripherals-worker-classification",
            "legal-peripherals-employment-policy-drafting",
            "legal-peripherals-hiring-termination-review",
            "legal-peripherals-internal-investigation",
            "legal-peripherals-leave-tracking",
            "legal-peripherals-international-expansion",
        ),
    ),
    SurfaceLink(
        "review-a-commercial-contract",
        tools=(
            "legal_list_regulations",
            "legal_get_regulation",
            "legal_lookup_data_class",
        ),
        prompts=("legal-peripherals-operator", "legal-peripherals-commercial-counsel"),
        skills=(
            "legal-peripherals-contract-review",
            "legal-peripherals-contract-lifecycle",
            "legal-peripherals-contract-escalation",
        ),
    ),
    SurfaceLink(
        "record-a-filing-document",
        tools=("legal_ingest_filing_file",),
        prompts=(
            "legal-peripherals-operator",
            "legal-peripherals-compliance-counsel",
            "legal-peripherals-employment-counsel",
        ),
        skills=(
            "legal-peripherals-regulatory-gap-tracker",
            "legal-peripherals-leave-tracking",
            "legal-peripherals-internal-investigation",
        ),
    ),
)

LOCATIONS = (
    DataLocation(
        "secretary-of-state-records",
        ("BusinessEntity", "Jurisdiction"),
        "OPENCORPORATES_API_TOKEN",
        "sos_entity_lookup",
        route_param="state",
        federation_key="entity_id",
    ),
    DataLocation(
        "state-statute-rules",
        ("Statute", "CharterTemplate"),
        "legal_peripherals_mcp/compliance_kb.py",
        "lookup_statute_rules",
        route_param="state",
    ),
    DataLocation(
        "compliance-ontology-suite",
        ("Regulation", "Obligation", "Control", "Sector", "DataClassification"),
        "legal_peripherals_mcp/ontology",
        "legal_get_regulation",
        federation_key="regulation",
    ),
    DataLocation(
        "legal-filing-drafts",
        ("LegalFiling", "MediaAsset"),
        "drafts",
        "legal_ingest_filing_file",
        federation_key="file",
    ),
)

ROLES = (
    BusinessRole(
        "formation-specialist",
        tasks=(
            "look-up-an-entity",
            "file-for-an-ein",
            "research-a-state-statute",
            "track-entity-compliance",
        ),
    ),
    BusinessRole(
        "compliance-counsel",
        tasks=(
            "ground-a-regulatory-question",
            "gate-data-classes",
            "record-a-filing-document",
        ),
    ),
    BusinessRole(
        "employment-counsel",
        tasks=("review-an-employment-matter", "record-a-filing-document"),
    ),
    BusinessRole("commercial-counsel", tasks=("review-a-commercial-contract",)),
)
