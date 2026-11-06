"""Backtest d'indicateurs classiques sur l'or (journalier GC=F, 2006 à aujourd'hui).

Règles figées avant le test : 17 stratégies avec leurs paramètres standard (aucun réglage),
2 modes (achat seulement ; achat + vente) = 34 essais, tous comptés. Position prise à la clôture du jour du signal,
gain = clôture suivante. Frais 0,025 % par changement de position (0,05 % l'aller-retour).
Développement = 70 % anciens ; contrôle = 30 % récents."""
import datetime as dt
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "resultats" / "indicateurs_v1.md"
FRAIS_COTE = 0.00025


def charger():
    d = pd.read_csv(RACINE / "data" / "or_ohlc_jour.csv")
    d["date"] = pd.to_datetime(d["date_utc"].str[:10])
    d = d.drop_duplicates("date", keep="last").set_index("date")
    d = d[(d["close"] > 0) & (d["high"] > d["low"])]
    if d.index[-1].date() >= dt.datetime.now(dt.timezone.utc).date():
        d = d.iloc[:-1]
    return d


def rsi(c, n):
    d = c.diff()
    g = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    p = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + g / p)


def atr(h, l, c, n):
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def machine(n, entree_long, sortie_long, entree_court, sortie_court):
    """Position à états : les fonctions reçoivent l'indice t et disent si on entre / sort."""
    pos = np.zeros(n)
    p = 0
    for t in range(n):
        if p == 0:
            if entree_long(t):
                p = 1
            elif entree_court(t):
                p = -1
        elif p > 0 and sortie_long(t):
            p = 0
            if entree_court(t):
                p = -1
        elif p < 0 and sortie_court(t):
            p = 0
            if entree_long(t):
                p = 1
        pos[t] = p
    return pos


def nz(x):
    return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)


def strategies(d):
    c, h, l = d["close"], d["high"], d["low"]
    n = len(d)
    S = {}
    r14 = nz(rsi(c, 14)); r14ok = rsi(c, 14).notna().values
    S["RSI 14, retour à la moyenne (30/70)"] = machine(n, lambda t: r14ok[t] and r14[t] < 30, lambda t: r14[t] > 50,
                                                      lambda t: r14ok[t] and r14[t] > 70, lambda t: r14[t] < 50)
    r2 = nz(rsi(c, 2)); m200 = c.rolling(200).mean(); m5 = c.rolling(5).mean()
    c_, m200_, m5_ = c.values, nz(m200), nz(m5)
    ok200 = m200.notna().values
    S["RSI 2 de Connors + tendance MA200"] = machine(n, lambda t: ok200[t] and r2[t] < 10 and c_[t] > m200_[t], lambda t: c_[t] > m5_[t],
                                                    lambda t: ok200[t] and r2[t] > 90 and c_[t] < m200_[t], lambda t: c_[t] < m5_[t])
    e12, e26 = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    macd = e12 - e26
    sig = macd.ewm(span=9, adjust=False).mean()
    S["MACD 12-26-9 (croisement)"] = np.where(np.arange(n) < 35, 0, np.where(macd > sig, 1, -1)).astype(float)
    mid, sd = c.rolling(20).mean(), c.rolling(20).std()
    up, lo = nz(mid + 2 * sd), nz(mid - 2 * sd)
    mid_, okb = nz(mid), mid.notna().values
    S["Bollinger 20-2, retour à la moyenne"] = machine(n, lambda t: okb[t] and c_[t] < lo[t], lambda t: c_[t] >= mid_[t],
                                                       lambda t: okb[t] and c_[t] > up[t], lambda t: c_[t] <= mid_[t])
    S["Bollinger 20-2, cassure"] = machine(n, lambda t: okb[t] and c_[t] > up[t], lambda t: c_[t] < mid_[t],
                                           lambda t: okb[t] and c_[t] < lo[t], lambda t: c_[t] > mid_[t])
    lo14, hi14 = l.rolling(14).min(), h.rolling(14).max()
    k = (100 * (c - lo14) / (hi14 - lo14)).rolling(3).mean()
    dd = k.rolling(3).mean()
    kk, dv, kok = nz(k), nz(dd), dd.notna().values
    S["Stochastique 14-3-3 (zones 20/80)"] = machine(
        n, lambda t: t > 0 and kok[t] and kk[t] < 20 and kk[t] > dv[t] and kk[t - 1] <= dv[t - 1], lambda t: kk[t] > 80,
        lambda t: t > 0 and kok[t] and kk[t] > 80 and kk[t] < dv[t] and kk[t - 1] >= dv[t - 1], lambda t: kk[t] < 20)
    a10 = atr(h, l, c, 10).values
    hl2 = ((h + l) / 2).values
    bu, bl = hl2 + 3 * a10, hl2 - 3 * a10
    fu, fl, st = bu.copy(), bl.copy(), np.zeros(n)
    tr = 1
    for t in range(1, n):
        fu[t] = bu[t] if (bu[t] < fu[t - 1] or c_[t - 1] > fu[t - 1]) else fu[t - 1]
        fl[t] = bl[t] if (bl[t] > fl[t - 1] or c_[t - 1] < fl[t - 1]) else fl[t - 1]
        if tr == 1 and c_[t] < fl[t]:
            tr = -1
        elif tr == -1 and c_[t] > fu[t]:
            tr = 1
        st[t] = tr
    st[:15] = 0
    S["SuperTrend 10-3"] = st
    up_m, dn_m = h.diff(), -l.diff()
    a14 = atr(h, l, c, 14)
    pdi = 100 * pd.Series(np.where((up_m > dn_m) & (up_m > 0), up_m, 0), index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / a14
    mdi = 100 * pd.Series(np.where((dn_m > up_m) & (dn_m > 0), dn_m, 0), index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / a14
    adx = (100 * (pdi - mdi).abs() / (pdi + mdi)).ewm(alpha=1 / 14, adjust=False).mean()
    m20, m50 = c.rolling(20).mean(), c.rolling(50).mean()
    S["ADX 14 > 25 + sens MA20/MA50"] = np.where((adx > 25) & m50.notna(), np.sign(m20 - m50), 0).astype(float)
    m200s = c.rolling(200).mean()
    S["Croix dorée MA50 / MA200"] = np.where(m200s.notna(), np.sign(m50 - m200s), 0).astype(float)
    tk = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kj = (h.rolling(26).max() + l.rolling(26).min()) / 2
    sa = ((tk + kj) / 2).shift(26)
    sb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    hautn, bas_n = pd.concat([sa, sb], axis=1).max(axis=1), pd.concat([sa, sb], axis=1).min(axis=1)
    S["Ichimoku (cours / nuage)"] = np.where(sa.notna() & sb.notna(), np.where(c > hautn, 1, np.where(c < bas_n, -1, 0)), 0).astype(float)
    S["Momentum ROC 12 jours"] = np.where(c.shift(12).notna(), np.sign(c / c.shift(12) - 1), 0).astype(float)
    hh20, ll10 = h.shift(1).rolling(20).max().values, l.shift(1).rolling(10).min().values
    ll20, hh10 = l.shift(1).rolling(20).min().values, h.shift(1).rolling(10).max().values
    hh20, ll10, ll20, hh10 = nz(hh20), nz(ll10), nz(ll20), nz(hh10)
    okd = h.shift(1).rolling(20).max().notna().values
    S["Donchian 20 / sortie 10 (tortues)"] = machine(n, lambda t: okd[t] and c_[t] > hh20[t], lambda t: c_[t] < ll10[t],
                                                     lambda t: okd[t] and c_[t] < ll20[t], lambda t: c_[t] > hh10[t])
    tp = (h + l + c) / 3
    smatp = tp.rolling(20).mean()
    mad = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    cci = nz((tp - smatp) / (0.015 * mad)); cok = mad.notna().values
    S["CCI 20 (±100)"] = machine(n, lambda t: cok[t] and cci[t] > 100, lambda t: cci[t] < 0,
                                 lambda t: cok[t] and cci[t] < -100, lambda t: cci[t] > 0)
    wr = nz(-100 * (h.rolling(14).max() - c) / (h.rolling(14).max() - l.rolling(14).min())); wok = h.rolling(14).max().notna().values
    S["Williams %R 14, retour à la moyenne"] = machine(n, lambda t: wok[t] and wr[t] < -80, lambda t: wr[t] > -50,
                                                      lambda t: wok[t] and wr[t] > -20, lambda t: wr[t] < -50)
    ema20 = c.ewm(span=20, adjust=False).mean()
    a10s = atr(h, l, c, 10)
    ku, kl, e20 = nz(ema20 + 2 * a10s), nz(ema20 - 2 * a10s), nz(ema20)
    S["Canal de Keltner 20-10-2 (cassure)"] = machine(n, lambda t: t > 20 and c_[t] > ku[t], lambda t: c_[t] < e20[t],
                                                      lambda t: t > 20 and c_[t] < kl[t], lambda t: c_[t] > e20[t])
    hv, lv = h.values, l.values
    sar, ps = np.zeros(n), np.zeros(n)
    tend, af, ep, s0 = 1, 0.02, hv[0], lv[0]
    sar[0] = s0
    for t in range(1, n):
        s1 = sar[t - 1] + af * (ep - sar[t - 1])
        if tend == 1:
            s1 = min(s1, lv[t - 1], lv[t - 2] if t > 1 else lv[t - 1])
            if lv[t] < s1:
                tend, s1, ep, af = -1, ep, lv[t], 0.02
            elif hv[t] > ep:
                ep, af = hv[t], min(af + 0.02, 0.2)
        else:
            s1 = max(s1, hv[t - 1], hv[t - 2] if t > 1 else hv[t - 1])
            if hv[t] > s1:
                tend, s1, ep, af = 1, ep, hv[t], 0.02
            elif lv[t] < ep:
                ep, af = lv[t], min(af + 0.02, 0.2)
        sar[t], ps[t] = s1, tend
    ps[:5] = 0
    S["SAR parabolique 0,02-0,2"] = ps
    S["Momentum 12 mois (252 jours)"] = np.where(c.shift(252).notna(), np.sign(c / c.shift(252) - 1), 0).astype(float)
    return S


def perf(pos, ret, a, b):
    p, r = pos[a:b], ret[a:b]
    prev = np.concatenate([[pos[a - 1] if a > 0 else 0], p[:-1]])
    brut = prev * r
    cout = np.abs(p - prev) * FRAIS_COTE
    return brut - cout, brut - 2 * np.abs(p - prev) * FRAIS_COTE, prev


def nw(x, lag=5):
    n = len(x)
    m = x.mean()
    u = x - m
    s = u @ u / n
    for k in range(1, lag + 1):
        s += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return m / math.sqrt(s / n) if s > 0 else float("nan")


def sharpe(x):
    return x.mean() / x.std() * math.sqrt(252) if x.std() > 0 else 0.0


def dd_max(x):
    cum = np.cumsum(x)
    return (cum - np.maximum.accumulate(cum)).min() * 100


def p_decalage(pos, ret, a, b, vrai, rng, n=1000):
    L = b - a
    p = pos[a:b]
    r = ret[a:b]
    cnt = 0
    for _ in range(n):
        s = rng.integers(20, L - 20)
        q = np.roll(p, s)
        prev = np.concatenate([[q[-1]], q[:-1]])
        x = prev * r - np.abs(q - prev) * FRAIS_COTE
        if x.mean() >= vrai:
            cnt += 1
    return cnt / n


def fr(x, d=2):
    return ("{:." + str(d) + "f}").format(x).replace(".", ",")


def main():
    d = charger()
    ret = d["close"].pct_change().shift(-1).fillna(0).values.copy()  # gain du jour t -> t+1
    ret[-1] = 0
    n = len(d)
    deb = 260
    coupe = int(deb + (n - deb) * 0.7)
    S = strategies(d)
    rng = np.random.default_rng(2026)
    lignes, surveiller, probables = [], [], []
    bh_dev, bh_ctl = ret[deb:coupe], ret[coupe:n - 1]
    for nom, pos in S.items():
        for mode in ("achat + vente", "achat seulement"):
            p = pos.copy() if mode == "achat + vente" else np.clip(pos, 0, None)
            xd, xd2, _ = perf(p, ret, deb, coupe)
            xc, xc2, prev = perf(p, ret, coupe, n - 1)
            trades = int(((np.abs(np.diff(np.concatenate([[0], p[coupe:n - 1]]))) > 0) & (p[coupe:n - 1] != 0)).sum())
            t_c = nw(xc)
            pv = p_decalage(p, ret, coupe, n - 1, xc.mean(), rng)
            expo = (np.abs(prev) > 0).mean() * 100
            ok1 = xd.mean() > 0 and xc.mean() > 0 and xc2.mean() > 0
            if ok1 and t_c >= 2 and pv <= 0.01:
                v = "Avantage probable"
                probables.append("%s (%s)" % (nom, mode))
            elif ok1 and pv <= 0.05:
                v = "À surveiller"
                surveiller.append("%s (%s)" % (nom, mode))
            else:
                v = "Rejeté"
            lignes.append("| %s | %s | %s | %s %% | %s | %s | %s | %s | %s %% | %d | %s |" % (
                nom, mode, fr(sharpe(xd)), fr(xc.mean() * 252 * 100, 1), fr(sharpe(xc)), fr(t_c, 1), fr(pv * 100, 0) + " %",
                fr(sharpe(xc2)), fr(dd_max(xc), 0), trades, v))
    texte = ["# Backtest d'indicateurs sur l'or (v1)", "",
             "Données : %d jours (%s à %s), futures GC=F. Développement (70 %%) : %s à %s. Contrôle (30 %%) : %s à %s." % (
                 n, d.index[0].date(), d.index[-1].date(), d.index[deb].date(), d.index[coupe - 1].date(), d.index[coupe].date(), d.index[-1].date()),
             "", "**%d essais comptés** (17 stratégies, 2 modes). Aucun paramètre n'a été ajusté : valeurs standard." % len(lignes),
             "", "**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
             "Référence : garder l'or en contrôle = Sharpe %s, rendement annuel %s %%." % (fr(sharpe(bh_ctl)), fr(bh_ctl.mean() * 252 * 100, 1)), "",
             "## Résultats", "",
             "Sharpe = rendement / risque annualisé (au-dessus de 0,5 c'est bien, au-dessus de 1 c'est rare). « Hasard » = part de 1 000 décalages aléatoires de la même série de positions qui font au moins aussi bien : c'est le test qui neutralise la tendance haussière de l'or. Frais ×2 : Sharpe avec frais doublés.", "",
             "| Indicateur | Mode | Sharpe développement | Rendement annuel contrôle | Sharpe contrôle | t contrôle | Hasard | Sharpe contrôle, frais ×2 | Perte max contrôle | Entrées contrôle | Verdict |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"] + lignes + ["", "## Conclusion", ""]
    if probables:
        texte.append("Avantage probable (seuil strict : t ≥ 2, au plus 1 % de hasard, positif en développement et en contrôle, frais ×2) : " + "; ".join(probables) + ".")
    else:
        texte.append("**Aucune stratégie n'obtient « avantage probable ».**")
    if surveiller:
        texte.append("\nÀ surveiller (au plus 5 %% de hasard, mais %d essais : au moins 1 à 2 sont attendus par hasard) : %s." % (len(lignes), "; ".join(surveiller)))
    texte += ["", "## Limites", "",
              "- Signal et exécution à la même clôture : légèrement optimiste. Données journalières seulement.",
              "- Frais 0,05 % l'aller-retour, sans financement de nuit ni écart de prix réel.",
              "- Le mode « achat seulement » profite de la hausse de l'or sur la période : seul le test de hasard le corrige.",
              "- %d essais : avec un seuil à 5 %%, environ %d paraissent bons par chance." % (len(lignes), round(len(lignes) * 0.05)),
              "- Paramètres standard non optimisés : une version optimisée serait plus belle sur le passé et pire dans le futur."]
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text("\n".join(texte) + "\n", encoding="utf-8")
    print("\n".join(texte))


if __name__ == "__main__":
    main()
