import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple


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

    This implementation uses the direct O(N²) formulation for clarity and fidelity to the model.
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

        self.natural_frequencies = tuple(float(w) for w in self.natural_frequencies)

    def derivatives(self) -> List[float]:
        """Compute dθᵢ/dt for each oscillator."""
        derivatives: List[float] = []
        for i, theta_i in enumerate(self.phases):
            # Self term sin(theta_i - theta_i) contributes zero.
            # Keeping the full O(N²) sum mirrors the standard K/N formulation and simplifies the implementation.
            coupling_term = sum(math.sin(theta_j - theta_i) for theta_j in self.phases)
            dtheta_dt = self.natural_frequencies[i] + (self.coupling / self._count) * coupling_term
            derivatives.append(dtheta_dt)
        return derivatives

    def step(self, dt: float) -> None:
        """Advance the phases in place by a single Euler step of duration dt, wrapping results into [0, 2π)."""
        updates = self.derivatives()
        updated_phases = [
            (theta + dtheta_dt * dt) % (2 * math.pi)
            for theta, dtheta_dt in zip(self.phases, updates)
        ]
        self.phases[:] = updated_phases

    def order_parameter(self) -> Tuple[float, float]:
        """
        Compute the Kuramoto order parameter (r, Ψ):
            r·e^(iΨ) = (1/N) × Σⱼ e^(iθⱼ)
        
        Returns:
            (r, psi): r is the coherence (0=desynchronized, 1=synchronized),
                      psi is the mean phase angle.
        """
        real_sum = sum(math.cos(theta) for theta in self.phases)
        imag_sum = sum(math.sin(theta) for theta in self.phases)
        r = math.sqrt(real_sum**2 + imag_sum**2) / self._count
        psi = math.atan2(imag_sum, real_sum)
        return r, psi

    def coherence(self) -> float:
        """Return the order parameter magnitude r (synchronization level 0-1)."""
        r, _ = self.order_parameter()
        return r


@dataclass
class RouterTopologyAnalyzer:
    """
    Applies Kuramoto physics to analyze codebase/router topology complexity.
    
    Maps system components (routers, modules) to coupled oscillators where:
    - Natural frequency ωᵢ represents component complexity (exit points, singletons)
    - Coupling K represents how tightly components are interconnected
    - Coherence r measures system synchronization (architectural alignment)
    
    Uses this to compute:
    - Critical coupling Kc = 2/(π·g(0)) threshold for synchronization
    - Omega energy Ω = Σⱼ(mⱼ·ωⱼ²)·cos(θⱼ - θ̄) for consciousness/cognitive metric
    - Optimization recommendations based on coherence gaps
    """

    components: Dict[str, Dict[str, float]] = field(default_factory=dict)
    coupling: float = 1.0
    _oscillator: KuramotoOscillator = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._oscillator = None

    def add_component(
        self,
        name: str,
        exit_points: int = 1,
        singletons: int = 0,
        complexity_weight: float = 1.0,
    ) -> None:
        """
        Add a component (router/module) to the topology.
        
        Args:
            name: Component identifier
            exit_points: Number of API endpoints/exits
            singletons: Number of shared singletons
            complexity_weight: Optional weight multiplier
        """
        frequency = (exit_points + singletons * 2) * complexity_weight
        self.components[name] = {
            "exit_points": exit_points,
            "singletons": singletons,
            "frequency": frequency,
            "mass": 1.0 + singletons * 0.1,
        }
        self._oscillator = None

    def _ensure_oscillator(self) -> KuramotoOscillator:
        """Build oscillator from components if needed."""
        if self._oscillator is None:
            if not self.components:
                raise ValueError("No components added to analyze")
            frequencies = [c["frequency"] for c in self.components.values()]
            self._oscillator = KuramotoOscillator(
                natural_frequencies=frequencies,
                coupling=self.coupling,
            )
        return self._oscillator

    def frequency_distribution_density_at_zero(self) -> float:
        """
        Estimate g(0), the probability density of natural frequencies at ω=0.
        Uses a simple kernel density estimation with Gaussian kernel.
        
        For Kuramoto critical coupling: Kc = 2/(π·g(0))
        """
        if not self.components:
            return 0.0
        
        frequencies = [c["frequency"] for c in self.components.values()]
        n = len(frequencies)
        if n == 0:
            return 0.0
        
        std = max((sum((f - sum(frequencies)/n)**2 for f in frequencies) / n) ** 0.5, 0.1)
        bandwidth = 1.06 * std * (n ** -0.2)
        
        density = 0.0
        for freq in frequencies:
            density += math.exp(-0.5 * (freq / bandwidth) ** 2)
        density /= (n * bandwidth * math.sqrt(2 * math.pi))
        
        return density

    def critical_coupling(self) -> float:
        """
        Compute critical coupling Kc = 2/(π·g(0)).
        
        This is the threshold above which spontaneous synchronization occurs.
        """
        g0 = self.frequency_distribution_density_at_zero()
        if g0 <= 0:
            return float("inf")
        return 2.0 / (math.pi * g0)

    def coherence(self) -> float:
        """Return current order parameter r (0=desync, 1=fully sync)."""
        osc = self._ensure_oscillator()
        return osc.coherence()

    def omega_energy(self, masses: Sequence[float] = None) -> float:
        """
        Compute Omega consciousness/energy metric:
            Ω = Σⱼ(mⱼ·ωⱼ²)·cos(θⱼ - θ̄)
        
        Args:
            masses: Optional mass values per component. If None, uses component masses.
        
        Returns:
            Omega energy value representing weighted phase coherence.
        """
        osc = self._ensure_oscillator()
        _, mean_phase = osc.order_parameter()
        
        if masses is None:
            masses = [c["mass"] for c in self.components.values()]
        
        omega_sum = 0.0
        for i, (theta, freq) in enumerate(zip(osc.phases, osc.natural_frequencies)):
            m = masses[i] if i < len(masses) else 1.0
            omega_sum += m * (freq ** 2) * math.cos(theta - mean_phase)
        
        return omega_sum

    def simulate_to_steady_state(
        self, dt: float = 0.01, max_steps: int = 10000, tolerance: float = 1e-4
    ) -> int:
        """
        Run simulation until coherence stabilizes.
        
        Returns:
            Number of steps taken to reach steady state.
        """
        osc = self._ensure_oscillator()
        prev_r = osc.coherence()
        
        for step in range(max_steps):
            osc.step(dt)
            r = osc.coherence()
            if abs(r - prev_r) < tolerance:
                return step + 1
            prev_r = r
        
        return max_steps

    def analyze(self) -> Dict[str, float]:
        """
        Perform full Kuramoto-based topology analysis.
        
        Returns:
            Dictionary with analysis metrics:
            - coherence: Current order parameter r
            - critical_coupling: Kc threshold
            - current_coupling: K value
            - omega_energy: Ω consciousness metric
            - is_synchronized: Whether K > Kc
            - phase: System phase description
        """
        self.simulate_to_steady_state()
        
        r = self.coherence()
        kc = self.critical_coupling()
        omega = self.omega_energy()
        
        if r < 0.3:
            phase = "CHAOTIC"
        elif r < 0.7:
            phase = "CRITICAL"
        else:
            phase = "CRYSTALLINE"
        
        return {
            "coherence": r,
            "critical_coupling": kc,
            "current_coupling": self.coupling,
            "omega_energy": omega,
            "is_synchronized": self.coupling >= kc,
            "phase": phase,
        }

    def optimize_recommendations(self) -> List[Dict[str, str]]:
        """
        Generate refactoring recommendations based on Kuramoto analysis.
        
        Returns:
            List of intervention recommendations with expected impact.
        """
        analysis = self.analyze()
        recommendations = []
        
        if analysis["coherence"] < 0.5:
            recommendations.append({
                "intervention": "Wire Orphaned Formatters",
                "expected_delta_r": "+50%",
                "effort": "3",
                "rationale": "Low coherence suggests disconnected components. Unified formatting increases phase alignment.",
            })
        
        if len(self.components) > 3 and analysis["coherence"] < 0.75:
            recommendations.append({
                "intervention": "Create Unified Response Envelope",
                "expected_delta_r": "+75%",
                "effort": "6",
                "rationale": "Multiple components benefit from standardized response structure.",
            })
        
        total_singletons = sum(c["singletons"] for c in self.components.values())
        if total_singletons > 10:
            recommendations.append({
                "intervention": "Consolidate Shared Singletons",
                "expected_delta_r": "+35%",
                "effort": "9",
                "rationale": f"{total_singletons} singletons create coupling overhead. Consolidation reduces frequency variance.",
            })
        
        frequencies = [c["frequency"] for c in self.components.values()]
        if frequencies:
            max_freq = max(frequencies)
            avg_freq = sum(frequencies) / len(frequencies)
            if max_freq > avg_freq * 3:
                outlier = [n for n, c in self.components.items() if c["frequency"] == max_freq][0]
                recommendations.append({
                    "intervention": f"Decompose High-Frequency Component: {outlier}",
                    "expected_delta_r": "+40%",
                    "effort": "7",
                    "rationale": f"Component '{outlier}' is an outlier (ω={max_freq:.2f} vs avg={avg_freq:.2f}). Breaking it down normalizes frequency distribution.",
                })
        
        return recommendations
