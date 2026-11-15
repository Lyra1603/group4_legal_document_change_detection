"""Deterministic HTTP CONTRACT DOUBLE. This is NOT a LightRAG service."""
from copy import deepcopy
import json
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[2]


def sample():
    fixture = json.loads((ROOT / "test/fixtures/reports/common_contract.json").read_text(encoding="utf-8"))
    documents = list(fixture["documents"].values())
    # Same article title and text, but a different reference document/version.
    duplicate = deepcopy(documents[-1])
    duplicate.update(document_id="ref_2", filename="reference_other_version.docx")
    documents.append(duplicate)
    versions = {d["document_id"]: "fixture-version-1" for d in documents}
    versions["ref_2"] = "fixture-version-2"
    item = deepcopy(fixture["report"]["results"][0]["amendment"])
    return documents, versions, item, fixture


class ContractServer:
    """Only implements response shapes inspected at the pinned upstream commit."""
    def __init__(self, workspace="demo", behavior="normal"):
        self.workspace, self.behavior = workspace, behavior
        self.records = []
        self.calls = []
        self.deleted = []

    def __call__(self, request):
        path = request.url.path
        self.calls.append((request.method, path))
        body = json.loads(request.content) if request.content else {}
        if path == "/health":
            return httpx.Response(200, json={"status": "healthy", "core_version": "1.5.7",
                                           "configuration": {"workspace": self.workspace},
                                           "pipeline_busy": False, "pipeline_active": False})
        if path == "/documents/status_counts":
            return httpx.Response(200, json={"status_counts": {"processed": len(self.records), "pending": 0}})
        if path == "/documents/texts":
            self.records = [{"id": f"doc-{i}", "file_path": s, "content": t,
                             "status": "pending" if self.behavior == "pending" else "processed"}
                            for i, (s, t) in enumerate(zip(body["file_sources"], body["texts"]))]
            if self.behavior == "lost_ack":
                raise httpx.ReadTimeout("contract double lost ack", request=request)
            return httpx.Response(200, json={"status": "success", "track_id": "track-demo"})
        if path == "/documents/track_status/track-demo":
            return httpx.Response(200, json={"track_id": "track-demo", "documents": self.records,
                                           "total_count": len(self.records), "status_summary": {}})
        if path == "/query/data":
            if self.behavior == "timeout":
                raise httpx.ReadTimeout("contract double timeout", request=request)
            chunks = [{"file_path": r["file_path"], "content": r["content"],
                       "chunk_id": f"chunk-{i}", "reference_id": str(i)}
                      for i, r in enumerate(self.records)]
            if self.behavior == "empty":
                chunks = []
            if self.behavior == "foreign":
                chunks[0]["file_path"] = "foreign_comparison.txt"
            if self.behavior == "paraphrase":
                chunks[0]["content"] = "A fabricated legal conclusion."
            return httpx.Response(200, json={"status": "success", "message": "CONTRACT DOUBLE",
                                           "data": {"chunks": chunks, "entities": [], "relationships": [], "references": []},
                                           "metadata": {"test_double": True}})
        if path == "/documents/delete_document":
            if self.behavior == "cleanup_busy":
                return httpx.Response(200, json={"status": "busy", "doc_id": "", "message": "busy"})
            self.deleted.extend(body["doc_ids"])
            self.records = [r for r in self.records if r["id"] not in body["doc_ids"]]
            return httpx.Response(200, json={"status": "deletion_started", "doc_id": "", "message": "scheduled"})
        if path == "/graphs":
            return httpx.Response(200, json={"nodes": [], "edges": [], "test_double": True})
        return httpx.Response(404, json={"error": "unknown contract double route"})
