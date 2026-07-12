"""Skill-presence/parity tests for the legal practice-area domain suite.

CONCEPT:LP-OS.governance.legal-domain-suite. Validates every ``SKILL.md`` under
``legal_peripherals_mcp/skills`` has well-formed frontmatter (``name`` matching its
directory, a ``skill_type``, a non-empty ``description``) and that the 18 new
skills covering the regulatory/employment/commercial/privacy practice areas
(+ two cross-domain skills) are present alongside the 3 pre-existing
entity-formation skills.
"""

from __future__ import annotations

from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).resolve().parent.parent / "legal_peripherals_mcp" / "skills"

PRE_EXISTING_SKILLS = {
    "legal-peripherals-entity-lookup",
    "legal-peripherals-ein-filing",
    "legal-peripherals-statute-lookup",
}

NEW_DOMAIN_SKILLS = {
    # regulatory
    "legal-peripherals-regulatory-gap-tracker",
    "legal-peripherals-regulatory-feed-watch",
    "legal-peripherals-policy-redraft",
    # employment
    "legal-peripherals-worker-classification",
    "legal-peripherals-employment-policy-drafting",
    "legal-peripherals-hiring-termination-review",
    "legal-peripherals-internal-investigation",
    "legal-peripherals-leave-tracking",
    "legal-peripherals-international-expansion",
    # commercial
    "legal-peripherals-contract-review",
    "legal-peripherals-contract-lifecycle",
    "legal-peripherals-contract-escalation",
    # privacy
    "legal-peripherals-privacy-agreement-review",
    "legal-peripherals-dsar-response",
    "legal-peripherals-privacy-impact-assessment",
    "legal-peripherals-privacy-gap-monitor",
    # cross-domain / corporate entity-formation
    "legal-peripherals-compliance-watch",
    "legal-peripherals-entity-compliance-tracker",
}


def _frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill_md}: missing frontmatter fence"
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4 : end + 1])


def _skill_dirs() -> list[Path]:
    return sorted(
        p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").exists()
    )


def test_all_expected_skills_present_on_disk():
    found = {p.name for p in _skill_dirs()}
    expected = PRE_EXISTING_SKILLS | NEW_DOMAIN_SKILLS
    missing = expected - found
    assert not missing, f"expected skills missing from disk: {missing}"


def test_every_skill_has_well_formed_frontmatter():
    for skill_dir in _skill_dirs():
        fm = _frontmatter(skill_dir / "SKILL.md")
        assert fm.get("name") == skill_dir.name, (
            f"{skill_dir}: frontmatter name '{fm.get('name')}' != dir name"
        )
        assert fm.get("skill_type") in {"skill", "workflow", "graph"}, (
            f"{skill_dir}: missing/invalid skill_type"
        )
        assert fm.get("description"), f"{skill_dir}: missing description"
        assert fm.get("license"), f"{skill_dir}: missing license"


def test_new_skills_cross_reference_at_least_one_sibling():
    """Every new skill's body links to at least one other legal-peripherals-*
    skill under a Related section — proves the domain isn't a disconnected
    silo, mirroring the ontology's cross-domain-link requirement."""
    for name in NEW_DOMAIN_SKILLS:
        body = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
        assert "## Related" in body, f"{name}: missing Related section"
        assert "legal-peripherals-" in body.split("## Related", 1)[1], (
            f"{name}: Related section doesn't cross-reference a sibling skill"
        )


def test_new_skills_declare_when_not_to_use():
    for name in NEW_DOMAIN_SKILLS:
        body = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
        assert "When NOT to use" in body, f"{name}: missing 'When NOT to use' section"
