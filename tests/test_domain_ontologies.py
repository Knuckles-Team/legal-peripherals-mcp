"""Legal practice-area domain ontology suite — validity, reuse, and cross-link
tests for the ``domain_<name>.ttl`` modules.

CONCEPT:LP-OS.governance.legal-domain-suite. Validates that each
``domain_regulatory.ttl`` / ``domain_employment.ttl`` / ``domain_commercial.ttl`` /
``domain_privacy.ttl`` / ``domain_corporate.ttl`` / ``domain_litigation.ttl`` module
parses as valid Turtle, imports ``compliance.ttl`` + ``legal.ttl``, declares its
expected classes, is discoverable through the ``agent_utilities.ontology_providers``
entry-point directory, and cross-links into the existing compliance/legal ontology
(FLSA, HIPAA, LLC) rather than floating disconnected. Mirrors
``test_compliance_ontology.py``'s style.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

rdflib = pytest.importorskip("rdflib")
from rdflib.namespace import OWL, RDF  # noqa: E402

ONTOLOGY_DIR = (
    Path(__file__).resolve().parent.parent / "legal_peripherals_mcp" / "ontology"
)
UPPER_TTL = ONTOLOGY_DIR / "compliance.ttl"
LEGAL_TTL = ONTOLOGY_DIR / "legal.ttl"
DOMAIN_TTLS = sorted(ONTOLOGY_DIR.glob("domain_*.ttl"))

KG = rdflib.Namespace("http://knuckles.team/kg#")
UPPER_IRI = rdflib.URIRef("http://knuckles.team/kg/legal-compliance")
LEGAL_IRI = rdflib.URIRef("http://knuckles.team/kg/legal")

DOMAIN_MODULES = {
    "domain_regulatory.ttl": {
        "iri": "http://knuckles.team/kg/legal-domain-regulatory",
        "classes": {
            "RegulatoryChangeNotice",
            "RegulatoryComment",
            "AgencyGuidance",
            "EnforcementAction",
            "ComplianceGapRemediation",
        },
    },
    "domain_employment.ttl": {
        "iri": "http://knuckles.team/kg/legal-domain-employment",
        "classes": {
            "Employee",
            "EmploymentContract",
            "RestrictiveCovenant",
            "HandbookPolicy",
            "WorkerClassificationAssessment",
            "InternalInvestigation",
            "LeaveRequest",
            "InternationalExpansionProject",
        },
    },
    "domain_commercial.ttl": {
        "iri": "http://knuckles.team/kg/legal-domain-commercial",
        "classes": {
            "Contract",
            "NDAAgreement",
            "MSAAgreement",
            "VendorAgreement",
            "ContractAmendment",
            "RenewalDeadline",
            "ContractReviewFinding",
            "EscalationRoute",
        },
    },
    "domain_privacy.ttl": {
        "iri": "http://knuckles.team/kg/legal-domain-privacy",
        "classes": {
            "DataSubjectRequest",
            "DataProcessingAgreement",
            "PrivacyImpactAssessment",
            "ProcessingActivity",
            "ConsentRecord",
        },
    },
    "domain_corporate.ttl": {
        "iri": "http://knuckles.team/kg/legal-domain-corporate",
        "classes": {
            "Company",
            "BoardResolution",
            "WrittenConsent",
            "DiligenceFinding",
            "MaterialContract",
            "ClosingChecklistItem",
            "EntityComplianceDeadline",
        },
    },
    "domain_litigation.ttl": {
        "iri": "http://knuckles.team/kg/legal-domain-litigation",
        "classes": {
            "DemandLetter",
            "LegalHold",
            "Deposition",
            "PrivilegeLogEntry",
            "Subpoena",
            "ClaimChart",
            "ChronologyEvent",
        },
    },
}


def _graph(*paths: Path) -> Any:
    g = rdflib.Graph()
    for p in paths:
        g.parse(str(p), format="turtle")
    return g


def _full_graph() -> Any:
    return _graph(
        UPPER_TTL, LEGAL_TTL, *ONTOLOGY_DIR.glob("compliance_*.ttl"), *DOMAIN_TTLS
    )


# --------------------------------------------------------------------------- #
# Provider discovery
# --------------------------------------------------------------------------- #


def test_provider_globs_all_domain_modules():
    """The ontology package dir carries every domain module; the hub loader globs
    ``*.ttl`` here with zero extra code."""
    import legal_peripherals_mcp.ontology as provider

    provider_dir = Path(provider.__file__).resolve().parent
    ttls = {p.name for p in provider_dir.glob("*.ttl")}
    for expected in DOMAIN_MODULES:
        assert expected in ttls, f"{expected} missing from ontology provider dir"


def test_init_docstring_documents_domain_modules():
    """The task requires each new domain module be added to __init__.py's docstring."""
    import legal_peripherals_mcp.ontology as provider

    doc = provider.__doc__ or ""
    for module_name in DOMAIN_MODULES:
        assert module_name in doc, (
            f"{module_name} not documented in ontology/__init__.py"
        )


# --------------------------------------------------------------------------- #
# Per-module structure
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("module_path", DOMAIN_TTLS, ids=lambda p: p.name)
def test_module_parses(module_path: Path):
    g = _graph(module_path)
    assert len(g) > 0


@pytest.mark.parametrize(
    "module_name,spec",
    sorted(DOMAIN_MODULES.items()),
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_module_declares_ontology_iri_and_imports(module_name: str, spec: dict):
    g = _graph(ONTOLOGY_DIR / module_name)
    onto_iri = rdflib.URIRef(spec["iri"])
    assert (onto_iri, RDF.type, OWL.Ontology) in g
    imports = set(g.objects(onto_iri, OWL.imports))
    assert UPPER_IRI in imports, (
        f"{module_name} does not import the compliance upper ontology"
    )
    assert LEGAL_IRI in imports, f"{module_name} does not import legal.ttl"


@pytest.mark.parametrize(
    "module_name,spec",
    sorted(DOMAIN_MODULES.items()),
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_module_defines_expected_classes(module_name: str, spec: dict):
    g = _graph(ONTOLOGY_DIR / module_name)
    for cls in spec["classes"]:
        assert (KG[cls], RDF.type, OWL.Class) in g, (
            f"{module_name}: missing class :{cls}"
        )


# --------------------------------------------------------------------------- #
# Cross-domain links (the task's explicit ask: FLSA / HIPAA / LLC cross-links)
# --------------------------------------------------------------------------- #


def test_employment_worker_classification_cross_links_flsa_obligations():
    g = _full_graph()
    outcomes = list(
        g.objects(
            KG.MisclassifiedContractorAssessment, KG.classificationTriggersObligation
        )
    )
    assert KG.FLSAMinimumWageObligation in outcomes
    assert KG.FLSAOvertimeObligation in outcomes


def test_commercial_contract_cross_links_hipaa_attestation_via_dataclass():
    g = _full_graph()
    assert (KG.ExamplePHIVendorAgreement, KG.classifiedAs, KG.PHI) in g
    assert (KG.ExamplePHIVendorAgreement, KG.governedBy, KG.HIPAA) in g
    assert (
        KG.ExamplePHIVendorAgreement,
        KG.requiresAttestation,
        KG.HIPAABusinessAssociateAgreement,
    ) in g


def test_corporate_entity_compliance_deadline_tracks_llc_reporting_requirement():
    g = _full_graph()
    assert (
        KG.ExampleLLCAnnualReportDeadline,
        KG.tracksRequirement,
        KG.LLCAnnualReportRequirement,
    ) in g


def test_privacy_declares_gdpr_and_ccpa_tagged_pii():
    g = _full_graph()
    for reg in (KG.GDPR, KG.CCPA):
        assert (reg, RDF.type, KG.Regulation) in g
        assert (reg, KG.appliesToDataClass, KG.PII) in g
        obligations = list(g.objects(reg, KG.imposesObligation))
        assert obligations
        for ob in obligations:
            assert list(g.objects(ob, KG.requiresControl))


def test_litigation_matter_composes_with_employment_domain():
    """A litigation ClaimChart/ChronologyEvent attaches to the SAME EmploymentLawMatter
    individual employment's module would use — proving the domain modules compose on
    one shared entity rather than each owning a disconnected silo."""
    g = _full_graph()
    assert (KG.ExampleWageHourMatter, RDF.type, KG.EmploymentLawMatter) in g
    assert (KG.ExampleWageHourMatter, KG.governedByEmploymentStatute, KG.FLSA) in g
    assert (
        KG.ExampleWageHourClaimChart,
        KG.chartsCauseOfAction,
        KG.ExampleWageHourMatter,
    ) in g
    assert (
        KG.ExampleWageHourChronologyEvent,
        KG.partOfMatter,
        KG.ExampleWageHourMatter,
    ) in g


def test_regulatory_gap_remediation_cross_links_hipaa_requirement():
    g = _full_graph()
    assert (
        KG.PHIEncryptionGapRemediation,
        KG.remediatesGap,
        KG.HIPAAPHIEncryptionRequirement,
    ) in g


# --------------------------------------------------------------------------- #
# Full-suite integrity
# --------------------------------------------------------------------------- #


def test_full_suite_including_domain_modules_parses_as_one_graph():
    all_ttls = sorted(ONTOLOGY_DIR.glob("*.ttl"))
    g = _graph(*all_ttls)
    assert len(g) > 1000


def test_domain_modules_declare_no_duplicate_class_across_each_other():
    """No two domain modules primarily TYPE (rdf:type) the same local-named subject —
    intentional cross-file *enrichment* triples (e.g. domain_employment.ttl adding
    :documentedInPolicy to compliance_flsa.ttl's :FLSATimekeepingControl) are fine and
    expected; a duplicate ``a owl:Class``/individual declaration is not."""
    typed_subject_owners: dict[str, set[str]] = {}
    for ttl in DOMAIN_TTLS:
        g = _graph(ttl)
        for s in set(g.subjects(RDF.type, None)):
            if str(s).startswith(str(KG)):
                typed_subject_owners.setdefault(str(s), set()).add(ttl.name)
    collisions = {
        s: owners for s, owners in typed_subject_owners.items() if len(owners) > 1
    }
    assert not collisions, (
        f"duplicate type declarations across domain modules: {collisions}"
    )


def test_new_classes_do_not_redefine_existing_upper_or_legal_or_compliance_classes():
    """Guards against the domain modules accidentally redeclaring a class already
    owned by compliance.ttl / legal.ttl / another compliance_<x>.ttl module."""
    already_declared: set[str] = set()
    for ttl in [UPPER_TTL, LEGAL_TTL, *sorted(ONTOLOGY_DIR.glob("compliance_*.ttl"))]:
        g = _graph(ttl)
        already_declared |= {
            str(s).rsplit("#", 1)[-1] for s in g.subjects(RDF.type, OWL.Class)
        }
    for module_name, spec in DOMAIN_MODULES.items():
        overlap = spec["classes"] & already_declared
        assert not overlap, f"{module_name} redeclares existing class(es): {overlap}"
