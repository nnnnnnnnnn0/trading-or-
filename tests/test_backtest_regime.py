"""Tests du backtest Régime or sur données synthétiques (aucun réseau, aucune donnée réelle)."""
import gzip
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts" / "backtests"))
import backtest_regime as br  # noqa: E402


def serie(n=1500, derive=0.0004, bruit=0.01, graine=1, debut="2010-01-04"):
    rng = np.random.default_rng(graine)
    idx = pd.bdate_range(debut, periods=n)
    c = 1000 * np.cumprod(1 + derive + bruit * rng.standard_normal(n))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.003
    l = np.minimum(o, c) * 0.997
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx)


class Decisions(unittest.TestCase):
    def test_un_seul_jour_par_semaine_le_dernier(self):
        idx = pd.bdate_range("2024-01-01", "2024-01-31")
        d = br.jours_de_decision(idx)
        self.assertEqual({x.dayofweek for x in idx[d][:-1]}, {4})   # chaque vendredi
        self.assertTrue(d[-1])                                         # le tout dernier jour est une décision
        self.assertEqual(d.sum(), 5)

    def test_semaine_avec_ferie_le_vendredi(self):
        idx = pd.DatetimeIndex(["2024-03-25", "2024-03-26", "2024-03-27", "2024-03-28", "2024-04-01"])  # vendredi saint absent
        d = br.jours_de_decision(idx)
        self.assertEqual(list(d), [False, False, False, True, True])


class SansRegardDansLeFutur(unittest.TestCase):
    def test_score_independant_du_futur(self):
        g = serie()
        dxy = serie(graine=2)["close"]
        taux = serie(graine=3)["close"] / 500
        t1, m1 = br.scores(g["close"], dxy, taux)
        k = 1000
        g2, dxy2, taux2 = g.copy(), dxy.copy(), taux.copy()
        g2.iloc[k + 1:] *= 3
        dxy2.iloc[k + 1:] *= 0.2
        taux2.iloc[k + 1:] += 5
        t2, m2 = br.scores(g2["close"], dxy2, taux2)
        self.assertEqual(t1.iloc[k], t2.iloc[k])
        self.assertEqual(m1.iloc[k], m2.iloc[k])

    def test_macro_utilise_la_veille(self):
        idx = pd.bdate_range("2020-01-01", periods=300)
        c = pd.Series(np.linspace(100, 200, 300), index=idx)
        dxy = pd.Series(100.0, index=idx)
        taux = pd.Series(1.0, index=idx)
        dxy.iloc[200:] = 90.0          # chute du dollar à partir du jour 200
        t, m = br.scores(c, dxy, taux)
        # le jour 200 lui-même ne voit pas encore la chute (décalage d'un jour)
        self.assertEqual(m.iloc[200], 0.0)
        self.assertEqual(m.iloc[201], 0.5)   # dollar en baisse : -(-1)/2


class Positions(unittest.TestCase):
    def test_taille_plafonnee_et_signe(self):
        g = serie(bruit=0.001)     # volatilité très faible -> levier plafonné
        idx = g.index
        dec = br.jours_de_decision(idx)
        pos = br.positions(g, np.ones(len(g)), dec)
        self.assertLessEqual(np.abs(pos).max(), br.LEVIER_MAX + 1e-12)
        self.assertTrue((pos >= 0).all())
        self.assertAlmostEqual(pos[-1], br.LEVIER_MAX, places=6)

    def test_taille_selon_la_volatilite(self):
        g = serie(bruit=0.02, derive=0.0)
        dec = br.jours_de_decision(g.index)
        pos = br.positions(g, -np.ones(len(g)), dec)
        i = int(np.where(dec)[0][-5])
        vol = g["close"].pct_change().rolling(20).std().iloc[i] * math.sqrt(252)
        self.assertAlmostEqual(pos[i], -min(br.LEVIER_MAX, br.VOL_CIBLE / vol), places=6)

    def test_sortie_de_securite(self):
        idx = pd.bdate_range("2022-01-03", periods=60)
        rng = np.random.default_rng(5)
        c = 100 * np.cumprod(1 + 0.004 * rng.standard_normal(60))
        c[40:] *= 0.8             # chute de 20 % : très au-delà de 3 ATR
        g = pd.DataFrame({"open": c, "high": c * 1.005, "low": c * 0.995, "close": c}, index=idx)
        dec = np.zeros(60, dtype=bool)
        dec[30] = True            # une seule décision : achat
        pos = br.positions(g, np.ones(60), dec)
        self.assertGreater(pos[30], 0)
        self.assertGreater(pos[39], 0)
        self.assertEqual(pos[40], 0)          # sortie dès la clôture sous le stop
        self.assertEqual(pos[-1], 0)          # pas de retour avant la décision suivante

    def test_sans_signal_a_plat(self):
        g = serie()
        dec = br.jours_de_decision(g.index)
        pos = br.positions(g, np.zeros(len(g)), dec)
        self.assertTrue((pos == 0).all())


class Rendements(unittest.TestCase):
    def test_frais_et_financement(self):
        idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"])   # une nuit chacune
        c = pd.Series([100.0, 100.0, 100.0, 100.0], index=idx)
        pos = np.array([0.0, 1.0, 1.0, 0.0])
        dates = idx.values.astype("datetime64[D]")
        r = br.rendements(pos, c, dates)
        self.assertAlmostEqual(r[0], 0.0)
        self.assertAlmostEqual(r[1], -br.FRAIS_COTE - br.FINANCEMENT)           # entrée + 1 nuit
        self.assertAlmostEqual(r[2], -br.FINANCEMENT)                           # 1 nuit
        self.assertAlmostEqual(r[3], -br.FRAIS_COTE)                            # sortie

    def test_week_end_trois_nuits_et_vente_gagnante(self):
        idx = pd.DatetimeIndex(["2024-01-05", "2024-01-08"])    # vendredi -> lundi
        c = pd.Series([100.0, 90.0], index=idx)
        r = br.rendements(np.array([-1.0, 0.0]), c, idx.values.astype("datetime64[D]"))
        self.assertAlmostEqual(r[0], 0.10 - br.FRAIS_COTE - 3 * br.FINANCEMENT)


class Mesures(unittest.TestCase):
    def test_stats_simples(self):
        s = br.stats(np.array([0.01, -0.01] * 100))
        self.assertAlmostEqual(s["ann"], 0.0, places=6)
        self.assertLess(s["dd"], 0)
        self.assertEqual(br.stats(np.zeros(10))["sharpe"], 0.0)

    def test_deflated_sharpe_hasard_et_signal(self):
        rng = np.random.default_rng(4)
        T = 4000
        hasard = rng.normal(0, 0.01, T)
        fort = rng.normal(0.0015, 0.01, T)
        ecart = 1 / math.sqrt(T - 1)
        self.assertLess(br.deflated_sharpe(hasard, 3, ecart), 0.95)
        self.assertGreater(br.deflated_sharpe(fort, 3, ecart), 0.99)
        # plus on a fait d'essais, plus le seuil monte
        moyen = rng.normal(0.0003, 0.01, T)
        self.assertGreater(br.deflated_sharpe(moyen, 3, ecart), br.deflated_sharpe(moyen, 250, ecart))

    def test_hasard_circulaire(self):
        g = serie(n=900, graine=7)
        dec = br.jours_de_decision(g.index)
        # exposition fortement liée au futur (impossible en vrai) : le test du hasard doit la juger meilleure que les décalages
        c = g["close"].values
        fut = np.zeros(len(c)); fut[:-5] = c[5:] / c[:-5] - 1
        d = np.where(fut > 0, 1.0, -1.0)
        pos = br.positions(g, d, dec)
        dates = g.index.values.astype("datetime64[D]")
        r = br.rendements(pos, g["close"], dates)
        p = br.p_decalage(pos, g["close"], dates, 300, 800, r[300:800].mean(), np.random.default_rng(1), n=200)
        self.assertLessEqual(p, 0.2)

    def test_fr_et_pct(self):
        self.assertEqual(br.fr(1.234), "1,23")
        self.assertEqual(br.pct(0.1234), "12,3 %")


class ModuleB(unittest.TestCase):
    def test_segments_et_t(self):
        jours = pd.bdate_range("2023-01-02", periods=30)
        lignes = []
        for j in jours:
            for h in range(0, 24):
                # prix : monte la nuit (h<13 ou h>=21), plat pendant la séance américaine
                lignes.append((pd.Timestamp(j) + pd.Timedelta(hours=h), 0))
        t = pd.DatetimeIndex([x[0] for x in lignes], tz="UTC")
        niveau, vals = 1000.0, []
        for ts in t:
            vals.append(niveau)
            if not (13 <= ts.hour < 21):
                niveau *= 1.0002
        o = pd.Series(vals, index=t)
        # 5 min seulement à l'heure pile suffit pour ce test
        s = br.segments(o)
        self.assertGreater(len(s), 20)
        self.assertTrue((s["us"].abs() < 1e-9).all())
        self.assertTrue((s["hors_us"] > 0).all())
        self.assertGreater(br.nw_t(s["hors_us"] - s["us"]), 5)

    def test_nw_t_constante_positive(self):
        x = np.random.default_rng(3).normal(0.1, 1, 500)
        self.assertGreater(br.nw_t(x), 1.5)


class DeBoutEnBout(unittest.TestCase):
    def test_rapport_complet_sur_donnees_synthetiques(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "histo").mkdir()
            g = serie(n=2600, derive=0.0003, graine=11, debut="2012-01-02")

            def ecrire(nom, df, cols):
                d = df.copy()
                d.insert(0, "date_utc", d.index.strftime("%Y-%m-%d 00:00"))
                d["volume"] = 0
                d[cols].to_csv(tmp / nom, index=False)

            cols = ["date_utc", "open", "high", "low", "close", "volume"]
            ecrire("or_jour.csv", g, cols)
            dxy = serie(n=2600, graine=12, debut="2012-01-02") * 0.1
            ecrire("dollar_dxy.csv", dxy, cols)
            tx = serie(n=2600, graine=13, debut="2012-01-02") * 0.001
            ecrire("taux_reels_10ans.csv", tx, cols)
            # 5 min : deux ans de données horaires suffisent, 13 h-21 h plat, nuit en hausse
            t = pd.date_range("2022-01-03", "2023-12-29", freq="1h", tz="UTC")
            niveau, vals = 1500.0, []
            for ts in t:
                vals.append(niveau)
                if ts.dayofweek < 5 and not (13 <= ts.hour < 21):
                    niveau *= 1.0001
            d5 = pd.DataFrame({"date_utc": t.strftime("%Y-%m-%d %H:%M:%S+00:00"), "open": vals})
            for an, x in d5.groupby(t.year):
                with gzip.open(tmp / "histo" / ("xauusd_5m_%d.csv.gz" % an), "wt") as f:
                    x.to_csv(f, index=False)
            avant = (br.DATA, br.SORTIE)
            br.DATA, br.SORTIE = tmp, tmp / "res" / "regime_v1.md"
            try:
                import contextlib, io
                with contextlib.redirect_stdout(io.StringIO()):
                    br.rapport()
                texte = br.SORTIE.read_text(encoding="utf-8")
            finally:
                br.DATA, br.SORTIE = avant
            self.assertIn("Module A", texte)
            self.assertIn("Verdict", texte)
            self.assertIn("H1", texte)
            self.assertIn("Un bon backtest ne prouve rien", texte)


if __name__ == "__main__":
    unittest.main()
