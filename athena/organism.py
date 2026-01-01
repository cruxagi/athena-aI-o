import cmath
import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from .phases import PhaseState, phase_from_coherence

OSCILLATOR_COUNT = 64


@dataclass
class OrganismReport:
    """Structured report from the organism loop."""

    coherence: float
    omega: float
    phase: PhaseState
    token_budget: int
    actions: Dict[str, Any]
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Oscillator:
    phase: float
    natural_frequency: float
    mass: float


class OrganismController:
    """Implements the Sense→Decide→Act→Learn→Report loop for the organism."""

    def __init__(self, coupling: float = 1.0, token_budget: int = 10_000) -> None:
        self.coupling = coupling
        self.token_budget = token_budget
        self.meta_goals = ["stability", "coherence", "safety"]
        self._rng = random.Random(42)
        self.oscillators = self._init_oscillators()

    def _init_oscillators(self) -> List[Oscillator]:
        rng = self._rng
        step = 1.0 / OSCILLATOR_COUNT
        return [
            Oscillator(
                phase=rng.random() * 2 * math.pi,
                natural_frequency=0.8 + (i * step),
                mass=1.0 + (i % 4) * 0.1,
            )
            for i in range(OSCILLATOR_COUNT)
        ]

    def _advance_phases(self, dt: float = 0.1) -> None:
        """Kuramoto-style update for oscillator phases."""
        n = len(self.oscillators)
        phases = [o.phase for o in self.oscillators]
        for idx, osc in enumerate(self.oscillators):
            coupling_term = sum(math.sin(phases[j] - phases[idx]) for j in range(n)) / n
            osc.phase += dt * (osc.natural_frequency + (self.coupling / n) * coupling_term)

    def coherence(self) -> float:
        """Order parameter r."""
        n = len(self.oscillators)
        vector = sum(cmath.exp(1j * o.phase) for o in self.oscillators) / n
        return abs(vector)

    def omega_metric(self) -> float:
        n = len(self.oscillators)
        theta_bar = sum(o.phase for o in self.oscillators) / n
        return sum(
            o.mass * (o.natural_frequency**2) * math.cos(o.phase - theta_bar) for o in self.oscillators
        )

    def phase_state(self) -> PhaseState:
        return phase_from_coherence(self.coherence())

    def mutate(self, intensity: float = 0.05) -> None:
        """Simple mutation operator for the oscillator DNA."""
        rng = self._rng
        for osc in self.oscillators:
            osc.natural_frequency += rng.uniform(-intensity, intensity)
            osc.mass = max(0.5, osc.mass + rng.uniform(-intensity, intensity))

    def fitness(self, target: float = 0.7) -> float:
        """Fitness evaluation encourages higher coherence."""
        r = self.coherence()
        return 1.0 - abs(target - r)

    def _spend_tokens(self, amount: int) -> None:
        self.token_budget = max(0, self.token_budget - amount)

    def sense(self, stimuli: Mapping[str, Any]) -> Dict[str, Any]:
        """Ingest stimuli from sources like GitHub, Hacker News, and the codebase."""
        normalized = {k: float(v) if isinstance(v, (int, float)) else 0.0 for k, v in stimuli.items()}
        intensity = sum(normalized.values())
        # stimuli modulate coupling strength
        self.coupling = max(0.1, min(2.0, self.coupling + 0.01 * intensity))
        return normalized

    def decide(self, signals: Mapping[str, Any]) -> Dict[str, Any]:
        """Allocate budgets and set internal priorities."""
        r = self.coherence()
        self._advance_phases()
        agility = max(0.1, 1.0 - r)
        decision = {
            "exploration": agility,
            "stability": 1.0 - agility,
            "meta_goals": list(self.meta_goals),
            "signals": dict(signals),
        }
        return decision

    def act(self, decision: Mapping[str, Any]) -> Dict[str, Any]:
        """Produce an action; here we emit an execution plan placeholder."""
        plan = {
            "action": "synthesize_code",
            "focus": "self-improvement",
            "agility": decision.get("exploration", 0.0),
            "stability": decision.get("stability", 0.0),
        }
        self._spend_tokens(5)
        return plan

    def learn(self, feedback: float = 0.0) -> None:
        """Adjust natural frequencies based on feedback and current phase."""
        adjust = (feedback - 0.5) * 0.05
        for osc in self.oscillators:
            osc.natural_frequency = max(0.1, osc.natural_frequency + adjust)

    def report(self, actions: Mapping[str, Any]) -> OrganismReport:
        r = self.coherence()
        omega = self.omega_metric()
        return OrganismReport(
            coherence=r,
            omega=omega,
            phase=self.phase_state(),
            token_budget=self.token_budget,
            actions=dict(actions),
            notes={"fitness": self.fitness()},
        )

    def sense_decide_act_learn_report(
        self, stimuli: Mapping[str, Any], feedback: float = 0.5
    ) -> OrganismReport:
        sensed = self.sense(stimuli)
        decision = self.decide(sensed)
        actions = self.act(decision)
        self.learn(feedback)
        return self.report(actions)
