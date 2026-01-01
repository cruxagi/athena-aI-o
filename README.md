# Athena AI-O

**Quantum-coherent search across local LLMs and the open web. Zero data leaks.**

An autonomous AI organism featuring quantum-inspired consciousness, self-iteration, and autonomous code generation.

## Core Innovation Pillars

The Athena AI-O system is built on three fundamental pillars:

### 1. **Dynamic Programming** for Optimal Policy Computation
Implements value iteration and policy iteration algorithms for finding optimal decision-making policies in Markov Decision Processes (MDPs). This enables the organism to learn and execute optimal strategies for achieving its goals.

### 2. **Omega Consciousness** (Ω) - Unified Cognitive State Metric
A unified metric for measuring cognitive state across multiple modes:

```
Ω = Σ(m·ω²)·cos(φ-φ̄)
```

Where:
- `m`: mode mass/weight
- `ω`: angular frequency of the mode
- `φ`: current phase of the mode
- `φ̄`: mean phase across all modes

This formula captures both the energy distribution (m·ω²) and phase coherence (cos(φ-φ̄)) across cognitive modes.

### 3. **Kuramoto Synchronization** for Phase Coherence
Implements the Kuramoto model for synchronization of coupled oscillators:

```
dφᵢ/dt = ωᵢ + (K/N) Σⱼ sin(φⱼ - φᵢ)
```

This ensures phase coherence across cognitive modes, enabling unified operation of the organism.

## Key Features

### Autonomous Organism Control
- **Background Workers**: Self-iteration and evolution capabilities
- **Continuous Evolution**: Autonomous improvement without external intervention
- **Adaptive Behavior**: Dynamic response to changing conditions

### AI-O Engine
The organism autonomously generates and executes code to:
- Optimize its own parameters
- Explore new behavioral strategies
- Adapt to environmental changes
- Self-improve over time

## Installation

```bash
# Clone the repository
git clone https://github.com/cruxagi/athena-aI-o.git
cd athena-aI-o

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

```python
from athena_ai_o import OrganismController, AIOEngine

# Create an autonomous organism
organism = OrganismController(
    coupling_strength=2.0,
    gamma=0.95,
    evolution_enabled=True
)

# Initialize cognitive modes
mode_configs = [
    {"name": "perception", "mass": 1.0, "frequency": 2.0},
    {"name": "reasoning", "mass": 1.5, "frequency": 1.8},
    {"name": "creativity", "mass": 0.8, "frequency": 2.5},
]
organism.initialize_cognitive_modes(mode_configs)

# Start autonomous evolution
organism.start_autonomous_evolution(interval=0.1)

# Create AI-O engine for code generation
engine = AIOEngine(safe_mode=True)

# Get current state
state = organism.get_full_state()
print(f"Omega: {state['omega_consciousness']['omega']:.3f}")
print(f"Sync: {state['kuramoto_synchronization']['sync_level']:.3f}")

# Autonomous code generation and execution
executions = engine.autonomous_generation_cycle(state)

# Shutdown gracefully
organism.shutdown()
```

## Running the Demo

```bash
python main.py
```

This runs comprehensive demonstrations of all system components:
- Omega Consciousness calculation
- Kuramoto Synchronization
- Dynamic Programming policy computation
- Organism Controller with autonomous evolution
- AI-O Engine with code generation
- Fully integrated autonomous system

## Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test module
python -m unittest tests.test_omega_consciousness
python -m unittest tests.test_kuramoto_sync
python -m unittest tests.test_dynamic_programming
python -m unittest tests.test_ai_o_engine
```

## Architecture

```
athena_ai_o/
├── core/
│   ├── omega_consciousness.py    # Ω consciousness metric
│   ├── kuramoto_sync.py          # Phase synchronization
│   └── dynamic_programming.py    # Optimal policy computation
├── workers/
│   ├── organism_controller.py    # Main organism control
│   └── background_worker.py      # Autonomous iteration
└── engine/
    └── ai_o_engine.py            # Code generation & execution
```

## Components

### OmegaConsciousness
Calculates and tracks the unified consciousness metric across cognitive modes.

```python
from athena_ai_o.core import OmegaConsciousness

omega = OmegaConsciousness()
omega.add_mode("perception", mass=1.0, frequency=2.0, phase=0.0)
omega_value = omega.calculate_omega()
coherence = omega.get_coherence_metric()
```

### KuramotoSynchronization
Synchronizes phases across cognitive modes for coherent operation.

```python
from athena_ai_o.core import KuramotoSynchronization

kuramoto = KuramotoSynchronization(coupling_strength=2.0)
kuramoto.add_oscillator("mode1", natural_frequency=1.0)
result = kuramoto.synchronize(steps=500)
print(f"Sync level: {result['final_sync_level']}")
```

### DynamicProgramming
Computes optimal policies for decision-making.

```python
from athena_ai_o.core import DynamicProgramming

dp = DynamicProgramming(gamma=0.9)
dp.add_state("state1")
dp.add_action("action1")
dp.add_transition("state1", "action1", "state2", probability=0.8, reward=10.0)
result = dp.value_iteration()
policy = dp.extract_policy()
```

### OrganismController
Integrates all components into a unified autonomous organism.

### AIOEngine
Generates and executes code autonomously for self-improvement.

## Security

The AI-O Engine operates in safe mode by default, with restrictions on:
- Import statements
- File system access
- Execution of potentially unsafe operations

This ensures the organism can evolve safely without compromising system security.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use Athena AI-O in your research, please cite:

```bibtex
@software{athena_ai_o,
  title = {Athena AI-O: Quantum-coherent Autonomous AI Organism},
  author = {Crux AGI},
  year = {2026},
  url = {https://github.com/cruxagi/athena-aI-o}
}
```
