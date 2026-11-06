"""Tests sur des séries SYNTHÉTIQUES (inventées pour vérifier le code, pas de vraies données de marché)."""
import math
import sys
import unittest
from pathlib import Path

for _d in ("donnees", "quotidien", "backtests"):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / _d))
import fetch_or  # noqa: E402
import signaux_or as s  # noqa: E402


class TestSignaux(unittest.TestCase):
    def test_cassure_haussiere(self):
        c = [100 + (i % 3) * 0.1 for i in range(60)] + [105.0]
        r = s.cassure_20(c)
        self.assertEqual(r["sens"], "Long")
        self.assertLess(r["stop"], r["entree"])

    def test_cassure_baissiere(self):
        c = [100 + (i % 3) * 0.1 for i in range(60)] + [95.0]
        r = s.cassure_20(c)
        self.assertEqual(r["sens"], "Short")
        self.assertGreater(r["stop"], r["entree"])

    def test_pas_de_cassure_si_plat(self):
        c = [100 + (i % 3) * 0.1 for i in range(80)]
        self.assertIsNone(s.cassure_20(c))

    def test_repli_dans_la_tendance(self):
        c = [100 + i * 0.5 for i in range(80)]
        c.append(c[-1] - 20)
        r = s.repli_tendance(c)
        self.assertEqual(r["sens"], "Long")
        self.assertLess(r["stop"], r["entree"])
        self.assertGreater(r["objectif"], r["entree"])

    def test_pas_de_repli_si_hausse_continue(self):
        c = [100 + i * 0.5 for i in range(81)]
        self.assertIsNone(s.repli_tendance(c))

    def test_compression_puis_cassure(self):
        c = [100 + (1 - i / 220) * (-1) ** i for i in range(200)]
        c.append(105.0)
        r = s.compression(c)
        self.assertIsNotNone(r)
        self.assertEqual(r["sens"], "Long")
        self.assertLess(r["stop"], r["entree"])

    def test_pas_de_compression_sans_donnees_suffisantes(self):
        self.assertIsNone(s.compression([100.0] * 50))

    def test_rapport_sans_signal(self):
        dates = ["2026-01-%02d" % (i % 28 + 1) for i in range(60)]
        texte = s.rapport(dates, [100.0] * 60, [])
        self.assertIn("Aucun signal valide", texte)


class TestConversion(unittest.TestCase):
    def test_retire_les_week_ends_et_trie(self):
        objet = {"nominal": "XAUUSD", "data": [
            {"date": "2026-11-02", "price": "3911.6"},   # lundi
            {"date": "2026-11-01", "price": "3875.5"},   # dimanche
            {"date": "2026-10-30", "price": "3900.0"},   # vendredi
        ]}
        self.assertEqual(fetch_or.convertir(objet), [("2026-10-30", 3900.0), ("2026-11-02", 3911.6)])

    def test_message_d_erreur(self):
        with self.assertRaises(SystemExit):
            fetch_or.convertir({"Information": "limite atteinte"})


if __name__ == "__main__":
    unittest.main()
