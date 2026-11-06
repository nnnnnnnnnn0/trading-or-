"""Stratégies intraday (achat ET vente) sur l'or, bougies 1 h GC=F (juin 2024 à aujourd'hui).

Règles figées avant le test : 15 stratégies à paramètres standard + 24 heures de la journée = 39 essais comptés.
Positions seulement de 7 h à 20 h UTC, toujours à plat à 20 h UTC (pas de nuit, pas de financement).
Frais 0,025 % par changement de position (0,05 % l'aller-retour) ; test avec frais doublés.
Développement = 60 % anciens ; contrôle = 40 % récents, ouvert une seule fois.
Test de hasard : on tire au sort le sens de chaque ordre (achat / vente), le moment restant le même."""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_indicateurs as bi  # noqa: E402
from backtest_indicateurs import atr, fr, nw, nz, rsi  # noqa: E402

RACINE = bi.RACINE
SORTIE = RACINE / "resultats" / "intraday_v1.md"
FC = 0.00025
H0, H1 = 7, 19  # on décide à la clôture des bougies H0..H1-1 ; à plat à la clôture de la bougie H1


def charger():
    d = pd.read_csv(RACINE / "data" / "or_ohlc_1h.csv")
    d["t"] = pd.to_datetime(d["date_utc"], utc=True)
    d = d.drop_duplicates("t", keep="last").set_index("t").sort_index()
    d = d[~((d["open"] == d["high"]) & (d["high"] == d["low"]) & (d["low"] == d["close"]))]
    return d.iloc[:-1]  # dernière bougie en cours


def preparer(d):
    t = d.index
    n = len(d)
    heure, jour = t.hour.values, t.normalize().values
    suiv_ok = np.zeros(n, bool)
    suiv_ok[:-1] = (t[1:] - t[:-1]) == pd.Timedelta(hours=1)
    return n, heure, jour, suiv_ok


def boucle(n, heure, jour, suiv_ok, decide):
    """decide(t, etat) -> nouvelle position (+1/-1/0) à la clôture de la bougie t (seulement dans la session)."""
    pos = np.zeros(n)
    p, etat, jour_courant = 0, {}, None
    for t in range(n):
        if jour[t] != jour_courant:
            jour_courant, p, etat = jour[t], 0, {"entrees": 0}
        if H0 <= heure[t] < H1 and suiv_ok[t]:
            p = decide(t, p, etat)
        else:
            p = 0
        pos[t] = p
    return pos


def strategies(d, n, heure, jour, suiv_ok):
    c, h, l, o = d["close"], d["high"], d["low"], d["open"]
    cv, hv, lv, ov = c.values, h.values, l.values, o.values
    S = {}
    ser = pd.Series(np.arange(n), index=d.index)
    # niveaux de séance
    asie_h, asie_l, ny_h, ny_l, veille_h, veille_l, veille_c = (np.full(n, np.nan) for _ in range(7))
    df = pd.DataFrame({"j": jour, "h": hv, "l": lv, "c": cv, "hr": heure})
    jours = list(dict.fromkeys(jour))
    prev = None
    for j in jours:
        idx = np.where(jour == j)[0]
        sub = df.iloc[idx]
        a = sub[sub["hr"] < H0]
        if len(a):
            asie_h[idx], asie_l[idx] = a["h"].max(), a["l"].min()
        nyb = sub[sub["hr"] == 13]
        if len(nyb):
            ny_h[idx], ny_l[idx] = nyb["h"].iloc[0], nyb["l"].iloc[0]
        if prev is not None:
            veille_h[idx], veille_l[idx], veille_c[idx] = prev
        prev = (sub["h"].max(), sub["l"].min(), sub["c"].iloc[-1])

    def cassure(hh, ll, h_min):
        def f(t, p, e):
            if np.isnan(hh[t]) or heure[t] < h_min:
                return p
            mid = (hh[t] + ll[t]) / 2
            if p == 0 and e["entrees"] == 0:
                if cv[t] > hh[t]:
                    e["entrees"] = 1
                    return 1
                if cv[t] < ll[t]:
                    e["entrees"] = 1
                    return -1
            if p > 0 and cv[t] < mid:
                return 0
            if p < 0 and cv[t] > mid:
                return 0
            return p
        return f
    S["Cassure de la plage asiatique (0-7 h UTC)"] = boucle(n, heure, jour, suiv_ok, cassure(asie_h, asie_l, H0))
    S["Cassure de la première heure américaine (13 h UTC)"] = boucle(n, heure, jour, suiv_ok, cassure(ny_h, ny_l, 14))
    S["Cassure du plus haut / plus bas de la veille"] = boucle(n, heure, jour, suiv_ok, cassure(veille_h, veille_l, H0))

    def etat_machine(el, sl, es, ss):
        def f(t, p, e):
            if p == 0:
                if el(t):
                    return 1
                if es(t):
                    return -1
            elif p > 0 and sl(t):
                return -1 if es(t) else 0
            elif p < 0 and ss(t):
                return 1 if el(t) else 0
            return p
        return f
    r14, ok14 = rsi(c, 14).values, rsi(c, 14).notna().values
    S["RSI 14 1 h, retour à la moyenne (30/70)"] = boucle(n, heure, jour, suiv_ok, etat_machine(
        lambda t: ok14[t] and r14[t] < 30, lambda t: r14[t] > 50, lambda t: ok14[t] and r14[t] > 70, lambda t: r14[t] < 50))
    mid, sd = c.rolling(20).mean(), c.rolling(20).std()
    up, lo, mm, okb = nz(mid + 2 * sd), nz(mid - 2 * sd), nz(mid), mid.notna().values
    S["Bollinger 20-2 1 h, retour à la moyenne"] = boucle(n, heure, jour, suiv_ok, etat_machine(
        lambda t: okb[t] and cv[t] < lo[t], lambda t: cv[t] >= mm[t], lambda t: okb[t] and cv[t] > up[t], lambda t: cv[t] <= mm[t]))
    S["Bollinger 20-2 1 h, cassure"] = boucle(n, heure, jour, suiv_ok, etat_machine(
        lambda t: okb[t] and cv[t] > up[t], lambda t: cv[t] < mm[t], lambda t: okb[t] and cv[t] < lo[t], lambda t: cv[t] > mm[t]))
    e20, e50 = nz(c.ewm(span=20, adjust=False).mean()), nz(c.ewm(span=50, adjust=False).mean())
    S["Moyennes EMA 20 / 50 (1 h)"] = boucle(n, heure, jour, suiv_ok, lambda t, p, e: 0 if t < 60 else (1 if e20[t] > e50[t] else -1))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sg = nz(macd.ewm(span=9, adjust=False).mean())
    mc = nz(macd)
    S["MACD 12-26-9 (1 h)"] = boucle(n, heure, jour, suiv_ok, lambda t, p, e: 0 if t < 40 else (1 if mc[t] > sg[t] else -1))
    lo14, hi14 = l.rolling(14).min(), h.rolling(14).max()
    k = (100 * (c - lo14) / (hi14 - lo14)).rolling(3).mean()
    dd = k.rolling(3).mean()
    kk, dv, kok = nz(k), nz(dd), dd.notna().values
    S["Stochastique 14-3-3 (1 h)"] = boucle(n, heure, jour, suiv_ok, etat_machine(
        lambda t: t > 0 and kok[t] and kk[t] < 20 and kk[t] > dv[t] and kk[t - 1] <= dv[t - 1], lambda t: kk[t] > 80,
        lambda t: t > 0 and kok[t] and kk[t] > 80 and kk[t] < dv[t] and kk[t - 1] >= dv[t - 1], lambda t: kk[t] < 20))
    hh24, ll24 = nz(h.shift(1).rolling(24).max()), nz(l.shift(1).rolling(24).min())
    hh12, ll12 = nz(h.shift(1).rolling(12).max()), nz(l.shift(1).rolling(12).min())
    okd = h.shift(1).rolling(24).max().notna().values
    S["Donchian 24 h / sortie 12 h"] = boucle(n, heure, jour, suiv_ok, etat_machine(
        lambda t: okd[t] and cv[t] > hh24[t], lambda t: cv[t] < ll12[t], lambda t: okd[t] and cv[t] < ll24[t], lambda t: cv[t] > hh12[t]))
    a10 = atr(h, l, c, 10).values
    hl2 = ((h + l) / 2).values
    bu, bl = hl2 + 3 * a10, hl2 - 3 * a10
    fu, fl, st, tr = bu.copy(), bl.copy(), np.zeros(n), 1
    for t in range(1, n):
        fu[t] = bu[t] if (bu[t] < fu[t - 1] or cv[t - 1] > fu[t - 1]) else fu[t - 1]
        fl[t] = bl[t] if (bl[t] > fl[t - 1] or cv[t - 1] < fl[t - 1]) else fl[t - 1]
        if tr == 1 and cv[t] < fl[t]:
            tr = -1
        elif tr == -1 and cv[t] > fu[t]:
            tr = 1
        st[t] = tr
    S["SuperTrend 10-3 (1 h)"] = boucle(n, heure, jour, suiv_ok, lambda t, p, e: 0 if t < 15 else int(st[t]))
    tk = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kj = (h.rolling(26).max() + l.rolling(26).min()) / 2
    sa = ((tk + kj) / 2).shift(26)
    sb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    top, bot = nz(pd.concat([sa, sb], axis=1).max(axis=1)), nz(pd.concat([sa, sb], axis=1).min(axis=1))
    oki = (sa.notna() & sb.notna()).values
    S["Ichimoku 1 h (cours / nuage)"] = boucle(n, heure, jour, suiv_ok, lambda t, p, e: 0 if not oki[t] else (1 if cv[t] > top[t] else -1 if cv[t] < bot[t] else 0))
    S["Momentum 6 h"] = boucle(n, heure, jour, suiv_ok, lambda t, p, e: 0 if t < 6 else int(np.sign(cv[t] - cv[t - 6])))
    S["Direction de la première heure de Londres (7 h UTC)"] = boucle(n, heure, jour, suiv_ok, lambda t, p, e: (
        int(np.sign(cv[t] - ov[t])) if heure[t] == 7 else p))
    return S


def episodes(pos, ret, a, b, mult=1.0):
    """Liste (brut, coût) par ordre : suite continue de bougies tenues dans le même sens."""
    brut, cout, jours = [], [], []
    i = a
    while i < b:
        if pos[i] == 0:
            i += 1
            continue
        s, j = pos[i], i
        g = 0.0
        while j < b and pos[j] == s:
            g += s * ret[j]
            j += 1
        brut.append(g)
        cout.append(2 * FC * mult)
        jours.append(i)
        i = j
    return np.array(brut), np.array(cout), jours


def jour_pnl(pos, ret, a, b, jour, mult=1.0):
    p = pos[a:b]
    prev = np.concatenate([[0], p[:-1]])
    x = p * ret[a:b] - np.abs(p - prev) * FC * mult
    return pd.Series(x).groupby(jour[a:b]).sum().values


def evaluer(pos, ret, a, b, jour, rng):
    g, c, _ = episodes(pos, ret, a, b)
    if len(g) < 5:
        return None
    net = g - c
    _, c2, _ = episodes(pos, ret, a, b, 2.0)
    pj = jour_pnl(pos, ret, a, b, jour)
    sh = pj.mean() / pj.std() * math.sqrt(252) if pj.std() > 0 else 0.0
    cnt = 0
    m0 = net.mean()
    for _ in range(1000):
        s = rng.choice([-1, 1], size=len(g))
        if (s * g - c).mean() >= m0:
            cnt += 1
    return {"n": len(g), "taux": (net > 0).mean(), "moy": m0 * 100, "moy2": (g - c2).mean() * 100, "t": nw(pj), "sh": sh, "p": cnt / 1000,
            "dd": (np.cumsum(pj) - np.maximum.accumulate(np.cumsum(pj))).min() * 100}


def main():
    d = charger()
    n, heure, jour, suiv_ok = preparer(d)
    ret = np.zeros(n)
    cv = d["close"].values
    ret[:-1] = np.where(suiv_ok[:-1], cv[1:] / cv[:-1] - 1, 0)
    S = strategies(d, n, heure, jour, suiv_ok)
    deb = 60
    coupe = int(deb + (n - deb) * 0.6)
    rng = np.random.default_rng(2026)
    lignes, probables, proches = [], [], []
    for nom, pos in S.items():
        for mode, p in (("achat + vente", pos), ("achat seulement", np.clip(pos, 0, None)), ("vente seulement", np.clip(pos, None, 0))):
            ed, ec = evaluer(p, ret, deb, coupe, jour, rng), evaluer(p, ret, coupe, n - 1, jour, rng)
            if ed is None or ec is None:
                continue
            ok = ec["n"] >= 30 and ed["moy"] > 0 and ec["moy"] > 0 and ec["moy2"] > 0 and ec["t"] >= 2 and ec["p"] <= 0.01
            proche = ec["n"] >= 30 and ed["moy"] > 0 and ec["moy"] > 0 and ec["p"] <= 0.05
            v = "Candidat" if ok else "À surveiller" if proche else "Rejeté"
            if mode == "achat + vente":
                essai = True
            if ok and mode == "achat + vente":
                probables.append(nom)
            elif proche and mode == "achat + vente":
                proches.append(nom)
            lignes.append("| %s | %s | %d | %s %% | %s %% | %s | %s | %s %% | %s | %s %% | %s |" % (
                nom, mode, ec["n"], fr(ed["moy"], 3), fr(ec["moy"], 3), fr(ec["t"], 1), fr(ec["p"] * 100, 0) + " %", fr(ec["taux"] * 100, 0),
                fr(ec["sh"]), fr(ec["moy2"], 3), v))
    # heures de la journée
    ph = {}
    for hr in range(24):
        m = (heure == hr) & suiv_ok
        idx = np.where(m)[0]
        r = ret[idx] * 100
        dev, ctl = r[idx < coupe], r[idx >= coupe]
        if len(dev) > 30 and len(ctl) > 30:
            ph[hr] = (dev.mean(), dev.mean() / (dev.std() / math.sqrt(len(dev))), ctl.mean(), ctl.mean() / (ctl.std() / math.sqrt(len(ctl))))
    meil = sorted(ph.items(), key=lambda z: -abs(z[1][1]))[:5]
    t0, t1 = d.index[0].date(), d.index[-1].date()
    texte = ["# Stratégies intraday de l'or, achat et vente (v1)", "",
             "Données : %d bougies 1 h (%s à %s), futures GC=F. Développement : jusqu'au %s. Contrôle (ouvert une seule fois) : du %s à %s." % (
                 n, t0, t1, d.index[coupe - 1].date(), d.index[coupe].date(), t1),
             "", "**39 essais comptés** (15 stratégies, 24 heures). Aucun réglage : valeurs standard. À plat chaque soir (20 h UTC), jamais de nuit.",
             "", "**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
             "**Attention : seulement 2,4 ans de données horaires** (l'historique 5 min plus long est encore en cours de téléchargement). Tout résultat ici est une hypothèse à confirmer, pas une preuve.", "",
             "Critères de « candidat » (mode achat + vente) : au moins 30 ordres en contrôle, rendement moyen par ordre positif en développement et en contrôle, aussi avec frais doublés, t ≥ 2, au plus 1 % de hasard (sens des ordres tiré au sort).", "",
             "| Stratégie | Mode | Ordres (contrôle) | Rendement moyen par ordre, développement | Rendement moyen par ordre, contrôle | t contrôle | Hasard | Réussite contrôle | Sharpe contrôle | Rendement moyen, frais ×2 | Verdict |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"] + lignes + [
             "", "## Heures de la journée (rendement moyen d'une bougie 1 h, en %, UTC)", "",
             "| Heure UTC | Développement | t | Contrôle | t |", "| --- | --- | --- | --- | --- |"] + [
             "| %d h | %s | %s | %s | %s |" % (hr, fr(v[0], 3), fr(v[1], 1), fr(v[2], 3), fr(v[3], 1)) for hr, v in meil] + ["",
             "Les heures les plus marquées en développement sont à comparer au contrôle : un effet réel garde le même sens. Un effet d'une heure (quelques millièmes de %) reste inférieur aux frais d'un aller-retour (0,05 %).", "",
             "## Conclusion", ""]
    texte.append("**Candidats (achat + vente)** : " + "; ".join(probables) + "." if probables else "**Aucune stratégie intraday n'est retenue comme candidate.**")
    if proches:
        texte.append("\nÀ surveiller (au plus 5 % de hasard, mais pas assez nets) : " + "; ".join(proches) + ".")
    texte += ["", "## Limites", "",
              "- 2,4 ans seulement : une seule configuration de marché (hausse forte de l'or). Résultats fragiles.",
              "- Exécution à la clôture de la bougie du signal, frais estimés 0,05 % l'aller-retour, pas d'écart de prix réel de courtier, pas de dérapage (slippage).",
              "- Futures GC=F, pas l'or au comptant ; heures UTC, donc la relation avec l'ouverture de Londres ou de New York change avec l'heure d'été.",
              "- 39 essais : avec un seuil à 5 %, environ 2 paraissent bons par hasard. Une confirmation en paper trading reste nécessaire."]
    SORTIE.write_text("\n".join(texte) + "\n", encoding="utf-8")
    print("\n".join(texte))


if __name__ == "__main__":
    main()
