# Legal Peripherals MCP Agent Specs

> Claude Code loads this file via `CLAUDE.md` (`@AGENTS.md` import) — the two stay
> in sync. Edit **this** file, not `CLAUDE.md`.

<!-- CONCEPT:LEGAL-001 -->
<!-- CONCEPT:LEGAL-002 -->
<!-- CONCEPT:LEGAL-003 -->

This file acts as a machine-readable README for AI coding agents collaborating on this repository.

## Tech Stack & Architecture
- **Language**: Python >= 3.11
- **Ecosystem**: `agent-utilities` Dynamic Facade
- **MCP Server**: FastMCP (stdio and HTTP support)
- **Key Files**:
  - `legal_peripherals_mcp/mcp_server.py`: FastMCP entry points and tool registration.
  - `legal_peripherals_mcp/api_client.py`: API facade inheriting from custom domain modules.
  - `legal_peripherals_mcp/auth.py`: Credentials loading, credential validation, and authentication headers.

## Commands

### Quality & Linting
Run pre-commit hooks locally:
```bash
pre-commit run --all-files
```

### Execution & Run
Launch the FastMCP server in stdio mode:
```bash
python -m legal_peripherals_mcp.mcp_server
```

### Testing Suite
Execute the entire test suite:
```bash
pytest -v
```

## Project Structure

### File Tree
```text
.
├── .bumpversion.cfg
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
├── README.md
├── pyproject.toml
├── requirements.txt
├── docs
│   ├── concepts.md
│   ├── index.md
│   └── overview.md
├── docker
│   └── compose.yml
└── legal_peripherals_mcp
    ├── __init__.py
    ├── agent_server.py
    ├── api_client.py
    ├── auth.py
    ├── mcp
    │   ├── __init__.py
    │   ├── mcp_ein.py
    │   ├── mcp_sos.py
    │   └── mcp_statute.py
    └── mcp_server.py
```

## Concept Registry

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:LEGAL-001` | Secretary of State Crawlers | Dynamic business entity lookup & verifications across 50 states |
| `CONCEPT:LEGAL-002` | IRS EIN & Off-Hours Filing | SS-4 PDF drafting and scheduling compliance operations |
| `CONCEPT:LEGAL-003` | Statutes & Charter Templates | LLC/corporate filing guidelines and dynamic template lookups |
| `CONCEPT:ECO-4.0` | Ecosystem Compliance | Multi-package integration compliance standard |

---

## When Stuck
1. Check the local mock context implementation in `tests/conftest.py`.
2. Propose an Implementation Plan first before adding new endpoints.

## ⛔ No Scratch or Temporary Files in Repository

**NEVER write any of the following to this repository:**
- Temporary test scripts (`test_*.py`, `debug_*.py` outside of `tests/`)
- Scratch scripts or experimental one-off files
- Log files (`.log`, `.txt` command output)
- Random text files with command output or debug dumps
- Any file that is NOT production source code, tests in `tests/`, or documentation

**Why:** These files expose private filesystem paths, credentials, and internal infrastructure details when pushed to GitHub publicly.

**Where to put scratch work instead:**
- Use `~/workspace/scratch/` for temporary scripts and experiments
- Use `~/workspace/reports/` for command output and reports
- Keep test scripts in the `tests/` directory following proper pytest conventions


## ⛔ Keep the Repository Root Pristine — No Scratch / Temp / Debug Files

**The repository ROOT must contain only canonical project files** (packaging,
config, docs, lockfiles). The only hidden directories allowed at root are
`.git/`, `.github/`, and `.specify/` (plus a local, git-ignored `.venv/`).

**NEVER write any of the following — anywhere in the repo, and ESPECIALLY at the root:**
- One-off / debug / migration scripts: `fix_*.py`, `migrate_*.py`, `refactor_*.py`,
  `replace_*.py`, `update_*.py`, `debug_*.py`, or `test_*.py` **at the root**
  (real tests live in `tests/` only).
- Databases / data dumps: `*.db`, `*.db-wal`, `*.sqlite*`, `*.corrupted`.
- Logs / command output: `*.log`, scratch `*.txt`, `*.orig`, `*.rej`, `*.bak`.
- Build artifacts: `*.tsbuildinfo`, compiled binaries, coverage files.
- AI agent scratch directories: `.agent/`, `.agents/`, `.agent_data/`, `.tmp/`,
  `.hypothesis/`, or any per-tool cache committed to git.
- Any file that is NOT production source, a test in `tests/`, documentation, or
  a recognized config/lockfile.

**Why:** scratch at the root leaks private paths/credentials, bloats the tree,
and erodes a pristine codebase.

**Where scratch goes instead:** `~/workspace/scratch/` (experiments),
`~/workspace/reports/` (command output); tests go in `tests/` (pytest).
Before finishing a task, run `git status` and confirm no stray root files were added.
