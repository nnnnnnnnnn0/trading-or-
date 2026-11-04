import sys, unittest, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import backtest_mtf as m

U = dt.timezone.utc


def serie(barres, debut=dt.datetime(2026, 3, 2, 8, 0, tzinfo=U)):
    lignes = [[debut + dt.timedelta(hours=i)] + list(b) for i, b in enumerate(barres)]
    return m.Serie(lignes, 60)


class TestSimuler(unittest.TestCase):
    def test_objectif_2R(self):
        s = serie([(100, 100.5, 99.5, 100), (100, 104.5, 99.5, 104), (104, 104, 104, 104)])
        t = m.simuler(s, 0, 1, 100.0, 2.0, "swing", frais=0)
        self.assertAlmostEqual(t["R"], 2.0)

    def test_stop_prioritaire_meme_bougie(self):
        s = serie([(100, 105, 97, 100), (100, 100, 100, 100)])
        t = m.simuler(s, 0, 1, 100.0, 2.0, "swing", frais=0)
        self.assertAlmostEqual(t["R"], -1.0)

    def test_vente(self):
        s = serie([(100, 100.5, 95.5, 96), (96, 96, 96, 96)])
        t = m.simuler(s, 0, -1, 100.0, 2.0, "swing", frais=0)
        self.assertAlmostEqual(t["R"], 2.0)

    def test_sortie_intraday_21h_paris(self):
        # 08h UTC = 09h Paris (hiver) ; 21h Paris = 20h UTC -> sortie à l'ouverture de la bougie 12
        barres = [(100, 101.5, 99.5, 101.2)] * 20
        s = serie(barres)
        t = m.simuler(s, 0, 1, 100.0, 2.0, "intraday", frais=0)
        self.assertEqual(t["sortie"], 12)

    def test_securite_6h(self):
        barres = [(100, 100.5, 99.5, 100.0)] * 10
        s = serie(barres)
        t = m.simuler(s, 0, 1, 100.0, 2.0, "swing", frais=0)
        self.assertEqual(t["sortie"], 5)

    def test_couts(self):
        s = serie([(100, 104.5, 99.5, 104), (104, 104, 104, 104)])
        a = m.simuler(s, 0, 1, 100.0, 2.0, "swing", frais=0)["R"]
        b = m.simuler(s, 0, 1, 100.0, 2.0, "swing", frais=1)["R"]
        self.assertLess(b, a)


if __name__ == "__main__":
    unittest.main()
