# athena-aI-o
Quantum-coherent search across local LLMs and the open web. Zero data leaks.

## Kuramoto Physics for Codebase Analysis

This module implements the Kuramoto model for coupled oscillators and applies it to analyze codebase complexity and router topology.

### Core Components

#### KuramotoOscillator

Implements the Kuramoto model:

```
dθᵢ/dt = ωᵢ + (K/N) × Σⱼ sin(θⱼ - θᵢ)
```

Key methods:
- `derivatives()` - Compute phase derivatives
- `step(dt)` - Advance simulation by time step
- `order_parameter()` - Returns (r, Ψ) where r is coherence (0-1)
- `coherence()` - Returns order parameter magnitude r

#### RouterTopologyAnalyzer

Applies Kuramoto physics to analyze codebase/router topology complexity.

```python
from kuramoto import RouterTopologyAnalyzer

analyzer = RouterTopologyAnalyzer(coupling=1.0)

# Add components with their complexity metrics
analyzer.add_component('omega-routes', exit_points=42, singletons=8)
analyzer.add_component('orchestrator-dual', exit_points=14, singletons=5)
analyzer.add_component('agent-routes', exit_points=10, singletons=2)

# Run full analysis
result = analyzer.analyze()
print(f"Coherence: {result['coherence']:.2f}")
print(f"Critical Coupling: {result['critical_coupling']:.2f}")
print(f"Phase: {result['phase']}")

# Get refactoring recommendations
for rec in analyzer.optimize_recommendations():
    print(f"[Effort {rec['effort']}] {rec['intervention']}")
```

### Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| Coherence r | `(1/N) × \|Σⱼ e^(iθⱼ)\|` | Synchronization level (0=chaotic, 1=crystalline) |
| Critical Coupling Kc | `2/(π·g(0))` | Threshold for spontaneous synchronization |
| Omega Energy Ω | `Σⱼ(mⱼ·ωⱼ²)·cos(θⱼ - θ̄)` | Weighted phase coherence metric |

### Phase States

- **CHAOTIC** (r < 0.3): Desynchronized, high complexity
- **CRITICAL** (0.3 ≤ r < 0.7): Partial synchronization
- **CRYSTALLINE** (r ≥ 0.7): Fully synchronized, aligned architecture

## Testing

```bash
python -m unittest discover tests -v
```
