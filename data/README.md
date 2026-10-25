# Synthetic pilot data

This directory contains small, synthetic fixtures for developing and testing
the baseline evaluator. They are not legal documents and must not be used as
the independent benchmark or as evidence that the acceptance targets have
been met.

Each case under `T1/` contains:

- `v1.txt`: the original document text.
- `s.txt`: the amendment instruction or amended text.
- `gold.json`: the manually assigned expected result for the baseline-shaped
  evaluator case.
- `README.md`: the case purpose and annotation rationale.
- `review.md`: annotation and review status.

The current evaluator consumes `AlignedPair` results, while the target SRS
uses `AmendmentItem` and `SemanticChange`. These fixtures intentionally keep a
small baseline expectation so they can be used before the shared contract is
migrated.
