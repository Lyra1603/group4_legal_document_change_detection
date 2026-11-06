"""Conservative development limits, configurable until measured by the team."""
from dataclasses import dataclass
import os
import math


@dataclass(frozen=True)
class Settings:
    max_file_bytes: int = 10 * 1024 * 1024
    max_request_bytes: int = 32 * 1024 * 1024
    max_docx_expanded_bytes: int = 64 * 1024 * 1024
    max_references: int = 5
    max_characters: int = 500_000
    max_amendments: int = 200
    max_concurrent: int = 2
    deadline_seconds: float = 60

    def __post_init__(self):
        if any(not math.isfinite(value) or value <= 0 for value in vars(self).values()):
            raise ValueError('All processing limits must be positive')

    @classmethod
    def from_env(cls):
        defaults = cls()
        return cls(**{name: type(value)(os.getenv('LEGAL_' + name.upper(), value))
                      for name, value in vars(defaults).items()})
