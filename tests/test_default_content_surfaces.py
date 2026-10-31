"""CONN-LEGAL-PERIPHERALS-MCP-CONNECTOR-CONTENT-R001: the server lists its packaged skills, ontology and prompts by default."""

from __future__ import annotations

import asyncio
import importlib
from pathlib import Path

import pytest
from fastmcp import Client

PACKAGE = "legal_peripherals_mcp"
ROOT = Path(list(importlib.import_module(PACKAGE).__path__)[0])

pytestmark = pytest.mark.spec("CONN-LEGAL-PERIPHERALS-MCP-CONNECTOR-CONTENT-R001")


def _server():
    from unittest.mock import patch

    from fastmcp import FastMCP

    module = importlib.import_module("legal_peripherals_mcp.mcp_server")
    with patch(
        "sys.argv", ["connector", "--transport", "stdio", "--auth-type", "none"]
    ):
        result = module.get_mcp_instance()
    if isinstance(result, FastMCP):
        return result
    return next(value for value in result if isinstance(value, FastMCP))


async def _listings():
    from importlib.metadata import version

    async with Client(_server(), mode="legacy") as client:
        assert client.initialize_result is not None
        assert client.initialize_result.server_info.version == version(
            "legal-peripherals-mcp"
        )
        resources = {str(r.uri) for r in await client.list_resources()}
        prompts = {p.name for p in await client.list_prompts()}
        for uri in resources:
            if uri.startswith(("ontology://", "shapes://")):
                directory = ROOT / "ontology"
                if uri.startswith("shapes://"):
                    directory = directory / "shapes"
                actual = await client.read_resource(uri)
                assert (
                    actual[0].text.encode()
                    == (directory / uri.rsplit("/", 1)[-1]).read_bytes()
                )
    return resources, prompts


def test_default_content_surfaces() -> None:
    resources, prompts = asyncio.run(_listings())
    if list(ROOT.glob("skills/*/SKILL.md")):
        assert any(u.startswith("skill://") for u in resources)
    if list(ROOT.glob("ontology/*.ttl")):
        assert any(u.startswith("ontology://legal-peripherals-mcp/") for u in resources)
    for path in ROOT.glob("prompts/*.json"):
        if not path.name.startswith("_"):
            assert path.stem in prompts


@pytest.fixture(autouse=True)
def _no_outbound_network(monkeypatch):
    import socket

    attempts = []

    def refuse(*_args, **_kwargs):
        attempts.append(1)
        raise AssertionError("content publication must not contact an external system")

    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")
    monkeypatch.setattr(socket.socket, "connect", refuse)
    yield
    assert not attempts, "outbound attempts must not be swallowed by an adapter"
    print("external_network_connect_attempts=0")


def test_sdk_floor_supports_content_identity_and_current_pack_protocol() -> None:
    import tomllib
    from packaging.requirements import Requirement

    project = tomllib.loads((ROOT.parent / "pyproject.toml").read_text())["project"]
    declared = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        declared.extend(extra)
    sdk = [Requirement(value) for value in declared if value.startswith("scion-sdk")]
    assert sdk
    for requirement in sdk:
        from packaging.version import Version

        floor = max(Version(s.version) for s in requirement.specifier if s.operator == ">=")
        assert floor >= Version("0.6.3")
        assert not requirement.specifier.contains("0.7.0")
        assert not requirement.specifier.contains("0.5.9")


def test_production_pack_binds_packaged_ontology_and_shapes():
    import hashlib
    from importlib.metadata import version

    from scion_sdk.artifacts.pack import build_content_pack
    from scion_sdk.artifacts.resources import ResourceArtifactKind
    from scion_sdk.ports.session import TransportEndpoint
    from scion_sdk.transports.mcp import McpTransport

    async def capture():
        async with McpTransport().session(
            TransportEndpoint(in_process=_server(), mcp_min_interval_seconds=0.1)
        ) as session:
            raw_requirements = {
                str(resource.uri): resource.model_dump(mode="json", by_alias=True)
                .get("_meta", {})
                .get("eg.annotations", {})
                .get("requires_capabilities", [])
                for resource in await session.list_resources()
            }
            pack = await build_content_pack(
                session,
                connector="legal-peripherals-mcp",
                kinds=(ResourceArtifactKind(),),
            )
            return pack, raw_requirements

    pack, raw_requirements = asyncio.run(capture())
    assert pack.server_package_version == version("legal-peripherals-mcp")
    entries = {str(entry.uri): entry for entry in pack.archive.entries}
    assert "connector://resources" in entries
    for path in ROOT.glob("ontology/**/*.ttl"):
        scheme = "shapes" if path.parent.name == "shapes" else "ontology"
        uri = f"{scheme}://legal-peripherals-mcp/{path.name}"
        entry = entries[uri]
        body = pack.archive.data[
            entry.body.offset : entry.body.offset + entry.body.length
        ]
        assert entry.body.sha256 == hashlib.sha256(body).hexdigest()
        # The SDK scopes external imports into declared pack requirements. The
        # raw MCP resource is byte-exact above; the pack must preserve every
        # other triple and record each removed import, without fetching it.
        from rdflib import Graph
        from rdflib.compare import isomorphic
        from rdflib.namespace import OWL

        expected = Graph().parse(data=path.read_text(), format="turtle")
        ontology_uris = {key for key in entries if key.startswith("ontology://")}
        removed = {
            str(target)
            for _, _, target in expected.triples((None, OWL.imports, None))
            if str(target) not in ontology_uris or str(target) == uri
        }
        for triple in list(expected.triples((None, OWL.imports, None))):
            if str(triple[2]) in removed:
                expected.remove(triple)
        actual = Graph().parse(data=body.decode(), format="turtle")
        assert isomorphic(actual, expected), path.name
        assert set(entry.annotations.requires_capabilities or ()) == (
            set(raw_requirements[uri])
            | {"ontology-import:" + target for target in removed}
        )
        if not removed:
            assert entry.body.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()


def test_canonical_and_legacy_routes_preserve_the_full_tool_surface():
    from scion_sdk.connector import build_server

    async def capture():
        _, canonical = build_server(
            PACKAGE, command_args=["--transport", "stdio", "--auth-type", "none"]
        )
        async with (
            Client(_server()) as legacy_client,
            Client(canonical) as canonical_client,
        ):
            legacy = {
                tool.name: tool.model_dump(mode="json")
                for tool in await legacy_client.list_tools()
            }
            declared = {
                tool.name: tool.model_dump(mode="json")
                for tool in await canonical_client.list_tools()
            }
        assert len(legacy) == 9
        assert declared == legacy

    asyncio.run(capture())


def test_legacy_cli_configuration_file_still_controls_host_and_port(
    tmp_path, monkeypatch
):
    import json

    from legal_peripherals_mcp.mcp_server import get_mcp_instance

    config = tmp_path / "connector.json"
    config.write_text(json.dumps({"HOST": "127.0.0.1", "PORT": 9187}))
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("CONNECTOR_CONFIG_FILE", str(config))
    _, args, _ = get_mcp_instance(
        command_args=["--transport", "stdio", "--auth-type", "none"]
    )
    assert (args.host, args.port) == ("127.0.0.1", 9187)


def test_each_server_registers_existing_ingest_tools_once(monkeypatch):
    from scion_sdk.connector import build_server

    module = importlib.import_module("legal_peripherals_mcp.mcp_server")
    calls = []
    original = module.register_ingest_tools

    def track(server):
        calls.append(server)
        return original(server)

    monkeypatch.setattr(module, "register_ingest_tools", track)
    legacy = _server()
    _, canonical = build_server(
        PACKAGE, command_args=["--transport", "stdio", "--auth-type", "none"]
    )
    assert calls == [legacy, canonical]


def test_sdk_loader_preserves_explicit_source_mapping_and_resource_contracts():
    from scion_sdk.ingest.live_declaration import load_declaration

    from legal_peripherals_mcp import connector_sources as declared

    actual = load_declaration(PACKAGE)
    assert actual.connector == "legal-peripherals-mcp"
    assert (
        len(actual.sources),
        len(actual.schema_mappings),
        len(actual.resources),
    ) == (1, 70, 70)
    sources = {item.source_id: item for item in actual.sources}
    for item in declared.SOURCES:
        for entry in item["connector_sources"]:
            source = sources[entry["source_id"]]
            assert source.tools == (entry["tool"],)
            for field, value in entry.items():
                if field not in {"tool", "mapping"}:
                    assert getattr(source, field) == value
    assert set(actual.schema_mappings) == set(declared.SCHEMA_MAPPINGS)
    for name, mapping in declared.SCHEMA_MAPPINGS.items():
        assert actual.schema_mappings[name].fields == mapping["fields"]
        assert actual.schema_mappings[name].ontology_class == mapping.get(
            "ontology_class"
        )
    resources = {item.name: item for item in actual.resources}
    for resource in declared.RESOURCES:
        for field, value in resource.items():
            assert getattr(resources[resource["name"]], field) == value
