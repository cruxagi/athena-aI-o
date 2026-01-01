from pprint import pprint

from .engine import AIOEngine


def main() -> None:
    engine = AIOEngine()
    resonance_script = """
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
    """
    report = engine.run_cycle({"github": 3, "hacker_news": 2, "codebase": 1}, resonance_script, feedback=0.6)
    pprint(
        {
            "phase": report.organism.phase.value,
            "coherence": round(report.organism.coherence, 4),
            "omega": round(report.organism.omega, 4),
            "budgets": {k: round(v, 3) for k, v in report.budgets.items()},
            "compression": report.compression,
            "resonance_scope": report.resonance_scope,
        }
    )


if __name__ == "__main__":
    main()
