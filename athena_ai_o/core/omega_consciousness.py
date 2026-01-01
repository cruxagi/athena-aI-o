"""
Omega Consciousness: Unified metric for cognitive state.

Formula: Ω = Σ(m·ω²)·cos(φ-φ̄)

Where:
- m: mode mass/weight
- ω: angular frequency of the mode
- φ: current phase of the mode
- φ̄: mean phase across all modes
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CognitiveMode:
    """Represents a single cognitive mode."""
    name: str
    mass: float  # m: mode weight/importance
    frequency: float  # ω: angular frequency
    phase: float  # φ: current phase (in radians)
    
    def energy(self) -> float:
        """Calculate mode energy: m·ω²"""
        return self.mass * (self.frequency ** 2)


class OmegaConsciousness:
    """
    Omega Consciousness calculator for unified cognitive state metric.
    
    Implements the formula: Ω = Σ(m·ω²)·cos(φ-φ̄)
    """
    
    def __init__(self):
        self.modes: List[CognitiveMode] = []
        self.history: List[float] = []
        
    def add_mode(self, name: str, mass: float, frequency: float, phase: float = 0.0) -> None:
        """
        Add a cognitive mode to the system.
        
        Args:
            name: Mode identifier
            mass: Mode weight/importance
            frequency: Angular frequency
            phase: Initial phase (radians)
        """
        mode = CognitiveMode(name=name, mass=mass, frequency=frequency, phase=phase)
        self.modes.append(mode)
        
    def update_mode_phase(self, name: str, phase: float) -> None:
        """Update the phase of a specific mode."""
        for mode in self.modes:
            if mode.name == name:
                mode.phase = phase
                break
                
    def get_mode(self, name: str) -> Optional[CognitiveMode]:
        """Retrieve a mode by name."""
        for mode in self.modes:
            if mode.name == name:
                return mode
        return None
        
    def calculate_mean_phase(self) -> float:
        """
        Calculate mean phase φ̄ across all modes.
        
        Returns:
            Mean phase in radians
        """
        if not self.modes:
            return 0.0
        
        # Use circular mean for phase averaging
        sin_sum = sum(np.sin(mode.phase) for mode in self.modes)
        cos_sum = sum(np.cos(mode.phase) for mode in self.modes)
        
        return np.arctan2(sin_sum, cos_sum)
        
    def calculate_omega(self) -> float:
        """
        Calculate Omega Consciousness: Ω = Σ(m·ω²)·cos(φ-φ̄)
        
        Returns:
            Omega consciousness value
        """
        if not self.modes:
            return 0.0
            
        mean_phase = self.calculate_mean_phase()
        
        omega = 0.0
        for mode in self.modes:
            energy = mode.energy()  # m·ω²
            phase_diff = mode.phase - mean_phase  # φ - φ̄
            omega += energy * np.cos(phase_diff)
            
        # Store in history
        self.history.append(omega)
        
        return omega
        
    def get_state_summary(self) -> Dict:
        """
        Get a summary of the current consciousness state.
        
        Returns:
            Dictionary with omega, mean_phase, and mode details
        """
        omega = self.calculate_omega()
        mean_phase = self.calculate_mean_phase()
        
        mode_details = []
        for mode in self.modes:
            mode_details.append({
                'name': mode.name,
                'mass': mode.mass,
                'frequency': mode.frequency,
                'phase': mode.phase,
                'energy': mode.energy(),
                'phase_diff': mode.phase - mean_phase
            })
            
        return {
            'omega': omega,
            'mean_phase': mean_phase,
            'mode_count': len(self.modes),
            'modes': mode_details,
            'history_length': len(self.history)
        }
        
    def get_coherence_metric(self) -> float:
        """
        Calculate coherence metric based on phase distribution.
        
        Returns:
            Value between 0 (incoherent) and 1 (fully coherent)
        """
        if len(self.modes) < 2:
            return 1.0
            
        mean_phase = self.calculate_mean_phase()
        
        # Calculate phase variance
        phase_diffs = [mode.phase - mean_phase for mode in self.modes]
        phase_variance = np.var(phase_diffs)
        
        # Convert variance to coherence (0 variance = 1 coherence)
        coherence = np.exp(-phase_variance)
        
        return coherence
        
    def evolve(self, dt: float = 0.01) -> None:
        """
        Evolve cognitive modes forward in time.
        
        Args:
            dt: Time step for evolution
        """
        for mode in self.modes:
            # Phase evolves as: dφ/dt = ω
            mode.phase += mode.frequency * dt
            # Keep phase in [0, 2π)
            mode.phase = mode.phase % (2 * np.pi)
