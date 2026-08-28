"""Characterization tests for the top-level Code Enhancer CLI driver.

Exercises ``run_enhancer.run_enhancer`` against a temp
``CODE_ENHANCER_SCRIPTS_DIR`` populated with a couple of fake analyzer/report/
handoff scripts, with the module's ``SPECIFY_DIR`` patched to a temp directory
so the real project's ``.specify/`` tree is never touched by the test run.
"""

from __future__ import annotations

import importlib
import json
import sys
import textwrap
from pathlib import Path

import pytest


def _load_module(monkeypatch, scripts_dir: Path, specify_dir: Path):
    monkeypatch.setenv("CODE_ENHANCER_SCRIPTS_DIR", str(scripts_dir))
    sys.modules.pop("run_enhancer", None)
    module = importlib.import_module("run_enhancer")
    monkeypatch.setattr(module, "SPECIFY_DIR", specify_dir)
    return module


def _write_script(scripts_dir: Path, name: str, body: str) -> None:
    (scripts_dir / f"{name}.py").write_text(textwrap.dedent(body), encoding="utf-8")


@pytest.mark.concept("LEGAL-003")
def test_run_enhancer_aggregates_success_missing_and_filtered_analyzers(
    tmp_path, monkeypatch, capsys
):
    """One analyzer scores, one is filtered (score -1), and the fifteen with no
    matching script on disk each fail to load and are recorded as an F-grade
    fallback -- exercising the success, filtered, and load-failure branches of
    the analyzer loop in one run."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    specify_dir = tmp_path / ".specify"

    _write_script(
        scripts_dir,
        "analyze_project",
        """
        def analyze_project(project_dir):
            return {
                "domain": "Project",
                "score": 90,
                "grade": "A",
                "findings": [],
                "justifications": [],
            }
        """,
    )
    _write_script(
        scripts_dir,
        "audit_dependencies",
        """
        def audit_dependencies(project_dir):
            return {
                "domain": "Dependencies",
                "score": -1,
                "grade": "N/A",
                "findings": [],
                "justifications": [],
            }
        """,
    )
    _write_script(
        scripts_dir,
        "generate_report",
        """
        def generate_report(results, *, project_name, output_path):
            from pathlib import Path

            Path(output_path).write_text("report for " + project_name, encoding="utf-8")
        """,
    )
    _write_script(
        scripts_dir,
        "generate_sdd_handoff",
        """
        def generate_sdd_handoff(results, *, project_name, output_dir):
            pass
        """,
    )

    module = _load_module(monkeypatch, scripts_dir, specify_dir)
    module.run_enhancer()

    out = capsys.readouterr().out
    assert "Finished analyze_project" in out
    assert "Operation failed" in out  # the 15 analyzers with no script on disk

    results_path = specify_dir / "results.json"
    assert results_path.exists()
    saved = json.loads(results_path.read_text(encoding="utf-8"))
    domains = {r["domain"] for r in saved}
    assert "Project" in domains
    assert "Dependencies" not in domains  # score == -1 is filtered out
    assert any(r["grade"] == "F" for r in saved)  # load-failure fallback entries

    report_path = specify_dir / "reports" / "code_enhancement_report.md"
    assert report_path.exists()
    assert "report for" in report_path.read_text(encoding="utf-8")


@pytest.mark.concept("LEGAL-003")
def test_run_enhancer_survives_missing_report_and_handoff_scripts(
    tmp_path, monkeypatch, capsys
):
    """generate_report.py / generate_sdd_handoff.py absent from SCRIPTS_DIR is a
    handled failure (printed, not raised) -- run_enhancer must still return."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    specify_dir = tmp_path / ".specify"

    module = _load_module(monkeypatch, scripts_dir, specify_dir)
    module.run_enhancer()  # must not raise

    out = capsys.readouterr().out
    assert "Compiling final results" in out
    assert (specify_dir / "results.json").exists()
    assert not (specify_dir / "reports" / "code_enhancement_report.md").exists()
