"""Tests for AI-O Engine module."""

import unittest
from athena_ai_o.engine.ai_o_engine import AIOEngine, CodeExecution, GeneratedCode


class TestAIOEngine(unittest.TestCase):
    """Test cases for AI-O Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = AIOEngine(safe_mode=True)
        
    def test_initialization(self):
        """Test initialization."""
        self.assertTrue(self.engine.safe_mode)
        self.assertEqual(len(self.engine.execution_history), 0)
        self.assertEqual(len(self.engine.generated_code_history), 0)
        self.assertGreater(len(self.engine.namespace), 0)
        
    def test_validate_code_valid(self):
        """Test code validation with valid code."""
        code = "x = 1 + 2\nprint(x)"
        is_valid, error = self.engine.validate_code(code)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
    def test_validate_code_syntax_error(self):
        """Test code validation with syntax error."""
        code = "x = 1 +"
        is_valid, error = self.engine.validate_code(code)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        
    def test_validate_code_forbidden_import(self):
        """Test code validation with forbidden import."""
        code = "import os"
        is_valid, error = self.engine.validate_code(code)
        self.assertFalse(is_valid)
        self.assertIn("Import", error)
        
    def test_execute_code_success(self):
        """Test successful code execution."""
        code = "result = 2 + 3"
        execution = self.engine.execute_code(code)
        
        self.assertTrue(execution.success)
        self.assertIsNone(execution.error)
        self.assertEqual(self.engine.namespace['result'], 5)
        
    def test_execute_code_with_output(self):
        """Test code execution with output."""
        code = "print('Hello, AI-O!')"
        execution = self.engine.execute_code(code)
        
        self.assertTrue(execution.success)
        self.assertIn("Hello, AI-O!", execution.output)
        
    def test_execute_code_with_error(self):
        """Test code execution with runtime error."""
        code = "x = 1 / 0"
        execution = self.engine.execute_code(code)
        
        self.assertFalse(execution.success)
        self.assertIsNotNone(execution.error)
        self.assertIn("ZeroDivisionError", execution.error)
        
    def test_generate_optimization_code(self):
        """Test optimization code generation."""
        code = self.engine.generate_optimization_code(
            metric="sync_level",
            current_value=0.5,
            target_value=0.9
        )
        
        self.assertIsInstance(code, str)
        self.assertIn("sync_level", code)
        self.assertIn("0.5", code)
        self.assertIn("0.9", code)
        self.assertEqual(len(self.engine.generated_code_history), 1)
        
    def test_generate_exploration_code(self):
        """Test exploration code generation."""
        code = self.engine.generate_exploration_code(num_samples=5)
        
        self.assertIsInstance(code, str)
        self.assertIn("explore", code)
        self.assertIn("5", code)
        
    def test_generate_adaptation_code(self):
        """Test adaptation code generation."""
        context = {
            'omega': 0.8,
            'sync_level': 0.6
        }
        code = self.engine.generate_adaptation_code(context)
        
        self.assertIsInstance(code, str)
        self.assertIn("adapt", code)
        
    def test_autonomous_generation_cycle(self):
        """Test autonomous generation cycle."""
        organism_state = {
            'omega_consciousness': {'omega': 0.5},
            'kuramoto_synchronization': {'sync_level': 0.4}
        }
        
        executions = self.engine.autonomous_generation_cycle(organism_state)
        
        self.assertIsInstance(executions, list)
        self.assertGreater(len(executions), 0)
        
    def test_get_status(self):
        """Test getting engine status."""
        # Execute some code
        self.engine.execute_code("x = 1")
        
        status = self.engine.get_status()
        
        self.assertIn('safe_mode', status)
        self.assertIn('total_executions', status)
        self.assertEqual(status['total_executions'], 1)
        
    def test_clear_history(self):
        """Test clearing history."""
        self.engine.execute_code("x = 1")
        self.engine.generate_exploration_code(5)
        
        self.engine.clear_history()
        
        self.assertEqual(len(self.engine.execution_history), 0)
        self.assertEqual(len(self.engine.generated_code_history), 0)


if __name__ == '__main__':
    unittest.main()
