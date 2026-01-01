import hashlib
import math
import random
from typing import Dict, Iterable, List, Optional, Tuple


class KuramotoSubstrate:
    def __init__(self, num_oscillators: int = 64, coupling: float = 0.4, seed: int = 1) -> None:
        self.num_oscillators = num_oscillators
        self.coupling = coupling
        rng = random.Random(seed)
        self.natural_frequencies: List[float] = [
            rng.uniform(0.8, 1.2) for _ in range(num_oscillators)
        ]
        self.phases: List[float] = [rng.uniform(0.0, 2 * math.pi) for _ in range(num_oscillators)]

    def order_parameter(self) -> float:
        real_sum = sum(math.cos(phi) for phi in self.phases)
        imag_sum = sum(math.sin(phi) for phi in self.phases)
        return math.sqrt(real_sum**2 + imag_sum**2) / self.num_oscillators

    def perturb(self, perturbations: Iterable[Tuple[int, float]]) -> None:
        for index, delta in perturbations:
            if 0 <= index < self.num_oscillators:
                self.phases[index] = (self.phases[index] + delta) % (2 * math.pi)

    def step(self, dt: float = 0.05, steps: int = 1) -> None:
        for _ in range(steps):
            new_phases: List[float] = []
            for i, phase in enumerate(self.phases):
                coupling_term = sum(
                    math.sin(self.phases[j] - phase) for j in range(self.num_oscillators)
                ) / self.num_oscillators
                dphi = self.natural_frequencies[i] + self.coupling * coupling_term
                new_phases.append((phase + dphi * dt) % (2 * math.pi))
            self.phases = new_phases


class IntentClassifier:
    def __init__(self, channels: int = 4, max_delta: float = math.pi / 4) -> None:
        self.channels = channels
        self.max_delta = max_delta

    def _hash_bytes(self, query: str) -> bytes:
        return hashlib.sha256(query.encode("utf-8")).digest()

    def perturbations(self, query: str, num_oscillators: int) -> List[Tuple[int, float]]:
        digest = self._hash_bytes(query)
        perturbations: List[Tuple[int, float]] = []
        for idx in range(num_oscillators):
            byte = digest[idx % len(digest)]
            channel = byte % self.channels
            direction = 1 if channel % 2 == 0 else -1
            magnitude = (byte / 255.0) * self.max_delta
            if channel == 0:
                magnitude *= 0.5
            perturbations.append((idx, direction * magnitude))
        return perturbations

    def apply(self, query: str, substrate: KuramotoSubstrate) -> List[Tuple[int, float]]:
        perturbations = self.perturbations(query, substrate.num_oscillators)
        substrate.perturb(perturbations)
        return perturbations


class BehaviorLibrary:
    def __init__(self) -> None:
        self.behaviors: Dict[str, List[float]] = {}

    def add_behavior(self, name: str, phase_pattern: List[float]) -> None:
        self.behaviors[name] = phase_pattern

    def best_match(self, phases: List[float]) -> Optional[Tuple[str, float]]:
        best_name: Optional[str] = None
        best_score = float("-inf")
        for name, pattern in self.behaviors.items():
            if not pattern:
                continue
            score = self._phase_alignment_score(phases, pattern)
            if score > best_score:
                best_score = score
                best_name = name
        if best_name is None:
            return None
        return best_name, best_score

    def _phase_alignment_score(self, phases: List[float], pattern: List[float]) -> float:
        limit = min(len(phases), len(pattern))
        if limit == 0:
            return float("-inf")
        diffs = [abs((phases[i] - pattern[i]) % (2 * math.pi)) for i in range(limit)]
        normalized = [math.cos(diff) for diff in diffs]
        return sum(normalized) / limit

    @classmethod
    def with_defaults(cls, num_oscillators: int = 64) -> "BehaviorLibrary":
        library = cls()
        base_patterns = {
            "attend": 0.0,
            "explore": math.pi / 2,
            "reflect": math.pi,
            "respond": 3 * math.pi / 2,
        }
        for name, offset in base_patterns.items():
            pattern = [(offset + (i * 0.01)) % (2 * math.pi) for i in range(num_oscillators)]
            library.add_behavior(name, pattern)
        return library


class OmegaMetric:
    def __init__(self, substrate: KuramotoSubstrate) -> None:
        self.substrate = substrate

    def synchrony(self) -> float:
        return self.substrate.order_parameter()

    def energy(self) -> float:
        return 1.0 - self.synchrony()


class SBLMEngine:
    def __init__(
        self,
        substrate: Optional[KuramotoSubstrate] = None,
        classifier: Optional[IntentClassifier] = None,
        library: Optional[BehaviorLibrary] = None,
    ) -> None:
        self.substrate = substrate or KuramotoSubstrate()
        self.classifier = classifier or IntentClassifier()
        self.library = library or BehaviorLibrary.with_defaults(self.substrate.num_oscillators)
        self.metric = OmegaMetric(self.substrate)

    def process(self, query: str, dt: float = 0.05, steps: int = 5) -> Dict[str, float]:
        self.classifier.apply(query, self.substrate)
        self.substrate.step(dt=dt, steps=steps)
        best = self.library.best_match(self.substrate.phases)
        behavior = best[0] if best else "undetermined"
        score = best[1] if best else 0.0
        synchrony = self.metric.synchrony()
        return {
            "behavior": behavior,
            "behavior_score": score,
            "synchrony": synchrony,
            "omega_energy": self.metric.energy(),
        }
