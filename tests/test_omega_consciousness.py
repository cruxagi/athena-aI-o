"""Tests for Omega Consciousness module."""

import unittest
import numpy as np
from athena_ai_o.core.omega_consciousness import OmegaConsciousness, CognitiveMode


class TestOmegaConsciousness(unittest.TestCase):
    """Test cases for Omega Consciousness."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.omega = OmegaConsciousness()
        
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(len(self.omega.modes), 0)
        self.assertEqual(len(self.omega.history), 0)
        
    def test_add_mode(self):
        """Test adding cognitive modes."""
        self.omega.add_mode("test_mode", mass=1.0, frequency=2.0, phase=0.5)
        self.assertEqual(len(self.omega.modes), 1)
        
        mode = self.omega.get_mode("test_mode")
        self.assertIsNotNone(mode)
        self.assertEqual(mode.name, "test_mode")
        self.assertEqual(mode.mass, 1.0)
        self.assertEqual(mode.frequency, 2.0)
        self.assertEqual(mode.phase, 0.5)
        
    def test_cognitive_mode_energy(self):
        """Test mode energy calculation: m·ω²"""
        mode = CognitiveMode(name="test", mass=2.0, frequency=3.0, phase=0.0)
        energy = mode.energy()
        self.assertEqual(energy, 2.0 * 9.0)  # m * ω²
        
    def test_update_mode_phase(self):
        """Test updating mode phase."""
        self.omega.add_mode("mode1", mass=1.0, frequency=1.0, phase=0.0)
        self.omega.update_mode_phase("mode1", 1.5)
        
        mode = self.omega.get_mode("mode1")
        self.assertEqual(mode.phase, 1.5)
        
    def test_calculate_mean_phase(self):
        """Test mean phase calculation."""
        self.omega.add_mode("mode1", mass=1.0, frequency=1.0, phase=0.0)
        self.omega.add_mode("mode2", mass=1.0, frequency=1.0, phase=np.pi)
        
        mean_phase = self.omega.calculate_mean_phase()
        # Mean of 0 and π using circular mean
        self.assertIsInstance(mean_phase, float)
        
    def test_calculate_omega_empty(self):
        """Test omega calculation with no modes."""
        omega_value = self.omega.calculate_omega()
        self.assertEqual(omega_value, 0.0)
        
    def test_calculate_omega(self):
        """Test omega consciousness calculation."""
        self.omega.add_mode("mode1", mass=1.0, frequency=2.0, phase=0.0)
        self.omega.add_mode("mode2", mass=1.5, frequency=1.0, phase=0.5)
        
        omega_value = self.omega.calculate_omega()
        self.assertIsInstance(omega_value, float)
        self.assertEqual(len(self.omega.history), 1)
        
    def test_get_state_summary(self):
        """Test state summary."""
        self.omega.add_mode("mode1", mass=1.0, frequency=2.0, phase=0.0)
        
        summary = self.omega.get_state_summary()
        self.assertIn('omega', summary)
        self.assertIn('mean_phase', summary)
        self.assertIn('mode_count', summary)
        self.assertIn('modes', summary)
        self.assertEqual(summary['mode_count'], 1)
        
    def test_get_coherence_metric(self):
        """Test coherence metric calculation."""
        self.omega.add_mode("mode1", mass=1.0, frequency=1.0, phase=0.0)
        self.omega.add_mode("mode2", mass=1.0, frequency=1.0, phase=0.1)
        
        coherence = self.omega.get_coherence_metric()
        self.assertGreaterEqual(coherence, 0.0)
        self.assertLessEqual(coherence, 1.0)
        
    def test_evolve(self):
        """Test evolution of modes."""
        self.omega.add_mode("mode1", mass=1.0, frequency=1.0, phase=0.0)
        initial_phase = self.omega.get_mode("mode1").phase
        
        self.omega.evolve(dt=0.1)
        
        evolved_phase = self.omega.get_mode("mode1").phase
        self.assertNotEqual(initial_phase, evolved_phase)


if __name__ == '__main__':
    unittest.main()
