import math
import unittest

from kuramoto import KuramotoOscillator


class KuramotoOscillatorTest(unittest.TestCase):
    def test_derivatives_match_kuramoto_equation(self) -> None:
        osc = KuramotoOscillator(
            natural_frequencies=[1.0, 1.5],
            coupling=2.0,
            phases=[0.0, math.pi / 2],
        )

        derivatives = osc.derivatives()

        # Expected:
        # dθ0/dt = 1.0 + (2/2) * sin(pi/2 - 0) = 2.0
        # dθ1/dt = 1.5 + (2/2) * sin(0 - pi/2) = 0.5
        self.assertAlmostEqual(derivatives[0], 2.0, places=6)
        self.assertAlmostEqual(derivatives[1], 0.5, places=6)

    def test_step_advances_phases_using_derivatives(self) -> None:
        osc = KuramotoOscillator(
            natural_frequencies=[1.0, 1.5],
            coupling=2.0,
            phases=[0.0, math.pi / 2],
        )

        osc.step(0.1)

        self.assertAlmostEqual(osc.phases[0], 0.2, places=6)
        self.assertAlmostEqual(osc.phases[1], (math.pi / 2) + 0.05, places=6)


if __name__ == "__main__":
    unittest.main()
