"""Tests du backtest « Continuation Monte Carlo » v3 sur données synthétiques (aucun réseau, aucune donnée réelle)."""
import contextlib
import gzip
import io
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts" / "backtests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_continuation_v3 as c3  # noqa: E402
import backtest_montecarlo_v2 as m2  # noqa: E402
import backtest_regime as br  # noqa: E402
from test_montecarlo import donnees_synth  # noqa: E402

NS = c3.NS


class Sorties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = donnees_synth("2019-01-01", "2019-09-01", graine=6, derive=0.00002)
        cls.P = m2.preparer(cls.df)
        cls.s = c3.decisions(cls.P)

    def test_une_decision_par_jour_a_08h(self):
        s = self.s
        self.assertGreater(len(s), 60)
        self.assertTrue((s["date"].dt.hour == 8).all() and (s["date"].dt.minute == 0).all())
        self.assertEqual(len(s), s["jour"].nunique())

    def test_jours_de_sortie_et_nuits(self):
        s, P = self.s, self.P
        for k in (0, 2, 4):
            i_dl, ok, nuits = c3.sorties(P, s, k)
            self.assertTrue(ok.sum() > 50)
            heure = (P.t[i_dl[ok]] // NS % 86400)
            self.assertTrue((heure == 20 * 3600 + 55 * 60).all())            # toujours 20:55 UTC
        i_dl, ok, nuits = c3.sorties(P, s, 0)
        self.assertTrue((nuits[ok] == 0).all())
        # un mercredi à +2 jours de bourse = vendredi (2 nuits) ; un jeudi = lundi (4 nuits)
        i_dl, ok, nuits = c3.sorties(P, s, 2)
        jours = s["date"].dt.dayofweek.to_numpy()
        self.assertTrue((nuits[(jours == 2) & ok] == 2).all())
        self.assertTrue((nuits[(jours == 3) & ok] == 4).all())
        self.assertTrue((nuits[(jours == 4) & ok] == 4).all())               # vendredi -> mardi
        # les dernières décisions n'ont plus assez de jours devant elles
        self.assertFalse(c3.sorties(P, s, 4)[1][-1])

    def test_directions_coherentes(self):
        s = self.s
        d, t = c3.directions(s), c3.tendance(s)
        self.assertGreater(int((t != 0).sum()), 20)
        for v in ("C", "Cz"):
            self.assertTrue(((d[v] == 0) | (d[v] == t)).all(), v)            # toujours dans le sens de la tendance
        self.assertTrue((d["Ct"] == t).all())
        biais_ok = np.sign(s["biais"].to_numpy()) == t
        self.assertTrue(((d["C"] == 0) | biais_ok).all())                    # C exige un biais Monte Carlo dans le sens de la tendance

    def test_simulation_pas_de_chevauchement_et_couts(self):
        s, P = self.s, self.P
        for k in (0, 2, 4):
            tr = c3.simuler(P, s, c3.tendance(s), k)
            self.assertGreater(len(tr), 15, k)
            self.assertTrue((tr["date_sortie"].iloc[:-1].to_numpy() <= tr["date"].iloc[1:].to_numpy()).all(), k)    # une seule position
            self.assertTrue((tr["nuits"] >= 0).all())
            attendu = (c3.FRAIS_BASE + c3.FIN_BASE * tr["nuits"]) * tr["entree"] / tr["A"]
            self.assertTrue(np.allclose(tr["brut"] - tr["net"], attendu))
            self.assertTrue((tr["stress"] < tr["net"]).all())
            ratio = tr["A"] / (c3.STOP_A * math.sqrt(k + 1))
            self.assertTrue(np.isin(np.round(ratio, 9), np.round(s["A"].to_numpy(), 9)).all())      # stop = 3 A x racine(jours)
            self.assertNotIn("cible", set(tr["motif"]))                                               # pas d'objectif
        t0 = c3.simuler(P, s, c3.tendance(s), 0)
        t4 = c3.simuler(P, s, c3.tendance(s), 4)
        self.assertGreater(t4["nuits"].mean(), t0["nuits"].mean())

    def test_sans_signal_aucun_trade(self):
        self.assertEqual(len(c3.simuler(self.P, self.s, np.zeros(len(self.s), dtype=int), 2)), 0)

    def test_garder_l_or(self):
        av, ap = c3.garder_l_or(self.P, self.s)
        self.assertTrue(math.isfinite(av) and math.isfinite(ap))
        self.assertLessEqual(ap, av if av > 0 else ap)


class Criteres(unittest.TestCase):
    def mesure(self, dev, val, **kw):
        m = {"m_dev": dev, "t_dev": 3.0 if dev > 0 else -1.0, "n_dev": 200, "m_val": val, "t_val": 3.0 if val > 0 else -1.0, "n_val": 200,
             "n": 400, "ans_pos": 12, "ans_tot": 14, "dsr9": 0.99, "dsr367": 0.9, "apres": 0.05, "avant": 0.06, "stress": 0.01}
        m.update(kw)
        return m

    def test_tous_les_criteres_passent(self):
        c = self.mesure(0.2, 0.2)
        crit = c3.criteres(c, self.mesure(0.1, 0.1), self.mesure(0.05, 0.05), self.mesure(-0.01, 0.0))
        self.assertTrue(all(x[1] for x in crit), [x[0] for x in crit if not x[1]])
        self.assertEqual(len(crit), 7)

    def test_un_critere_echoue(self):
        c = self.mesure(0.2, 0.2)
        mauvais = self.mesure(0.3, 0.1)       # Cz meilleur que C en développement
        crit = c3.criteres(c, mauvais, self.mesure(0.05, 0.05), self.mesure(-0.01, 0.0))
        self.assertFalse(crit[5][1])
        crit = c3.criteres(self.mesure(0.2, 0.2, stress=-0.02), self.mesure(0.1, 0.1), self.mesure(0.05, 0.05), self.mesure(-0.01, 0.0))
        self.assertFalse(crit[6][1])
        nan = self.mesure(0.2, 0.2, m_dev=float("nan"))
        self.assertFalse(c3.criteres(nan, self.mesure(0.1, 0.1), self.mesure(0.05, 0.05), self.mesure(0.0, 0.0))[0][1])


class DeBoutEnBout(unittest.TestCase):
    def test_rapport_complet_sur_donnees_synthetiques(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "histo").mkdir()
            df = donnees_synth("2019-03-01", "2020-07-01", graine=4, derive=0.00002)
            d = df.copy()
            d.insert(0, "date_utc", d.index.strftime("%Y-%m-%d %H:%M:%S+00:00"))
            for an, x in d.groupby(df.index.year):
                with gzip.open(tmp / "histo" / ("xauusd_5m_%d.csv.gz" % an), "wt") as f:
                    x.to_csv(f, index=False)
            avant = (br.DATA, c3.SORTIE)
            br.DATA, c3.SORTIE = tmp, tmp / "res" / "continuation_monte_carlo_v3.md"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    c3.rapport(n_boot=200, n_hasard=3)
                texte = c3.SORTIE.read_text(encoding="utf-8")
            finally:
                br.DATA, c3.SORTIE = avant
            for mot in ("Verdict", "H0", "H2", "H4", "Cz sans simulation", "garder l'or", "Un bon backtest ne prouve rien"):
                self.assertIn(mot, texte)


if __name__ == "__main__":
    unittest.main()
