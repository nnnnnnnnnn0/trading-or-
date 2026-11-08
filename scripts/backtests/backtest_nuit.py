"""Stratégie « Nuit or » v1 : acheter à 21 h UTC, vendre à 13 h UTC le jour de bourse suivant. Règles : regles/strategie_nuit_v1.md.

  python scripts/backtests/backtest_nuit.py   # -> resultats/nuit_v1.md
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_regime as br  # noqa: E402

VARIANTES = {"A (frais de base)": (0.0005, 0.00015), "B (frais réduits de moitié)": (0.00025, 0.000075)}


def trades(seg, aller_retour, par_nuit):
    return seg["hors_us"] - aller_retour - seg["nuits"] * par_nuit


def mesures(x):
    x = np.asarray(x, dtype=float)
    eq = np.cumsum(x)
    return {"moy": x.mean(), "t": br.nw_t(x), "sharpe": x.mean() / x.std() * math.sqrt(252), "ann": x.mean() * 252,
            "gagnants": (x > 0).mean(), "dd": (eq - np.maximum.accumulate(eq)).min()}


def rapport():
    o = br.lire_5m()
    seg = br.segments(o)
    n = len(seg)
    coupe = int(n * 0.6)
    bornes = np.linspace(0, n, 5).astype(int)
    txt = ["# Stratégie Nuit or v1 : résultats", "",
           "Règles : `regles/strategie_nuit_v1.md`, figées avant le test. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
           "Achat à 21 h UTC, vente à 13 h UTC le jour de bourse suivant, or au comptant 5 min, %d trades du %s au %s. Gain brut moyen par trade (sans frais) : %s." % (
               n, seg.index[0].date(), seg.index[-1].date(), br.pct(seg["hors_us"].mean(), 3)), "",
           "| Variante | Gain net moyen par trade | t | Rendement annuel | Sharpe | Trades gagnants | Perte max (cumulée) | Développement (moy. / t) | Contrôle (moy. / t) | Blocs (moy. par trade) | Années positives | Deflated Sharpe (2 / 250 essais) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    verdict = None
    for nom, (ar, nu) in VARIANTES.items():
        x = trades(seg, ar, nu)
        m = mesures(x)
        d, c = mesures(x.iloc[:coupe]), mesures(x.iloc[coupe:])
        blocs = [x.iloc[a:b].mean() for a, b in zip(bornes[:-1], bornes[1:])]
        par_an = x.groupby(x.index.year).mean()
        ann_pos = (par_an > 0).mean()
        ecart = 1 / math.sqrt(n - 1)
        d2, d250 = br.deflated_sharpe(x.values, 2, ecart), br.deflated_sharpe(x.values, 250, ecart)
        txt.append("| %s | %s | %s | %s | %s | %s | %s | %s / %s | %s / %s | %s | %s | %s / %s |" % (
            nom, br.pct(m["moy"], 3), br.fr(m["t"], 1), br.pct(m["ann"]), br.fr(m["sharpe"]), br.pct(m["gagnants"], 0), br.pct(m["dd"], 0),
            br.pct(d["moy"], 3), br.fr(d["t"], 1), br.pct(c["moy"], 3), br.fr(c["t"], 1), " | ".join(br.pct(b, 3) for b in blocs) if False else " ; ".join(br.pct(b, 3) for b in blocs),
            br.pct(ann_pos, 0), br.fr(d2), br.fr(d250)))
        if nom.startswith("A"):
            manque = [t for ok, t in ((m["moy"] > 0 and d["moy"] > 0 and c["moy"] > 0 and d["t"] >= 2 and c["t"] >= 2, "gain net positif avec t ≥ 2 en développement et en contrôle"),
                                      (sum(b > 0 for b in blocs) >= 3, "positif dans moins de 3 blocs sur 4"),
                                      (ann_pos >= 0.7, "moins de 70 % d'années positives"), (d2 >= 0.95, "Deflated Sharpe < 0,95")) if not ok]
            verdict = manque
            par_an_a = par_an
    txt += ["", "### Verdict (variante A)", ""]
    txt.append("**Tous les critères sont remplis.** Candidat pour du paper trading en conditions réelles, pas une preuve." if not verdict else
               "**Critères non remplis : " + " ; ".join(verdict) + ".** La stratégie n'est pas retenue ; elle n'est pas retouchée pour la faire passer.")
    brut = seg["hors_us"].mean()
    nuits_moy = seg["nuits"].mean()
    txt += ["", "Frais aller-retour qui annuleraient le gain brut (financement de %s par nuit inclus, %s nuits en moyenne) : %s. Frais de base : 0,050 %%." % (
        "0,015 %", br.fr(nuits_moy), br.pct(max(0.0, brut - nuits_moy * 0.00015), 3)), "",
        "### Gain net moyen par année (variante A)", "", "| Année | Gain net moyen par trade |", "| --- | --- |"]
    txt += ["| %d | %s |" % (y, br.pct(v, 3)) for y, v in par_an_a.items()]
    txt += ["", "## Limites", "",
            "- Heures UTC fixes : l'ouverture américaine se décale d'une heure selon l'heure d'été.",
            "- Entrée et sortie aux prix d'ouverture de barres 5 min, sans glissement ; or au comptant ; frais estimés, pas ceux d'un courtier précis.",
            "- Cette règle vient d'un résultat vu sur les mêmes données (H1) : le test est moins indépendant qu'il n'en a l'air."]
    out = br.RACINE / "resultats" / "nuit_v1.md"
    out.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))


if __name__ == "__main__":
    rapport()
