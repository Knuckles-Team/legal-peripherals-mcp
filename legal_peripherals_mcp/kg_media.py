"""Native epistemic-graph blob ingestion for drafted legal filings.

CONCEPT:AU-KG.ingest.list-durable-media. Drafted filing artifacts (SS-4 drafts, trust
indentures, operating agreements — the ``drafts/*.txt`` files this package produces) are
stored as content-addressed **blobs** with a ``:MediaAsset`` graph node carrying the
filing metadata, in ONE cross-modal ACID commit, via the agent-utilities ``MediaStore``
(surfaced through ``native_ingest.media_store``). This makes the raw filing bytes — not
just a filesystem path — durable, deduped, and queryable inside the knowledge graph.

The required native media authority surfaces engine failures explicitly.
"""

from __future__ import annotations

import logging
import mimetypes
import os
from typing import Any


logger = logging.getLogger("legal_peripherals_mcp.kg_media")

_SOURCE = "legal-peripherals-mcp"


def _media_store(*args: object, **kwargs: object) -> object:
    """Build the required native ``MediaStore`` authority.

    SDK-GAP: Always raises now; see KnowledgeGraphIngestUnavailable.
    """
    _kg_unavailable("_media_store")


def _resolve_media_store(media_store: Any | None) -> Any:
    return media_store if media_store is not None else _media_store()


def _read_filing_bytes(file_path: str) -> bytes | None:
    """Read a filing file's bytes; ``None`` (logged) on any read failure."""
    try:
        with open(file_path, "rb") as fh:
            return fh.read()
    except OSError as e:
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return None


def _filing_metadata(
    filing_type: str, file_path: str, extra: dict[str, Any] | None
) -> dict[str, Any]:
    meta = {"filing_type": filing_type, "filename": os.path.basename(file_path)}
    if extra:
        meta.update({k: v for k, v in extra.items() if v is not None})
    return meta


def _store_filing_asset(
    store: Any, data: bytes, mime: str, display: str, meta: dict[str, Any]
) -> Any:
    return store.store_media(
        data,
        media_type="document",
        mime_type=mime,
        source=_SOURCE,
        name=display,
        extra=meta,
    )


def ingest_filing_file(
    file_path: str | None,
    *,
    filing_type: str = "legal_document",
    name: str = "",
    extra: dict[str, Any] | None = None,
    media_store: Any | None = None,
) -> dict[str, Any] | None:
    """Store a drafted filing file as a blob + ``:MediaAsset`` in the knowledge graph.

    Returns ``{asset_id, digest, size_bytes, media_type}`` on success. Invalid paths
    return ``None``; engine/store failures propagate.
    """
    if not file_path or not os.path.exists(file_path):
        return None
    store = _resolve_media_store(media_store)

    mime = mimetypes.guess_type(file_path)[0] or "text/plain"
    data = _read_filing_bytes(file_path)
    if data is None:
        return None

    meta = _filing_metadata(filing_type, file_path, extra)
    display = name or os.path.basename(file_path)

    stored = _store_filing_asset(store, data, mime, display, meta)
    if stored is None:
        return None

    asset_id = getattr(stored, "asset_id", None)
    digest = getattr(stored, "digest", "") or ""
    logger.info(
        "KG media ingest: stored %s (%d bytes) as asset %s digest %s",
        display,
        len(data),
        asset_id,
        digest[:16],
    )
    return {
        "asset_id": asset_id,
        "digest": digest,
        "size_bytes": len(data),
        "media_type": "document",
    }


class KnowledgeGraphIngestUnavailable(RuntimeError):
    """Direct-to-graph ingestion is unavailable from this connector.

    SDK-GAP (EH-48x, /var/tmp/l9/finish/au-decon-G4c/SDK-GAPS.md): raised in
    place of the old ``agent_utilities.knowledge_graph`` native-ingest call --
    agent-connector-sdk has no facade over EG's typed ingestion protocol yet,
    and the fleet precedent (agents/world-reference-mcp) moves direct-to-graph
    delivery to agent_connector_sdk.runner/sinks at the deployment layer, out
    of connector scope.
    """


def _kg_unavailable(name: str) -> None:
    raise KnowledgeGraphIngestUnavailable(
        f"{name}: direct-to-graph ingestion moved out of connector code "
        "(agent-utilities removed); no agent-connector-sdk facade exists yet "
        "-- see SDK-GAPS.md"
    )
