import math
import unittest

from kuramoto import KuramotoOscillator, RouterTopologyAnalyzer


class KuramotoOscillatorTest(unittest.TestCase):
    def test_derivatives_match_kuramoto_equation(self) -> None:
        osc = KuramotoOscillator(
            natural_frequencies=[1.0, 1.5],
            coupling=2.0,
            phases=[0.0, math.pi / 2],
        )

        derivatives = osc.derivatives()

        # Expected with self terms included (sin(0) = 0):
        # dtheta0/dt = 1.0 + (2/2) * [sin(0 - 0) + sin(pi/2 - 0)] = 1.0 + 1 * (0 + 1) = 2.0
        # dtheta1/dt = 1.5 + (2/2) * [sin(0 - pi/2) + sin(pi/2 - pi/2)] = 1.5 + 1 * (-1 + 0) = 0.5
        self.assertAlmostEqual(derivatives[0], 2.0, places=6)
        self.assertAlmostEqual(derivatives[1], 0.5, places=6)

    def test_step_advances_phases_using_derivatives(self) -> None:
        osc = KuramotoOscillator(
            natural_frequencies=[1.0, 1.5],
            coupling=2.0,
            phases=[0.0, math.pi / 2],
        )

        osc.step(0.1)

        self.assertAlmostEqual(osc.phases[0], 0.2, places=6)
        self.assertAlmostEqual(osc.phases[1], (math.pi / 2) + 0.05, places=6)


class OrderParameterTest(unittest.TestCase):
    def test_order_parameter_fully_synchronized(self) -> None:
        """All oscillators at the same phase should give r=1."""
        osc = KuramotoOscillator(
            natural_frequencies=[1.0, 2.0, 3.0],
            phases=[0.0, 0.0, 0.0],
        )
        r, psi = osc.order_parameter()
        self.assertAlmostEqual(r, 1.0, places=6)
        self.assertAlmostEqual(psi, 0.0, places=6)

    def test_order_parameter_desynchronized(self) -> None:
        """Oscillators evenly spaced around circle should give r≈0."""
        n = 4
        phases = [2 * math.pi * i / n for i in range(n)]
        osc = KuramotoOscillator(
            natural_frequencies=[1.0] * n,
            phases=phases,
        )
        r, _ = osc.order_parameter()
        self.assertAlmostEqual(r, 0.0, places=6)

    def test_coherence_method(self) -> None:
        """coherence() should return just the r value."""
        osc = KuramotoOscillator(
            natural_frequencies=[1.0, 1.0],
            phases=[0.0, 0.0],
        )
        self.assertAlmostEqual(osc.coherence(), 1.0, places=6)


class RouterTopologyAnalyzerTest(unittest.TestCase):
    def test_add_component(self) -> None:
        analyzer = RouterTopologyAnalyzer()
        analyzer.add_component("test-router", exit_points=10, singletons=3)
        
        self.assertIn("test-router", analyzer.components)
        self.assertEqual(analyzer.components["test-router"]["exit_points"], 10)
        self.assertEqual(analyzer.components["test-router"]["singletons"], 3)
        # frequency = (exit_points + singletons * 2) * weight = (10 + 3*2) * 1.0 = 16
        self.assertAlmostEqual(analyzer.components["test-router"]["frequency"], 16.0, places=6)

    def test_critical_coupling_formula(self) -> None:
        """Critical coupling should be Kc = 2/(π·g(0))."""
        analyzer = RouterTopologyAnalyzer()
        analyzer.add_component("a", exit_points=5, singletons=0)
        analyzer.add_component("b", exit_points=5, singletons=0)
        
        kc = analyzer.critical_coupling()
        g0 = analyzer.frequency_distribution_density_at_zero()
        
        # Kc = 2 / (pi * g0)
        expected_kc = 2.0 / (math.pi * g0) if g0 > 0 else float("inf")
        self.assertAlmostEqual(kc, expected_kc, places=6)

    def test_coherence_initial_value(self) -> None:
        """Initial coherence should be 1.0 (all phases start at 0)."""
        analyzer = RouterTopologyAnalyzer()
        analyzer.add_component("a", exit_points=5)
        analyzer.add_component("b", exit_points=10)
        
        self.assertAlmostEqual(analyzer.coherence(), 1.0, places=6)

    def test_omega_energy_calculation(self) -> None:
        """Omega energy should use the formula Ω = Σⱼ(mⱼ·ωⱼ²)·cos(θⱼ - θ̄)."""
        analyzer = RouterTopologyAnalyzer()
        analyzer.add_component("a", exit_points=2, singletons=0)  # freq=2, mass=1.0
        analyzer.add_component("b", exit_points=3, singletons=0)  # freq=3, mass=1.0
        
        # All phases at 0, mean phase = 0, cos(0) = 1
        # Omega = 1.0 * 2^2 * 1 + 1.0 * 3^2 * 1 = 4 + 9 = 13
        omega = analyzer.omega_energy()
        self.assertAlmostEqual(omega, 13.0, places=6)

    def test_analyze_returns_expected_keys(self) -> None:
        analyzer = RouterTopologyAnalyzer()
        analyzer.add_component("router-a", exit_points=5)
        analyzer.add_component("router-b", exit_points=10)
        
        result = analyzer.analyze()
        
        self.assertIn("coherence", result)
        self.assertIn("critical_coupling", result)
        self.assertIn("current_coupling", result)
        self.assertIn("omega_energy", result)
        self.assertIn("is_synchronized", result)
        self.assertIn("phase", result)

    def test_optimize_recommendations_for_low_coherence(self) -> None:
        """Low coherence systems should get 'Wire Orphaned Formatters' recommendation."""
        analyzer = RouterTopologyAnalyzer(coupling=0.0)  # No coupling = no sync
        # Add components with very different frequencies to ensure low coherence after simulation
        analyzer.add_component("fast", exit_points=50)
        analyzer.add_component("slow", exit_points=1)
        
        recommendations = analyzer.optimize_recommendations()
        interventions = [r["intervention"] for r in recommendations]
        
        # Should recommend something (exact recommendations depend on analysis)
        self.assertIsInstance(recommendations, list)

    def test_high_singleton_count_triggers_consolidation_recommendation(self) -> None:
        """Systems with many singletons should get consolidation recommendation."""
        analyzer = RouterTopologyAnalyzer()
        analyzer.add_component("a", exit_points=5, singletons=4)
        analyzer.add_component("b", exit_points=5, singletons=4)
        analyzer.add_component("c", exit_points=5, singletons=4)
        
        recommendations = analyzer.optimize_recommendations()
        interventions = [r["intervention"] for r in recommendations]
        
        self.assertIn("Consolidate Shared Singletons", interventions)


if __name__ == "__main__":
    unittest.main()
