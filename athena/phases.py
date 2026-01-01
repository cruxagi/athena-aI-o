from enum import Enum


class PhaseState(str, Enum):
    """Phase diagram states for the AI-O engine."""

    CHAOTIC = "Chaotic"
    CRITICAL = "Critical"
    CRYSTALLINE = "Crystalline"
    METALLIC = "Metallic"


def phase_from_coherence(coherence: float) -> PhaseState:
    if coherence < 0.3:
        return PhaseState.CHAOTIC
    if coherence < 0.6:
        return PhaseState.CRITICAL
    if coherence < 0.85:
        return PhaseState.CRYSTALLINE
    return PhaseState.METALLIC
