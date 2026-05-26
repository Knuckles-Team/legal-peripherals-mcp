# Legal Peripherals MCP Agent Specs

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
