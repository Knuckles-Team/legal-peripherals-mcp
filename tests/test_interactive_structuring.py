"""Characterization tests for the interactive holding-company structuring CLI.

No test coverage existed for this script before (an 871-line, single async
``main()`` with cyclomatic 65 / cognitive 90 covering argument parsing, path
selection, per-path input gathering, and six drafting phases). These exercise
``main()`` end-to-end for every ``--non-interactive`` path plus the interactive
path-selection prompt, mocking the three MCP tool calls it makes (SOS lookup,
statute rules, EIN draft) and redirecting the script's ``drafts_dir`` (derived
from the module's own ``__file__``) to a ``tmp_path`` so the real repo's
``drafts/`` tree is never touched by a test run.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

MODULE_NAME = "scripts.interactive_structuring"


def _load_module(tmp_path: Path):
    """Fresh-import the script, with its ``__file__`` redirected under
    ``tmp_path`` so ``drafts_dir`` (``dirname(dirname(__file__)) / "drafts"``)
    never resolves to the real repo's ``drafts/`` directory."""
    sys.modules.pop(MODULE_NAME, None)
    module = importlib.import_module(MODULE_NAME)
    fake_scripts_dir = tmp_path / "fakerepo" / "scripts"
    fake_scripts_dir.mkdir(parents=True)
    module.__file__ = str(fake_scripts_dir / "interactive_structuring.py")
    return module


def _mock_externals(monkeypatch, module) -> None:
    monkeypatch.setattr(
        module, "handle_sos_lookup", AsyncMock(return_value="SOS: entity is active")
    )
    monkeypatch.setattr(
        module,
        "handle_statute_rules",
        AsyncMock(
            return_value=(
                "--- Statutory Summary ---\nDefault majority-vote rule applies.\n"
                "--- Recommended Template ---\nSTANDARD TEMPLATE TEXT"
            )
        ),
    )
    monkeypatch.setattr(
        module,
        "handle_ein_draft",
        AsyncMock(return_value="=== SS-4 DRAFT ===\nLegal Name: Test Entity"),
    )


def _run_main(monkeypatch, module, argv: list[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["interactive_structuring.py", *argv])
    import asyncio

    asyncio.run(module.main())


@pytest.mark.concept("LEGAL-004")
@pytest.mark.parametrize("path", [1, 2, 3, 4])
def test_main_non_interactive_generates_expected_files_per_path(
    tmp_path, monkeypatch, capsys, path
):
    """Every non-interactive path completes and writes its phase-specific files
    plus a structure diagram and summary -- without prompting for input."""
    module = _load_module(tmp_path)
    _mock_externals(monkeypatch, module)

    _run_main(monkeypatch, module, ["--path", str(path), "--non-interactive"])

    out = capsys.readouterr().out
    assert "SUCCESS" in out

    drafts_dir = tmp_path / "fakerepo" / "drafts"
    summary = json.loads((drafts_dir / "structuring_summary.json").read_text())
    assert summary["path_selected"] == path
    assert (drafts_dir / "structure_diagram.txt").exists()

    generated = summary["files_generated"]
    if path == 4:
        assert generated["sovereign_trust_indenture"] is not None
        assert generated["commodity_asset_pool_registry"] is not None
        assert generated["managing_directors_dividend_resolution"] is not None
        assert generated["trust_agreement"] is None
        assert generated["llc_operating_agreement"] is None
        assert generated["assignment_of_membership_interest"] is None
        assert generated["ein_ss4_draft"] is not None  # path 4 drafts an EIN
    elif path == 1:
        assert generated["trust_agreement"] is not None
        assert generated["llc_operating_agreement"] is not None
        assert generated["ein_ss4_draft"] is not None
        assert generated["assignment_of_membership_interest"] is None
    elif path == 2:
        assert generated["trust_agreement"] is not None
        assert generated["assignment_of_membership_interest"] is not None
        assert generated["amended_operating_agreement"] is not None
        assert generated["ein_ss4_draft"] is not None
        assert generated["llc_operating_agreement"] is None
    else:  # path == 3: link pre-existing entities, no new trust, no EIN
        assert generated["trust_agreement"] is None
        assert generated["assignment_of_membership_interest"] is not None
        assert generated["amended_operating_agreement"] is not None
        assert generated["ein_ss4_draft"] is None
        assert generated["llc_operating_agreement"] is None


@pytest.mark.concept("LEGAL-004")
def test_main_non_interactive_path4_bypasses_sos_lookup(tmp_path, monkeypatch, capsys):
    """Path 4 (sovereign trust) asserts non-statutory status and never calls the
    real SOS lookup tool."""
    module = _load_module(tmp_path)
    _mock_externals(monkeypatch, module)

    _run_main(monkeypatch, module, ["--path", "4", "--non-interactive"])

    module.handle_sos_lookup.assert_not_awaited()
    out = capsys.readouterr().out
    assert "Non-Statutory/Common Law Trust" in out


@pytest.mark.concept("LEGAL-004")
def test_main_non_interactive_other_paths_call_sos_lookup(tmp_path, monkeypatch):
    """Paths 1-3 perform a real SOS lookup for the LLC."""
    module = _load_module(tmp_path)
    _mock_externals(monkeypatch, module)

    _run_main(monkeypatch, module, ["--path", "1", "--non-interactive"])

    module.handle_sos_lookup.assert_awaited_once()
    _, kwargs = module.handle_sos_lookup.await_args
    assert kwargs["state"] == "DE"
    assert kwargs["entity_name"] == "Liberty Holdings LLC"


@pytest.mark.concept("LEGAL-004")
def test_main_non_interactive_respects_explicit_field_overrides(tmp_path, monkeypatch):
    """Explicit --trust-name/--llc-name/etc. args win over the path's defaults."""
    module = _load_module(tmp_path)
    _mock_externals(monkeypatch, module)

    _run_main(
        monkeypatch,
        module,
        [
            "--path",
            "1",
            "--non-interactive",
            "--trust-name",
            "Custom Trust",
            "--llc-name",
            "Custom LLC",
            "--state",
            "tx",
        ],
    )

    drafts_dir = tmp_path / "fakerepo" / "drafts"
    summary = json.loads((drafts_dir / "structuring_summary.json").read_text())
    assert summary["trust_name"] == "Custom Trust"
    assert summary["llc_name"] == "Custom LLC"
    assert summary["jurisdiction_state"] == "TX"  # normalized upper-case


@pytest.mark.concept("LEGAL-004")
def test_main_interactive_path_selection_prompts_when_no_path_given(
    tmp_path, monkeypatch, capsys
):
    """With no --path and not --non-interactive, the CLI prompts for a
    selection, and all subsequent prompts are also driven by stdin."""
    module = _load_module(tmp_path)
    _mock_externals(monkeypatch, module)

    # One input() answer per prompt: path selection, then path-1's six prompts.
    answers = iter(
        [
            "1",  # path selection
            "Interactive Trust",
            "Interactive Trustee",
            "123 Test St",
            "Interactive LLC",
            "NV",
            "Testing purposes",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    _run_main(monkeypatch, module, [])

    out = capsys.readouterr().out
    assert "Selected Path: Path 1" in out
    assert "SUCCESS" in out

    drafts_dir = tmp_path / "fakerepo" / "drafts"
    summary = json.loads((drafts_dir / "structuring_summary.json").read_text())
    assert summary["trust_name"] == "Interactive Trust"
    assert summary["llc_name"] == "Interactive LLC"
    assert summary["jurisdiction_state"] == "NV"


@pytest.mark.concept("LEGAL-004")
def test_main_interactive_path_selection_defaults_to_1_on_bad_input(
    tmp_path, monkeypatch, capsys
):
    """A non-numeric path selection answer falls back to path 1 rather than
    raising."""
    module = _load_module(tmp_path)
    _mock_externals(monkeypatch, module)

    answers = iter(
        [
            "not-a-number",  # path selection -> falls back to 1
            "T",
            "TT",
            "TA",
            "L",
            "DE",
            "P",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    _run_main(monkeypatch, module, [])

    out = capsys.readouterr().out
    assert "Selected Path: Path 1" in out
