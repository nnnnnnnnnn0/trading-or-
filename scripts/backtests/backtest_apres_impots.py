"""Règles « achat seulement » sur l'or, après impôts (règles : regles/apres_impots_v1.md, figées). Lancé une seule fois.

  python scripts/backtests/backtest_apres_impots.py   # -> resultats/apres_impots_v1.md
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_regime as br  # noqa: E402

FRAIS_COTE, TER, IMPOT = 0.00025, 0.0015, 0.314
DEBUT = pd.Timestamp("2012-01-02")
N_ESSAIS, N_PROJET = 4, 340


def simuler(held, ret, dates, taux=IMPOT, frais=FRAIS_COTE, ter=TER):
    """held[k] = 1 si l'or est détenu pendant la séance k (de la clôture k-1 à la clôture k). Retourne (valeur finale, trajectoire).
    Plus-value réalisée à chaque sortie ; impôt `taux` sur le net de l'année (moins-values reportées) ; position ouverte à la fin : vendue."""
    n = len(held)
    E, basis, carry, real, prev = 1.0, None, 0.0, 0.0, 0
    chemin = np.empty(n)
    for k in range(n):
        h = int(held[k])
        if h and not prev:
            basis = E
            E *= 1 - frais
        if h:
            E *= (1 + ret[k]) * (1 - ter / 252)
        suivant = int(held[k + 1]) if k + 1 < n else 0
        if h and not suivant:
            E *= 1 - frais
            real += E - basis
            basis = None
        prev = h
        if k == n - 1 or dates[k + 1].year != dates[k].year:
            net = real + carry
            impot = taux * max(0.0, net)
            if impot > 0:
                if basis is not None:
                    basis *= (E - impot) / E
                E -= impot
            carry, real = min(0.0, net), 0.0
        chemin[k] = E
    return E, chemin


def etat_vers_detenu(etat):
    """Décision à la clôture t, exécutée à la clôture t+1 : détenu pendant la séance t+2."""
    held = np.zeros(len(etat))
    held[2:] = etat[:-2]
    return held


def etats(g, dxy, taux):
    c = g["close"]
    n = len(c)
    dec_sem = br.jours_de_decision(g.index)
    mois = g.index.to_period("M")
    dec_mois = np.append(mois.values[1:] != mois.values[:-1], True)
    sma200 = c.rolling(200).mean()
    cond_a = (c > sma200).values & sma200.notna().values
    cond_b = (c / c.shift(252) - 1 > 0).values & c.shift(252).notna().values
    macro = ((taux.shift(1).diff(63) < 0) | (dxy.shift(1).diff(63) < 0)).values
    def pas_a_pas(cond, dec):
        e, s = np.zeros(n), 0.0
        for t in range(n):
            if dec[t]:
                s = 1.0 if cond[t] else 0.0
            e[t] = s
        return e
    A = pas_a_pas(cond_a, dec_sem)
    B = pas_a_pas(cond_b, dec_mois)
    C = pas_a_pas(cond_a & macro, dec_sem)
    D, s, pic, entree = np.zeros(n), 0.0, -np.inf, None
    cv = c.values
    for t in range(n):
        if s == 1.0 and entree is not None and t >= entree:
            pic = max(pic, cv[t])
            if cv[t] < 0.88 * pic:
                s, entree, pic = 0.0, None, -np.inf
        if dec_sem[t]:
            if s == 0.0 and cond_a[t]:
                s, entree, pic = 1.0, t + 1, -np.inf
            elif s == 1.0 and not cond_a[t]:
                s, entree, pic = 0.0, None, -np.inf
        D[t] = s
    return {"A  Tendance 200 jours": A, "B  Momentum 12 mois": B, "C  Tendance + macro": C, "D  Tendance 200 j + sortie de sécurité": D}


def max_dd(chemin):
    return float((chemin / np.maximum.accumulate(chemin) - 1).min())


def cagr(E, annees):
    return E ** (1 / annees) - 1


def rapport():
    g, dxy, taux = br.charger()
    g = g[g.index >= DEBUT]
    dxy, taux = dxy.reindex(g.index), taux.reindex(g.index)
    dates = list(g.index)
    ret = g["close"].pct_change().fillna(0.0).values
    n = len(g)
    annees = (g.index[-1] - g.index[0]).days / 365.25
    bh = np.ones(n)
    E_bh, ch_bh = simuler(bh, ret, dates)
    _, ch_bh0 = simuler(bh, ret, dates, taux=0.0)
    dd_bh = max_dd(ch_bh0)
    blocs = np.linspace(0, n, 5).astype(int)
    rng = np.random.default_rng(2026)
    txt = ["# Règles « achat seulement » sur l'or après impôts : résultats", "",
           "Règles : `regles/apres_impots_v1.md`, figées avant le test, lancées une seule fois. Or journalier (GC=F) du %s au %s (%d séances, %s ans). **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**" % (
               g.index[0].date(), g.index[-1].date(), n, br.fr(annees, 1)), "",
           "Hypothèses : frais 0,05 % l'aller-retour + 0,15 % par an de détention ; impôt 31,4 % des plus-values nettes de l'année (taux 2026 du prélèvement forfaitaire en France, moins-values reportées, position ouverte vendue à la fin) ; décision aux clôtures, exécution à la clôture suivante. Pas un conseil fiscal.", "",
           "| Règle | Jours investis | Entrées par an | Rendement annuel avant impôts | Après impôts 31,4 % | Après impôts 45 % | Valeur finale après impôts (1 = capital) | Perte max (avant impôts) | Après impôts par bloc (4 blocs) | Hasard | Deflated Sharpe (4 / 340 essais) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    _, chemin_bh45 = simuler(bh, ret, dates, taux=0.45)
    txt.append("| R  Garder l'or | 100 %% | 0 | %s | %s | %s | %s | %s | %s | — | — |" % (
        br.pct(cagr(ch_bh0[-1], annees)), br.pct(cagr(E_bh, annees)), br.pct(cagr(chemin_bh45[-1], annees)), br.fr(E_bh, 2), br.pct(dd_bh, 0),
        " / ".join(br.pct(cagr(simuler(bh[a:b], ret[a:b], dates[a:b])[0], (dates[b - 1] - dates[a]).days / 365.25), 0) for a, b in zip(blocs[:-1], blocs[1:]))))
    verdicts = {}
    for nom, etat in etats(g, dxy, taux).items():
        held = etat_vers_detenu(etat)
        E, ch = simuler(held, ret, dates)
        E0, ch0 = simuler(held, ret, dates, taux=0.0)
        E45, _ = simuler(held, ret, dates, taux=0.45)
        dd = max_dd(ch0)
        entrees = int(((held[1:] == 1) & (held[:-1] == 0)).sum())
        cb = [cagr(simuler(held[a:b], ret[a:b], dates[a:b])[0], (dates[b - 1] - dates[a]).days / 365.25) for a, b in zip(blocs[:-1], blocs[1:])]
        quot = ch0[1:] / ch0[:-1] - 1
        net_j = lambda h: h * ret - np.abs(h - np.concatenate([[0.0], h[:-1]])) * FRAIS_COTE - h * TER / 252
        vrai = net_j(held).mean()
        bat = 0
        for _ in range(1000):
            k = int(rng.integers(63, n - 63))
            if net_j(np.roll(held, k)).mean() >= vrai:
                bat += 1
        p = bat / 1000
        ecart = 1 / math.sqrt(len(quot) - 1)
        d4, d340 = br.deflated_sharpe(quot, N_ESSAIS, ecart), br.deflated_sharpe(quot, N_PROJET, ecart)
        gain_bh, gain = E_bh - 1, E - 1
        manque = [t for ok, t in ((cagr(E, annees) > 0 and sum(c_ > 0 for c_ in cb) >= 3, "rendement après impôts positif sur la période et dans 3 blocs sur 4"),
                                  (gain >= 0.7 * gain_bh and abs(dd) <= 0.6 * abs(dd_bh), "au moins 70 % du rendement de garder l'or avec une perte max réduite à 60 %"),
                                  (p <= 0.05, "pas meilleure que le hasard"), (d4 >= 0.95, "Deflated Sharpe")) if not ok]
        verdicts[nom] = manque
        txt.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s |" % (
            nom, br.pct(held.mean(), 0), br.fr(entrees / annees, 1), br.pct(cagr(E0, annees)), br.pct(cagr(E, annees)), br.pct(cagr(E45, annees)), br.fr(E, 2), br.pct(dd, 0),
            " / ".join(br.pct(c_, 0) for c_ in cb), br.pct(p, 0), br.fr(d4, 2), br.fr(d340, 2)))
    txt += ["", "Blocs égaux de %s ans environ ; « hasard » = part de 1 000 décalages aléatoires des mêmes expositions qui rapportent au moins autant." % br.fr(annees / 4, 1), "",
            "### Verdict", ""]
    ok = [k for k, m in verdicts.items() if not m]
    if ok:
        txt.append("**Règles qui remplissent tous les critères : %s.** Ce sont des candidates, pas une preuve." % " ; ".join(ok))
    else:
        txt.append("**Aucune règle ne remplit tous les critères.**")
    for k, m in verdicts.items():
        txt.append("- %s : %s." % (k, "tous les critères remplis" if not m else "critères non remplis : " + " ; ".join(m)))
    txt += ["", "## Limites", "",
            "- La période 2012-2026 contient une forte hausse de l'or (surtout 2019-2026) : « garder l'or » en profite pleinement, et toute règle qui le quitte la subit. Ce n'est pas une prévision.",
            "- Futures GC=F, séance du jour ; exécution aux clôtures sans glissement ; frais et impôts estimés (moins-values reportées sans limite de durée, ce qui est une simplification).",
            "- Environ 340 essais ont été faits dans ce projet ; le Deflated Sharpe à 340 essais est donné par honnêteté."]
    out = br.RACINE / "resultats" / "apres_impots_v1.md"
    out.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))


if __name__ == "__main__":
    rapport()
