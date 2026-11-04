import sys, unittest, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import backtest_or as b


def serie(valeurs):
    d0 = datetime.date(2020, 1, 1)
    return [d0 + datetime.timedelta(days=i) for i in range(len(valeurs))]


class TestSimuler(unittest.TestCase):
    def test_objectif_atteint_donne_2R(self):
        c = [100.0] * 160 + [100, 100, 104, 105, 110]
        ind = {"vol": [1.0] * len(c), "m50": [0] * len(c)}
        # compression : entrée j+1=161 à 100, stop 98 -> objectif 104 (2R)
        t = b.simuler("compression", 160, 1, 98.0, c, serie(c), ind, frais=0)
        self.assertAlmostEqual(t["R"], 2.0)

    def test_stop_touche(self):
        c = [100.0] * 160 + [100, 100, 97, 97, 97]
        ind = {"vol": [1.0] * len(c), "m50": [0] * len(c)}
        t = b.simuler("compression", 160, 1, 98.0, c, serie(c), ind, frais=0)
        self.assertAlmostEqual(t["R"], -1.5)

    def test_risque_invalide(self):
        c = [100.0] * 170
        ind = {"vol": [1.0] * 170, "m50": [0] * 170}
        self.assertIsNone(b.simuler("compression", 160, 1, 100.0, c, serie(c), ind))

    def test_couts_reduisent_R(self):
        c = [100.0] * 160 + [100, 100, 104, 105, 110]
        ind = {"vol": [1.0] * len(c), "m50": [0] * len(c)}
        a = b.simuler("compression", 160, 1, 98.0, c, serie(c), ind, frais=0)["R"]
        z = b.simuler("compression", 160, 1, 98.0, c, serie(c), ind, frais=1)["R"]
        self.assertLess(z, a)


if __name__ == "__main__":
    unittest.main()
