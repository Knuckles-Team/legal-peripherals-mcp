"""Native epistemic-graph blob ingestion for drafted legal filings.

CONCEPT:AU-KG.ingest.list-durable-media. Drafted filing artifacts (SS-4 drafts, trust
indentures, operating agreements — the ``drafts/*.txt`` files this package produces) are
stored as content-addressed **blobs** with a ``:MediaAsset`` graph node carrying the
filing metadata, in ONE cross-modal ACID commit, via the agent-utilities ``MediaStore``
(surfaced through ``native_ingest.media_store``). This makes the raw filing bytes — not
just a filesystem path — durable, deduped, and queryable inside the knowledge graph.

Best-effort and dependency-/engine-guarded: with no KG stack or no reachable engine every
entry point **no-ops** (returns ``None``), so the connector keeps working with zero KG
infrastructure.
"""

from __future__ import annotations

import logging
import mimetypes
import os
from typing import Any

logger = logging.getLogger("legal_peripherals_mcp.kg_media")

_SOURCE = "legal-peripherals-mcp"


def _media_store() -> Any | None:
    """Build a ``MediaStore`` over a live engine, or ``None`` when unavailable."""
    # Preferred: the shared native_ingest seam already knows how to build one.
    try:
        from agent_utilities.knowledge_graph.memory.native_ingest import media_store

        store = media_store()
        if store is not None:
            return store
    except Exception as e:  # noqa: BLE001 — primitive absent; fall through
        logger.debug("native_ingest.media_store unavailable: %s", e)
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
        from agent_utilities.knowledge_graph.memory.media_store import MediaStore
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG media ingest unavailable (import): %s", e)
        return None
    try:
        engine = GraphComputeEngine()
        if getattr(engine, "_client", None) is None:
            return None
        return MediaStore(engine)
    except Exception as e:  # noqa: BLE001 — no reachable engine
        logger.debug("KG media ingest: engine unreachable: %s", e)
        return None


def ingest_filing_file(
    file_path: str | None,
    *,
    filing_type: str = "legal_document",
    name: str = "",
    extra: dict[str, Any] | None = None,
    media_store: Any | None = None,
) -> dict[str, Any] | None:
    """Store a drafted filing file as a blob + ``:MediaAsset`` in the knowledge graph.

    Returns ``{asset_id, digest, size_bytes, media_type}`` on success, or ``None`` when
    there is no engine, no file, or the store failed (never raises). ``media_store`` may
    be injected (tests); otherwise one is built on demand.
    """
    if not file_path or not os.path.exists(file_path):
        return None
    store = media_store if media_store is not None else _media_store()
    if store is None:
        return None

    mime = mimetypes.guess_type(file_path)[0] or "text/plain"
    try:
        with open(file_path, "rb") as fh:
            data = fh.read()
    except OSError as e:
        logger.warning("KG media ingest: cannot read %s: %s", file_path, e)
        return None

    meta = {"filing_type": filing_type, "filename": os.path.basename(file_path)}
    if extra:
        meta.update({k: v for k, v in extra.items() if v is not None})
    display = name or os.path.basename(file_path)

    try:
        stored = store.store_media(
            data,
            media_type="document",
            mime_type=mime,
            source=_SOURCE,
            name=display,
            extra=meta,
        )
    except Exception as e:  # noqa: BLE001 — engine/store failure is non-fatal
        logger.warning("KG media ingest: store_media failed: %s", e)
        return None
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
