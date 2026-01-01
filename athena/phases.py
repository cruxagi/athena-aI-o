from enum import Enum


class PhaseState(str, Enum):
    """Phase diagram states for the AI-O engine."""

    CHAOTIC = "Chaotic"
    CRITICAL = "Critical"
    CRYSTALLINE = "Crystalline"
    METALLIC = "Metallic"
