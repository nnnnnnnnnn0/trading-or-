"""Tests de la mécanique d'ordres de la stratégie Compression Or (données inventées)."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "backtests"))
import backtest_compression as bc  # noqa: E402


def faux(barres_k, apres=((100, 100, 100, 100),) * 4):
    """4 jours de 4 barres. Jour 0 : compression (H=100, B=98, ATR=1). Jour 1 : barres_k. Jours 2-3 : plats."""
    jour0 = [(99, 100, 98, 99)] * 4
    lignes = jour0 + list(barres_k) + list(apres) + list(apres)
    ts = []
    for j in range(4):
        for b in range(4):
            ts.append(np.datetime64("2024-01-01") + np.timedelta64(j, "D") + np.timedelta64(b * 5, "m"))
    d = bc.Donnees.__new__(bc.Donnees)
    d.ts = np.array(ts, dtype="datetime64[ns]")
    a = np.array(lignes, dtype=float)
    d.O, d.H, d.L, d.C = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
    d.s = np.array([0, 4, 8, 12])
    d.e = d.s + 4
    d.h = np.array([100.0, d.H[4:8].max(), d.H[8:12].max(), d.H[12:].max()])
    d.l = np.array([98.0, d.L[4:8].min(), d.L[8:12].min(), d.L[12:].min()])
    d.c = np.array([99.0, d.C[7], d.C[11], d.C[15]])
    d.atr = np.array([1.0, 1.0, 1.0, 1.0])
    d.n = 4
    return d


class Mecanique(unittest.TestCase):
    def test_achat_puis_objectif(self):
        d = faux([(99, 99.5, 98.5, 99), (99, 100.5, 99.5, 100.4), (100.4, 102.6, 100.4, 102.5), (102.5, 102.5, 102.5, 102.5)])
        t = bc.simuler(d, 0, 0)
        self.assertEqual(t["sens"], 1)
        self.assertEqual(t["type"], "objectif")
        self.assertAlmostEqual(t["brut"], 2.0)
        self.assertAlmostEqual(t["net"], 2.0 - bc.FRAIS_AR * 100)           # frais en R : 0,05 % de 100 / ATR 1

    def test_stop_prioritaire_dans_la_meme_barre(self):
        d = faux([(99, 99.5, 98.5, 99), (99, 100.5, 99.5, 100.4), (100.4, 102.6, 98.9, 100), (100, 100, 100, 100)])
        t = bc.simuler(d, 0, 0)
        self.assertEqual(t["type"], "stop")
        self.assertAlmostEqual(t["brut"], -1.0)

    def test_vente_et_sortie_au_temps(self):
        d = faux([(98.2, 98.9, 97.9, 98.1), (98.1, 98.2, 97.5, 97.6), (97.6, 97.9, 97.5, 97.8), (97.8, 97.9, 97.6, 97.7)],
                 apres=((97.7, 97.9, 97.6, 97.8),) * 4)
        t = bc.simuler(d, 0, 0)
        self.assertEqual(t["sens"], -1)
        self.assertEqual(t["type"], "temps")
        self.assertGreater(t["brut"], 0)

    def test_deux_niveaux_dans_la_meme_barre_ignore(self):
        d = faux([(99, 100.5, 97.5, 99)] + [(99, 99, 99, 99)] * 3)
        self.assertTrue(bc.simuler(d, 0, 0)["conflit"])

    def test_une_seule_direction_en_variante_b(self):
        d = faux([(99, 100.5, 97.5, 99)] + [(99, 99, 99, 99)] * 3)
        t = bc.simuler(d, 0, 1)             # achat seul : pas de conflit
        self.assertFalse(t["conflit"])
        self.assertEqual(t["sens"], 1)

    def test_gap_a_l_ouverture(self):
        d = faux([(101, 101.2, 100.5, 101), (101, 101.1, 100.9, 101), (101, 101, 101, 101), (101, 101, 101, 101)],
                 apres=((101, 101, 101, 101),) * 4)
        t = bc.simuler(d, 0, 0)
        self.assertEqual(t["sens"], 1)
        self.assertEqual(t["type"], "temps")
        self.assertAlmostEqual(t["brut"], 0.0)       # entrée à 101 (ouverture) et non à 100 ; sortie à 101

    def test_pas_de_trade_si_rien_touche(self):
        d = faux([(99, 99.5, 98.5, 99)] * 4)
        self.assertIsNone(bc.simuler(d, 0, 0))


class Regroupement(unittest.TestCase):
    def test_jours_valides_et_compression(self):
        idx = pd.date_range("2024-01-01 22:00", periods=288 * 40, freq="5min", tz="UTC")
        rng = np.random.default_rng(1)
        c = 1000 + np.cumsum(rng.normal(0, 0.3, len(idx)))
        df = pd.DataFrame({"open": c, "high": c + 0.2, "low": c - 0.2, "close": c, "volume": 1.0}, index=idx)
        df.iloc[:288, df.columns.get_loc("volume")] = 0.0      # un jour sans activité : ignoré
        d = bc.Donnees(df)
        self.assertEqual(d.n, 39)
        self.assertTrue((d.r > 0).all())
        self.assertIsInstance(d.comprime(20), bool)


if __name__ == "__main__":
    unittest.main()
