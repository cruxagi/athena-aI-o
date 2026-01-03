from dataclasses import dataclass
from typing import Dict

from .phases import phase_from_coherence


@dataclass
class CompressionReport:
    delta_ratio: float
    semantic_ratio: float
    tensor_projection: float
    quantum_hint: float
    hubbard_phase: str
    unified_7d_metric: float
    details: Dict[str, float]


class CompressionSystem:
    """Lightweight compression estimator for offline use."""

    def __init__(self) -> None:
        self.last_payload = ""

    def _ratio(self, value: int, baseline: int) -> float:
        return 0.0 if baseline == 0 else max(0.0, min(1.0, 1 - (value / baseline)))

    def stenographic(self, payload: str) -> float:
        data = payload.encode()
        if not data:
            return 0.0
        # Approximate run-length encoding size: 1 byte for value + 4 bytes for count per run.
        per_run_overhead = 5
        runs = 1
        last = data[0]
        for b in data[1:]:
            if b != last:
                runs += 1
                last = b
        compressed = runs * per_run_overhead
        return self._ratio(compressed, len(data))

    def delta_compress(self, payload: str) -> float:
        if self.last_payload == "":
            # First observation: treat entire payload as delta to preserve baseline behavior.
            delta = len(payload)
        else:
            delta = sum(1 for a, b in zip(payload, self.last_payload) if a != b) + abs(
                len(payload) - len(self.last_payload)
            )
        return self._ratio(delta, max(len(payload), 1))

    def semantic_compress(self, payload: str) -> float:
        tokens = payload.split()
        unique = len(set(tokens))
        return self._ratio(unique, max(len(tokens), 1))

    def tensor_projection(self, payload: str) -> float:
        # Heuristic "tensor-like" projection metric used as one axis in the unified_7d_metric.
        # Maps characters to modulo-7 residues, sums them, normalizes by length*7, then clamps via _ratio.
        # Higher values loosely indicate more regular residue patterns; purely heuristic, not real tensor algebra.
        return self._ratio(sum(ord(c) % 7 for c in payload), max(len(payload), 1) * 7)

    def quantum_hint(self, payload: str) -> float:
        # Shor-inspired placeholder using modular periodicity.
        modulus = 97
        residues = {ord(c) % modulus for c in payload}
        return self._ratio(len(residues), modulus)

    def hubbard_phase(self, coherence: float) -> str:
        return phase_from_coherence(coherence).value

    def project(self, payload: str, coherence: float) -> CompressionReport:
        delta_ratio = self.delta_compress(payload)
        semantic_ratio = self.semantic_compress(payload)
        tensor_projection = self.tensor_projection(payload)
        quantum_hint = self.quantum_hint(payload)
        # Equal-weight heuristic; semantic_ratio appears twice to emphasize lexical compaction vs dispersion.
        unified = sum(
            [
                delta_ratio,
                semantic_ratio,
                tensor_projection,
                quantum_hint,
                coherence,
                self.stenographic(payload),
                1.0 - semantic_ratio,
            ]
        ) / 7
        report = CompressionReport(
            delta_ratio=delta_ratio,
            semantic_ratio=semantic_ratio,
            tensor_projection=tensor_projection,
            quantum_hint=quantum_hint,
            hubbard_phase=self.hubbard_phase(coherence),
            unified_7d_metric=unified,
            details={
                "coherence": coherence,
                "stenographic": self.stenographic(payload),
                "delta_semantic_product": delta_ratio * semantic_ratio,
            },
        )
        self.last_payload = payload
        return report
