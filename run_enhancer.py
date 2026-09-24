#!/usr/bin/env python3
import importlib.util
import json
import os
import time
from pathlib import Path

from legal_peripherals_mcp._persistence_privacy_compat import sanitize_for_persistence

# Paths
SCRIPTS_DIR_VALUE = os.getenv("CODE_ENHANCER_SCRIPTS_DIR")
if not SCRIPTS_DIR_VALUE:
    raise SystemExit("CODE_ENHANCER_SCRIPTS_DIR must be configured")
SCRIPTS_DIR = Path(SCRIPTS_DIR_VALUE).expanduser().resolve()
PROJECT_DIR = Path(__file__).parent.resolve()
SPECIFY_DIR = PROJECT_DIR / ".specify"


_ANALYZERS = [
    ("analyze_project", "analyze_project"),
    ("audit_dependencies", "audit_dependencies"),
    ("analyze_codebase", "analyze_codebase"),
    ("analyze_security", "analyze_security"),
    ("analyze_tests", "analyze_tests"),
    ("audit_documentation", "audit_documentation"),
    ("analyze_architecture", "analyze_architecture"),
    ("trace_concepts", "trace_concepts"),
    ("run_linters", "run_linters"),
    ("run_precommit", "run_precommit"),
    ("run_tests", "run_tests"),
    ("analyze_directory_density", "analyze_directory_density"),
    ("analyze_ui", "analyze_ui"),
    ("analyze_version_sync", "analyze_version_sync"),
    ("audit_changelog", "audit_changelog"),
    ("grade_pytest", "grade_pytest"),
    ("scan_env_vars", "scan_env_vars"),
]


def _load_analyzer_function(module_name: str, func_name: str):
    """Dynamically load one analyzer script's entry-point function.

    Returns ``None`` (and prints a notice) when the script's import spec can't
    be built at all -- a state distinct from the script existing but failing.
    """
    script_path = SCRIPTS_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, str(script_path))
    if spec is None or spec.loader is None:
        print(f"❌ Could not load spec for {module_name}")
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, func_name)


def _run_one_analyzer(module_name: str, func_name: str) -> dict | None:
    """Run one analyzer script against ``PROJECT_DIR``.

    Returns the analyzer's result dict, ``None`` if its spec couldn't be
    built, or a synthesized F-grade fallback dict if it raised.
    """
    print(f"\n🔍 Running analyzer: {module_name}...")
    start_time = time.monotonic()
    try:
        func = _load_analyzer_function(module_name, func_name)
        if func is None:
            return None
        result = func(str(PROJECT_DIR))
        elapsed = time.monotonic() - start_time
        print(
            f"✅ Finished {module_name} in {elapsed:.2f}s (Score: {result.get('score', 'N/A')}, Grade: {result.get('grade', 'N/A')})"
        )
        return result
    except Exception as e:
        print(f"Operation failed: {type(e).__name__}")
        return {
            "domain": module_name.replace("_", " ").title(),
            "score": 0,
            "grade": "F",
            "findings": [f"Analysis error: {type(e).__name__[:200]}"],
            "justifications": [],
        }


def _run_all_analyzers(analyzers: list[tuple[str, str]]) -> list[dict]:
    """Run every analyzer, keeping results with a real score (excludes -1/N-A)."""
    results = []
    for module_name, func_name in analyzers:
        result = _run_one_analyzer(module_name, func_name)
        if result is not None and result.get("score", 0) != -1:
            results.append(result)
    return results


def _write_results_json(safe_results: list[dict]) -> None:
    SPECIFY_DIR.mkdir(parents=True, exist_ok=True)
    results_json_path = SPECIFY_DIR / "results.json"
    results_json_path.write_text(json.dumps(safe_results, indent=2), encoding="utf-8")
    print("💾 Sanitized results saved successfully")


def _generate_markdown_report(safe_results: list[dict]) -> None:
    try:
        report_spec = importlib.util.spec_from_file_location(
            "generate_report", str(SCRIPTS_DIR / "generate_report.py")
        )
        if report_spec is None or report_spec.loader is None:
            raise Exception("Could not load generate_report spec")
        report_module = importlib.util.module_from_spec(report_spec)
        report_spec.loader.exec_module(report_module)

        report_md_path = SPECIFY_DIR / "reports" / "code_enhancement_report.md"
        report_md_path.parent.mkdir(parents=True, exist_ok=True)

        report_module.generate_report(
            safe_results,
            project_name=PROJECT_DIR.name,
            output_path=str(report_md_path),
        )
        print("📄 Prettified report written successfully")
    except Exception as e:
        print(f"Operation failed: {type(e).__name__}")


def _generate_sdd_handoff_artifact(results: list[dict]) -> None:
    try:
        sdd_spec = importlib.util.spec_from_file_location(
            "generate_sdd_handoff", str(SCRIPTS_DIR / "generate_sdd_handoff.py")
        )
        if sdd_spec is None or sdd_spec.loader is None:
            raise Exception("Could not load generate_sdd_handoff spec")
        sdd_module = importlib.util.module_from_spec(sdd_spec)
        sdd_spec.loader.exec_module(sdd_module)

        sdd_module.generate_sdd_handoff(
            results, project_name=PROJECT_DIR.name, output_dir=str(PROJECT_DIR)
        )
        print("🎯 SDD handoff successfully written to: .specify/specs/")
    except Exception as e:
        print(f"Operation failed: {type(e).__name__}")


def run_enhancer():
    print("🚀 Starting Code Enhancer on project:", PROJECT_DIR.name)

    results = _run_all_analyzers(_ANALYZERS)

    print("\n📝 Compiling final results...")
    safe_results, _privacy_report = sanitize_for_persistence(results)

    _write_results_json(safe_results)
    _generate_markdown_report(safe_results)
    _generate_sdd_handoff_artifact(results)


if __name__ == "__main__":
    run_enhancer()
