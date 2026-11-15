"""Narrow HTTP adapter for HKUDS/LightRAG v1.5.7 (28ff1b05...).

Experimental isolation policy: an empty, dedicated server/storage for ONE
comparison. Persistent endpoint reservation is deliberately not auto-recycled.
Different concurrent comparisons need different dedicated server instances.
No dynamic workspace header or global delete is used.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from threading import Lock
from urllib.parse import quote, urlsplit

import httpx

from ..config import LightRAGConfig
from .chunk_builder import SourceChunk

UPSTREAM_COMMIT = "28ff1b05f2ac3f3e6fa14dd2cd33656579bd0c9c"
UPSTREAM_VERSION = "1.5.7"


class RetrievalError(RuntimeError):
    """Safe code only; response bodies/credentials must not enter logs/errors."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class LightRAGClient:
    def __init__(self, config: LightRAGConfig, comparison_id: str, ledger_dir: Path,
                 *, deadline: float, transport=None):
        if not comparison_id:
            raise ValueError("comparison_id required")
        self.config, self.deadline = config, deadline
        self.comparison_id = comparison_id
        self.ready = False
        self.registry_sources: set[str] = set()
        self.ids: dict[str, str] = {}
        self.track_id: str | None = None
        self.submitted = False
        self._index_lock = Lock()
        self.closed = False
        # Normalize default ports/trailing slash to avoid trivial alias races.
        url = urlsplit(config.base_url)
        port = url.port or (443 if url.scheme == "https" else 80)
        endpoint = f"{url.scheme}://{url.hostname.lower()}:{port}{url.path.rstrip('/')}"
        ledger_dir.mkdir(parents=True, exist_ok=True)
        self.ledger = ledger_dir / (hashlib.sha256(endpoint.encode()).hexdigest() + ".json")
        self.state = {"comparison_id": comparison_id, "endpoint_hash": self.ledger.stem,
                      "workspace": config.workspace, "upstream_commit": UPSTREAM_COMMIT,
                      "phase": "RESERVED", "track_id": None, "documents": {}}
        try:
            with self.ledger.open("x", encoding="utf-8") as f:
                json.dump(self.state, f)
        except FileExistsError:
            raise RetrievalError("SERVER_RESERVED") from None
        self.http = httpx.Client(base_url=config.base_url.rstrip("/"), transport=transport,
                                 headers={"X-API-Key": config.api_key} if config.api_key else {},
                                 follow_redirects=False, trust_env=False)

    def _save(self, phase: str):
        self.state.update(phase=phase, track_id=self.track_id, documents=self.ids)
        # The reservation itself must remain present on crash; no automatic unlock.
        with self.ledger.open("w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _request(self, method: str, path: str, *, deadline=None, **kwargs):
        end = self.deadline if deadline is None else deadline
        for attempt in range(2 if method == "GET" else 1):
            remaining = end - time.monotonic()
            if remaining <= 0:
                raise RetrievalError("RETRIEVAL_TIMEOUT")
            try:
                with self.http.stream(method, path, timeout=min(self.config.timeout, remaining), **kwargs) as r:
                    if r.status_code in {502, 503, 504} and method == "GET" and attempt == 0:
                        continue
                    if r.status_code >= 300:
                        raise RetrievalError("RETRIEVAL_HTTP_ERROR")
                    data = bytearray()
                    for part in r.iter_bytes():
                        if time.monotonic() >= end:
                            raise RetrievalError("RETRIEVAL_TIMEOUT")
                        data.extend(part)
                        if len(data) > self.config.max_response_bytes:
                            raise RetrievalError("RETRIEVAL_RESPONSE_LIMIT")
                result = json.loads(data)
                if not isinstance(result, dict):
                    raise RetrievalError("RETRIEVAL_PROTOCOL_ERROR")
                return result
            except httpx.RequestError:
                if method == "GET" and attempt == 0:
                    continue
                raise RetrievalError("RETRIEVAL_UNAVAILABLE") from None
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise RetrievalError("RETRIEVAL_PROTOCOL_ERROR") from None
        raise RetrievalError("RETRIEVAL_UNAVAILABLE")

    def verify_server(self):
        health = self._request("GET", "/health")
        if health.get("status") != "healthy" or health.get("core_version") != UPSTREAM_VERSION:
            raise RetrievalError("SERVER_VERSION_UNVERIFIED")
        if health.get("configuration", {}).get("workspace") != self.config.workspace:
            raise RetrievalError("SERVER_SCOPE_UNVERIFIED")
        if health.get("pipeline_busy") or health.get("pipeline_active"):
            raise RetrievalError("SERVER_NOT_EMPTY")
        counts = self._request("GET", "/documents/status_counts").get("status_counts")
        if not isinstance(counts, dict) or not counts or any(type(v) is not int or v != 0 for v in counts.values()):
            raise RetrievalError("SERVER_NOT_EMPTY")
        self._save("VERIFIED_EMPTY")

    def _track(self, *, deadline=None):
        if not self.track_id:
            raise RetrievalError("INDEX_TRACKING_UNKNOWN")
        data = self._request("GET", "/documents/track_status/" + quote(self.track_id, safe=""), deadline=deadline)
        docs = data.get("documents")
        if data.get("track_id") != self.track_id or not isinstance(docs, list):
            raise RetrievalError("INDEX_PROTOCOL_ERROR")
        seen_sources, seen_ids = set(), set()
        for doc in docs:
            if not isinstance(doc, dict):
                raise RetrievalError("INDEX_PROTOCOL_ERROR")
            source, did = doc.get("file_path"), doc.get("id")
            if not isinstance(source, str) or source not in self.registry_sources or not isinstance(did, str) or not did or source in seen_sources or did in seen_ids:
                raise RetrievalError("INDEX_SOURCE_MISMATCH")
            if source in self.ids and self.ids[source] != did:
                raise RetrievalError("INDEX_SOURCE_MISMATCH")
            seen_sources.add(source)
            seen_ids.add(did)
            self.ids[source] = did
        self._save("TRACKING")
        return docs

    def index(self, chunks: list[SourceChunk]):
        with self._index_lock:
            return self._index(chunks)

    def _index(self, chunks: list[SourceChunk]):
        sources = {c.file_source for c in chunks}
        if (not chunks or len(sources) != len(chunks) or len(chunks) > self.config.max_chunks
                or any(c.comparison_id != self.comparison_id or len(c.text) > self.config.max_chunk_chars for c in chunks)):
            raise RetrievalError("INDEX_INPUT_INVALID")
        if self.submitted and not self.track_id:
            raise RetrievalError("INDEX_SUBMISSION_UNCERTAIN")
        if self.track_id:
            if sources != self.registry_sources:
                raise RetrievalError("INDEX_ALREADY_SUBMITTED")
            if self.ready:
                return  # same in-session request, no duplicate POST
        else:
            self.verify_server()
            self.registry_sources = sources
            self.state["sources"] = sorted(sources)
            self._save("SUBMITTING_UNKNOWN_UNTIL_ACK")
            self.submitted = True
            response = self._request("POST", "/documents/texts", json={
                "texts": [c.indexed_text for c in chunks],
                "file_sources": [c.file_source for c in chunks]})
            self.track_id = response.get("track_id") or None
            if response.get("status") != "success" or not isinstance(self.track_id, str):
                self._save("SUBMISSION_FAILED_OR_PARTIAL" if self.track_id else "SUBMITTING_UNKNOWN_UNTIL_ACK")
                raise RetrievalError("INDEX_SUBMISSION_FAILED")
            self._save("SUBMITTED")
        while True:
            docs = self._track()
            if any(d.get("status") == "failed" for d in docs):
                raise RetrievalError("INDEX_FAILED")
            if len(docs) == len(chunks) and all(d.get("status") == "processed" for d in docs):
                self.ready = True
                self._save("READY")
                return
            self._pause(self.deadline)

    def _pause(self, deadline):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RetrievalError("INDEX_NOT_READY")
        time.sleep(min(self.config.poll_interval, remaining))

    def query(self, query: str):
        if not self.ready:
            raise RetrievalError("INDEX_NOT_READY")
        if not query.strip() or len(query) > 8000:
            raise RetrievalError("QUERY_INVALID")
        result = self._request("POST", "/query/data", json={
            "query": query, "mode": self.config.mode, "top_k": self.config.top_k,
            "chunk_top_k": self.config.top_k, "max_total_tokens": self.config.max_tokens,
            "enable_rerank": False})
        if result.get("status") != "success" or not isinstance(result.get("data"), dict):
            raise RetrievalError("RETRIEVAL_FAILED")
        data = result["data"]
        if not isinstance(data.get("chunks"), list):
            raise RetrievalError("RETRIEVAL_PROTOCOL_ERROR")
        if len(data["chunks"]) > self.config.top_k:
            raise RetrievalError("RETRIEVAL_RESPONSE_LIMIT")
        return data

    def graph(self):
        if not self.ready:
            raise RetrievalError("INDEX_NOT_READY")
        return self._request("GET", "/graphs", params={"label": "*", "max_depth": 2, "max_nodes": 100})

    def cleanup(self, *, budget: float = 10):
        """Return a safe issue code or None; never equate scheduling with deletion."""
        self.ready = False
        end = time.monotonic() + budget
        try:
            if not self.track_id:
                # POST may have succeeded without ACK: leave server quarantined.
                if self.state["phase"] == "SUBMITTING_UNKNOWN_UNTIL_ACK":
                    self._save("CLEANUP_PENDING_UNKNOWN_SUBMISSION")
                    return "CLEANUP_PENDING"
                self._save("NO_INGESTION_ACKNOWLEDGED")
                return None
            docs = self._track(deadline=end)
            if len(self.ids) != len(self.registry_sources) or any(d.get("status") not in {"processed", "failed"} for d in docs):
                raise RetrievalError("CLEANUP_PENDING")
            if docs:
                response = self._request("DELETE", "/documents/delete_document", deadline=end,
                                         json={"doc_ids": sorted(self.ids.values()),
                                               "delete_file": False, "delete_llm_cache": True})
                if response.get("status") != "deletion_started":
                    raise RetrievalError("CLEANUP_PENDING")
                while self._track(deadline=end):
                    self._pause(end)
            health = self._request("GET", "/health", deadline=end)
            counts = self._request("GET", "/documents/status_counts", deadline=end).get("status_counts")
            if health.get("pipeline_busy") or health.get("pipeline_active") or not isinstance(counts, dict) or not counts or any(v != 0 for v in counts.values()):
                raise RetrievalError("CLEANUP_PENDING")
            self._save("DELETION_CONFIRMED_SERVER_STILL_RESERVED")
            return None
        except RetrievalError:
            self._save("CLEANUP_PENDING")
            return "CLEANUP_PENDING"
        finally:
            self.close()

    def close(self):
        if not self.closed:
            self.http.close()
            self.closed = True
