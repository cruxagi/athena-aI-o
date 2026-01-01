"""
Main entry point for Athena AI-O system.

Demonstrates the integration of all core pillars:
- Dynamic Programming for optimal policy computation
- Omega Consciousness as a unified metric for cognitive state
- Kuramoto Synchronization for phase coherence across cognitive modes
- Autonomous organism control with background workers
- AI-O Engine for autonomous code generation and execution
"""

import time
import logging
from athena_ai_o import (
    OmegaConsciousness,
    KuramotoSynchronization,
    DynamicProgramming,
    OrganismController,
    AIOEngine
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_omega_consciousness():
    """Demonstrate Omega Consciousness calculation."""
    logger.info("=== Omega Consciousness Demo ===")
    
    omega = OmegaConsciousness()
    
    # Add cognitive modes
    omega.add_mode("perception", mass=1.0, frequency=2.0, phase=0.0)
    omega.add_mode("reasoning", mass=1.5, frequency=1.5, phase=1.0)
    omega.add_mode("creativity", mass=0.8, frequency=3.0, phase=2.0)
    omega.add_mode("memory", mass=1.2, frequency=1.0, phase=0.5)
    
    # Calculate omega consciousness
    omega_value = omega.calculate_omega()
    coherence = omega.get_coherence_metric()
    
    logger.info(f"Omega Consciousness: {omega_value:.3f}")
    logger.info(f"Coherence Metric: {coherence:.3f}")
    
    # Get state summary
    state = omega.get_state_summary()
    logger.info(f"Number of modes: {state['mode_count']}")
    logger.info(f"Mean phase: {state['mean_phase']:.3f} rad")
    
    return omega


def demo_kuramoto_synchronization():
    """Demonstrate Kuramoto Synchronization."""
    logger.info("\n=== Kuramoto Synchronization Demo ===")
    
    kuramoto = KuramotoSynchronization(coupling_strength=2.0)
    
    # Add oscillators
    kuramoto.add_oscillator("osc1", natural_frequency=1.0)
    kuramoto.add_oscillator("osc2", natural_frequency=1.2)
    kuramoto.add_oscillator("osc3", natural_frequency=0.9)
    kuramoto.add_oscillator("osc4", natural_frequency=1.1)
    
    # Run synchronization
    result = kuramoto.synchronize(steps=500, dt=0.01)
    
    logger.info(f"Synchronization level: {result['final_sync_level']:.3f}")
    logger.info(f"Converged: {result['converged']}")
    logger.info(f"Steps taken: {result['steps_taken']}")
    
    return kuramoto


def demo_dynamic_programming():
    """Demonstrate Dynamic Programming for optimal policy."""
    logger.info("\n=== Dynamic Programming Demo ===")
    
    dp = DynamicProgramming(gamma=0.9)
    
    # Define a simple MDP (grid world)
    states = ["s0", "s1", "s2", "s3", "goal"]
    actions = ["up", "down", "left", "right"]
    
    # Add states and actions
    for state in states:
        dp.add_state(state)
    for action in actions:
        dp.add_action(action)
        
    # Add transitions (simplified example)
    transitions = [
        {"from_state": "s0", "action": "right", "to_state": "s1", 
         "probability": 0.8, "reward": 0.0},
        {"from_state": "s0", "action": "right", "to_state": "s0", 
         "probability": 0.2, "reward": 0.0},
        {"from_state": "s1", "action": "right", "to_state": "s2", 
         "probability": 0.8, "reward": 0.0},
        {"from_state": "s2", "action": "down", "to_state": "s3", 
         "probability": 0.8, "reward": 0.0},
        {"from_state": "s3", "action": "right", "to_state": "goal", 
         "probability": 0.8, "reward": 10.0},
    ]
    
    for trans in transitions:
        dp.add_transition(**trans)
        
    # Compute optimal policy
    result = dp.value_iteration(max_iterations=100)
    policy = dp.extract_policy()
    
    logger.info(f"Policy computation converged: {result['converged']}")
    logger.info(f"Iterations: {result['iterations']}")
    logger.info(f"Optimal policy: {policy}")
    
    return dp


def demo_organism_controller():
    """Demonstrate Autonomous Organism Controller."""
    logger.info("\n=== Organism Controller Demo ===")
    
    organism = OrganismController(
        coupling_strength=1.5,
        gamma=0.9,
        evolution_enabled=True
    )
    
    # Initialize cognitive modes
    mode_configs = [
        {"name": "perception", "mass": 1.0, "frequency": 2.0},
        {"name": "reasoning", "mass": 1.5, "frequency": 1.5},
        {"name": "creativity", "mass": 0.8, "frequency": 3.0},
    ]
    organism.initialize_cognitive_modes(mode_configs)
    
    # Setup decision space
    states = ["explore", "exploit", "rest"]
    actions = ["gather_info", "use_knowledge", "consolidate"]
    transitions = [
        {"from_state": "explore", "action": "gather_info", "to_state": "exploit",
         "probability": 0.7, "reward": 1.0},
        {"from_state": "exploit", "action": "use_knowledge", "to_state": "rest",
         "probability": 0.8, "reward": 5.0},
        {"from_state": "rest", "action": "consolidate", "to_state": "explore",
         "probability": 0.9, "reward": 2.0},
    ]
    organism.setup_decision_space(states, actions, transitions)
    
    # Compute optimal policy
    organism.compute_optimal_policy()
    
    # Synchronize modes
    sync_result = organism.synchronize_modes(steps=300)
    logger.info(f"Initial synchronization: {sync_result['final_sync_level']:.3f}")
    
    # Calculate consciousness
    omega_value = organism.calculate_consciousness()
    logger.info(f"Initial omega consciousness: {omega_value:.3f}")
    
    # Run a few evolution steps manually
    for i in range(5):
        metrics = organism.evolve_step(dt=0.01)
        logger.info(f"Evolution step {i+1}: omega={metrics['omega']:.3f}, "
                   f"sync={metrics['sync_level']:.3f}")
    
    # Get full state
    state = organism.get_full_state()
    logger.info(f"Organism state: {state['organism']}")
    
    return organism


def demo_ai_o_engine():
    """Demonstrate AI-O Engine for autonomous code generation."""
    logger.info("\n=== AI-O Engine Demo ===")
    
    engine = AIOEngine(safe_mode=True)
    
    # Generate optimization code
    code = engine.generate_optimization_code(
        metric="sync_level",
        current_value=0.5,
        target_value=0.9
    )
    
    logger.info("Generated optimization code")
    
    # Execute the code
    result = engine.execute_code(code)
    logger.info(f"Execution success: {result.success}")
    if result.output:
        logger.info(f"Output:\n{result.output}")
        
    # Generate exploration code
    code = engine.generate_exploration_code(num_samples=5)
    result = engine.execute_code(code)
    logger.info(f"Exploration execution success: {result.success}")
    
    # Get engine status
    status = engine.get_status()
    logger.info(f"Engine status: {status}")
    
    return engine


def demo_integrated_system():
    """Demonstrate fully integrated autonomous system."""
    logger.info("\n=== Integrated System Demo ===")
    
    # Create organism with all components
    organism = OrganismController(
        coupling_strength=2.0,
        gamma=0.95,
        evolution_enabled=True
    )
    
    # Initialize cognitive modes
    mode_configs = [
        {"name": "perception", "mass": 1.0, "frequency": 2.0, "phase": 0.0},
        {"name": "reasoning", "mass": 1.5, "frequency": 1.8, "phase": 0.5},
        {"name": "creativity", "mass": 0.8, "frequency": 2.5, "phase": 1.0},
        {"name": "memory", "mass": 1.2, "frequency": 1.2, "phase": 1.5},
    ]
    organism.initialize_cognitive_modes(mode_configs)
    
    # Create AI-O engine
    engine = AIOEngine(safe_mode=True)
    
    # Run autonomous evolution briefly
    logger.info("Starting autonomous evolution...")
    organism.start_autonomous_evolution(interval=0.05)
    
    # Let it run for a short time
    time.sleep(1.0)
    
    # Get organism state
    state = organism.get_full_state()
    
    # Use AI-O engine to generate adaptation code
    executions = engine.autonomous_generation_cycle(state)
    logger.info(f"Autonomous cycle executed {len(executions)} code blocks")
    
    # Stop evolution
    organism.stop_autonomous_evolution()
    
    # Final state
    final_state = organism.get_full_state()
    logger.info(f"Final iterations: {final_state['organism']['iteration_count']}")
    logger.info(f"Final omega: {final_state['omega_consciousness']['omega']:.3f}")
    logger.info(f"Final sync: {final_state['kuramoto_synchronization']['sync_level']:.3f}")
    
    organism.shutdown()
    
    return organism, engine


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Athena AI-O System - Quantum-coherent autonomous organism")
    logger.info("=" * 60)
    
    try:
        # Run individual demos
        demo_omega_consciousness()
        demo_kuramoto_synchronization()
        demo_dynamic_programming()
        demo_organism_controller()
        demo_ai_o_engine()
        
        # Run integrated system demo
        demo_integrated_system()
        
        logger.info("\n" + "=" * 60)
        logger.info("All demonstrations completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during demonstration: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
