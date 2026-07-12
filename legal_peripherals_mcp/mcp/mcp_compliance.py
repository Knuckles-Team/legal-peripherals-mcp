"""CONCEPT:LP-OS.governance.legal-compliance-kb Action-routed compliance-ontology lookup.

Answers structured queries against the package's bundled OWL/RDF compliance +
domain ontology suite (``legal_peripherals_mcp/ontology/*.ttl``) — no external API,
no fabrication. This is the KG-native grounding surface every new domain skill
(regulatory, employment, commercial, privacy, corporate, litigation) calls into for
"what does this regulation require" / "what controls satisfy this data class" /
"what does a compliance gate require for this data classification" answers.
"""

from __future__ import annotations

from typing import Any

from agent_utilities.base_utilities import get_logger

from legal_peripherals_mcp.compliance_kb import ComplianceLookupError, run_action

logger = get_logger(__name__)


async def handle_compliance_lookup(
    action: str,
    regulation: str = "",
    sector: str = "",
    data_class: str = "",
    data_classes: str = "",
    ctx: Any = None,
) -> dict[str, Any]:
    """Run one ``legal_compliance_lookup`` action against the bundled ontology suite.

    Actions: ``list_domains``, ``list_regulations`` (optional ``sector``/
    ``data_class`` filter), ``regulation_detail`` (requires ``regulation``),
    ``sector_lookup`` (requires ``sector``), ``dataclass_lookup`` (requires
    ``data_class``), ``gate_requirements`` (requires comma-separated
    ``data_classes``).
    """
    if ctx:
        await ctx.info(f"legal_compliance_lookup action={action}")
    try:
        result = run_action(
            action,
            regulation=regulation,
            sector=sector,
            data_class=data_class,
            data_classes=data_classes,
        )
        return {"action": action, "result": result}
    except ComplianceLookupError as exc:
        logger.warning("Compliance lookup failed: %s", exc)
        return {"action": action, "error": str(exc)}
