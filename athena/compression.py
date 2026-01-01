from dataclasses import dataclass
from typing import Dict


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
        return self._ratio(len(payload.encode()), max(1, len(payload)))

    def delta_compress(self, payload: str) -> float:
        delta = sum(1 for a, b in zip(payload, self.last_payload) if a != b) + abs(
            len(payload) - len(self.last_payload)
        )
        return self._ratio(delta, max(len(payload), 1))

    def semantic_compress(self, payload: str) -> float:
        tokens = payload.split()
        unique = len(set(tokens))
        return self._ratio(unique, max(len(tokens), 1))

    def tensor_projection(self, payload: str) -> float:
        # Placeholder tensor metric; higher when payload is short and regular.
        return self._ratio(sum(ord(c) % 7 for c in payload), max(len(payload), 1) * 7)

    def quantum_hint(self, payload: str) -> float:
        # Shor-inspired placeholder using modular periodicity.
        modulus = 97
        residues = {ord(c) % modulus for c in payload}
        return self._ratio(len(residues), modulus)

    def hubbard_phase(self, coherence: float) -> str:
        if coherence < 0.3:
            return "Chaotic"
        if coherence < 0.6:
            return "Critical"
        if coherence < 0.85:
            return "Crystalline"
        return "Metallic"

    def project(self, payload: str, coherence: float) -> CompressionReport:
        delta_ratio = self.delta_compress(payload)
        semantic_ratio = self.semantic_compress(payload)
        tensor_projection = self.tensor_projection(payload)
        quantum_hint = self.quantum_hint(payload)
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
