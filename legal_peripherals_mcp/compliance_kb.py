"""CONCEPT:LP-OS.governance.legal-compliance-kb Ontology-native compliance lookups.

Loads every ``*.ttl`` module bundled under ``legal_peripherals_mcp/ontology`` — the
same directory the ``agent_utilities.ontology_providers`` hub federates — into one
in-memory rdflib graph and answers structured queries against it. No external API,
no fabrication: every answer traces back to a declared ontology triple (a
:Regulation, :Obligation, :Control, ...). Backs the ``legal_compliance_lookup``
action-routed MCP tool (``legal_peripherals_mcp/mcp/mcp_compliance.py``).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

KG = "http://knuckles.team/kg#"
ONTOLOGY_DIR = Path(__file__).resolve().parent / "ontology"

VALID_ACTIONS = frozenset(
    {
        "list_domains",
        "list_regulations",
        "regulation_detail",
        "sector_lookup",
        "dataclass_lookup",
        "gate_requirements",
    }
)


class ComplianceLookupError(Exception):
    """Raised for an invalid action or an entity not found in the ontology suite."""


def _uri(name: str):
    import rdflib

    return rdflib.URIRef(f"{KG}{name}")


@lru_cache(maxsize=1)
def _graph():
    """Parse the full bundled ontology suite once and cache the merged graph.

    ``rdflib`` is a last-resort Python fallback kept out of the slim MCP serving
    image (the engine's native RDF/SPARQL surface is the primary path — see
    agent-utilities' dependency-discipline note on the semantic-web stack);
    this reports an honest unavailability notice instead of crashing when
    it isn't installed.
    """
    try:
        import rdflib
    except ImportError as exc:  # pragma: no cover - exercised only without rdflib
        raise ComplianceLookupError(
            "rdflib is not installed; install legal-peripherals-mcp[ontology] "
            "(or [all]) to enable legal_compliance_lookup, or query the "
            "epistemic-graph engine's native RDF/SPARQL surface instead."
        ) from exc

    g = rdflib.Graph()
    for path in sorted(ONTOLOGY_DIR.glob("*.ttl")):
        g.parse(str(path), format="turtle")
    return g


def _local_name(uri: Any) -> str:
    text = str(uri)
    return text.rsplit("#", 1)[-1] if "#" in text else text.rsplit("/", 1)[-1]


def _label(g: Any, uri: Any) -> str:
    from rdflib.namespace import RDFS

    lbl = g.value(uri, RDFS.label)
    return str(lbl) if lbl is not None else _local_name(uri)


def _comment(g: Any, uri: Any) -> str:
    from rdflib.namespace import RDFS

    c = g.value(uri, RDFS.comment)
    return str(c) if c is not None else ""


def list_domains() -> list[dict[str, Any]]:
    """List every owl:Ontology module federated in this package's ontology dir."""
    g = _graph()
    from rdflib.namespace import OWL, RDF

    out = []
    for onto in g.subjects(RDF.type, OWL.Ontology):
        imports = sorted(str(i) for i in g.objects(onto, OWL.imports))
        out.append(
            {
                "iri": str(onto),
                "label": _label(g, onto),
                "comment": _comment(g, onto),
                "imports": imports,
            }
        )
    return sorted(out, key=lambda d: d["iri"])


def list_regulations(sector: str = "", data_class: str = "") -> list[dict[str, Any]]:
    """List :Regulation individuals, optionally filtered by Sector or DataClassification.

    ``sector``/``data_class`` match either the short local name (e.g. ``PHI``,
    ``MedicalSector``) or the full rdfs:label (e.g. ``Protected Health
    Information``, ``Medical Sector``), case-insensitively.
    """
    g = _graph()
    from rdflib.namespace import RDF

    def _matches(uris: Any, needle: str) -> bool:
        if not needle:
            return True
        needle_lc = needle.strip().lower()
        return any(
            needle_lc in _local_name(u).lower() or needle_lc in _label(g, u).lower()
            for u in uris
        )

    out = []
    for reg in g.subjects(RDF.type, _uri("Regulation")):
        sector_uris = list(g.objects(reg, _uri("appliesToSector")))
        dataclass_uris = list(g.objects(reg, _uri("appliesToDataClass")))
        sectors = [_label(g, s) for s in sector_uris]
        data_classes = [_label(g, d) for d in dataclass_uris]
        if not _matches(sector_uris, sector):
            continue
        if not _matches(dataclass_uris, data_class):
            continue
        authorities = [_label(g, a) for a in g.objects(reg, _uri("enforcedBy"))]
        out.append(
            {
                "id": _local_name(reg),
                "label": _label(g, reg),
                "comment": _comment(g, reg),
                "sectors": sectors,
                "data_classes": data_classes,
                "authorities": authorities,
            }
        )
    return sorted(out, key=lambda r: r["id"])


def regulation_detail(regulation: str) -> dict[str, Any]:
    """Full detail for one :Regulation individual — obligations, controls, penalties, reporting."""
    if not regulation:
        raise ComplianceLookupError(
            "regulation is required for action=regulation_detail"
        )
    g = _graph()
    from rdflib.namespace import RDF

    reg_uri = _uri(regulation)
    if (reg_uri, RDF.type, _uri("Regulation")) not in g:
        raise ComplianceLookupError(
            f"No Regulation named '{regulation}' in the ontology suite."
        )

    obligations = []
    for ob in g.objects(reg_uri, _uri("imposesObligation")):
        controls = [
            {"id": _local_name(c), "label": _label(g, c), "comment": _comment(g, c)}
            for c in g.objects(ob, _uri("requiresControl"))
        ]
        penalties = [_label(g, p) for p in g.objects(ob, _uri("violation"))]
        obligations.append(
            {
                "id": _local_name(ob),
                "label": _label(g, ob),
                "comment": _comment(g, ob),
                "controls": controls,
                "penalties": penalties,
            }
        )

    reporting = [
        {"id": _local_name(r), "label": _label(g, r), "comment": _comment(g, r)}
        for r in g.objects(reg_uri, _uri("hasReportingRequirement"))
    ]

    return {
        "id": _local_name(reg_uri),
        "label": _label(g, reg_uri),
        "comment": _comment(g, reg_uri),
        "sectors": [_label(g, s) for s in g.objects(reg_uri, _uri("appliesToSector"))],
        "data_classes": [
            _label(g, d) for d in g.objects(reg_uri, _uri("appliesToDataClass"))
        ],
        "authorities": [_label(g, a) for a in g.objects(reg_uri, _uri("enforcedBy"))],
        "obligations": obligations,
        "reporting_requirements": reporting,
    }


def sector_lookup(sector: str) -> list[dict[str, Any]]:
    """Regulations applying to a named Sector (finance/medical/government/private)."""
    if not sector:
        raise ComplianceLookupError("sector is required for action=sector_lookup")
    return list_regulations(sector=sector)


def dataclass_lookup(data_class: str) -> list[dict[str, Any]]:
    """Regulations applying to a named DataClassification (e.g. PHI, PII, PCI, FinancialData, CUI)."""
    if not data_class:
        raise ComplianceLookupError(
            "data_class is required for action=dataclass_lookup"
        )
    return list_regulations(data_class=data_class)


def gate_requirements(data_classes: list[str]) -> dict[str, Any]:
    """Resolve the ComplianceRequirement/Control set a governed entity must satisfy.

    Mirrors the join a :ComplianceGate performs: given the data classifications a
    service/asset/contract carries, resolve every applicable :Regulation and the
    Control(s) each of its Obligations requires.
    """
    if not data_classes:
        raise ComplianceLookupError(
            "data_classes is required for action=gate_requirements"
        )

    regulations = []
    seen: set[str] = set()
    for dc in data_classes:
        for reg in list_regulations(data_class=dc):
            if reg["id"] in seen:
                continue
            seen.add(reg["id"])
            regulations.append(regulation_detail(reg["id"]))

    controls: set[str] = set()
    for reg in regulations:
        for ob in reg["obligations"]:
            for c in ob["controls"]:
                controls.add(c["label"])

    return {
        "data_classes": data_classes,
        "applicable_regulations": [r["id"] for r in regulations],
        "required_controls": sorted(controls),
        "detail": regulations,
    }


def run_action(action: str, **kwargs: Any) -> Any:
    """Dispatch a ``legal_compliance_lookup`` MCP action to its handler."""
    if action not in VALID_ACTIONS:
        raise ComplianceLookupError(
            f"Unknown action '{action}'. Valid actions: {sorted(VALID_ACTIONS)}"
        )
    if action == "list_domains":
        return list_domains()
    if action == "list_regulations":
        return list_regulations(
            sector=kwargs.get("sector", ""), data_class=kwargs.get("data_class", "")
        )
    if action == "regulation_detail":
        return regulation_detail(kwargs.get("regulation", ""))
    if action == "sector_lookup":
        return sector_lookup(kwargs.get("sector", ""))
    if action == "dataclass_lookup":
        return dataclass_lookup(kwargs.get("data_class", ""))
    if action == "gate_requirements":
        raw = kwargs.get("data_classes") or ""
        data_classes = (
            raw
            if isinstance(raw, list)
            else [d.strip() for d in raw.split(",") if d.strip()]
        )
        return gate_requirements(data_classes)
    raise ComplianceLookupError(f"Unhandled action '{action}'.")  # pragma: no cover
