"""Opt-in destructive-by-ID tests ONLY against dedicated disposable instances."""
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import unittest

from backend.app.config import LightRAGConfig
from backend.app.context.chunk_builder import build_chunks
from backend.app.context.lightrag_client import LightRAGClient, RetrievalError
from backend.app.context.source_registry import SourceRegistry
from test.context_suite.demo import run_demo
from test.context_suite.support import sample
from time import monotonic


@unittest.skipUnless(os.getenv("POCS_LIGHTRAG_REAL_TEST") == "1", "Real server opt-in/credentials absent")
class RealServiceTests(unittest.TestCase):
    @unittest.skipIf(os.getenv("POCS_LIGHTRAG_URL_2"), "Run concurrent scenario instead; every scenario needs fresh instances")
    def test_real_ingest_query_graph_sources_and_cleanup(self):
        result = run_demo(real=True)
        self.assertIsNone(result["failure"])
        self.assertIsNone(result["cleanup_issue"])
        self.assertIsNotNone(result["upstream_extracted_graph"])
        self.assertTrue(result["enabled"]["raw_retrieval"]["chunks"])
        self.assertFalse(result["enabled"]["issues"])

    @unittest.skipUnless(os.getenv("POCS_LIGHTRAG_URL_2") and os.getenv("POCS_LIGHTRAG_WORKSPACE_2"), "Second dedicated server absent")
    def test_real_two_servers_concurrent_and_cross_source_rejection(self):
        documents, versions, _, _ = sample()
        def run(n):
            config = LightRAGConfig.from_env() if n == 1 else LightRAGConfig(
                os.environ["POCS_LIGHTRAG_URL_2"], os.environ["POCS_LIGHTRAG_WORKSPACE_2"],
                api_key=os.getenv("POCS_LIGHTRAG_API_KEY_2", ""))
            chunks = build_chunks(f"real-concurrent-{n}", documents, versions)
            registry = SourceRegistry(chunks, documents)
            client = LightRAGClient(config, f"real-concurrent-{n}", Path("runtime/lightrag/leases"), deadline=monotonic()+300)
            try:
                with self.assertRaises(RetrievalError):
                    client.query("report deadline")
                client.index(chunks)
                client.index(chunks)
                data = client.query("Find the reporting obligation and the definition of report")
                self.assertTrue(data["chunks"])
                for chunk in data["chunks"]:
                    registry.evidence(chunk)
                return chunks, data
            finally:
                self.assertIsNone(client.cleanup())
        with ThreadPoolExecutor(2) as pool:
            a, b = list(pool.map(run, [1, 2]))
        registry = SourceRegistry(a[0], documents)
        for chunk in b[1]["chunks"]:
            with self.assertRaises(ValueError):
                registry.evidence(chunk)


if __name__ == "__main__":
    unittest.main()
