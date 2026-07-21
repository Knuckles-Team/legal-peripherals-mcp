"""Native blob ingestion for drafted filings — coverage with a fake MediaStore.

Exercises ``kg_media.ingest_filing_file`` without a live engine: a fake store captures
the bytes + metadata, invalid paths return no result, and native failures propagate.
CONCEPT:AU-KG.ingest.list-durable-media.
"""

from __future__ import annotations

import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError

from legal_peripherals_mcp.kg_media import ingest_filing_file


class _Stored:
    asset_id = "asset-1"
    digest = "deadbeefdeadbeef"


class _FakeStore:
    def __init__(self):
        self.calls = []

    def store_media(self, data, *, media_type, mime_type, source, name, extra):
        self.calls.append(
            {
                "data": data,
                "media_type": media_type,
                "mime_type": mime_type,
                "source": source,
                "name": name,
                "extra": extra,
            }
        )
        return _Stored()


def test_ingest_filing_file_stores_blob(tmp_path):
    p = tmp_path / "ss4.txt"
    p.write_text("=== Form SS-4 Draft ===\nLegal Name: Acme LLC\n")
    store = _FakeStore()
    res = ingest_filing_file(
        str(p),
        filing_type="ss4_ein",
        name="Acme SS-4",
        extra={"state": "DE"},
        media_store=store,
    )
    assert res is not None
    assert res["asset_id"] == "asset-1"
    assert res["media_type"] == "document"
    assert res["size_bytes"] > 0
    call = store.calls[0]
    assert call["source"] == "legal-peripherals-mcp"
    assert call["name"] == "Acme SS-4"
    assert call["extra"]["filing_type"] == "ss4_ein"
    assert call["extra"]["state"] == "DE"
    assert call["extra"]["filename"] == "ss4.txt"


def test_ingest_missing_file_is_noop():
    assert ingest_filing_file("/no/such/file.txt", media_store=_FakeStore()) is None


def test_ingest_none_path_is_noop():
    assert ingest_filing_file(None, media_store=_FakeStore()) is None


def test_ingest_native_store_failure_propagates(tmp_path, monkeypatch):
    p = tmp_path / "doc.txt"
    p.write_text("hi")
    import legal_peripherals_mcp.kg_media as kg_media

    def fail():
        raise NativeIngestError("native media store is unavailable")

    monkeypatch.setattr(kg_media, "_native_media_store", fail)
    with pytest.raises(NativeIngestError, match="unavailable"):
        ingest_filing_file(str(p), media_store=None)
