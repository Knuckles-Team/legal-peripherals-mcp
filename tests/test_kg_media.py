"""Native blob ingestion for drafted filings — coverage with a fake MediaStore.

Exercises ``kg_media.ingest_filing_file`` without a live engine: a fake store captures
the bytes + metadata, and the no-engine / missing-file paths no-op.
CONCEPT:AU-KG.ingest.list-durable-media.
"""

from __future__ import annotations

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


def test_ingest_no_store_is_noop(tmp_path, monkeypatch):
    p = tmp_path / "doc.txt"
    p.write_text("hi")
    # No injected store and no engine reachable → resolver yields None → no-op.
    import legal_peripherals_mcp.kg_media as kg_media

    monkeypatch.setattr(kg_media, "_media_store", lambda: None)
    assert ingest_filing_file(str(p), media_store=None) is None
