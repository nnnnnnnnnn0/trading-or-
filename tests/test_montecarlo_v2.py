"""Tests du backtest « Confluence Monte Carlo » v2 sur données synthétiques (aucun réseau, aucune donnée réelle)."""
import contextlib
import gzip
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts" / "backtests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_montecarlo_v2 as m2  # noqa: E402
import backtest_regime as br  # noqa: E402
from test_montecarlo import donnees_synth  # noqa: E402

NS = m2.NS
COLS_SIGNAL = ["A", "atr_med", "ema20", "ema100", "dtrend", "biais", "q", "z", "rv", "cible_mc", "cible_z"]


class Cone(unittest.TestCase):
    def test_position_monotone_et_bornes(self):
        fen = np.random.default_rng(1).normal(0, 0.001, m2.FENETRE)
        tri, _ = m2.cone(fen)
        qs = [m2.position_q(tri, 20, x) for x in (-0.05, -0.01, 0.0, 0.01, 0.05)]
        self.assertEqual(qs, sorted(qs))
        self.assertLess(qs[0], 0.01)
        self.assertGreater(qs[-1], 0.99)
        self.assertTrue(0.35 < qs[2] < 0.65)

    def test_mediane_suit_la_derive(self):
        bruit = np.random.default_rng(2).normal(0, 0.0002, m2.FENETRE)
        _, med_h = m2.cone(0.0006 + bruit)
        _, med_b = m2.cone(-0.0006 + bruit)
        self.assertGreater(med_h[-1], 0.01)
        self.assertLess(med_b[-1], -0.01)
        self.assertEqual(len(med_h), m2.PAS)

    def test_deterministe(self):
        fen = np.random.default_rng(3).normal(0, 0.001, m2.FENETRE)
        a, b = m2.cone(fen), m2.cone(fen)
        self.assertTrue(np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]))


class Sortie(unittest.TestCase):
    def barres(self, lignes):
        o = np.array([x[0] for x in lignes], float)
        h = np.array([x[1] for x in lignes], float)
        l = np.array([x[2] for x in lignes], float)
        return np.arange(len(o), dtype=np.int64) * 300 * NS, o, h, l

    def test_cible_distance_explicite(self):
        t, o, h, l = self.barres([(100, 100.5, 99.8), (100, 102.1, 99.9), (101, 101, 101)])
        px, motif, fin = m2.sortie(t, o, h, l, 0, 2, 1, 1.5, 2.0)         # stop 98,5 ; cible 102
        self.assertEqual((motif, round(px, 6)), ("cible", 102.0))
        self.assertEqual(fin, 600 * NS)

    def test_stop_prioritaire_meme_barre(self):
        t, o, h, l = self.barres([(100, 100.5, 99.8), (100, 103, 98.0), (100, 100, 100)])
        px, motif, _ = m2.sortie(t, o, h, l, 0, 2, 1, 1.5, 2.0)
        self.assertEqual((motif, round(px, 6)), ("stop", 98.5))

    def test_stop_gappe(self):
        t, o, h, l = self.barres([(100, 100.2, 99.9), (96.0, 96.5, 95.5), (96, 96, 96)])
        px, motif, _ = m2.sortie(t, o, h, l, 0, 2, 1, 1.5, 2.0)
        self.assertEqual((motif, px), ("stop", 96.0))

    def test_vente_et_sortie_dans_le_temps(self):
        t, o, h, l = self.barres([(100, 100.3, 99.9), (99.0, 99.2, 97.9), (98, 98, 98)])
        px, motif, _ = m2.sortie(t, o, h, l, 0, 2, -1, 1.5, 2.0)          # cible 98
        self.assertEqual((motif, round(px, 6)), ("cible", 98.0))
        t, o, h, l = self.barres([(100, 100.4, 99.6), (100.1, 100.5, 99.7), (100.2, 100.6, 99.9)])
        px, motif, fin = m2.sortie(t, o, h, l, 0, 2, 1, 1.5, 2.0)
        self.assertEqual((motif, round(px, 6), fin), ("heure", 100.2, 600 * NS))


class Distances(unittest.TestCase):
    def test_bornes_de_distance_et_sens(self):
        P = SimpleNamespace(o=np.array([100.0, 100.0, 100.0, 100.0]))
        s = pd.DataFrame({"i0": [0, 1, 2, 3], "A": [1.0] * 4, "cible_mc": [102.0, 100.5, 110.0, 97.5]})
        d = m2.distances(P, s, np.array([1, 1, 1, -1]), "cible_mc")
        self.assertEqual(d[0], 2.0)
        self.assertTrue(np.isnan(d[1]))               # 0,5 A < 1,0 A : pas de trade
        self.assertEqual(d[2], 3.0)                   # plafonnée à 3 A
        self.assertEqual(d[3], 2.5)                   # vente : l'objectif est sous l'entrée
        d = m2.distances(P, s, np.array([0, 1, 1, -1]), "cible_mc")
        self.assertTrue(np.isnan(d[0]))               # pas de signal


class Decisions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = donnees_synth("2019-01-01", "2019-09-01", graine=5, derive=0.00001)
        cls.P = m2.preparer(cls.df)
        cls.s = m2.decisions(cls.P)

    def test_grille_de_decision(self):
        s = self.s
        self.assertGreater(len(s), 500)
        self.assertTrue((s["date"].dt.dayofweek < 5).all())
        self.assertTrue(set(s["date"].dt.minute) <= {0, 30})
        h = s["date"].dt.hour + s["date"].dt.minute / 60
        self.assertTrue(((h >= 8) & (h <= 16.5)).all())
        self.assertTrue(((s["q"] >= 0) & (s["q"] <= 1)).all())

    def test_signaux_independants_du_futur(self):
        s1, df = self.s, self.df
        T = int(s1["T"].iloc[len(s1) * 3 // 4])
        df2 = df.copy()
        apres = df2.index > pd.Timestamp(T, unit="ns", tz="UTC")
        for col in ("open", "high", "low", "close"):
            df2.loc[apres, col] = df2.loc[apres, col] * 3
        df2.loc[apres & (df2["volume"] > 0), "volume"] = 50
        s2 = m2.decisions(m2.preparer(df2))
        a, b = s1[s1["T"] == T].iloc[0], s2[s2["T"] == T].iloc[0]
        for col in COLS_SIGNAL:
            if np.isnan(a[col]):
                self.assertTrue(np.isnan(b[col]), col)
            else:
                self.assertEqual(a[col], b[col], col)

    def test_volume_relatif_meme_heure_jours_precedents(self):
        df = self.df.copy()
        h7 = (df.index >= "2019-06-11 07:00") & (df.index < "2019-06-11 08:00")      # un mardi
        df.loc[h7, "volume"] = 20                                                      # volume de 07 h doublé ce jour-là
        s = m2.decisions(m2.preparer(df))
        mardi = s[s["date"] == pd.Timestamp("2019-06-11 08:00", tz="UTC")].iloc[0]
        mercredi = s[s["date"] == pd.Timestamp("2019-06-12 08:00", tz="UTC")].iloc[0]
        self.assertAlmostEqual(mardi["rv"], 2.0)
        self.assertAlmostEqual(mercredi["rv"], 120 / 126)    # la moyenne de référence inclut le mardi doublé

    def test_variantes_coherentes(self):
        s = self.s
        d = m2.directions(s)
        self.assertGreater(int((d["Fnt"] != 0).sum()), 0)
        for sans in ("Fnt", "Fnv"):
            self.assertTrue(((d["F"] == 0) | (d["F"] == d[sans])).all(), sans)
        tend_h = (s["dtrend"] > 0) & (s["ema20"] > s["ema100"])
        tend_b = (s["dtrend"] < 0) & (s["ema20"] < s["ema100"])
        self.assertTrue(((d["F"] != 1) | tend_h).all())
        self.assertTrue(((d["F"] != -1) | tend_b).all())
        self.assertTrue(((d["Fz"] != 1) | tend_h).all())
        self.assertTrue(((d["Fz"] != -1) | tend_b).all())

    def test_simulation_une_position_et_deux_par_jour(self):
        s, P = self.s, self.P
        tr = m2.simuler(P, s, np.ones(len(s), dtype=int), s["A"].to_numpy())
        self.assertGreater(len(tr), 100)
        par_jour = tr.groupby(tr["date"].dt.date).size()
        self.assertLessEqual(int(par_jour.max()), m2.MAX_PAR_JOUR)
        debuts = tr["date"].astype("int64").to_numpy()
        self.assertTrue((np.diff(debuts) >= 30 * 60 * NS).all())
        attendu = m2.FRAIS_BASE * tr["entree"] / tr["A"]
        self.assertTrue(np.allclose(tr["brut"] - tr["net"], attendu))

    def test_aucun_signal_aucun_trade(self):
        s, P = self.s, self.P
        self.assertEqual(len(m2.simuler(P, s, np.zeros(len(s), dtype=int), s["A"].to_numpy())), 0)

    def test_calibration_et_tableau(self):
        c = m2.calibration_cone(self.P, self.s)
        self.assertGreater(len(c), 50)
        self.assertTrue(((c["q"] >= 0) & (c["q"] <= 1)).all())
        self.assertGreater(len(m2.tableau_calibration(c)), 3)


class DeBoutEnBout(unittest.TestCase):
    def test_rapport_complet_sur_donnees_synthetiques(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "histo").mkdir()
            df = donnees_synth("2019-03-01", "2020-07-01", graine=3, derive=0.00001)
            d = df.copy()
            d.insert(0, "date_utc", d.index.strftime("%Y-%m-%d %H:%M:%S+00:00"))
            for an, x in d.groupby(df.index.year):
                with gzip.open(tmp / "histo" / ("xauusd_5m_%d.csv.gz" % an), "wt") as f:
                    x.to_csv(f, index=False)
            avant = (br.DATA, m2.SORTIE)
            br.DATA, m2.SORTIE = tmp, tmp / "res" / "montecarlo_intraday_v2.md"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    m2.rapport(n_boot=200, n_hasard=3)
                texte = m2.SORTIE.read_text(encoding="utf-8")
            finally:
                br.DATA, m2.SORTIE = avant
            for mot in ("Verdict", "Fz", "Fnt", "Fnv", "Témoin hasard", "cône", "Un bon backtest ne prouve rien"):
                self.assertIn(mot, texte)


if __name__ == "__main__":
    unittest.main()
