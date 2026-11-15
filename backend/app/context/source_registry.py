"""Application provenance is authoritative; extracted KG assertions are not."""
from dataclasses import asdict
from copy import deepcopy
import hashlib
import json

from ..schemas.report_validation import validate_sources
from .chunk_builder import SourceChunk


class SourceRegistry:
    def __init__(self, chunks: list[SourceChunk], documents: list[dict]):
        self.chunks = {c.file_source: c for c in chunks}
        self.documents = {d["document_id"]: deepcopy(d) for d in documents}
        if len(self.chunks) != len(chunks) or len(self.documents) != len(documents):
            raise ValueError("Ambiguous source identities")
        if len({c.comparison_id for c in chunks}) != 1:
            raise ValueError("Registry must belong to exactly one comparison")
        for c in chunks:
            document = self.documents.get(c.document_id)
            if document is None or document["role"] != c.role:
                raise ValueError("Registry role/document mismatch")
            validate_sources({"document_id": c.document_id, "source_refs": [c.source_ref],
                              "quote": c.text}, self.documents)

    def evidence(self, retrieved: dict) -> dict:
        # Do NOT match by basename: that would accept a forged foreign path.
        if not isinstance(retrieved, dict):
            raise ValueError("Malformed retrieval chunk")
        source, content = retrieved.get("file_path"), retrieved.get("content")
        if not isinstance(source, str) or source not in self.chunks or not isinstance(content, str):
            raise ValueError("Unknown retrieval source")
        chunk = self.chunks[source]
        # Strip only this record's exact header; never accept model paraphrases.
        header = chunk.indexed_text[:-len(chunk.text)]
        quote = content.removeprefix(header).strip()
        if not quote or quote not in chunk.text:
            raise ValueError("Retrieval quote is not literal source text")
        evidence = {"document_id": chunk.document_id,
                    "source_refs": [chunk.source_ref], "quote": quote}
        validate_sources(evidence, self.documents)
        return evidence

    def manifest(self):
        return [asdict(c) for c in self.chunks.values()]

    def source_graph(self):
        """Deterministic provenance graph, NOT an observed upstream KG.

        Qualified IDs preserve same-named units across document/role/version.
        No legal amendment/effect relationships are inferred here.
        """
        nodes, edges = {}, []
        for c in self.chunks.values():
            # file_source includes comparison identity; same text never joins sessions.
            key = [c.comparison_id, c.document_id, c.role, c.version]
            doc = "document_" + hashlib.sha256(json.dumps(key).encode()).hexdigest()
            unit = c.file_source
            nodes[doc] = {"id": doc, "type": "DocumentVersion", "document_id": c.document_id,
                          "comparison_id": c.comparison_id, "role": c.role, "version": c.version}
            nodes[unit] = {"id": unit, "type": "SourceBlock", "document_id": c.document_id,
                           "source_refs": [c.source_ref], "quote": c.text}
            edges.append({"source": doc, "target": unit, "type": "HAS_SOURCE_BLOCK",
                          "basis": "PROJECT_SOURCE", "inferred": False})
        return {"kind": "PROJECT_SOURCE_GRAPH_NOT_LIGHTRAG_KG",
                "nodes": list(nodes.values()), "edges": edges}
