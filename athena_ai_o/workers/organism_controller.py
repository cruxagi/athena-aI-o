"""
Organism Controller: Autonomous organism control system.

Manages the autonomous organism with integrated consciousness,
synchronization, and decision-making capabilities.
"""

import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import logging

from ..core.omega_consciousness import OmegaConsciousness
from ..core.kuramoto_sync import KuramotoSynchronization
from ..core.dynamic_programming import DynamicProgramming
from .background_worker import BackgroundWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrganismController:
    """
    Autonomous organism control system.
    
    Integrates consciousness, synchronization, and decision-making
    for autonomous organism operation and evolution.
    """
    
    def __init__(self, 
                 coupling_strength: float = 1.0,
                 gamma: float = 0.9,
                 evolution_enabled: bool = True):
        """
        Initialize organism controller.
        
        Args:
            coupling_strength: Kuramoto coupling strength
            gamma: DP discount factor
            evolution_enabled: Enable autonomous evolution
        """
        # Core components
        self.omega = OmegaConsciousness()
        self.kuramoto = KuramotoSynchronization(coupling_strength=coupling_strength)
        self.dp = DynamicProgramming(gamma=gamma)
        
        # Background worker for self-iteration
        self.worker = BackgroundWorker()
        self.evolution_enabled = evolution_enabled
        
        # State tracking
        self.iteration_count = 0
        self.start_time: Optional[datetime] = None
        self._lock = threading.Lock()
        
        # Evolution history
        self.evolution_history: List[Dict] = []
        
    def initialize_cognitive_modes(self, mode_configs: List[Dict]) -> None:
        """
        Initialize cognitive modes for the organism.
        
        Args:
            mode_configs: List of mode configurations with keys:
                         name, mass, frequency, phase (optional)
        """
        for config in mode_configs:
            # Add to omega consciousness
            self.omega.add_mode(
                name=config['name'],
                mass=config.get('mass', 1.0),
                frequency=config.get('frequency', 1.0),
                phase=config.get('phase', 0.0)
            )
            
            # Add corresponding oscillator to Kuramoto
            self.kuramoto.add_oscillator(
                id=config['name'],
                natural_frequency=config.get('frequency', 1.0),
                initial_phase=config.get('phase', None)
            )
            
        logger.info(f"Initialized {len(mode_configs)} cognitive modes")
        
    def setup_decision_space(self, states: List[str], actions: List[str],
                            transitions: List[Dict]) -> None:
        """
        Setup decision-making space for the organism.
        
        Args:
            states: List of state identifiers
            actions: List of action identifiers
            transitions: List of transition dicts with keys:
                        from_state, action, to_state, probability, reward
        """
        # Add states
        for state_id in states:
            self.dp.add_state(state_id)
            
        # Add actions
        for action_id in actions:
            self.dp.add_action(action_id)
            
        # Add transitions
        for trans in transitions:
            self.dp.add_transition(
                from_state=trans['from_state'],
                action=trans['action'],
                to_state=trans['to_state'],
                probability=trans['probability'],
                reward=trans['reward']
            )
            
        logger.info(f"Setup decision space: {len(states)} states, {len(actions)} actions")
        
    def compute_optimal_policy(self, method: str = 'value_iteration') -> Dict:
        """
        Compute optimal policy using dynamic programming.
        
        Args:
            method: 'value_iteration' or 'policy_iteration'
            
        Returns:
            Result dictionary from DP computation
        """
        if method == 'value_iteration':
            result = self.dp.value_iteration()
            self.dp.extract_policy()
        elif method == 'policy_iteration':
            result = self.dp.policy_iteration()
        else:
            raise ValueError(f"Unknown method: {method}")
            
        logger.info(f"Policy computation completed: {result['iterations']} iterations")
        return result
        
    def synchronize_modes(self, steps: int = 1000) -> Dict:
        """
        Synchronize cognitive modes using Kuramoto model.
        
        Args:
            steps: Maximum synchronization steps
            
        Returns:
            Synchronization result dictionary
        """
        result = self.kuramoto.synchronize(steps=steps)
        
        # Update omega consciousness phases to match synchronized phases
        for osc in self.kuramoto.oscillators:
            self.omega.update_mode_phase(osc.id, osc.phase)
            
        logger.info(f"Mode synchronization: level={result['final_sync_level']:.3f}")
        return result
        
    def calculate_consciousness(self) -> float:
        """
        Calculate current omega consciousness value.
        
        Returns:
            Omega consciousness value
        """
        omega_value = self.omega.calculate_omega()
        logger.debug(f"Omega consciousness: {omega_value:.3f}")
        return omega_value
        
    def evolve_step(self, dt: float = 0.01) -> Dict:
        """
        Perform one evolution step.
        
        Args:
            dt: Time step for evolution
            
        Returns:
            Dictionary with evolution metrics
        """
        with self._lock:
            # Evolve omega consciousness
            self.omega.evolve(dt)
            
            # Perform Kuramoto step
            sync_level = self.kuramoto.step(dt)
            
            # Update omega phases from Kuramoto
            for osc in self.kuramoto.oscillators:
                self.omega.update_mode_phase(osc.id, osc.phase)
                
            # Calculate consciousness
            omega_value = self.omega.calculate_omega()
            coherence = self.omega.get_coherence_metric()
            
            self.iteration_count += 1
            
            metrics = {
                'iteration': self.iteration_count,
                'omega': omega_value,
                'sync_level': sync_level,
                'coherence': coherence,
                'timestamp': datetime.now().isoformat()
            }
            
            self.evolution_history.append(metrics)
            
            return metrics
            
    def start_autonomous_evolution(self, interval: float = 0.1) -> None:
        """
        Start autonomous evolution in background.
        
        Args:
            interval: Time between evolution steps (seconds)
        """
        if not self.evolution_enabled:
            logger.warning("Evolution is disabled")
            return
            
        # Add evolution task to background worker
        self.worker.add_task(
            name='evolution',
            function=lambda: self.evolve_step(),
            interval=interval
        )
        
        # Start worker
        self.worker.start()
        self.start_time = datetime.now()
        
        logger.info(f"Autonomous evolution started (interval={interval}s)")
        
    def stop_autonomous_evolution(self) -> None:
        """Stop autonomous evolution."""
        self.worker.stop()
        logger.info("Autonomous evolution stopped")
        
    def get_optimal_action(self, state_id: str) -> Optional[str]:
        """
        Get optimal action for current state.
        
        Args:
            state_id: Current state identifier
            
        Returns:
            Optimal action ID or None
        """
        return self.dp.get_optimal_action(state_id)
        
    def get_full_state(self) -> Dict[str, Any]:
        """
        Get complete organism state.
        
        Returns:
            Dictionary with all state information
        """
        with self._lock:
            omega_state = self.omega.get_state_summary()
            kuramoto_state = self.kuramoto.get_state()
            dp_state = self.dp.get_state_summary()
            worker_status = self.worker.get_status()
            
            return {
                'organism': {
                    'iteration_count': self.iteration_count,
                    'start_time': self.start_time.isoformat() if self.start_time else None,
                    'evolution_enabled': self.evolution_enabled,
                    'evolution_history_length': len(self.evolution_history)
                },
                'omega_consciousness': omega_state,
                'kuramoto_synchronization': kuramoto_state,
                'dynamic_programming': dp_state,
                'background_worker': worker_status
            }
            
    def add_custom_task(self, name: str, function: Callable, interval: float) -> None:
        """
        Add custom background task.
        
        Args:
            name: Task identifier
            function: Function to execute
            interval: Time between executions (seconds)
        """
        self.worker.add_task(name, function, interval)
        
    def shutdown(self) -> None:
        """Gracefully shutdown the organism."""
        logger.info("Shutting down organism controller...")
        self.stop_autonomous_evolution()
        logger.info("Organism controller shutdown complete")
