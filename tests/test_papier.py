"""Tests du moteur de paper trading 5 min et des 28 stratégies (données inventées)."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts" / "papier"))
sys.path.insert(0, str(RACINE / "scripts" / "backtests"))
import moteur  # noqa: E402
import strategies  # noqa: E402
from indicateurs import croise_haut, front, rsi  # noqa: E402


def marche(jours=12, debut="2026-11-02 00:00", graine=3, vol=0.0006):
    idx = pd.date_range(debut, periods=288 * jours, freq="5min", tz="UTC")
    idx = idx[idx.dayofweek < 5]
    rng = np.random.default_rng(graine)
    c = 4000 * np.cumprod(1 + vol * rng.standard_normal(len(idx)))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + 0.0002 * rng.random(len(idx)))
    l = np.minimum(o, c) * (1 - 0.0002 * rng.random(len(idx)))
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": rng.integers(50, 500, len(idx)).astype(float)}, index=idx)


def plat(h=100.0):
    idx = pd.date_range("2026-11-09 00:00", periods=288, freq="5min", tz="UTC")     # un lundi
    return pd.DataFrame({"open": h, "high": h + 0.01, "low": h - 0.01, "close": h, "volume": 100.0}, index=idx)


def lancer(df, i_signal, sens=1, atr=1.0, famille=strategies.TENDANCE, n=None):
    if n:
        df = df.iloc[:n]
    a = pd.Series(False, index=df.index)
    a.iloc[i_signal] = True
    z = pd.Series(False, index=df.index)
    aux = moteur.preparer(df)
    return moteur.simuler(df, aux, np.full(len(df), atr), a if sens > 0 else z, z if sens > 0 else a, famille)


class Mecanique(unittest.TestCase):
    def test_objectif_tendance(self):
        df = plat()
        df.iloc[125, df.columns.get_loc("high")] = 104.5            # signal 10:00, entrée 10:05 à 100, objectif 4 ATR
        o = lancer(df, 120)
        self.assertEqual(len(o), 1)
        self.assertEqual(o[0]["motif"], "objectif")
        self.assertAlmostEqual(o[0]["R_brut"], 2.0)
        self.assertAlmostEqual(o[0]["taille_oz"], 25.0)              # 50 $ / (2 x 1)
        self.assertLess(o[0]["R_net"], o[0]["R_brut"])
        self.assertLess(o[0]["R_stress"], o[0]["R_net"])

    def test_stop_prioritaire_meme_barre(self):
        df = plat()
        df.iloc[123, df.columns.get_loc("high")] = 105
        df.iloc[123, df.columns.get_loc("low")] = 97
        o = lancer(df, 120)
        self.assertEqual(o[0]["motif"], "stop")
        self.assertAlmostEqual(o[0]["R_brut"], -1.0)

    def test_stop_gappe_a_l_ouverture(self):
        df = plat()
        df.iloc[123, df.columns.get_loc("open")] = 97
        df.iloc[123, df.columns.get_loc("low")] = 96.9
        o = lancer(df, 120)
        self.assertAlmostEqual(o[0]["R_brut"], -1.5)

    def test_vente_objectif_retour(self):
        df = plat()
        df.iloc[124, df.columns.get_loc("low")] = 98.4                 # vente à 100, objectif 1,5 ATR = 98,5
        o = lancer(df, 120, sens=-1, famille=strategies.RETOUR)
        self.assertEqual(o[0]["sens"], "vente")
        self.assertEqual(o[0]["motif"], "objectif")
        self.assertAlmostEqual(o[0]["R_brut"], 0.75)

    def test_cloture_21h(self):
        df = plat()
        o = lancer(df, 19 * 12 + 10)                                     # signal 19:50, entrée 19:55
        self.assertEqual(o[0]["motif"], "clôture 21h")
        self.assertEqual(o[0]["duree_min"], 65)

    def test_duree_max(self):
        df = plat()
        o = lancer(df, 120)
        self.assertEqual(o[0]["motif"], "durée max")
        self.assertEqual(o[0]["duree_min"], 36 * 5)

    def test_hors_horaires_et_week_end(self):
        df = plat()
        self.assertEqual(lancer(df, 12 * 6), [])                         # signal 06:00 : entrée avant 07:00
        self.assertEqual(lancer(df, 20 * 12), [])                        # signal 20:00 : entrée après 20:00
        idx = pd.date_range("2026-11-14 00:00", periods=288, freq="5min", tz="UTC")   # samedi
        sam = pd.DataFrame({"open": 100.0, "high": 100.01, "low": 99.99, "close": 100.0, "volume": 100.0}, index=idx)
        self.assertEqual(lancer(sam, 120), [])

    def test_ordre_non_clos_en_fin_de_donnees(self):
        df = plat()
        self.assertEqual(lancer(df, 120, n=130), [])                     # données coupées avant la fin possible : pas d'ordre
        df2 = plat()
        df2.iloc[125, df2.columns.get_loc("high")] = 104.5
        self.assertEqual(len(lancer(df2, 120, n=130)), 1)                # objectif déjà touché : ordre clos

    def test_une_seule_position(self):
        df = plat()
        a = pd.Series(False, index=df.index)
        a.iloc[120] = True
        a.iloc[122] = True
        aux = moteur.preparer(df)
        o = moteur.simuler(df, aux, np.full(len(df), 1.0), a, pd.Series(False, index=df.index), strategies.TENDANCE)
        self.assertEqual(len(o), 1)

    def test_debut_du_paper_trading(self):
        df = plat()
        a = pd.Series(False, index=df.index)
        a.iloc[120] = True
        aux = moteur.preparer(df)
        o = moteur.simuler(df, aux, np.full(len(df), 1.0), a, pd.Series(False, index=df.index), strategies.TENDANCE,
                           debut=pd.Timestamp("2026-11-10", tz="UTC"))
        self.assertEqual(o, [])


class Strategies(unittest.TestCase):
    def test_28_strategies_et_temoin(self):
        noms = [s[1] for s in strategies.STRATEGIES]
        self.assertEqual(len(noms), 29)
        self.assertEqual(len(set(noms)), 29)
        self.assertEqual(sorted(s[0] for s in strategies.STRATEGIES), list(range(0, 29)))

    def test_aucun_regard_dans_le_futur(self):
        df = marche(jours=12)
        n1 = len(df) * 2 // 3
        for num, nom, fam, f in strategies.STRATEGIES:
            a_tot, v_tot = f(df)
            a_cut, v_cut = f(df.iloc[:n1])
            pd.testing.assert_series_equal(a_tot.iloc[:n1].fillna(False).astype(bool), a_cut.fillna(False).astype(bool), check_names=False, obj="achat " + nom)
            pd.testing.assert_series_equal(v_tot.iloc[:n1].fillna(False).astype(bool), v_cut.fillna(False).astype(bool), check_names=False, obj="vente " + nom)

    def test_signaux_booleens_et_alignes(self):
        df = marche(jours=6)
        for num, nom, fam, f in strategies.STRATEGIES:
            a, v = f(df)
            self.assertEqual(len(a), len(df), nom)
            self.assertEqual(len(v), len(df), nom)

    def test_indicateurs(self):
        s = pd.Series([1.0, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 6])
        r = rsi(s, 3)
        self.assertTrue(((r.dropna() >= 0) & (r.dropna() <= 100)).all())
        a = pd.Series([1.0, 2, 3, 2, 1])
        self.assertEqual(list(croise_haut(a, 1.5)), [False, True, False, False, False])
        self.assertEqual(list(front(pd.Series([False, True, True, False, True]))), [False, True, False, False, True])

    def test_temoin_deterministe(self):
        df = marche(jours=5)
        a1, v1 = strategies.s_hasard(df)
        a2, v2 = strategies.s_hasard(df.iloc[:500])
        pd.testing.assert_series_equal(a1.iloc[:500], a2, check_names=False)
        self.assertGreater(int(a1.sum() + v1.sum()), 0)


class Journal(unittest.TestCase):
    def test_journal_de_bout_en_bout(self):
        df = marche(jours=16, debut="2026-11-09 00:00", vol=0.0015)
        ordres = moteur.tout_simuler(df, debut=moteur.DEBUT_PAPIER)
        self.assertGreater(len(ordres), 20)
        self.assertTrue(set(["num", "strategie", "R_net", "gain_usd_net", "motif"]).issubset(ordres.columns))
        self.assertTrue((ordres["entree_ts"] >= moteur.DEBUT_PAPIER).all())
        self.assertTrue((ordres["sortie_ts"] >= ordres["entree_ts"]).all())
        self.assertTrue((ordres["sortie_ts"].dt.hour * 60 + ordres["sortie_ts"].dt.minute <= 20 * 60 + 55).all())
        # une seule position à la fois par stratégie
        for _, x in ordres.groupby("num"):
            x = x.sort_values("entree_ts")
            self.assertTrue((x["entree_ts"].values[1:] > x["sortie_ts"].values[:-1]).all())
        # déterministe : deux exécutions donnent le même journal
        pd.testing.assert_frame_equal(ordres, moteur.tout_simuler(df, debut=moteur.DEBUT_PAPIER))
        with tempfile.TemporaryDirectory() as tmp:
            avant = moteur.RACINE
            moteur.RACINE = Path(tmp)
            try:
                moteur.ecrire_journal(ordres, df)
            finally:
                moteur.RACINE = avant
            self.assertTrue((Path(tmp) / "journal" / "ordres.csv").exists())
            texte = (Path(tmp) / "journal" / "classement.md").read_text(encoding="utf-8")
            self.assertIn("témoin", texte.lower())
            jours = list((Path(tmp) / "journal" / "jours").glob("*.md"))
            self.assertGreater(len(jours), 3)
            self.assertIn("Bilan du jour", jours[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
