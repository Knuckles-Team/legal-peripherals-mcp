# ⚖️ Legal Peripherals MCP Server

<p align="center">
  <img src="https://img.shields.io/badge/FastMCP-Server-4A154B?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastMCP Server">
  <img src="https://img.shields.io/badge/Compliance-IRS%20%7C%2050%20States-20639B?style=for-the-badge" alt="Compliance">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
</p>

A premium Model Context Protocol (MCP) server powered by **FastMCP** that exposes highly robust tools for automating legal operations and filing compliance. This server handles state-level Secretary of State (SOS) entities, off-hours compliant IRS Form SS-4 EIN drafting/scheduling, and corporate/LLC charter templates lookup.

---

## 🗺️ System Architecture

The following diagram illustrates how the `Legal Peripherals MCP Server` coordinates between external LLM clients, state Secretary of State (SOS) databases, the IRS Form SS-4 preparation engine, and local template resources:

```mermaid
graph TD
    Client[LLM / Agent Client] <-->|stdio / Server-Sent Events| MCP[FastMCP Server]
    
    subgraph Core Features [Legal Peripherals Engine]
        MCP -->|SOSTOOL| SOS[Secretary of State Lookup]
        MCP -->|EINTOOL| EIN[IRS Form SS-4 EIN Engine]
        MCP -->|STATUTETOOL| STATUTE["Statute & Charter Templates"]
    end

    subgraph State Scraping Layer
        SOS -->|Deep Scraper| TX[Texas Secretary of State]
        SOS -->|Deep Scraper| DE[Delaware Division of Corporations]
        SOS -->|Deep Scraper| WY[Wyoming Secretary of State]
        SOS -->|Deep Scraper| NV[Nevada SilverFlume]
        SOS -->|LLM Fallback| FB[Resilient Fallback Scraper]
    end

    subgraph IRS Filing Layer
        EIN -->|Check EST Time| activeCheck{"Is Monday-Friday<br/>7:00 AM - 10:00 PM EST?"}
        activeCheck -->|Yes / Override| fileNow[FILING IMMEDIATELY]
        activeCheck -->|No| queueLater[QUEUED FOR SCHEDULING]
    end

    subgraph Statute Knowledge
        STATUTE -->|State Statutes| defaults[Default Rules Mapping]
        STATUTE -->|Documents| templates[Corporate/LLC Charter Templates]
    end
```

---

## 🛠️ MCP Tools Mapping

The server registers the following standard FastMCP tools, which can be dynamically enabled or disabled via environment toggles:

| Tool Name | Parameters | Returns | Description |
| :--- | :--- | :--- | :--- |
| `sos_entity_lookup` | `state` (str), `entity_name` (str), `entity_id` (str, optional) | `str` (JSON/text result) | Performs Secretary of State entity lookups across all 50 states (utilizes optimized scrapers for TX, DE, WY, NV and fallbacks for others). |
| `draft_ein_form` | `legal_name` (str), `responsible_party_ssn` (str), `responsible_party_name` (str), `business_type` (str), etc. | `str` (drafted form & queue details) | Drafts IRS Form SS-4 and schedules filing with strict off-hours compliance (Mon-Fri 7:00 AM - 10:00 PM EST). Supports developer bypass override. |
| `lookup_statute_rules` | `state` (str), `entity_type` (str), `topic` (str) | `str` (statute details & templates) | Queries state statutory default rules (director voting, indemnification, etc.) and retrieves template charter links. |

---

## ⚙️ Environment Variables

Configure the server runtime using a `.env` file or direct container environment injections:

| Environment Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **`SOSTOOL`** | `bool` | `True` | Toggle the `sos_entity_lookup` tool. |
| **`EINTOOL`** | `bool` | `True` | Toggle the `draft_ein_form` tool. |
| **`STATUTETOOL`** | `bool` | `True` | Toggle the `lookup_statute_rules` tool. |
| **`BYPASS_IRS_FILING_HOURS`** | `bool` | `False` | Bypasses the active-hours restriction during development/testing, enabling immediate submission mockups at any hour. |
| **`LEGAL_PERIPHERALS_BASE_URL`** | `str` | `http://localhost:8000` | The base URL of the backing legal peripherals web platform API. |
| **`LEGAL_PERIPHERALS_TOKEN`** | `str` | `""` | The authentication token / bearer credential for the backing API. |
| **`LEGAL_PERIPHERALS_SSL_VERIFY`** | `bool` | `True` | Toggles whether SSL verification is enforced on backing requests. |

---

## 🚀 Deployment & Installation

### Option 1: Bare-Metal Setup (pip)

1. **Clone the Repository & Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your Environment**:
   Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. **Start the Server**:
   ```bash
   python -m legal_peripherals_mcp.mcp_server
   ```

---

### Option 2: Containerized Setup (Docker)

To run the Legal Peripherals MCP Server as a headless background container or expose it via an orchestrator (like Portainer):

1. **Build the Docker Image**:
   ```bash
   docker build -t legal-peripherals-mcp .
   ```

2. **Run the Container**:
   Pass your configuration variables as environment flags:
   ```bash
   docker run -d \
     --name legal-peripherals-mcp-service \
     -e SOSTOOL=True \
     -e EINTOOL=True \
     -e STATUTETOOL=True \
     -e BYPASS_IRS_FILING_HOURS=True \
     legal-peripherals-mcp
   ```

---

## 🧪 Running the Test Suite

We maintain 100% logic coverage using `pytest` to verify off-hours filing computations, bypass states, Secretary of State scrapers, and charter mappings:

```bash
# Run tests with detailed verbose output
pytest -v
```
