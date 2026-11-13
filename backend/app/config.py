"""Configuration for the optional, separately deployed LightRAG server."""
from dataclasses import dataclass, field
import os
from urllib.parse import urlsplit


@dataclass(frozen=True)
class LightRAGConfig:
    base_url: str
    workspace: str
    api_key: str = field(default="", repr=False)
    timeout: float = 10.0
    poll_interval: float = 0.5
    top_k: int = 8
    max_tokens: int = 4000
    max_chunks: int = 100
    max_chunk_chars: int = 12000
    max_response_bytes: int = 2_000_000
    mode: str = "mix"

    def __post_init__(self):
        url = urlsplit(self.base_url)
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError("Expected HTTP server URL without credentials/query/fragment")
        if not self.workspace or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_" for c in self.workspace):
            raise ValueError("Explicit alphanumeric workspace required")
        if self.mode not in {"mix", "hybrid", "local", "global", "naive"}:
            raise ValueError("Unsupported retrieval mode")
        if any(v <= 0 for v in (self.timeout, self.poll_interval, self.top_k, self.max_tokens,
                                self.max_chunks, self.max_chunk_chars, self.max_response_bytes)):
            raise ValueError("Retrieval limits must be positive")

    @classmethod
    def from_env(cls):
        return cls(base_url=os.environ["POCS_LIGHTRAG_URL"],
                   workspace=os.environ["POCS_LIGHTRAG_WORKSPACE"],
                   api_key=os.getenv("POCS_LIGHTRAG_API_KEY", ""),
                   timeout=float(os.getenv("POCS_LIGHTRAG_TIMEOUT", "10")),
                   poll_interval=float(os.getenv("POCS_LIGHTRAG_POLL_INTERVAL", "0.5")),
                   top_k=int(os.getenv("POCS_LIGHTRAG_TOP_K", "8")),
                   max_tokens=int(os.getenv("POCS_LIGHTRAG_MAX_TOKENS", "4000")),
                   max_chunks=int(os.getenv("POCS_LIGHTRAG_MAX_CHUNKS", "100")),
                   max_chunk_chars=int(os.getenv("POCS_LIGHTRAG_MAX_CHUNK_CHARS", "12000")),
                   max_response_bytes=int(os.getenv("POCS_LIGHTRAG_MAX_RESPONSE_BYTES", "2000000")),
                   mode=os.getenv("POCS_LIGHTRAG_MODE", "mix"))
