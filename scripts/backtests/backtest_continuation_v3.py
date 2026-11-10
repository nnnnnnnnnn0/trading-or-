"""Stratégie « Continuation Monte Carlo » v3 : règles dans regles/continuation_monte_carlo_v3.md (figées avant le test).
Lancé une seule fois sur les 14 ans de barres 5 min de l'or.

  python scripts/backtests/backtest_continuation_v3.py   # -> resultats/continuation_monte_carlo_v3.md

Réutilise la v2 (cône Monte Carlo, tendances, filtres) et la v1 (mesures). Une décision par jour à 08:00 UTC, dans le sens de la tendance,
trois durées de détention (sortie à 20:55 UTC du jour même, du 3e et du 5e jour de bourse), stop 3 A x racine du nombre de jours.
Le rendement quotidien du compte (Deflated Sharpe, impôts) est attribué à la date de SORTIE du trade.
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_compression as bc  # noqa: E402
import backtest_montecarlo as bm  # noqa: E402
import backtest_montecarlo_v2 as m2  # noqa: E402
import backtest_regime as br  # noqa: E402

NS, JOUR_NS = bm.NS, bm.JOUR_NS
STOP_A = 3.0
HORIZONS = (("H0", 0), ("H2", 2), ("H4", 4))
NOMS_H = {"H0": "H0 (sortie le jour même)", "H2": "H2 (3 jours de bourse)", "H4": "H4 (5 jours de bourse)"}
FRAIS_BASE, FIN_BASE = 0.0002, 0.00015
FRAIS_STRESS, FIN_STRESS = 0.0005, 0.0003
GRAINE = 2026
Z_25 = m2.Z_25
N_ESSAIS, CUMUL = 9, 367
MIN_TRADES_AN = 12
IMPOT = 0.314
SORTIE = br.RACINE / "resultats" / "continuation_monte_carlo_v3.md"


# ------------------------------------------------------------------ signaux
def decisions(P):
    """Les décisions de 08:00 UTC (une par jour valide) avec tous les signaux de la v2."""
    s = m2.decisions(P)
    s = s[(s["date"].dt.hour == 8) & (s["date"].dt.minute == 0)]
    return s.reset_index(drop=True)


def tendance(s):
    """+1 si tendance journalière et horaire haussières, -1 si baissières, 0 sinon."""
    haut = (s["dtrend"] > 0) & (s["ema20"] > s["ema100"])
    bas = (s["dtrend"] < 0) & (s["ema20"] < s["ema100"])
    return np.where(haut, 1, np.where(bas, -1, 0))


def directions(s):
    t = tendance(s)
    filtre = ((s["A"] >= s["atr_med"]) & (s["rv"] >= 1.0)).to_numpy()          # NaN -> faux
    qp = np.where(t > 0, s["q"].to_numpy(), 1 - s["q"].to_numpy())             # position dans le cône, dans le sens de la tendance
    zp = t * s["z"].to_numpy()
    biais_ok = np.sign(s["biais"].to_numpy()) == t
    return {"C": np.where((t != 0) & biais_ok & (qp > 0.25) & filtre, t, 0),
            "Cz": np.where((t != 0) & (zp > -Z_25) & filtre, t, 0),
            "Ct": t}


# ------------------------------------------------------------------ simulation
def sorties(P, s, k):
    """Pour chaque décision : barre de sortie (20:55 UTC du k-ième jour de bourse suivant), validité, nuits prévues."""
    jours = P.jours
    pe = np.searchsorted(jours, s["jour"].to_numpy()) + k
    ok = pe < len(jours)
    jour_sortie = jours[np.minimum(pe, len(jours) - 1)]
    echeance = jour_sortie + bm.SORTIE_S * NS
    i_dl = np.searchsorted(P.t, echeance)
    ok &= i_dl < len(P.t)
    ok &= (P.t[np.minimum(i_dl, len(P.t) - 1)] - echeance) <= 30 * 60 * NS
    return i_dl, ok, (jour_sortie - s["jour"].to_numpy()) // JOUR_NS


def simuler(P, s, sens, k):
    """Une position à la fois ; stop 3 A x racine(k+1) ; frais + financement par nuit calendaire, convertis en R (1 R = distance du stop)."""
    i_dl, ok, _ = sorties(P, s, k)
    T, I0, A = s["T"].to_numpy(), s["i0"].to_numpy(), s["A"].to_numpy()
    libre, lignes = -1, []
    for n in range(len(s)):
        sg = int(sens[n])
        if sg == 0 or not ok[n] or T[n] < libre:
            continue
        stop_d = STOP_A * math.sqrt(k + 1) * float(A[n])
        px, motif, fin = m2.sortie(P.t, P.o, P.h, P.l, int(I0[n]), int(i_dl[n]), sg, stop_d, np.inf)
        entree = float(P.o[I0[n]])
        brut = sg * (px - entree) / stop_d
        r = entree / stop_d
        nuits = int(fin // JOUR_NS - T[n] // JOUR_NS)
        lignes.append((s["date"].iloc[n], pd.Timestamp(fin, unit="ns", tz="UTC"), sg, entree, px, motif, stop_d, brut,
                       brut - (FRAIS_BASE + FIN_BASE * nuits) * r, brut - (FRAIS_STRESS + FIN_STRESS * nuits) * r, nuits))
        libre = fin
    return pd.DataFrame(lignes, columns=["date", "date_sortie", "sens", "entree", "sortie", "motif", "A", "brut", "net", "stress", "nuits"])


# ------------------------------------------------------------------ mesures
def mesures(tr, jours):
    dev, val = tr[tr["date"] < bm.SEPARATION], tr[tr["date"] >= bm.SEPARATION]
    m_dev, t_dev = bm.moy_t(dev["net"])
    m_val, t_val = bm.moy_t(val["net"])
    m_tot, t_tot = bm.moy_t(tr["net"])
    if len(tr):
        g = tr.groupby(tr["date"].dt.year)["net"].agg(["size", "sum"])
        g = g[g["size"] >= MIN_TRADES_AN]
        ans_pos, ans_tot = int((g["sum"] > 0).sum()), len(g)
    else:
        ans_pos = ans_tot = 0
    x = bm.serie_quotidienne(tr.assign(date=tr["date_sortie"]), jours)
    avant, apres = bm.rendements_annuels(x) if len(x) > 1 else (float("nan"), float("nan"))
    return {"n": len(tr), "gagnants": float((tr["net"] > 0).mean()) if len(tr) else float("nan"),
            "brut": float(tr["brut"].mean()) if len(tr) else float("nan"), "net": m_tot, "t": t_tot,
            "stress": float(tr["stress"].mean()) if len(tr) else float("nan"),
            "n_dev": len(dev), "m_dev": m_dev, "t_dev": t_dev, "n_val": len(val), "m_val": m_val, "t_val": t_val,
            "ans_pos": ans_pos, "ans_tot": ans_tot, "avant": avant, "apres": apres,
            "dsr9": bm.dsr(x.values, N_ESSAIS), "dsr367": bm.dsr(x.values, CUMUL)}


def garder_l_or(P, s):
    """Information : rendement annuel de l'achat-conservation sur la même période, avant impôts et après impôts (vente à la fin)."""
    a, b = float(P.o[s["i0"].iloc[0]]), float(P.o[s["i0"].iloc[-1]])
    ans = max(1e-9, (s["date"].iloc[-1] - s["date"].iloc[0]).days / 365.25)
    gain = b / a - 1
    apres = 1 + gain - IMPOT * max(0.0, gain)
    return (b / a) ** (1 / ans) - 1, apres ** (1 / ans) - 1


def sup(a, b):
    return bool(a > b)          # NaN -> faux


def criteres(mC, mZ, mT, mH):
    comp = [("Cz", mZ), ("Ct", mT), ("hasard", mH)]
    meilleur = all(sup(mC[p], m[p]) for _, m in comp for p in ("m_dev", "m_val"))
    detail = " ; ".join("%s %s / %s" % (nom, br.fr(m["m_dev"], 3), br.fr(m["m_val"], 3)) for nom, m in comp)
    return [
        ("Gain net moyen > 0 avec t ≥ 2 en développement (2012-2019)", mC["m_dev"] > 0 and mC["t_dev"] >= 2,
         "%s R, t = %s (%d trades)" % (br.fr(mC["m_dev"], 3), br.fr(mC["t_dev"], 1), mC["n_dev"])),
        ("Gain net moyen > 0 avec t ≥ 2 en validation (2020-2026)", mC["m_val"] > 0 and mC["t_val"] >= 2,
         "%s R, t = %s (%d trades)" % (br.fr(mC["m_val"], 3), br.fr(mC["t_val"], 1), mC["n_val"])),
        ("Au moins 100 trades et 60 % d'années positives", mC["n"] >= 100 and mC["ans_tot"] > 0 and mC["ans_pos"] / mC["ans_tot"] >= 0.6,
         "%d trades ; %d années positives sur %d" % (mC["n"], mC["ans_pos"], mC["ans_tot"])),
        ("Deflated Sharpe ≥ 0,95 (9 essais)", mC["dsr9"] >= 0.95, "DSR %s (367 essais : %s)" % (br.fr(mC["dsr9"], 2), br.fr(mC["dsr367"], 2))),
        ("Rendement annuel après impôts > 0", mC["apres"] > 0, "%s par an (%s avant impôts)" % (br.pct(mC["apres"], 1), br.pct(mC["avant"], 1))),
        ("C fait mieux que Cz, Ct et le hasard en développement et en validation", meilleur,
         "C %s / %s R contre %s (dév. / valid.)" % (br.fr(mC["m_dev"], 3), br.fr(mC["m_val"], 3), detail)),
        ("Gain net moyen > 0 avec les frais de stress", mC["stress"] > 0, "%s R par trade" % br.fr(mC["stress"], 3)),
    ]


# ------------------------------------------------------------------ rapport
def ligne(nom, m, ans):
    return "| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        nom, m["n"], br.fr(m["n"] / ans, 0), br.pct(m["gagnants"], 0), br.fr(m["brut"], 3), br.fr(m["net"], 3), br.fr(m["t"], 1),
        br.fr(m["stress"], 3), br.fr(m["m_dev"], 3), br.fr(m["m_val"], 3), "%d/%d" % (m["ans_pos"], m["ans_tot"]), br.pct(m["apres"], 1))


def rapport(n_boot=10000, n_hasard=100):
    df = bc.lire_5m_complet()
    P = m2.preparer(df)
    s = decisions(P)
    sens = directions(s)
    jours = P.jours[(P.jours >= s["jour"].iloc[0]) & (P.jours <= s["jour"].iloc[-1])]
    ans = max(1e-9, (s["date"].iloc[-1] - s["date"].iloc[0]).days / 365.25)
    trades, M, hasards = {}, {}, {}
    for h, k in HORIZONS:
        for v in ("C", "Cz", "Ct"):
            trades[(h, v)] = simuler(P, s, sens[v], k)
        rng = np.random.default_rng(GRAINE)
        trades[(h, "Hasard")] = simuler(P, s, np.where(sens["C"] != 0, rng.choice([-1, 1], size=len(s)), 0), k)
        moy = []
        for g in range(1, n_hasard + 1):
            r = np.random.default_rng(10_000 + g)
            tr = simuler(P, s, np.where(sens["C"] != 0, r.choice([-1, 1], size=len(s)), 0), k)
            if len(tr):
                moy.append(float(tr["net"].mean()))
        hasards[h] = np.array(moy)
        for v in ("C", "Cz", "Ct", "Hasard"):
            M[(h, v)] = mesures(trades[(h, v)], jours)
    crit = {h: criteres(M[(h, "C")], M[(h, "Cz")], M[(h, "Ct")], M[(h, "Hasard")]) for h, _ in HORIZONS}
    reussis = [h for h, _ in HORIZONS if all(c[1] for c in crit[h])]
    bh_av, bh_ap = garder_l_or(P, s)
    L = ["# Stratégie « Continuation Monte Carlo » v3 : résultats", "",
         "Règles figées avant le test : `regles/continuation_monte_carlo_v3.md`. Lancé une seule fois, sans retouche. **L'idée vient de l'observation d'un tableau de la v2 sur les mêmes données : ce test n'est donc pas indépendant** "
         "et un bon résultat ne serait qu'une piste à confirmer en avant. Or XAUUSD, barres 5 min Dukascopy 2012-2026 ; une décision par jour à 08:00 UTC, dans le sens de la tendance ; "
         "frais 0,02 % l'aller-retour + 0,015 % par nuit (stress 0,05 % + 0,03 %) ; risque 0,5 % du capital par trade (1 R = distance du stop, 3 ATR horaires × √jours de détention). "
         "Développement 2012-2019, validation 2020-2026.", "",
         "## Verdict", "",
         ("**%s : la variante C passe tous les critères figés.** À confirmer en avant avant toute confiance (voir l'avertissement ci-dessus)." % ", ".join(reussis) if reussis else
          "**Aucune des trois durées ne passe tous les critères figés : la continuation n'est pas « solide » au sens que nous avions fixé.** Les chiffres sont publiés tels quels, sans retouche de la règle."),
         "", "| Critère (figé avant le test) | H0 : le jour même | H2 : 3 jours | H4 : 5 jours |", "|---|---|---|---|"]
    for i in range(len(crit["H0"])):
        L.append("| %s | %s |" % (crit["H0"][i][0], " | ".join("%s %s" % ("✔" if crit[h][i][1] else "✘", crit[h][i][2]) for h, _ in HORIZONS)))
    L += ["", "Critères réussis (sur 7) : " + ", ".join("%s %d" % (h, sum(1 for c in crit[h] if c[1])) for h, _ in HORIZONS) + ".", "",
          "## Toutes les stratégies", "",
          "Moyennes par trade en R. Brut = sans frais ; net = frais de base et financement ; stress = frais de stress ; t = Newey-West sur le net. 12 colonnes : trades, trades par an, gagnants, brut, net, t, net (stress), net en développement, net en validation, années positives, rendement annuel après impôts.", "",
          "| Stratégie | Trades | par an | gagnants | brut | net | t | stress | dév. | valid. | années + | après impôts |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    noms = {"C": "C complète", "Cz": "Cz sans simulation", "Ct": "Ct tendance seule", "Hasard": "Hasard (jours de C)"}
    for h, _ in HORIZONS:
        for v in ("C", "Cz", "Ct", "Hasard"):
            L.append(ligne("%s : %s" % (h, noms[v]), M[(h, v)], ans))
    L += ["", "Sorties de C : " + " ; ".join("%s : %s" % (h, ", ".join("%s %d" % (a, b) for a, b in trades[(h, "C")]["motif"].value_counts().items()) or "aucun trade") for h, _ in HORIZONS) + ".",
          "Décisions à 08:00 évaluées : %d ; jours où C déclenche : %d, Cz : %d, Ct : %d." % (len(s), int((sens["C"] != 0).sum()), int((sens["Cz"] != 0).sum()), int((sens["Ct"] != 0).sum())), "",
          "Information : **garder l'or** sur la même période rapporte %s par an avant impôts et %s par an après impôts (vente à la fin, 31,4 %%)." % (br.pct(bh_av, 1), br.pct(bh_ap, 1)), "",
          "## Années, durée par durée (C : nombre de trades / total en R)", "", "| Année | H0 | H2 | H4 |", "|---|---|---|---|"]
    par_an = {}
    for h, _ in HORIZONS:
        tr = trades[(h, "C")]
        if len(tr):
            for an, g in tr.groupby(tr["date"].dt.year):
                par_an.setdefault(an, {})[h] = "%d / %s" % (len(g), br.fr(g["net"].sum(), 1))
    for an in sorted(par_an):
        L.append("| %d | %s |" % (an, " | ".join(par_an[an].get(h, "-") for h, _ in HORIZONS)))
    L += ["", "## Le hasard (information)", "",
          "Même jours que C, sens tiré au sort (graine 2026) puis 100 autres tirages par durée, mêmes stop et frais.", "",
          "| Durée | net du tirage principal | médiane des 100 tirages | 90 % des tirages entre | tirages au moins aussi bons que C |", "|---|---|---|---|---|"]
    for h, _ in HORIZONS:
        x, mC = hasards[h], M[(h, "C")]
        if len(x):
            L.append("| %s | %s R | %s R | %s et %s R | %s |" % (h, br.fr(M[(h, "Hasard")]["net"], 3), br.fr(float(np.median(x)), 3), br.fr(float(np.quantile(x, 0.05)), 3),
                                                              br.fr(float(np.quantile(x, 0.95)), 3), br.pct(float((x >= mC["net"]).mean()), 0) if mC["n"] else "n.d."))
    L += ["", "## Monte Carlo des résultats de C (information)", "",
          "10 000 rééchantillonnages des trades (avec remise) : probabilité que le total soit positif, fourchette 5-95 % du total en R, perte maximale médiane.", "",
          "| Durée | Trades | P(total > 0) | total 5 % - 95 % (R) | perte max médiane (R) |", "|---|---|---|---|---|"]
    for h, _ in HORIZONS:
        b = bm.bootstrap_trades(trades[(h, "C")]["net"].values, n_boot)
        if b:
            L.append("| %s | %d | %s | %s à %s | %s |" % (h, M[(h, "C")]["n"], br.pct(b["p_pos"], 0), br.fr(b["q05"], 1), br.fr(b["q95"], 1), br.fr(b["dd_med"], 1)))
    L += ["", "## À retenir", "",
          "- Essais cumulés dans ce dépôt : environ %d (dont les 9 stratégies de ce test)." % CUMUL,
          "- L'hypothèse vient des mêmes données : seule une confirmation en avant (paper trading, règles inchangées) aurait une vraie valeur.",
          "- Aucun paramètre n'a été ajusté après ce test (08:00, q' > 0,25, stop 3 A √jours, durées 0/2/4 jours).",
          "- Frais supposés à remplacer par ceux de ton courtier ; impôt 31,4 % (flat tax 2026), sans conseil fiscal.", "",
          "Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.", ""]
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    rapport()
