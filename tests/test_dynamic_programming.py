"""Tests for Dynamic Programming module."""

import unittest
from athena_ai_o.core.dynamic_programming import DynamicProgramming, State, Action


class TestDynamicProgramming(unittest.TestCase):
    """Test cases for Dynamic Programming."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dp = DynamicProgramming(gamma=0.9, theta=1e-6)
        
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.dp.gamma, 0.9)
        self.assertEqual(self.dp.theta, 1e-6)
        self.assertEqual(len(self.dp.states), 0)
        self.assertEqual(len(self.dp.actions), 0)
        
    def test_add_state(self):
        """Test adding states."""
        self.dp.add_state("s1", initial_value=5.0)
        self.assertIn("s1", self.dp.states)
        self.assertEqual(self.dp.value_function["s1"], 5.0)
        
    def test_add_action(self):
        """Test adding actions."""
        self.dp.add_action("a1")
        self.assertIn("a1", self.dp.actions)
        
    def test_add_transition(self):
        """Test adding transitions."""
        self.dp.add_state("s1")
        self.dp.add_state("s2")
        self.dp.add_action("a1")
        
        self.dp.add_transition("s1", "a1", "s2", probability=0.8, reward=10.0)
        self.assertEqual(len(self.dp.transitions), 1)
        
    def test_get_available_actions(self):
        """Test getting available actions."""
        self.dp.add_state("s1")
        self.dp.add_state("s2")
        self.dp.add_action("a1")
        self.dp.add_action("a2")
        
        self.dp.add_transition("s1", "a1", "s2", 0.5, 1.0)
        self.dp.add_transition("s1", "a2", "s2", 0.5, 2.0)
        
        actions = self.dp.get_available_actions("s1")
        self.assertEqual(set(actions), {"a1", "a2"})
        
    def test_calculate_q_value(self):
        """Test Q-value calculation."""
        self.dp.add_state("s1", initial_value=0.0)
        self.dp.add_state("s2", initial_value=10.0)
        self.dp.add_action("a1")
        
        self.dp.add_transition("s1", "a1", "s2", probability=1.0, reward=5.0)
        
        q_value = self.dp.calculate_q_value("s1", "a1")
        # Q = P(s'|s,a) * [R + γ*V(s')]
        # Q = 1.0 * [5.0 + 0.9 * 10.0] = 1.0 * 14.0 = 14.0
        self.assertAlmostEqual(q_value, 14.0)
        
    def test_value_iteration_simple(self):
        """Test value iteration on simple MDP."""
        # Simple two-state MDP
        self.dp.add_state("s1")
        self.dp.add_state("goal")
        self.dp.add_action("go")
        
        self.dp.add_transition("s1", "go", "goal", 1.0, 10.0)
        
        result = self.dp.value_iteration(max_iterations=100)
        
        self.assertTrue(result['converged'])
        self.assertIn('value_function', result)
        
    def test_extract_policy(self):
        """Test policy extraction."""
        self.dp.add_state("s1")
        self.dp.add_state("s2")
        self.dp.add_action("a1")
        self.dp.add_action("a2")
        
        self.dp.add_transition("s1", "a1", "s2", 1.0, 5.0)
        self.dp.add_transition("s1", "a2", "s2", 1.0, 10.0)
        
        self.dp.value_iteration()
        policy = self.dp.extract_policy()
        
        self.assertIn("s1", policy)
        # Should prefer a2 with higher reward
        self.assertEqual(policy["s1"], "a2")
        
    def test_policy_iteration(self):
        """Test policy iteration."""
        self.dp.add_state("s1")
        self.dp.add_state("s2")
        self.dp.add_action("a1")
        
        self.dp.add_transition("s1", "a1", "s2", 1.0, 10.0)
        
        result = self.dp.policy_iteration(max_iterations=100)
        
        self.assertIn('policy', result)
        self.assertIn('value_function', result)
        
    def test_get_optimal_action(self):
        """Test getting optimal action."""
        self.dp.add_state("s1")
        self.dp.add_state("s2")
        self.dp.add_action("a1")
        
        self.dp.add_transition("s1", "a1", "s2", 1.0, 10.0)
        self.dp.value_iteration()
        self.dp.extract_policy()
        
        action = self.dp.get_optimal_action("s1")
        self.assertEqual(action, "a1")
        
    def test_get_state_value(self):
        """Test getting state value."""
        self.dp.add_state("s1", initial_value=5.0)
        value = self.dp.get_state_value("s1")
        self.assertEqual(value, 5.0)
        
    def test_get_state_summary(self):
        """Test state summary."""
        self.dp.add_state("s1")
        self.dp.add_action("a1")
        
        summary = self.dp.get_state_summary()
        self.assertEqual(summary['num_states'], 1)
        self.assertEqual(summary['num_actions'], 1)


if __name__ == '__main__':
    unittest.main()
