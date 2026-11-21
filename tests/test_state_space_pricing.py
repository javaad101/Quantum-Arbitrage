import math
import unittest
from state_space_pricing import (
    chsh_tsirelson_value,
    construct_formula_primitives,
    eisenberg_noe_clearing,
    gaussian_elimination_rank,
    solve_linear_system,
)


class StateSpacePricingTests(unittest.TestCase):
    def test_proposition_1_equity_rank_deficiency(self):
        x_eq = [
            [0.0, 15.0, 45.0, 95.0],
            [0.0, 5.0, 25.0, 50.0],
        ]
        self.assertLessEqual(gaussian_elimination_rank(x_eq), 2)

    def test_theorem_1_phantom_equity_positive_under_simultaneous_liquidation(self):
        assets = [5.0, 10.0, 10.0, 0.0]
        liabilities = [
            [0.0, 40.0, 0.0, 20.0],
            [0.0, 0.0, 35.0, 0.0],
            [0.0, 30.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
        ]
        standalone, cleared, _ = eisenberg_noe_clearing(assets, liabilities)
        self.assertGreater(sum(standalone[:3]), sum(cleared[:3]))
        self.assertLessEqual(sum(cleared[:3]), sum(assets[:3]) + 1e-9)

    def test_corollary_1_exact_partition_and_arrow_debreu_inversion(self):
        X_prim, Y = construct_formula_primitives()
        self.assertEqual(gaussian_elimination_rank(X_prim), 4)
        for w in range(4):
            self.assertAlmostEqual(sum(X_prim[k][w] for k in range(4)), Y[w], places=11)

        true_q = [0.35, 0.28, 0.20, 0.12]
        prices = [sum(X_prim[k][w] * true_q[w] for w in range(4)) for k in range(4)]
        recovered_q = solve_linear_system(X_prim, prices)
        for w in range(4):
            self.assertAlmostEqual(recovered_q[w], true_q[w], places=11)

    def test_chsh_violates_classical_bound_at_tsirelson_limit(self):
        s = chsh_tsirelson_value()
        self.assertGreater(s, 2.0)
        self.assertAlmostEqual(s, 2.0 * math.sqrt(2.0), places=12)


if __name__ == "__main__":
    unittest.main()
