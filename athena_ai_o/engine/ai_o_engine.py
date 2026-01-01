"""
AI-O Engine: Autonomous code generation and execution system.

The organism autonomously generates and executes code to evolve
and improve itself based on consciousness and synchronization metrics.
"""

import ast
import sys
import traceback
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
import io
import contextlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeExecution:
    """Represents a code execution result."""
    code: str
    success: bool
    output: str
    error: Optional[str]
    timestamp: datetime
    execution_time: float
    

@dataclass
class GeneratedCode:
    """Represents autonomously generated code."""
    purpose: str
    code: str
    timestamp: datetime
    validated: bool = False
    

class AIOEngine:
    """
    AI-O Engine for autonomous code generation and execution.
    
    The organism uses this engine to generate and execute code
    for self-improvement and adaptation.
    """
    
    def __init__(self, safe_mode: bool = True):
        """
        Initialize AI-O Engine.
        
        Args:
            safe_mode: If True, restrict certain operations for safety
        """
        self.safe_mode = safe_mode
        self.execution_history: List[CodeExecution] = []
        self.generated_code_history: List[GeneratedCode] = []
        self.namespace: Dict[str, Any] = {}
        
        # Initialize safe namespace with useful modules
        self._initialize_namespace()
        
    def _initialize_namespace(self) -> None:
        """Initialize execution namespace with safe built-ins."""
        # Import safe modules
        import math
        import random
        import datetime
        import json
        
        self.namespace = {
            'math': math,
            'random': random,
            'datetime': datetime,
            'json': json,
            'print': print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
        }
        
    def validate_code(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate Python code for syntax and safety.
        
        Args:
            code: Python code string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse code to check syntax
            tree = ast.parse(code)
            
            if self.safe_mode:
                # Check for forbidden operations
                forbidden = ['import', 'exec', 'eval', '__import__', 'compile', 'open']
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                        return False, "Import statements not allowed in safe mode"
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in forbidden:
                                return False, f"Function '{node.func.id}' not allowed in safe mode"
                                
            return True, None
            
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"
            
    def execute_code(self, code: str, timeout: Optional[float] = None) -> CodeExecution:
        """
        Execute Python code in controlled environment.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time (seconds) - not implemented yet
            
        Returns:
            CodeExecution result object
        """
        start_time = datetime.now()
        
        # Validate code first
        is_valid, error = self.validate_code(code)
        if not is_valid:
            execution = CodeExecution(
                code=code,
                success=False,
                output="",
                error=f"Validation failed: {error}",
                timestamp=start_time,
                execution_time=0.0
            )
            self.execution_history.append(execution)
            return execution
            
        # Capture output
        output_buffer = io.StringIO()
        error_msg = None
        success = False
        
        try:
            with contextlib.redirect_stdout(output_buffer):
                # Execute code in namespace
                exec(code, self.namespace)
            success = True
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            logger.error(f"Code execution error: {error_msg}")
            
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        execution = CodeExecution(
            code=code,
            success=success,
            output=output_buffer.getvalue(),
            error=error_msg,
            timestamp=start_time,
            execution_time=execution_time
        )
        
        self.execution_history.append(execution)
        
        if success:
            logger.info(f"Code executed successfully in {execution_time:.3f}s")
        else:
            logger.error(f"Code execution failed: {error_msg}")
            
        return execution
        
    def generate_optimization_code(self, metric: str, current_value: float,
                                   target_value: float) -> str:
        """
        Generate code to optimize a specific metric.
        
        Args:
            metric: Metric name to optimize
            current_value: Current metric value
            target_value: Target metric value
            
        Returns:
            Generated Python code
        """
        code = f"""
# Auto-generated optimization code for {metric}
# Current: {current_value:.3f}, Target: {target_value:.3f}

def optimize_{metric.replace(' ', '_')}():
    current = {current_value}
    target = {target_value}
    
    # Calculate adjustment needed
    adjustment = target - current
    adjustment_factor = adjustment / max(abs(current), 0.001)
    
    print(f"Optimizing {metric}")
    print(f"  Current value: {{current:.3f}}")
    print(f"  Target value: {{target:.3f}}")
    print(f"  Adjustment needed: {{adjustment:.3f}}")
    print(f"  Adjustment factor: {{adjustment_factor:.3f}}")
    
    return adjustment_factor

# Execute optimization
result = optimize_{metric.replace(' ', '_')}()
"""
        
        generated = GeneratedCode(
            purpose=f"Optimize {metric}",
            code=code,
            timestamp=datetime.now(),
            validated=True
        )
        self.generated_code_history.append(generated)
        
        return code
        
    def generate_exploration_code(self, num_samples: int = 10) -> str:
        """
        Generate code for exploration and learning.
        
        Args:
            num_samples: Number of exploration samples
            
        Returns:
            Generated Python code
        """
        code = f"""
# Auto-generated exploration code
import random

def explore_parameter_space():
    samples = []
    
    for i in range({num_samples}):
        # Generate random parameter combinations
        params = {{
            'coupling_strength': random.uniform(0.5, 2.0),
            'frequency': random.uniform(0.5, 5.0),
            'mass': random.uniform(0.1, 2.0),
            'phase': random.uniform(0, 6.28)
        }}
        
        # Evaluate (placeholder)
        score = random.random()
        
        samples.append((params, score))
        
    # Sort by score
    samples.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Exploration complete: {{len(samples)}} samples")
    print(f"Best score: {{samples[0][1]:.3f}}")
    print(f"Best params: {{samples[0][0]}}")
    
    return samples

# Execute exploration
results = explore_parameter_space()
"""
        
        generated = GeneratedCode(
            purpose="Parameter space exploration",
            code=code,
            timestamp=datetime.now(),
            validated=True
        )
        self.generated_code_history.append(generated)
        
        return code
        
    def generate_adaptation_code(self, context: Dict[str, Any]) -> str:
        """
        Generate adaptation code based on current context.
        
        Args:
            context: Dictionary with context information
            
        Returns:
            Generated Python code
        """
        omega = context.get('omega', 0.0)
        sync_level = context.get('sync_level', 0.0)
        
        code = f"""
# Auto-generated adaptation code
# Context: omega={omega:.3f}, sync_level={sync_level:.3f}

def adapt_to_context():
    omega = {omega}
    sync_level = {sync_level}
    
    # Determine adaptation strategy
    if sync_level < 0.5:
        strategy = "increase_coupling"
        print("Low synchronization - increasing coupling strength")
    elif omega < 0.0:
        strategy = "phase_adjustment"
        print("Negative omega - adjusting phases")
    else:
        strategy = "maintain"
        print("System stable - maintaining current state")
    
    print(f"Adaptation strategy: {{strategy}}")
    print(f"  Omega: {{omega:.3f}}")
    print(f"  Sync level: {{sync_level:.3f}}")
    
    return strategy

# Execute adaptation
strategy = adapt_to_context()
"""
        
        generated = GeneratedCode(
            purpose="Context-based adaptation",
            code=code,
            timestamp=datetime.now(),
            validated=True
        )
        self.generated_code_history.append(generated)
        
        return code
        
    def autonomous_generation_cycle(self, organism_state: Dict[str, Any]) -> List[CodeExecution]:
        """
        Perform one autonomous code generation and execution cycle.
        
        Args:
            organism_state: Current state of the organism
            
        Returns:
            List of execution results
        """
        executions = []
        
        # Extract key metrics
        omega = organism_state.get('omega_consciousness', {}).get('omega', 0.0)
        sync_level = organism_state.get('kuramoto_synchronization', {}).get('sync_level', 0.0)
        
        logger.info(f"Autonomous cycle - Omega: {omega:.3f}, Sync: {sync_level:.3f}")
        
        # Generate and execute optimization code if needed
        if sync_level < 0.7:
            code = self.generate_optimization_code('sync_level', sync_level, 0.9)
            result = self.execute_code(code)
            executions.append(result)
            
        # Generate and execute adaptation code
        code = self.generate_adaptation_code({
            'omega': omega,
            'sync_level': sync_level
        })
        result = self.execute_code(code)
        executions.append(result)
        
        return executions
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get current engine status.
        
        Returns:
            Dictionary with engine status
        """
        successful_executions = sum(1 for e in self.execution_history if e.success)
        
        return {
            'safe_mode': self.safe_mode,
            'total_executions': len(self.execution_history),
            'successful_executions': successful_executions,
            'failed_executions': len(self.execution_history) - successful_executions,
            'generated_code_count': len(self.generated_code_history),
            'namespace_size': len(self.namespace)
        }
        
    def clear_history(self) -> None:
        """Clear execution and generation history."""
        self.execution_history.clear()
        self.generated_code_history.clear()
        logger.info("Engine history cleared")
