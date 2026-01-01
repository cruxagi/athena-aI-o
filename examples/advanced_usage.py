"""
Advanced usage example for Athena AI-O system.

This example demonstrates advanced features including:
- Custom background tasks
- Parameter tuning
- Monitoring and analysis
- Integration of all components
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import logging
from athena_ai_o import OrganismController, AIOEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def custom_analysis_task(organism):
    """Custom task for analyzing organism state."""
    state = organism.get_full_state()
    omega = state['omega_consciousness']['omega']
    sync = state['kuramoto_synchronization']['sync_level']
    coherence = organism.omega.get_coherence_metric()
    
    logger.info(f"Analysis - Ω: {omega:.3f}, Sync: {sync:.3f}, Coherence: {coherence:.3f}")


def main():
    """Advanced example of Athena AI-O usage."""
    logger.info("=== Advanced Athena AI-O Example ===")
    
    organism = OrganismController(coupling_strength=3.0, gamma=0.95, evolution_enabled=True)
    
    mode_configs = [
        {"name": "perception", "mass": 1.2, "frequency": 3.0, "phase": 0.0},
        {"name": "reasoning", "mass": 2.0, "frequency": 1.8, "phase": 0.5},
        {"name": "creativity", "mass": 0.8, "frequency": 4.0, "phase": 1.0},
    ]
    
    organism.initialize_cognitive_modes(mode_configs)
    organism.synchronize_modes(steps=500)
    organism.calculate_consciousness()
    
    organism.add_custom_task('analysis', lambda: custom_analysis_task(organism), interval=0.5)
    organism.start_autonomous_evolution(interval=0.1)
    
    time.sleep(2.0)
    
    final_state = organism.get_full_state()
    logger.info(f"Final Ω: {final_state['omega_consciousness']['omega']:.3f}")
    logger.info(f"Final sync: {final_state['kuramoto_synchronization']['sync_level']:.3f}")
    
    organism.shutdown()
    logger.info("Example completed successfully")


if __name__ == "__main__":
    main()
