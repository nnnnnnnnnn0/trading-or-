"""24 stratégies « sessions » (règles : regles/sessions_5m_v1.md, figées avant le test). Lancé une seule fois.

  python scripts/backtests/backtest_sessions.py   # -> resultats/sessions_v1.md
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_compression as bc  # noqa: E402
import backtest_regime as br  # noqa: E402

FRAIS_BASE, FRAIS_STRESS = 0.0002, 0.0005
IMPOT = 0.314
SEPARATION = pd.Timestamp("2020-01-01", tz="UTC")
N_ESSAIS, N_PROJET = 24, 330
HEURES = {"a22": (22, 0, -1), "h07": (7, 0, 0), "h08": (8, 0, 0), "h1330": (13, 30, 0), "h1430": (14, 30, 0), "h16": (16, 0, 0), "h1830": (18, 30, 0), "h2055": (20, 55, 0)}


def repères(df):
    """Prix d'ouverture aux heures clés, par jour de bourse (colonnes), + volume à chaque heure."""
    o, v = df["open"], df["volume"]
    jours = pd.DatetimeIndex(sorted(set(df.index.normalize().tz_localize(None))))
    jours = jours[jours.dayofweek < 5]
    P, V = pd.DataFrame(index=jours), pd.DataFrame(index=jours)
    for nom, (h, m, dec) in HEURES.items():
        sel = (df.index.hour == h) & (df.index.minute == m)
        s, sv = o[sel], v[sel]
        idx = s.index.normalize().tz_localize(None)
        if dec == -1:                                   # la barre de 22:00 d'un jour appartient à la séance du lendemain
            idx = idx + pd.Timedelta(days=1)
        P[nom] = pd.Series(s.values, index=idx).reindex(jours)
        V[nom] = pd.Series(sv.values, index=idx).reindex(jours)
    return P, V


def signes(P, d):
    rA, rL = P.h07 / P.a22 - 1, P.h1330 / P.h07 - 1
    rNYm, rNYd = P.h16 / P.h1330 - 1, P.h1830 / P.h1330 - 1
    rD, r5, r20 = P.h07 / P.h07.shift(1) - 1, P.h07 / P.h07.shift(5) - 1, P.h07 / P.h07.shift(20) - 1
    r1L, r1NY = P.h08 / P.h07 - 1, P.h1430 / P.h1330 - 1
    # clôture de la séance précédente dans son amplitude
    jour_int = P.index.values.astype("datetime64[D]").astype(np.int64)
    k = np.searchsorted(d.label, jour_int, side="left") - 1
    ok = k >= 14
    kk = np.where(ok, k, 0)
    loc = pd.Series(np.where(ok, (d.c[kk] - d.l[kk]) / np.where(d.r[kk] > 0, d.r[kk], np.nan), np.nan), index=P.index)
    atr = pd.Series(np.where(ok, d.atr[kk], np.nan), index=P.index)
    s = np.sign
    alea = pd.Series(np.random.default_rng(2026).choice([-1.0, 1.0], len(P)), index=P.index)
    def si(c, x):
        return x.where(c, 0.0)
    L = [
        (1, "Asie suivie", "h07", "h1330", s(rA)), (2, "Asie inversée", "h07", "h1330", -s(rA)),
        (3, "Londres suivie", "h1330", "h1830", s(rL)), (4, "Londres inversée", "h1330", "h1830", -s(rL)),
        (5, "New York matin suivi", "h16", "h2055", s(rNYm)), (6, "New York matin inversé", "h16", "h2055", -s(rNYm)),
        (7, "Veille suivie", "h07", "h1830", s(rD)), (8, "Veille inversée", "h07", "h1830", -s(rD)),
        (9, "Tendance 5 j suivie", "h07", "h1830", s(r5)), (10, "Tendance 5 j inversée", "h07", "h1830", -s(r5)),
        (11, "Tendance 20 j suivie", "h07", "h1830", s(r20)), (12, "Tendance 20 j inversée", "h07", "h1830", -s(r20)),
        (13, "1re heure Londres suivie", "h08", "h1330", s(r1L)), (14, "1re heure Londres inversée", "h08", "h1330", -s(r1L)),
        (15, "1re heure New York suivie", "h1430", "h1830", s(r1NY)), (16, "1re heure New York inversée", "h1430", "h1830", -s(r1NY)),
        (17, "Asie + Londres alignées", "h1330", "h1830", si(s(rA) == s(rL), s(rL))),
        (18, "Londres renverse l'Asie", "h1330", "h1830", si(s(rA) * s(rL) < 0, s(rL))),
        (19, "Clôture veille haut/bas suivie", "h07", "h1830", pd.Series(np.where(loc >= 0.8, 1.0, np.where(loc <= 0.2, -1.0, 0.0)), index=P.index)),
        (20, "Clôture veille haut/bas inversée", "h07", "h1830", -pd.Series(np.where(loc >= 0.8, 1.0, np.where(loc <= 0.2, -1.0, 0.0)), index=P.index)),
        (21, "Fin de New York suivie", "h1830", "h2055", s(rNYd)), (22, "Fin de New York inversée", "h1830", "h2055", -s(rNYd)),
        (23, "Londres suivie si tendance 20 j d'accord", "h1330", "h1830", si(s(rL) == s(r20), s(rL))),
        (24, "Asie suivie si tendance 20 j d'accord", "h07", "h1330", si(s(rA) == s(r20), s(rA))),
        (0, "Témoin hasard (Londres → New York)", "h1330", "h1830", alea),
    ]
    return L, atr


def simuler(df, P, V, atr, entree_cle, sortie_cle, sg):
    """Un trade par jour avec sg != 0 ; sortie à l'ouverture de la barre de sortie, stop à 1 ATR journalier."""
    O, H, Lo = df["open"].values, df["high"].values, df["low"].values
    he, hs = HEURES[entree_cle], HEURES[sortie_cle]
    te = (P.index + pd.Timedelta(hours=he[0], minutes=he[1])).tz_localize("UTC")
    ts = (P.index + pd.Timedelta(hours=hs[0], minutes=hs[1])).tz_localize("UTC")
    ie, ix = df.index.get_indexer(te), df.index.get_indexer(ts)
    rows = []
    sgv, atrv, vol = sg.values, atr.values, V[entree_cle].values
    for r in range(len(P)):
        s_ = sgv[r]
        if not s_ or np.isnan(s_) or ie[r] < 0 or ix[r] <= ie[r] or not atrv[r] > 0 or not vol[r] > 0:
            continue
        i, x = ie[r], ix[r]
        entree = O[i]
        stop = entree - s_ * atrv[r]
        hh, ll, oo = H[i:x], Lo[i:x], O[i:x]
        hit = (ll <= stop) if s_ > 0 else (hh >= stop)
        if hit.any():
            k = int(np.argmax(hit))
            px = stop if k == 0 else (min(stop, oo[k]) if s_ > 0 else max(stop, oo[k]))
            motif = "stop"
        else:
            px, motif = O[x], "heure"
        brut = s_ * (px / entree - 1)
        rows.append((P.index[r], int(s_), entree, px, motif, brut, brut - FRAIS_BASE, brut - FRAIS_STRESS, s_ * (px - entree) / atrv[r]))
    return pd.DataFrame(rows, columns=["date", "sens", "entree", "sortie", "motif", "brut", "net", "stress", "R"])


def apres_impots(dates, x):
    """Rendement 1 x le capital réinvesti ; impôt de 31,4 % des plus-values nettes de l'année, moins-values reportées."""
    E, carry = 1.0, 0.0
    d = pd.DataFrame({"y": pd.DatetimeIndex(dates).year, "x": x})
    for _, g in d.groupby("y"):
        debut = E
        E *= float(np.prod(1 + g["x"].values))
        net = (E - debut) + carry
        E -= IMPOT * max(0.0, net)
        carry = min(0.0, net)
    return E


def rapport():
    df = bc.lire_5m_complet()
    df = df[df.index >= pd.Timestamp("2012-01-01", tz="UTC")]
    d = bc.Donnees(df)
    P, V = repères(df)
    strats, atr = signes(P, d)
    annees = (P.index[-1] - P.index[0]).days / 365.25
    semaines = annees * 52.18
    lignes, passe, tous = [], [], {}
    for num, nom, e, s_, sg in strats:
        T = simuler(df, P, V, atr, e, s_, sg)
        tous[num] = T
        x = T["net"].values
        n = len(x)
        dev, val = T[T["date"] < SEPARATION.tz_localize(None)], T[T["date"] >= SEPARATION.tz_localize(None)]
        t_all = br.nw_t(x, 5)
        td, tv = br.nw_t(dev["net"].values, 5), br.nw_t(val["net"].values, 5)
        par_an = T.groupby(T["date"].dt.year)["net"].agg(["mean", "size"])
        par_an = par_an[par_an["size"] >= 20]
        pos_an = (par_an["mean"] > 0).mean()
        ecart = 1 / math.sqrt(n - 1)
        d24, d330 = br.deflated_sharpe(x, N_ESSAIS, ecart), br.deflated_sharpe(x, N_PROJET, ecart)
        E = apres_impots(T["date"].values, x)
        avant = np.prod(1 + x) ** (1 / annees) - 1
        apres = E ** (1 / annees) - 1
        manque = [t for ok, t in ((dev["net"].mean() > 0 and td >= 2, "développement"), (val["net"].mean() > 0 and tv >= 2, "validation"),
                                  (pos_an >= 0.6, "années positives"), (n / semaines >= 2, "fréquence"), (d24 >= 0.95, "Deflated Sharpe"), (apres > 0, "après impôts")) if not ok]
        if num != 0 and not manque:
            passe.append(nom)
        lignes.append((x.mean(), num, nom, n, n / semaines, (x > 0).mean(), T["brut"].mean(), x.mean(), T["stress"].mean(), t_all, dev["net"].mean(), td, val["net"].mean(), tv,
                       pos_an, d24, d330, avant, apres, manque))
    lignes.sort(key=lambda z: -z[0])
    bh = P.h07.dropna()
    g = bh.iloc[-1] / bh.iloc[0] - 1
    bh_avant = (1 + g) ** (1 / annees) - 1
    bh_apres = (1 + g - IMPOT * max(g, 0)) ** (1 / annees) - 1
    txt = ["# 24 stratégies « sessions » sur 14 ans : résultats", "",
           "Règles : `regles/sessions_5m_v1.md`, figées avant le test, lancées **une seule fois**. Or au comptant 5 min du %s au %s ; développement 2012-2019, validation 2020-2026. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**" % (P.index[0].date(), P.index[-1].date()), "",
           "Un trade par jour au plus par stratégie. Frais de base 0,02 % l'aller-retour (stress 0,05 %). Rendements par trade en %, pour 1 fois le capital. « Après impôts » = 31,4 % des plus-values nettes annuelles, moins-values reportées.", "",
           "Référence **garder l'or** (07:00 UTC, de %s à %s) : %s par an avant impôts, %s par an après impôts (vente à la fin)." % (P.index[0].date(), P.index[-1].date(), br.pct(bh_avant), br.pct(bh_apres)), "",
           "| N° | Stratégie | Ordres | Par semaine | Gagnants | Brut moyen | Net moyen | Net stress | t | Dév. 2012-2019 (net / t) | Valid. 2020-2026 (net / t) | Années positives | Deflated Sharpe (24 / 330 essais) | Rdt annuel avant / après impôts |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for (_, num, nom, n, sem, win, brut, net, stress, t_all, dm, td, vm, tv, pa, d24, d330, av, ap, manque) in lignes:
        txt.append("| %d | %s | %d | %s | %s | %s | %s | %s | %s | %s / %s | %s / %s | %s | %s / %s | %s / %s |" % (
            num, nom, n, br.fr(sem, 1), br.pct(win, 0), br.pct(brut, 3), br.pct(net, 3), br.pct(stress, 3), br.fr(t_all, 1), br.pct(dm, 3), br.fr(td, 1), br.pct(vm, 3), br.fr(tv, 1),
            br.pct(pa, 0), br.fr(d24, 2), br.fr(d330, 2), br.pct(av), br.pct(ap)))
    pos_net = [l for l in lignes if l[1] != 0 and l[7] > 0]
    nb_t2 = [l for l in lignes if l[1] != 0 and l[9] >= 2]
    nb_val = [l for l in lignes if l[1] != 0 and l[7] > 0 and l[13] >= 2 and l[11] >= 2]
    txt += ["", "### Verdict", ""]
    if passe:
        txt.append("**Stratégies qui remplissent tous les critères : %s.** Elles ne sont que candidates au paper trading en direct, pas une preuve." % ", ".join(passe))
    else:
        txt.append("**Aucune des 24 stratégies ne remplit tous les critères.**")
    txt += ["", "- Gain net moyen positif : %d stratégies sur 24 ; avec t ≥ 2 sur toute la période : %d ; positives avec t ≥ 2 à la fois en développement et en validation : %d." % (len(pos_net), len(nb_t2), len(nb_val)),
            "- Avec 24 essais, environ 1 stratégie atteint t ≥ 2 par pur hasard ; le témoin hasard donne un gain net moyen de %s." % br.pct([l for l in lignes if l[1] == 0][0][7], 3), "",
            "Critères non remplis, stratégie par stratégie (les 8 meilleures par gain net moyen) :", ""]
    for l in [l for l in lignes if l[1] != 0][:8]:
        txt.append("- %s : %s." % (l[2], ", ".join(l[-1]) if l[-1] else "tous remplis"))
    txt += ["", "## Limites", "",
            "- Heures UTC fixes : l'heure d'été décale les ouvertures de Londres et de New York d'une heure, ce qui brouille les fenêtres. Ouvertures de barres 5 min, pas de glissement ; frais estimés.",
            "- Impôts : hypothèse du prélèvement forfaitaire unique français de 31,4 % sur les plus-values de titres ; l'or physique, les CFD sur certains régimes ou un autre pays donnent d'autres résultats. Ce n'est pas un conseil fiscal.",
            "- Environ 330 essais ont été faits dans ce projet ; le Deflated Sharpe à 330 essais est donné par honnêteté."]
    out = br.RACINE / "resultats" / "sessions_v1.md"
    out.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))


if __name__ == "__main__":
    rapport()
