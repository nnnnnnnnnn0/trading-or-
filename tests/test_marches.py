"""Tests de l'alignement des signaux (séance t) et des ordres (ouverture et clôture de t+1)."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "backtests"))
import backtest_marches as bm  # noqa: E402


class Alignement(unittest.TestCase):
    def test_ordre_a_t_plus_1(self):
        idx = pd.bdate_range("2020-01-01", periods=5)
        g = pd.DataFrame({"open": [100, 101, 102, 103, 104.0], "close": [100.5, 102.0, 101.0, 104.0, 105.0]}, index=idx)
        sg = pd.Series([1.0, -1.0, 0.0, 1.0, 1.0], index=idx)
        T = bm.trades(g, sg)
        self.assertEqual(len(T), 3)                                  # jour sans signal et dernière séance (pas de t+1) écartés
        self.assertAlmostEqual(T["brut"].iloc[0], 1.0 * (102.0 / 101 - 1))      # signal du 1er jour : séance du 2e jour
        self.assertAlmostEqual(T["brut"].iloc[1], -1.0 * (101.0 / 102 - 1))
        self.assertAlmostEqual(T["net"].iloc[0], T["brut"].iloc[0] - bm.FRAIS_BASE)

    def test_signaux_n_utilisent_que_le_passe(self):
        idx = pd.bdate_range("2019-01-01", periods=400)
        rng = np.random.default_rng(0)
        mk = lambda s: pd.Series(100 * np.cumprod(1 + 0.01 * np.random.default_rng(s).standard_normal(400)), index=idx)
        g = pd.DataFrame({"open": mk(1), "high": mk(1), "low": mk(1), "close": mk(1)})
        C = {k: mk(i + 2) for i, k in enumerate(["dxy", "taux_reels", "argent", "mineurs", "sp500", "vix", "tnx", "tlt", "cuivre", "petrole"])}
        X1 = bm.signaux(g, C)
        k = 300
        g2, C2 = g.copy(), {a: b.copy() for a, b in C.items()}
        g2.iloc[k + 1:] *= 3
        for v in C2.values():
            v.iloc[k + 1:] *= 0.3
        X2 = bm.signaux(g2, C2)
        for num in X1:
            if num == 0:
                continue
            a, b = X1[num][1].iloc[k], X2[num][1].iloc[k]
            self.assertTrue((np.isnan(a) and np.isnan(b)) or a == b, X1[num][0])


if __name__ == "__main__":
    unittest.main()
