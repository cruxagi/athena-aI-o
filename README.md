# Athena AI-O (Offline USB Edition)

Turnkey, local-first AI system built around the SBLM (Small Behavior Language Model) using Kuramoto oscillator physics instead of large transformer models. Runs 100% offline — no API keys, no cloud dependencies.

## Core Capabilities
- **Organism Controller:** Sense → Decide → Act → Learn → Report loop with 64 coupled oscillators, meta-goals, mutation operators, fitness evaluation, and a simple token economy.
- **Resonance Controller (DSL):** Runtime macro layer with assignments, conditionals, functions, and macro calls that manipulate variables such as `K`, `massBudget`, `couplingBudget`, `r`, and `tok`.
- **AI-O Engine:** Integrates a 6D offset store to derive execution budgets (IPQ, batch, dt, conv, agg, lat, tok) and maps coherence into the phase diagram (Chaotic, Critical, Crystalline, Metallic).
- **Compression System:** Offline stenographic/delta/semantic estimators plus a 7D unified projection with Hubbard-inspired phase tagging.
- **Offline by Design:** Uses only the Python standard library; no network or cloud requirements.

## Quickstart
```bash
python -m athena
```

The sample run executes one Sense→Decide→Act→Learn→Report cycle, drives the resonance DSL, and prints budgets, phase, coherence, and compression metrics.

## Resonance DSL Example
```text
fn stabilize {
    couplingBudget += 0.1
    massBudget = max(0.5, massBudget - 0.1)
}
if r > 0.7 {
    K = K - 0.05
} else {
    K = K + 0.05
    stabilize()
}
tok = tok + 32
```
This program adjusts the organism’s coupling `K`, allocates budgets, and invokes a reusable macro.
