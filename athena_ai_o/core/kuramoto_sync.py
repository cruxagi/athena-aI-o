"""
Kuramoto Synchronization: Phase coherence across cognitive modes.

Implements the Kuramoto model for synchronization of coupled oscillators,
adapted for cognitive mode synchronization.

Model: dφᵢ/dt = ωᵢ + (K/N) Σⱼ sin(φⱼ - φᵢ)

Where:
- φᵢ: phase of oscillator i
- ωᵢ: natural frequency of oscillator i
- K: coupling strength
- N: number of oscillators
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Oscillator:
    """Represents a single oscillator in the Kuramoto model."""
    id: str
    natural_frequency: float  # ωᵢ
    phase: float  # φᵢ (in radians)
    
    
class KuramotoSynchronization:
    """
    Kuramoto Synchronization for phase coherence across cognitive modes.
    
    Implements the Kuramoto model to achieve phase synchronization
    among coupled oscillators representing cognitive modes.
    """
    
    def __init__(self, coupling_strength: float = 1.0):
        """
        Initialize Kuramoto synchronization system.
        
        Args:
            coupling_strength: K, the coupling strength between oscillators
        """
        self.coupling_strength = coupling_strength  # K
        self.oscillators: List[Oscillator] = []
        self.synchronization_history: List[float] = []
        
    def add_oscillator(self, id: str, natural_frequency: float, initial_phase: float = None) -> None:
        """
        Add an oscillator to the system.
        
        Args:
            id: Unique identifier for the oscillator
            natural_frequency: Natural frequency ωᵢ
            initial_phase: Initial phase (random if None)
        """
        if initial_phase is None:
            initial_phase = np.random.uniform(0, 2 * np.pi)
            
        oscillator = Oscillator(
            id=id,
            natural_frequency=natural_frequency,
            phase=initial_phase
        )
        self.oscillators.append(oscillator)
        
    def get_oscillator(self, id: str) -> Optional[Oscillator]:
        """Get oscillator by ID."""
        for osc in self.oscillators:
            if osc.id == id:
                return osc
        return None
        
    def calculate_order_parameter(self) -> Tuple[float, float]:
        """
        Calculate Kuramoto order parameter.
        
        The order parameter r measures the degree of synchronization:
        r·e^(iΨ) = (1/N) Σⱼ e^(iφⱼ)
        
        Returns:
            Tuple of (r, Ψ) where:
            - r ∈ [0,1]: synchronization level (0=incoherent, 1=fully synchronized)
            - Ψ: collective phase
        """
        if not self.oscillators:
            return 0.0, 0.0
            
        N = len(self.oscillators)
        
        # Calculate complex order parameter
        sum_exp = sum(np.exp(1j * osc.phase) for osc in self.oscillators)
        order_param = sum_exp / N
        
        r = abs(order_param)  # Synchronization level
        psi = np.angle(order_param)  # Collective phase
        
        return r, psi
        
    def step(self, dt: float = 0.01) -> float:
        """
        Perform one Kuramoto integration step.
        
        Updates phases according to: dφᵢ/dt = ωᵢ + (K/N) Σⱼ sin(φⱼ - φᵢ)
        
        Args:
            dt: Time step
            
        Returns:
            Current synchronization level r
        """
        if not self.oscillators:
            return 0.0
            
        N = len(self.oscillators)
        
        # Calculate phase derivatives for all oscillators
        phase_derivatives = []
        for i, osc_i in enumerate(self.oscillators):
            # Natural frequency term
            dphidt = osc_i.natural_frequency
            
            # Coupling term: (K/N) Σⱼ sin(φⱼ - φᵢ)
            coupling_sum = 0.0
            for osc_j in self.oscillators:
                coupling_sum += np.sin(osc_j.phase - osc_i.phase)
                
            dphidt += (self.coupling_strength / N) * coupling_sum
            phase_derivatives.append(dphidt)
            
        # Update phases using Euler method
        for i, osc in enumerate(self.oscillators):
            osc.phase += phase_derivatives[i] * dt
            # Keep phase in [0, 2π)
            osc.phase = osc.phase % (2 * np.pi)
            
        # Calculate and store synchronization level
        r, _ = self.calculate_order_parameter()
        self.synchronization_history.append(r)
        
        return r
        
    def synchronize(self, steps: int = 1000, dt: float = 0.01, 
                   convergence_threshold: float = 0.001) -> Dict:
        """
        Run synchronization until convergence or max steps.
        
        Args:
            steps: Maximum number of steps
            dt: Time step
            convergence_threshold: Stop if change in r < threshold
            
        Returns:
            Dictionary with synchronization results
        """
        r_values = []
        
        for step in range(steps):
            r = self.step(dt)
            r_values.append(r)
            
            # Check for convergence
            if step > 10:
                recent_change = abs(r_values[-1] - r_values[-2])
                if recent_change < convergence_threshold:
                    break
                    
        final_r, final_psi = self.calculate_order_parameter()
        
        return {
            'final_sync_level': final_r,
            'collective_phase': final_psi,
            'steps_taken': len(r_values),
            'converged': len(r_values) < steps,
            'sync_history': r_values
        }
        
    def get_phase_coherence_matrix(self) -> np.ndarray:
        """
        Calculate phase coherence matrix between all oscillators.
        
        Returns:
            N x N matrix where element (i,j) = cos(φᵢ - φⱼ)
        """
        N = len(self.oscillators)
        matrix = np.zeros((N, N))
        
        for i, osc_i in enumerate(self.oscillators):
            for j, osc_j in enumerate(self.oscillators):
                matrix[i, j] = np.cos(osc_i.phase - osc_j.phase)
                
        return matrix
        
    def get_state(self) -> Dict:
        """
        Get current state of the synchronization system.
        
        Returns:
            Dictionary with system state information
        """
        r, psi = self.calculate_order_parameter()
        
        oscillator_states = []
        for osc in self.oscillators:
            oscillator_states.append({
                'id': osc.id,
                'natural_frequency': osc.natural_frequency,
                'phase': osc.phase,
                'phase_deg': np.degrees(osc.phase)
            })
            
        return {
            'coupling_strength': self.coupling_strength,
            'num_oscillators': len(self.oscillators),
            'sync_level': r,
            'collective_phase': psi,
            'oscillators': oscillator_states,
            'history_length': len(self.synchronization_history)
        }
        
    def reset_phases(self, random: bool = True) -> None:
        """
        Reset oscillator phases.
        
        Args:
            random: If True, set random phases; if False, set all to 0
        """
        for osc in self.oscillators:
            if random:
                osc.phase = np.random.uniform(0, 2 * np.pi)
            else:
                osc.phase = 0.0
