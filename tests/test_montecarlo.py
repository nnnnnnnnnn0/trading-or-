"""Tests du backtest Monte Carlo intraday sur données synthétiques (aucun réseau, aucune donnée réelle)."""
import contextlib
import gzip
import io
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts" / "backtests"))
import backtest_montecarlo as bm  # noqa: E402
import backtest_regime as br  # noqa: E402

NS = bm.NS


def donnees_synth(debut, fin, graine=1, derive=0.0, bruit=0.0004):
    """Barres 5 min ; la semaine en continu avec volume, le week-end à plat sans volume (comme les vraies données)."""
    t = pd.date_range(debut, fin, freq="5min", tz="UTC", inclusive="left")
    rng = np.random.default_rng(graine)
    c = 1500 * np.cumprod(1 + derive + bruit * rng.standard_normal(len(t)))
    o = np.concatenate([[c[0]], c[:-1]])
    h, l = np.maximum(o, c) * 1.0002, np.minimum(o, c) * 0.9998
    we = t.dayofweek >= 5
    df = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": np.where(we, 0, 10)}, index=t)
    # week-end : prix figé (barres plates, volume nul)
    prix = df["close"].where(~we).ffill().bfill()
    for col in ("open", "high", "low", "close"):
        df.loc[we, col] = prix[we]
    return df


class ProbaMonteCarlo(unittest.TestCase):
    def test_hausse_forte_donne_proba_haute(self):
        fen = np.full(bm.FENETRE, 0.0006)          # toujours à la hausse
        pup, pdn = bm.proba_mc(fen, 1500.0, 3.0)
        self.assertGreater(pup, 900)
        self.assertLess(pdn, 50)

    def test_baisse_forte_donne_proba_basse(self):
        fen = np.full(bm.FENETRE, -0.0006)
        pup, pdn = bm.proba_mc(fen, 1500.0, 3.0)
        self.assertLess(pup, 50)
        self.assertGreater(pdn, 900)

    def test_fenetre_symetrique_donne_probas_proches_et_neutres(self):
        fen = np.array([0.0005, -0.0005] * (bm.FENETRE // 2))
        pup, pdn = bm.proba_mc(fen, 1500.0, 3.0)
        self.assertLess(abs(pup - pdn), 90)
        self.assertLess(pup, 500)           # sans tendance on reste sous le seuil d'achat
        self.assertLess(pdn, 500)

    def test_deterministe(self):
        fen = np.random.default_rng(3).normal(0.0001, 0.0005, bm.FENETRE)
        self.assertEqual(bm.proba_mc(fen, 1500.0, 3.0), bm.proba_mc(fen, 1500.0, 3.0))


class Sortie(unittest.TestCase):
    def barres(self, lignes):
        """lignes : liste de (open, high, low) ; l'indice 0 est la barre d'entrée."""
        o = np.array([x[0] for x in lignes], float)
        h = np.array([x[1] for x in lignes], float)
        l = np.array([x[2] for x in lignes], float)
        t = np.arange(len(o), dtype=np.int64) * 300 * NS
        return t, o, h, l

    def test_cible_achat(self):
        t, o, h, l = self.barres([(100, 100.5, 99.8), (100, 101.6, 99.9), (101, 101, 101)])
        px, motif, fin = bm.une_sortie(t, o, h, l, 0, 2, 1, 1.0)    # A = 1 : cible 101,5, stop 99
        self.assertEqual(motif, "cible")
        self.assertAlmostEqual(px, 101.5)
        self.assertEqual(fin, 600 * NS)

    def test_stop_achat_et_priorite_meme_barre(self):
        t, o, h, l = self.barres([(100, 100.5, 99.8), (100, 102, 98.5), (100, 100, 100)])
        px, motif, _ = bm.une_sortie(t, o, h, l, 0, 2, 1, 1.0)      # même barre : cible ET stop -> stop
        self.assertEqual(motif, "stop")
        self.assertAlmostEqual(px, 99.0)

    def test_stop_gappe_a_l_ouverture(self):
        t, o, h, l = self.barres([(100, 100.2, 99.9), (97.0, 97.5, 96.5), (97, 97, 97)])
        px, motif, _ = bm.une_sortie(t, o, h, l, 0, 2, 1, 1.0)
        self.assertEqual(motif, "stop")
        self.assertAlmostEqual(px, 97.0)                              # pire que le stop à 99

    def test_vente(self):
        t, o, h, l = self.barres([(100, 100.3, 99.9), (99.5, 99.6, 98.4), (98.5, 98.5, 98.5)])
        px, motif, _ = bm.une_sortie(t, o, h, l, 0, 2, -1, 1.0)     # cible 98,5, stop 101
        self.assertEqual(motif, "cible")
        self.assertAlmostEqual(px, 98.5)

    def test_sortie_a_l_heure(self):
        t, o, h, l = self.barres([(100, 100.2, 99.8), (100.1, 100.3, 99.7), (100.2, 100.4, 100.0)])
        px, motif, fin = bm.une_sortie(t, o, h, l, 0, 2, 1, 1.0)
        self.assertEqual(motif, "heure")
        self.assertAlmostEqual(px, 100.1 + 0.1)                       # ouverture de la barre d'échéance
        self.assertEqual(fin, 600 * NS)

    def test_barre_d_entree_compte_pour_le_stop(self):
        t, o, h, l = self.barres([(100, 100.2, 98.0), (100, 100, 100)])
        px, motif, _ = bm.une_sortie(t, o, h, l, 0, 1, 1, 1.0)
        self.assertEqual((motif, round(px, 6)), ("stop", 99.0))


class SignauxSansFutur(unittest.TestCase):
    def test_signal_independant_des_barres_suivantes(self):
        df = donnees_synth("2019-01-01", "2019-03-15", graine=5, derive=0.00001)
        P = bm.preparer(df)
        s1 = bm.decisions(P)
        self.assertGreater(len(s1), 100)
        k = len(s1) // 2
        T = int(s1["T"].iloc[k])
        # on massacre toutes les barres APRÈS la barre de décision : le signal à T ne doit pas bouger
        df2 = df.copy()
        apres = df2.index > pd.Timestamp(T, unit="ns", tz="UTC")
        for col in ("open", "high", "low", "close"):
            df2.loc[apres, col] = df2.loc[apres, col] * 3
        s2 = bm.decisions(bm.preparer(df2))
        a = s1[s1["T"] == T].iloc[0]
        b = s2[s2["T"] == T].iloc[0]
        for col in ("A", "rsi", "ema20", "ema100", "pup", "pdn"):
            self.assertEqual(a[col], b[col], col)

    def test_decisions_seulement_en_semaine_aux_heures_prevues(self):
        df = donnees_synth("2019-01-01", "2019-03-01", graine=2)
        s = bm.decisions(bm.preparer(df))
        self.assertTrue((s["date"].dt.dayofweek < 5).all())
        self.assertTrue(set(s["date"].dt.hour) <= set(bm.HEURES))
        self.assertTrue((s["date"].dt.minute == 0).all())


class Simulation(unittest.TestCase):
    def test_une_seule_position_et_pas_de_chevauchement(self):
        df = donnees_synth("2019-01-01", "2019-03-15", graine=8)
        P = bm.preparer(df)
        s = bm.decisions(P)
        tr = bm.simuler(P, s, np.ones(len(s), dtype=int))
        self.assertGreater(len(tr), 50)
        debuts = tr["date"].astype("int64").to_numpy()
        # chaque trade commence après la fin du précédent (fin >= début + 5 min) et à une heure de décision
        self.assertTrue((np.diff(debuts) >= 3600 * NS).all())
        self.assertTrue((tr["A"] > 0).all())

    def test_frais_en_r(self):
        df = donnees_synth("2019-01-01", "2019-02-15", graine=9)
        P = bm.preparer(df)
        s = bm.decisions(P)
        tr = bm.simuler(P, s, np.ones(len(s), dtype=int))
        attendu = bm.FRAIS_BASE * tr["entree"] / tr["A"]
        self.assertTrue(np.allclose(tr["brut"] - tr["net"], attendu))
        self.assertTrue((tr["stress"] < tr["net"]).all())

    def test_sans_signal_aucun_trade(self):
        df = donnees_synth("2019-01-01", "2019-02-15", graine=9)
        P = bm.preparer(df)
        s = bm.decisions(P)
        self.assertEqual(len(bm.simuler(P, s, np.zeros(len(s), dtype=int))), 0)

    def test_variantes_coherentes(self):
        df = donnees_synth("2019-01-01", "2019-04-15", graine=4, derive=0.00002)
        s = bm.decisions(bm.preparer(df))
        d = bm.directions(s)
        # V1 = V2 et V3 en même temps : jamais de signal V1 sans les deux autres
        self.assertTrue(((d["V1"] != 0) <= ((d["V2"] != 0) & (d["V3"] != 0))).all())
        self.assertTrue(((d["V1"] == d["V2"]) | (d["V1"] == 0)).all())
        self.assertTrue(((d["V1"] == d["V3"]) | (d["V1"] == 0)).all())


class Mesures(unittest.TestCase):
    def test_bootstrap_signal_fort_et_nul(self):
        rng = np.random.default_rng(1)
        fort = bm.bootstrap_trades(rng.normal(0.2, 1.0, 800), n_boot=500)
        nul = bm.bootstrap_trades(rng.normal(-0.2, 1.0, 800), n_boot=500)
        self.assertGreater(fort["p_pos"], 0.95)
        self.assertLess(nul["p_pos"], 0.05)
        self.assertGreaterEqual(fort["dd_med"], 0)
        self.assertLess(fort["q05"], fort["q95"])
        self.assertIsNone(bm.bootstrap_trades([1.0, 2.0], n_boot=10))

    def test_annees_et_decoupe(self):
        dates = pd.to_datetime(["2019-05-01"] * 25 + ["2021-05-01"] * 25 + ["2022-05-01"] * 5, utc=True)
        tr = pd.DataFrame({"date": dates, "net": [0.1] * 25 + [-0.1] * 25 + [1.0] * 5, "brut": 0.0, "stress": 0.0})
        self.assertEqual(bm.annees(tr), (1, 2))           # 2022 ignoré (moins de 20 trades)
        dev, val = bm.decoupe(tr)
        self.assertEqual((len(dev), len(val)), (25, 30))

    def test_serie_quotidienne_et_impot(self):
        jours = pd.date_range("2019-01-01", "2019-12-31", freq="D", tz="UTC")
        jours_ns = jours.values.astype("datetime64[ns]").astype(np.int64)
        tr = pd.DataFrame({"date": pd.to_datetime(["2019-03-01 09:00", "2019-03-01 12:00"], utc=True), "net": [1.0, 0.5],
                           "brut": 0.0, "stress": 0.0})
        x = bm.serie_quotidienne(tr, jours_ns)
        self.assertAlmostEqual(x["2019-03-01"], 1.5 * bm.RISQUE)
        self.assertAlmostEqual(x.sum(), 1.5 * bm.RISQUE)
        avant, apres = bm.rendements_annuels(x)
        self.assertGreater(avant, apres)                  # l'impôt réduit le gain
        self.assertGreater(apres, 0)

    def test_dsr_hasard_et_signal(self):
        rng = np.random.default_rng(2)
        self.assertLess(bm.dsr(rng.normal(0, 0.003, 3000), 3), 0.95)
        self.assertGreater(bm.dsr(rng.normal(0.0008, 0.003, 3000), 3), 0.95)


class DeBoutEnBout(unittest.TestCase):
    def test_rapport_complet_sur_donnees_synthetiques(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "histo").mkdir()
            df = donnees_synth("2019-10-01", "2020-04-01", graine=3, derive=0.00001)
            d = df.copy()
            d.insert(0, "date_utc", d.index.strftime("%Y-%m-%d %H:%M:%S+00:00"))
            for an, x in d.groupby(df.index.year):
                with gzip.open(tmp / "histo" / ("xauusd_5m_%d.csv.gz" % an), "wt") as f:
                    x.to_csv(f, index=False)
            avant = (br.DATA, bm.SORTIE)
            br.DATA, bm.SORTIE = tmp, tmp / "res" / "montecarlo_intraday_v1.md"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    bm.rapport(n_boot=200, n_hasard=3)
                texte = bm.SORTIE.read_text(encoding="utf-8")
            finally:
                br.DATA, bm.SORTIE = avant
            for mot in ("Verdict", "V1", "V2", "V3", "Témoin hasard", "Un bon backtest ne prouve rien"):
                self.assertIn(mot, texte)


if __name__ == "__main__":
    unittest.main()
