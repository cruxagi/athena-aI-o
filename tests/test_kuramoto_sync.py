"""Tests for Kuramoto Synchronization module."""

import unittest
import numpy as np
from athena_ai_o.core.kuramoto_sync import KuramotoSynchronization, Oscillator


class TestKuramotoSynchronization(unittest.TestCase):
    """Test cases for Kuramoto Synchronization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.kuramoto = KuramotoSynchronization(coupling_strength=1.0)
        
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.kuramoto.coupling_strength, 1.0)
        self.assertEqual(len(self.kuramoto.oscillators), 0)
        
    def test_add_oscillator(self):
        """Test adding oscillators."""
        self.kuramoto.add_oscillator("osc1", natural_frequency=1.0, initial_phase=0.5)
        self.assertEqual(len(self.kuramoto.oscillators), 1)
        
        osc = self.kuramoto.get_oscillator("osc1")
        self.assertIsNotNone(osc)
        self.assertEqual(osc.natural_frequency, 1.0)
        self.assertEqual(osc.phase, 0.5)
        
    def test_add_oscillator_random_phase(self):
        """Test adding oscillator with random phase."""
        self.kuramoto.add_oscillator("osc1", natural_frequency=1.0)
        osc = self.kuramoto.get_oscillator("osc1")
        
        self.assertGreaterEqual(osc.phase, 0.0)
        self.assertLess(osc.phase, 2 * np.pi)
        
    def test_calculate_order_parameter_empty(self):
        """Test order parameter with no oscillators."""
        r, psi = self.kuramoto.calculate_order_parameter()
        self.assertEqual(r, 0.0)
        self.assertEqual(psi, 0.0)
        
    def test_calculate_order_parameter(self):
        """Test order parameter calculation."""
        self.kuramoto.add_oscillator("osc1", 1.0, initial_phase=0.0)
        self.kuramoto.add_oscillator("osc2", 1.0, initial_phase=0.1)
        self.kuramoto.add_oscillator("osc3", 1.0, initial_phase=0.2)
        
        r, psi = self.kuramoto.calculate_order_parameter()
        self.assertGreaterEqual(r, 0.0)
        self.assertLessEqual(r, 1.0)
        self.assertIsInstance(psi, float)
        
    def test_step(self):
        """Test single integration step."""
        self.kuramoto.add_oscillator("osc1", 1.0, initial_phase=0.0)
        self.kuramoto.add_oscillator("osc2", 1.1, initial_phase=1.0)
        
        initial_phase1 = self.kuramoto.get_oscillator("osc1").phase
        
        r = self.kuramoto.step(dt=0.01)
        
        updated_phase1 = self.kuramoto.get_oscillator("osc1").phase
        self.assertNotEqual(initial_phase1, updated_phase1)
        self.assertIsInstance(r, float)
        
    def test_synchronize(self):
        """Test synchronization process."""
        self.kuramoto.add_oscillator("osc1", 1.0)
        self.kuramoto.add_oscillator("osc2", 1.1)
        self.kuramoto.add_oscillator("osc3", 0.9)
        
        result = self.kuramoto.synchronize(steps=500, dt=0.01)
        
        self.assertIn('final_sync_level', result)
        self.assertIn('collective_phase', result)
        self.assertIn('converged', result)
        self.assertGreaterEqual(result['final_sync_level'], 0.0)
        self.assertLessEqual(result['final_sync_level'], 1.0)
        
    def test_get_phase_coherence_matrix(self):
        """Test phase coherence matrix."""
        self.kuramoto.add_oscillator("osc1", 1.0, initial_phase=0.0)
        self.kuramoto.add_oscillator("osc2", 1.0, initial_phase=0.5)
        
        matrix = self.kuramoto.get_phase_coherence_matrix()
        self.assertEqual(matrix.shape, (2, 2))
        # Diagonal should be 1 (coherence with self)
        np.testing.assert_almost_equal(matrix[0, 0], 1.0)
        np.testing.assert_almost_equal(matrix[1, 1], 1.0)
        
    def test_get_state(self):
        """Test getting system state."""
        self.kuramoto.add_oscillator("osc1", 1.0)
        
        state = self.kuramoto.get_state()
        self.assertIn('coupling_strength', state)
        self.assertIn('num_oscillators', state)
        self.assertIn('sync_level', state)
        self.assertIn('oscillators', state)
        self.assertEqual(state['num_oscillators'], 1)
        
    def test_reset_phases(self):
        """Test resetting phases."""
        self.kuramoto.add_oscillator("osc1", 1.0, initial_phase=1.5)
        
        self.kuramoto.reset_phases(random=False)
        self.assertEqual(self.kuramoto.get_oscillator("osc1").phase, 0.0)


if __name__ == '__main__':
    unittest.main()
