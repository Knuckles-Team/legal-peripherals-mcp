"""Regulatory/legal compliance ontology suite — validity, reuse, and cross-link tests.

CONCEPT:LP-OS.governance.compliance-ontology-suite. Validates that ``compliance.ttl``
(the shared upper ontology) and each ``compliance_<framework>.ttl`` module parse as
valid Turtle, declare the expected classes/individuals, import the upper ontology,
reuse (never redefine) the shared hub/legal.ttl classes, and are discoverable through
the package's ``agent_utilities.ontology_providers`` entry-point directory. Also proves
the asset -> data-classification -> regulation join the suite exists for (e.g. a PHI
asset resolves to HIPAA via :classifiedAs/:appliesToDataClass, and directly via
:governedBy).
"""

from __future__ import annotations

from pathlib import Path

import pytest

rdflib = pytest.importorskip("rdflib")
from rdflib.namespace import OWL, RDF  # noqa: E402

ONTOLOGY_DIR = Path(__file__).resolve().parent.parent / "legal_peripherals_mcp" / "ontology"
UPPER_TTL = ONTOLOGY_DIR / "compliance.ttl"
MODULE_TTLS = sorted(ONTOLOGY_DIR.glob("compliance_*.ttl"))

KG = rdflib.Namespace("http://knuckles.team/kg#")
HUB_IRI = rdflib.URIRef("http://knuckles.team/kg")
LEGAL_IRI = rdflib.URIRef("http://knuckles.team/kg/legal")
UPPER_IRI = rdflib.URIRef("http://knuckles.team/kg/legal-compliance")

EXPECTED_UPPER_CLASSES = {
    "RegulatoryAuthority",
    "Obligation",
    "Control",
    "ComplianceRequirement",
    "Penalty",
    "Sector",
    "ReportingRequirement",
    "ComplianceGate",
    "Assessment",
    "Attestation",
}

EXPECTED_UPPER_PROPERTIES = {
    "appliesToSector",
    "appliesToDataClass",
    "imposesObligation",
    "requiresControl",
    "hasReportingRequirement",
    "triggeredByObligation",
    "enforcedBy",
    "violation",
    "derivedFromRegulation",
    "evaluatesRequirement",
    "attestsTo",
}

# Classes/properties this suite must REUSE (not redefine) — already declared in
# agent_utilities' hub ontology.ttl or this package's legal.ttl.
SHARED_CLASSES_NOT_REDEFINED = {
    "Regulation",
    "DataClassification",
    "Organization",
    "System",
    "GovernedEntity",
    "Jurisdiction",
    "Statute",
    "FederalStatute",
    "StateStatute",
    "RegulatoryFiling",
    "BusinessEntity",
    "CorporateGovernanceDoc",
}
SHARED_PROPERTIES_NOT_REDEFINED = {"governedBy", "classifiedAs"}

MODULE_REGULATIONS = {
    "compliance_hipaa.ttl": "HIPAA",
    "compliance_bsa_aml.ttl": "BSA_AML",
    "compliance_occ.ttl": "OCCBankSupervision",
    "compliance_dodd_frank.ttl": "DoddFrank",
    "compliance_cfpb.ttl": "CFPBConsumerProtection",
    "compliance_flsa.ttl": "FLSA",
    "compliance_taxation.ttl": "FederalTaxation",
    "compliance_llc.ttl": "LLCFormationGovernance",
}


def _graph(*paths: Path) -> "rdflib.Graph":
    g = rdflib.Graph()
    for p in paths:
        g.parse(str(p), format="turtle")
    return g


def _full_graph() -> "rdflib.Graph":
    return _graph(UPPER_TTL, *MODULE_TTLS)


# --------------------------------------------------------------------------- #
# Provider discovery
# --------------------------------------------------------------------------- #


def test_provider_globs_all_compliance_modules():
    """The ontology package dir carries the upper ontology + every regulation module the
    task requires; the hub loader globs ``*.ttl`` here with zero extra code."""
    import legal_peripherals_mcp.ontology as provider

    provider_dir = Path(provider.__file__).resolve().parent
    ttls = {p.name for p in provider_dir.glob("*.ttl")}
    assert "legal.ttl" in ttls
    assert "compliance.ttl" in ttls
    for expected in MODULE_REGULATIONS:
        assert expected in ttls, f"{expected} missing from ontology provider dir"


# --------------------------------------------------------------------------- #
# Upper ontology
# --------------------------------------------------------------------------- #


def test_upper_ontology_parses_and_has_iri():
    g = _graph(UPPER_TTL)
    assert len(g) > 0
    assert (UPPER_IRI, RDF.type, OWL.Ontology) in g
    imports = set(g.objects(UPPER_IRI, OWL.imports))
    assert HUB_IRI in imports
    assert LEGAL_IRI in imports


def test_upper_ontology_defines_expected_classes():
    g = _graph(UPPER_TTL)
    for cls in EXPECTED_UPPER_CLASSES:
        assert (KG[cls], RDF.type, OWL.Class) in g, f"missing class :{cls}"


def test_upper_ontology_defines_expected_properties():
    g = _graph(UPPER_TTL)
    for prop in EXPECTED_UPPER_PROPERTIES:
        assert (KG[prop], RDF.type, OWL.ObjectProperty) in g, f"missing property :{prop}"


def test_upper_ontology_declares_canonical_individuals():
    g = _graph(UPPER_TTL)
    for sector in ("FinanceSector", "MedicalSector", "GovernmentSector", "PrivateSector"):
        assert (KG[sector], RDF.type, KG.Sector) in g
    for dataclass in ("PHI", "PII", "PCI", "FinancialData", "CUI"):
        assert (KG[dataclass], RDF.type, KG.DataClassification) in g


def test_upper_ontology_reuses_shared_classes_not_redefines():
    """The compliance suite must reference — never redefine as owl:Class/owl:ObjectProperty —
    classes/properties the hub ontology or this package's legal.ttl already declare."""
    text = UPPER_TTL.read_text()
    for shared in SHARED_CLASSES_NOT_REDEFINED:
        assert f":{shared} a owl:Class" not in text, f":{shared} redefined as owl:Class"
    for shared in SHARED_PROPERTIES_NOT_REDEFINED:
        assert (
            f":{shared} a owl:ObjectProperty" not in text
        ), f":{shared} redefined as owl:ObjectProperty"
    # but it DOES reference :Regulation/:DataClassification/:governedBy/:classifiedAs
    assert ":Regulation" in text
    assert ":DataClassification" in text


# --------------------------------------------------------------------------- #
# Per-regulation modules
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("module_path", MODULE_TTLS, ids=lambda p: p.name)
def test_module_parses(module_path: Path):
    g = _graph(module_path)
    assert len(g) > 0


@pytest.mark.parametrize("module_path", MODULE_TTLS, ids=lambda p: p.name)
def test_module_imports_upper_ontology(module_path: Path):
    g = _graph(module_path)
    ontologies = list(g.subjects(RDF.type, OWL.Ontology))
    assert len(ontologies) == 1, f"{module_path.name} must declare exactly one owl:Ontology"
    imports = set(g.objects(ontologies[0], OWL.imports))
    assert UPPER_IRI in imports, f"{module_path.name} does not import {UPPER_IRI}"


@pytest.mark.parametrize(
    "module_name,regulation", sorted(MODULE_REGULATIONS.items())
)
def test_module_declares_its_regulation_tagged_sector_and_dataclass(
    module_name: str, regulation: str
):
    """Each regulation module declares a :Regulation individual tagged with at least one
    :appliesToSector and one :appliesToDataClass, and names a :RegulatoryAuthority via
    :enforcedBy — the sector/domain-class tagging the task requires."""
    g = _graph(ONTOLOGY_DIR / module_name)
    reg_uri = KG[regulation]
    assert (reg_uri, RDF.type, KG.Regulation) in g, f"{module_name}: {regulation} not a :Regulation"
    sectors = list(g.objects(reg_uri, KG.appliesToSector))
    assert sectors, f"{module_name}: {regulation} has no :appliesToSector"
    dataclasses = list(g.objects(reg_uri, KG.appliesToDataClass))
    assert dataclasses, f"{module_name}: {regulation} has no :appliesToDataClass"
    authorities = list(g.objects(reg_uri, KG.enforcedBy))
    assert authorities, f"{module_name}: {regulation} has no :enforcedBy authority"
    for authority in authorities:
        assert (authority, RDF.type, KG.RegulatoryAuthority) in g


@pytest.mark.parametrize(
    "module_name,regulation", sorted(MODULE_REGULATIONS.items())
)
def test_module_obligations_have_controls(module_name: str, regulation: str):
    """Every Obligation a Regulation imposes requires at least one Control."""
    g = _graph(ONTOLOGY_DIR / module_name)
    reg_uri = KG[regulation]
    obligations = list(g.objects(reg_uri, KG.imposesObligation))
    assert obligations, f"{module_name}: {regulation} imposes no obligations"
    for ob in obligations:
        assert (ob, RDF.type, KG.Obligation) in g
        controls = list(g.objects(ob, KG.requiresControl))
        assert controls, f"{module_name}: {ob} has no :requiresControl"
        for c in controls:
            assert (c, RDF.type, KG.Control) in g


def test_sar_reporting_requirement_cross_references_aml_obligation():
    """Cross-reference required by spec: the BSA SAR ReportingRequirement is triggered by
    an AML Obligation."""
    g = _graph(ONTOLOGY_DIR / "compliance_bsa_aml.ttl")
    assert (KG.BSASARFilingRequirement, RDF.type, KG.ReportingRequirement) in g
    triggers = list(g.objects(KG.BSASARFilingRequirement, KG.triggeredByObligation))
    assert KG.BSAAMLProgramObligation in triggers


def test_llc_module_reuses_legal_ttl_formation_filing_class():
    """The LLC module must reference (not redefine) legal.ttl's :LLCFormationFiling class,
    reusing the package's existing Secretary-of-State/EIN capability."""
    text = (ONTOLOGY_DIR / "compliance_llc.ttl").read_text()
    assert ":LLCFormationFiling a owl:Class" not in text
    assert ":LLCFormationFiling" in text  # referenced in commentary/documentation


# --------------------------------------------------------------------------- #
# Full-suite integrity
# --------------------------------------------------------------------------- #


def test_full_suite_parses_as_one_graph_with_no_local_name_collisions():
    """All ttl files in the ontology dir load together into one graph (the way the hub
    federates them) and no individual/class is declared (as subject) in more than one
    compliance module."""
    all_ttls = sorted(ONTOLOGY_DIR.glob("*.ttl"))
    g = _graph(*all_ttls)
    assert len(g) > 500

    subject_owners: dict[str, set[str]] = {}
    for ttl in [p for p in all_ttls if p.name.startswith("compliance")]:
        mg = _graph(ttl)
        for s in set(mg.subjects()):
            if str(s).startswith(str(KG)):
                subject_owners.setdefault(str(s), set()).add(ttl.name)
    collisions = {s: owners for s, owners in subject_owners.items() if len(owners) > 1}
    assert not collisions, f"local-name collisions across compliance modules: {collisions}"


# --------------------------------------------------------------------------- #
# The asset -> DataClassification -> Regulation cross-link (the join to the shared
# infra/asset ontology).
# --------------------------------------------------------------------------- #


def test_asset_with_phi_dataclass_resolves_to_hipaa_via_applies_to_data_class():
    g = _full_graph()
    example_asset = rdflib.URIRef("http://example.org/test#ExampleAsset")
    # Mirrors how any fleet package's real System/Server node would be classified.
    g.add((example_asset, KG.classifiedAs, KG.PHI))

    query = """
    PREFIX : <http://knuckles.team/kg#>
    SELECT ?regulation WHERE {
        ?asset :classifiedAs ?dataclass .
        ?regulation :appliesToDataClass ?dataclass .
    }
    """
    resolved = {row.regulation for row in g.query(query, initBindings={"asset": example_asset})}
    assert KG.HIPAA in resolved


def test_asset_can_also_be_directly_governed_by_a_regulation():
    """:governedBy (already defined in the hub ontology) is a valid direct edge from any
    governed entity straight to a specific compliance Regulation individual."""
    g = _full_graph()
    example_asset = rdflib.URIRef("http://example.org/test#ExampleAsset2")
    g.add((example_asset, KG.governedBy, KG.HIPAA))
    assert (example_asset, KG.governedBy, KG.HIPAA) in g
    assert (KG.HIPAA, RDF.type, KG.Regulation) in g
