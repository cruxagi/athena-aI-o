import math
import unittest

from sblm_engine import BehaviorLibrary, IntentClassifier, KuramotoSubstrate, OmegaMetric, SBLMEngine


class KuramotoSubstrateTest(unittest.TestCase):
    def test_order_parameter_improves_after_steps(self) -> None:
        substrate = KuramotoSubstrate(seed=42)
        initial = substrate.order_parameter()
        substrate.step(steps=200)
        after = substrate.order_parameter()
        self.assertGreater(after, initial)


class IntentClassifierTest(unittest.TestCase):
    def test_same_query_produces_deterministic_perturbations(self) -> None:
        substrate_one = KuramotoSubstrate(seed=3)
        substrate_two = KuramotoSubstrate(seed=3)
        classifier = IntentClassifier()

        perturb_one = classifier.apply("synchronize", substrate_one)
        perturb_two = classifier.apply("synchronize", substrate_two)

        self.assertEqual(perturb_one, perturb_two)
        for a, b in zip(substrate_one.phases, substrate_two.phases):
            self.assertAlmostEqual(a, b, places=7)


class BehaviorLibraryTest(unittest.TestCase):
    def test_best_match_prefers_closest_pattern(self) -> None:
        library = BehaviorLibrary()
        aligned = [0.01 for _ in range(64)]
        shifted = [math.pi for _ in range(64)]
        library.add_behavior("aligned", aligned)
        library.add_behavior("shifted", shifted)

        result = library.best_match([0.02 for _ in range(64)])
        self.assertIsNotNone(result)
        if result is None:
            return
        chosen, score = result
        self.assertEqual(chosen, "aligned")
        self.assertGreater(score, 0.5)


class OmegaMetricTest(unittest.TestCase):
    def test_energy_and_synchrony_are_complementary(self) -> None:
        substrate = KuramotoSubstrate(seed=5)
        metric = OmegaMetric(substrate)
        synchrony = metric.synchrony()
        self.assertGreaterEqual(synchrony, 0.0)
        self.assertLessEqual(synchrony, 1.0)
        energy = metric.energy()
        self.assertAlmostEqual(energy + synchrony, 1.0, places=5)


class SBLMEngineTest(unittest.TestCase):
    def test_process_returns_behavior_and_metrics(self) -> None:
        engine = SBLMEngine()
        result = engine.process("focus on clarity", steps=3)
        self.assertIn("behavior", result)
        self.assertIn(result["behavior"], engine.library.behaviors)
        self.assertGreaterEqual(result["synchrony"], 0.0)
        self.assertLessEqual(result["synchrony"], 1.0)
        self.assertGreaterEqual(result["omega_energy"], 0.0)
        self.assertLessEqual(result["omega_energy"], 1.0)


if __name__ == "__main__":
    unittest.main()
