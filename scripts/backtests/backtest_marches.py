"""12 règles sur les autres marchés pour prévoir l'or (règles : regles/marches_croises_v1.md, figées). Lancé une seule fois.

  python scripts/backtests/backtest_marches.py   # -> resultats/marches_croises_v1.md
"""
import datetime as dt
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_regime as br  # noqa: E402
import backtest_sessions as bs  # noqa: E402

DEBUT, SEPARATION = pd.Timestamp("2006-06-01"), pd.Timestamp("2016-01-01")
FRAIS_BASE, FRAIS_STRESS = 0.0002, 0.0005
N_ESSAIS, N_PROJET = 12, 340
FICHIERS = {"dxy": "dollar_dxy.csv", "taux_reels": "taux_reels_10ans.csv", "argent": "marche_argent.csv", "mineurs": "marche_mineurs_or.csv",
            "sp500": "marche_sp500.csv", "vix": "marche_vix.csv", "tnx": "marche_taux10ans.csv", "tlt": "marche_obligations_tlt.csv",
            "cuivre": "marche_cuivre.csv", "petrole": "marche_petrole.csv"}


def charger():
    aujourdhui = pd.Timestamp(dt.datetime.now(dt.timezone.utc).date())
    g = br.lire_prix("or_jour.csv")
    g = g[(g["close"] > 0) & (g["open"] > 0) & (g.index < aujourdhui)]
    g = g[g.index >= DEBUT]
    C = {k: br.lire_prix(f)["close"] for k, f in FICHIERS.items()}
    return g, C


def signaux(g, C):
    idx = g.index
    s = np.sign
    def al(x):
        return x.reindex(idx)
    r1 = {k: al(v.pct_change()) for k, v in C.items()}
    d1 = {k: al(v.diff()) for k, v in C.items()}
    rg = g["close"].pct_change()
    r5_dxy = al(C["dxy"].pct_change(5))
    ratio = (g["close"] / al(C["argent"])).pct_change(5)
    manque = lambda *xs: pd.concat(xs, axis=1).isna().any(axis=1)
    X = {
        1: ("Dollar du jour", -s(r1["dxy"])), 2: ("Dollar 5 jours", -s(r5_dxy)), 3: ("Rendement 10 ans", -s(d1["tnx"])),
        4: ("Taux réels (variation du jour)", -s(d1["taux_reels"])), 5: ("Argent", s(r1["argent"])), 6: ("Rapport or/argent 5 jours", -s(ratio)),
        7: ("Mineurs d'or devant l'or", s(r1["mineurs"] - rg)), 8: ("Actions (valeur refuge)", -s(r1["sp500"])),
        9: ("VIX (±5 %)", pd.Series(np.where(r1["vix"] > 0.05, 1.0, np.where(r1["vix"] < -0.05, -1.0, 0.0)), index=idx).where(~r1["vix"].isna())),
        10: ("Obligations TLT", s(r1["tlt"])), 11: ("Cuivre et pétrole", s((r1["cuivre"] + r1["petrole"]) / 2)),
    }
    score = -s(r1["dxy"]) - s(d1["tnx"]) + s(r1["tlt"]) + s(r1["argent"])
    X[12] = ("Score composé (≥ 3 sur 4)", pd.Series(np.where(score >= 3, 1.0, np.where(score <= -3, -1.0, 0.0)), index=idx).where(~score.isna()))
    X[0] = ("Témoin hasard", pd.Series(np.random.default_rng(2026).choice([-1.0, 1.0], len(idx)), index=idx))
    return X


def trades(g, sg):
    """Signal à la séance t, achat/vente de l'or à l'ouverture de t+1, sortie à la clôture de t+1."""
    jr = (g["close"] / g["open"] - 1).shift(-1)
    d = pd.DataFrame({"sens": sg, "brut_j": jr})
    d = d[(d["sens"] != 0) & d["sens"].notna() & d["brut_j"].notna()]
    d["brut"] = d["sens"] * d["brut_j"]
    d["net"] = d["brut"] - FRAIS_BASE
    d["stress"] = d["brut"] - FRAIS_STRESS
    d["date"] = d.index
    return d.reset_index(drop=True)


def rapport():
    g, C = charger()
    X = signaux(g, C)
    annees = (g.index[-1] - g.index[0]).days / 365.25
    semaines = annees * 52.18
    lignes, passe = [], []
    for num, (nom, sg) in X.items():
        T = trades(g, sg)
        x = T["net"].values
        n = len(x)
        dev, val = T[T["date"] < SEPARATION], T[T["date"] >= SEPARATION]
        t_all, td, tv = br.nw_t(x, 5), br.nw_t(dev["net"].values, 5), br.nw_t(val["net"].values, 5)
        par_an = T.groupby(T["date"].dt.year)["net"].agg(["mean", "size"])
        par_an = par_an[par_an["size"] >= 20]
        pos_an = (par_an["mean"] > 0).mean()
        ecart = 1 / math.sqrt(n - 1)
        d12, d340 = br.deflated_sharpe(x, N_ESSAIS, ecart), br.deflated_sharpe(x, N_PROJET, ecart)
        E = bs.apres_impots(T["date"].values, x)
        avant, apres = np.prod(1 + x) ** (1 / annees) - 1, E ** (1 / annees) - 1
        manque = [t for ok, t in ((dev["net"].mean() > 0 and td >= 2, "développement"), (val["net"].mean() > 0 and tv >= 2, "validation"),
                                  (pos_an >= 0.6, "années positives"), (n / semaines >= 2, "fréquence"), (d12 >= 0.95, "Deflated Sharpe"), (apres > 0, "après impôts")) if not ok]
        if num != 0 and not manque:
            passe.append(nom)
        lignes.append((x.mean(), num, nom, n, n / semaines, (x > 0).mean(), T["brut"].mean(), x.mean(), T["stress"].mean(), t_all, dev["net"].mean(), td, val["net"].mean(), tv,
                       pos_an, d12, d340, avant, apres, manque))
    lignes.sort(key=lambda z: -z[0])
    c = g["close"]
    gain = c.iloc[-1] / c.iloc[0] - 1
    bh_avant, bh_apres = (1 + gain) ** (1 / annees) - 1, (1 + gain - bs.IMPOT * max(gain, 0)) ** (1 / annees) - 1
    txt = ["# Autres marchés pour prévoir l'or : résultats", "",
           "Règles : `regles/marches_croises_v1.md`, figées avant le test, lancées **une seule fois**. Or GC=F du %s au %s ; développement jusqu'à fin 2015, validation depuis 2016. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**" % (g.index[0].date(), g.index[-1].date()), "",
           "Signal avec les clôtures de la séance t ; ordre sur l'or à l'ouverture de t+1, sortie à sa clôture. Frais 0,02 % l'aller-retour (stress 0,05 %), 1 fois le capital. « Après impôts » = 31,4 % des plus-values nettes annuelles, moins-values reportées.", "",
           "Référence **garder l'or** (%s ans) : %s par an avant impôts, %s par an après impôts (vente à la fin)." % (br.fr(annees, 1), br.pct(bh_avant), br.pct(bh_apres)), "",
           "| N° | Règle | Ordres | Par semaine | Gagnants | Brut moyen | Net moyen | Net stress | t | Dév. jusqu'à 2015 (net / t) | Valid. depuis 2016 (net / t) | Années positives | Deflated Sharpe (12 / 340 essais) | Rdt annuel avant / après impôts |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for (_, num, nom, n, sem, win, brut, net, stress, t_all, dm, td, vm, tv, pa, d12, d340, av, ap, manque) in lignes:
        txt.append("| %d | %s | %d | %s | %s | %s | %s | %s | %s | %s / %s | %s / %s | %s | %s / %s | %s / %s |" % (
            num, nom, n, br.fr(sem, 1), br.pct(win, 0), br.pct(brut, 3), br.pct(net, 3), br.pct(stress, 3), br.fr(t_all, 1), br.pct(dm, 3), br.fr(td, 1), br.pct(vm, 3), br.fr(tv, 1),
            br.pct(pa, 0), br.fr(d12, 2), br.fr(d340, 2), br.pct(av), br.pct(ap)))
    pos_net = [l for l in lignes if l[1] != 0 and l[7] > 0]
    nb_t2 = [l for l in lignes if l[1] != 0 and l[9] >= 2]
    nb_val = [l for l in lignes if l[1] != 0 and l[7] > 0 and l[13] >= 2 and l[11] >= 2]
    brut_pos = [l for l in lignes if l[1] != 0 and l[6] > 0]
    txt += ["", "### Verdict", ""]
    txt.append(("**Règles qui remplissent tous les critères : %s.** Candidates au paper trading, pas une preuve." % ", ".join(passe)) if passe else "**Aucune des 12 règles ne remplit tous les critères.**")
    txt += ["", "- Gain net moyen positif : %d règles sur 12 ; avec t ≥ 2 sur toute la période : %d ; positives avec t ≥ 2 à la fois en développement et en validation : %d. Gain brut (avant frais) positif : %d." % (len(pos_net), len(nb_t2), len(nb_val), len(brut_pos)),
            "- Avec 12 essais, environ 0,5 règle atteint t ≥ 2 par pur hasard.", "", "Critères non remplis (les 6 meilleures par gain net moyen) :", ""]
    for l in [l for l in lignes if l[1] != 0][:6]:
        txt.append("- %s : %s." % (l[2], ", ".join(l[-1]) if l[-1] else "tous remplis"))
    txt += ["", "## Limites", "",
            "- Données Yahoo gratuites (clôtures et ouvertures de futures à heures non parfaitement alignées : l'ouverture de t+1 est supposée après les clôtures de t). Frais et impôts estimés ; pas de glissement.",
            "- Impôts : hypothèse du prélèvement forfaitaire unique français de 31,4 % ; pas un conseil fiscal.",
            "- Environ 340 essais dans ce projet ; le Deflated Sharpe à 340 essais est donné par honnêteté."]
    out = br.RACINE / "resultats" / "marches_croises_v1.md"
    out.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))


if __name__ == "__main__":
    rapport()
