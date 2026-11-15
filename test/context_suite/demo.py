"""Reproducible demo. `contract` is a labelled HTTP double; `real` never is."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
import tempfile

import httpx

from backend.app.config import LightRAGConfig
from backend.app.context.chunk_builder import build_chunks
from backend.app.context.context_builder import build_context
from backend.app.context.lightrag_client import LightRAGClient, RetrievalError, UPSTREAM_COMMIT
from backend.app.context.source_registry import SourceRegistry
from test.context_suite.support import ContractServer, sample


def probe():
    """Actual HTTP probe, no mock transport or ingestion."""
    url = os.getenv("POCS_LIGHTRAG_URL", "http://127.0.0.1:9621")
    headers = {"X-API-Key": os.environ["POCS_LIGHTRAG_API_KEY"]} if os.getenv("POCS_LIGHTRAG_API_KEY") else {}
    try:
        with httpx.Client(timeout=2, trust_env=False, follow_redirects=False) as http:
            r = http.get(url.rstrip("/") + "/health", headers=headers)
            data = r.json() if r.status_code == 200 else {}
            return {"mode": "REAL_HTTP_PROBE", "status_code": r.status_code,
                    "healthy": data.get("status") == "healthy", "core_version": data.get("core_version"),
                    "retrieval_executed": False}
    except (httpx.HTTPError, ValueError):
        return {"mode": "REAL_HTTP_PROBE", "healthy": False,
                "code": "SERVER_UNAVAILABLE_OR_INVALID_RESPONSE", "retrieval_executed": False}


def coverage(item):
    return {(e["document_id"], r) for e in item["context"]["evidence"] for r in e["source_refs"]}


def run_demo(*, real=False, ledger_dir=Path("runtime/lightrag/leases")):
    if real and os.getenv("POCS_LIGHTRAG_REAL_TEST") != "1":
        raise ValueError("Set POCS_LIGHTRAG_REAL_TEST=1 only for a dedicated disposable server")
    documents, versions, item, _ = sample()
    # A controlled missing-context scenario, not a claim about actual law.
    item["context"]["references"][0].update(status="UNRESOLVED", evidence=[], reason="Not yet retrieved in this synthetic demo")
    comparison_id = "lightrag-synthetic-demo"
    config = LightRAGConfig.from_env() if real else LightRAGConfig("http://contract-double:9621", "demo")
    chunks = build_chunks(comparison_id, documents, versions,
                          max_chunks=config.max_chunks, max_chars=config.max_chunk_chars)
    registry = SourceRegistry(chunks, documents)
    started = time.perf_counter()
    disabled = build_context(item, registry, None)
    off_ms = (time.perf_counter() - started) * 1000
    transport = None if real else httpx.MockTransport(ContractServer())
    client = LightRAGClient(config, comparison_id, ledger_dir, deadline=time.monotonic() + 300, transport=transport)
    results, samples_ms, graph, failure, cleanup = [], [], None, None, None
    started = time.perf_counter()
    try:
        client.index(chunks)
        index_ms = (time.perf_counter() - started) * 1000
        for _ in range(3):
            t = time.perf_counter()
            results.append(build_context(item, registry, client))
            samples_ms.append((time.perf_counter() - t) * 1000)
        if real:
            graph = client.graph()  # raw extracted graph; not evidence automatically
    except RetrievalError as exc:
        failure, index_ms = exc.code, (time.perf_counter() - started) * 1000
    finally:
        cleanup = client.cleanup()
    gold = {("ref_1", "block:1")}
    enabled = results[0] if results else None
    # All selected source blocks count, including distractors. This is source
    # retrieval precision/recall only, not semantic/legal accuracy.
    selected = coverage(enabled.amendment) if enabled else set()
    def metrics(found):
        return {"source_precision": len(found & gold) / len(found) if found else None,
                "source_recall": len(found & gold) / len(gold), "source_count": len(found)}
    return {"mode": "REAL_LIGHTRAG_HTTP" if real else "CONTRACT_DOUBLE_NOT_LIGHTRAG",
            "generated_at": datetime.now(timezone.utc).isoformat(), "upstream_commit": UPSTREAM_COMMIT,
            "input": {"comparison_id": comparison_id, "documents": documents, "versions": versions, "amendment": item},
            "registry": registry.manifest(), "project_source_graph": registry.source_graph(),
            "upstream_extracted_graph": graph,
            "disabled": {"context": disabled.amendment["context"], "metrics": metrics(coverage(disabled.amendment)), "latency_ms": off_ms},
            "enabled": {"context": enabled.amendment["context"] if enabled else None,
                        "raw_retrieval": enabled.retrieved if enabled else None,
                        "issues": enabled.issues if enabled else [], "metrics": metrics(selected),
                        "index_ms": index_ms, "retrieval_latency_ms": samples_ms,
                        "repeat_consistency": len({json.dumps(r.amendment["context"], sort_keys=True, ensure_ascii=False) for r in results}) == 1 if results else None,
                        "validated_evidence_count": len(enabled.amendment["context"]["evidence"]) if enabled else 0},
            "expected_source_refs": [{"document_id": d, "source_ref": r} for d, r in gold],
            "failure": failure, "cleanup_issue": cleanup,
            "limits": ["Synthetic task, one instruction, three repeated queries; no official acceptance threshold.",
                       "No running Semantic Diff/model; semantic quality and legal validity are NOT measured.",
                       "Contract double results cannot demonstrate real retrieval/KG quality.",
                       "Dedicated instance isolation requires deployment storage separation and a common durable lease directory."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["contract", "real", "probe"], default="contract")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger-dir", type=Path)
    args = parser.parse_args()
    if args.mode == "probe":
        result = probe()
    elif args.mode == "contract" and args.ledger_dir is None:
        # Safe to discard reservations only for a transport with NO real server.
        with tempfile.TemporaryDirectory(prefix="pocs_contract_demo_") as temporary:
            result = run_demo(ledger_dir=Path(temporary))
    else:
        result = run_demo(real=args.mode == "real", ledger_dir=args.ledger_dir or Path("runtime/lightrag/leases"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": result["mode"], "output": str(args.output),
                      "failure": result.get("failure"), "cleanup_issue": result.get("cleanup_issue")}, ensure_ascii=True))


if __name__ == "__main__":
    main()
