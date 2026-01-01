import math
from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class KuramotoOscillator:
    """
    Implements the Kuramoto model:
        dθᵢ/dt = ωᵢ + (K/N) × Σⱼ sin(θⱼ - θᵢ)
    where:
        θᵢ: phase of oscillator i
        ωᵢ: natural frequency of oscillator i
        K:  coupling constant
        N:  number of oscillators
    """

    natural_frequencies: Sequence[float]
    coupling: float = 1.0
    phases: List[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._count = len(self.natural_frequencies)
        if self._count == 0:
            raise ValueError("At least one oscillator is required")

        if not self.phases:
            self.phases = [0.0 for _ in range(self._count)]
        elif len(self.phases) != self._count:
            raise ValueError("phases length must match natural frequencies")
        else:
            self.phases = [float(theta) for theta in self.phases]

        self.natural_frequencies = [float(w) for w in self.natural_frequencies]

    def derivatives(self) -> List[float]:
        """Compute dθᵢ/dt for each oscillator."""
        derivatives: List[float] = []
        for i, theta_i in enumerate(self.phases):
            coupling_term = sum(
                math.sin(theta_j - theta_i) for theta_j in self.phases
            )
            dtheta_dt = self.natural_frequencies[i] + (self.coupling / self._count) * coupling_term
            derivatives.append(dtheta_dt)
        return derivatives

    def step(self, dt: float) -> List[float]:
        """Advance the phases by a single Euler step of duration dt."""
        updates = self.derivatives()
        self.phases = [
            (theta + dtheta_dt * dt) % (2 * math.pi)
            for theta, dtheta_dt in zip(self.phases, updates)
        ]
        return self.phases
