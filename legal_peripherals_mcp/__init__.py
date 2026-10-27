from agent_connector_sdk.connector_identity import connector_version

__version__ = connector_version("legal_peripherals_mcp")
_MCP_AVAILABLE = True


from agent_connector_sdk.connector import Connector
from agent_connector_sdk.connector_hooks import RegistrationContext


def _register_legacy_surface(context: RegistrationContext) -> None:
    from legal_peripherals_mcp.mcp_server import register_server_surface

    register_server_surface(context.server)


connector = Connector(
    instructions="Legal Peripherals MCP Server - Automate state registrations and filing compliance.",
    extra_registrations=(_register_legacy_surface,),
)
