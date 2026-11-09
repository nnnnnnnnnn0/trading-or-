"""Tests du calcul d'impôt et des états des règles « achat seulement » (données inventées)."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "backtests"))
import backtest_apres_impots as ai  # noqa: E402


def jours(n=600):
    return list(pd.bdate_range("2020-01-01", periods=n))


class Impots(unittest.TestCase):
    def test_garder_sans_frais_impot_en_fin(self):
        d = jours(500)
        ret = np.full(500, 0.001)
        brut, _ = ai.simuler(np.ones(500), ret, d, taux=0.0, frais=0.0, ter=0.0)
        net, _ = ai.simuler(np.ones(500), ret, d, taux=0.3, frais=0.0, ter=0.0)
        self.assertAlmostEqual(brut, 1.001 ** 500)
        self.assertAlmostEqual(net, brut - 0.3 * (brut - 1), places=9)      # un seul impôt, sur la plus-value totale

    def test_perte_pas_d_impot_et_report(self):
        d = jours(500)
        ret = np.zeros(500)
        ret[10], ret[300] = -0.2, 0.25          # perte puis gain dans des années différentes
        held = np.zeros(500)
        held[5:20] = 1                           # trade 1 : perte
        held[290:310] = 1                        # trade 2 : gain
        brut, _ = ai.simuler(held, ret, d, taux=0.0, frais=0.0, ter=0.0)
        net, _ = ai.simuler(held, ret, d, taux=0.3, frais=0.0, ter=0.0)
        self.assertLessEqual(net, brut)
        self.assertGreaterEqual(net, brut - 0.3 * max(brut - 1, 0) - 1e-9)   # la perte reportée réduit l'impôt du gain suivant

    def test_pas_de_position_pas_de_changement(self):
        d = jours(100)
        e, ch = ai.simuler(np.zeros(100), np.full(100, 0.01), d)
        self.assertEqual(e, 1.0)

    def test_decalage_d_execution(self):
        etat = np.array([0, 0, 1, 1, 0, 0, 0], dtype=float)
        self.assertEqual(list(ai.etat_vers_detenu(etat)), [0, 0, 0, 0, 1, 1, 0])


if __name__ == "__main__":
    unittest.main()
