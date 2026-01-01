from dataclasses import dataclass
from typing import Any, Dict, Mapping

from .compression import CompressionReport, CompressionSystem
from .organism import OrganismController, OrganismReport
from .phases import phase_from_coherence
from .resonance import ResonanceController


@dataclass
class OffsetStore:
    """6D offset store (DNA) that seeds execution budgets."""

    ipq: float = 1.0
    batch: float = 1.0
    dt: float = 1.0
    conv: float = 1.0
    agg: float = 1.0
    lat: float = 1.0
    tok: float = 1.0

    def budgets(self, coherence: float) -> Dict[str, float]:
        scale = 0.5 + coherence
        return {
            "ipq": self.ipq * scale,
            "batch": max(1.0, self.batch * (1 + coherence)),
            "dt": max(0.1, self.dt * (1.5 - coherence)),
            "conv": self.conv * scale,
            "agg": self.agg * (1 + coherence / 2),
            "lat": max(0.1, self.lat * (1 - coherence / 2)),
            "tok": self.tok * (1 + coherence),
        }


@dataclass
class EngineReport:
    organism: OrganismReport
    budgets: Dict[str, float]
    compression: CompressionReport
    resonance_scope: Dict[str, Any]


class AIOEngine:
    """Offline, turnkey AI-O engine wiring all components together."""

    def __init__(self) -> None:
        self.offset_store = OffsetStore()
        self.organism = OrganismController()
        self.resonance = ResonanceController()
        self.compression = CompressionSystem()

    def run_cycle(self, stimuli: Mapping[str, Any], resonance_program: str = "", feedback: float = 0.5) -> EngineReport:
        organism_report = self.organism.sense_decide_act_learn_report(stimuli, feedback=feedback)
        budgets = self.offset_store.budgets(organism_report.coherence)
        scope = {
            "K": self.organism.coupling,
            "massBudget": budgets["batch"],
            "couplingBudget": budgets["ipq"],
            "r": organism_report.coherence,
            "coherence": organism_report.coherence,
            "tok": budgets["tok"],
        }
        scope = self.resonance.run(resonance_program, scope)
        payload = str(scope)
        compression_report = self.compression.project(payload, organism_report.coherence)
        return EngineReport(
            organism=organism_report,
            budgets=budgets,
            compression=compression_report,
            resonance_scope=scope,
        )
