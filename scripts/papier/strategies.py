"""Les 28 stratégies (+ témoin) du paper trading 5 min. Règles : regles/papier_5m_v1.md (figées).

Chaque fonction reçoit le DataFrame (index UTC, colonnes open, high, low, close, volume) et retourne deux séries booléennes
(achat, vente) évaluées à la CLÔTURE de chaque barre. L'entrée a lieu à l'ouverture de la barre suivante (voir moteur.py).
"""
import numpy as np
import pandas as pd

from indicateurs import (adx_di, aroon, atr, cci, croise_bas, croise_haut, ema, front, heikin_ashi, mfi, rsi, sar, sma,
                         supertrend)

TENDANCE, RETOUR = "tendance", "retour"


def _min_jour(df):
    return df.index.hour * 60 + df.index.minute


def _jour(df):
    return pd.Series(df.index.normalize(), index=df.index)


def _niveaux_veille(df):
    """Plus haut, plus bas, clôture de la journée UTC précédente (jour complet, donc connu)."""
    j = df.index.normalize()
    g = df.groupby(j).agg(h=("high", "max"), l=("low", "min"), c=("close", "last"))
    prec = g.shift()
    # les jours sans séance (week-end) : la « veille » est le dernier jour de bourse précédent
    prec = prec.where(prec.notna(), np.nan).ffill()
    m = prec.reindex(j)
    return (pd.Series(m["h"].values, index=df.index), pd.Series(m["l"].values, index=df.index), pd.Series(m["c"].values, index=df.index))


def _ouverture(df, debut, fin_range, fin_trade):
    """Plus haut / bas de la fenêtre [debut, fin_range[ (minutes UTC), connus seulement après fin_range ; actif jusqu'à fin_trade."""
    m = _min_jour(df)
    dans = pd.Series((m >= debut) & (m < fin_range), index=df.index)
    j = _jour(df)
    oh = df["high"].where(dans).groupby(j).cummax().groupby(j).ffill()
    ol = df["low"].where(dans).groupby(j).cummin().groupby(j).ffill()
    actif = pd.Series((m >= fin_range) & (m < fin_trade), index=df.index)
    return oh, ol, actif


def s_ema_9_21(df):
    a, b = ema(df.close, 9), ema(df.close, 21)
    return croise_haut(a, b), croise_bas(a, b)


def s_repli_ema50(df):
    c, e50, e200 = df.close, ema(df.close, 50), ema(df.close, 200)
    return croise_haut(c, e50) & (e50 > e200), croise_bas(c, e50) & (e50 < e200)


def s_macd(df):
    m = ema(df.close, 12) - ema(df.close, 26)
    h = m - ema(m, 9)
    return croise_haut(h, 0.0), croise_bas(h, 0.0)


def s_supertrend(df):
    st = supertrend(df.high, df.low, df.close, 10, 3.0)
    return (st > 0) & (st.shift() < 0), (st < 0) & (st.shift() > 0)


def s_donchian48(df):
    hh, ll = df.high.rolling(48).max().shift(), df.low.rolling(48).min().shift()
    return front(df.close > hh), front(df.close < ll)


def s_ichimoku(df):
    h, l, c = df.high, df.low, df.close
    tk = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kj = (h.rolling(26).max() + l.rolling(26).min()) / 2
    a = ((tk + kj) / 2).shift(26)
    b = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    haut, bas = pd.concat([a, b], axis=1).max(axis=1), pd.concat([a, b], axis=1).min(axis=1)
    return front((c > haut) & haut.notna()), front((c < bas) & bas.notna())


def s_adx_di(df):
    p, m, adx = adx_di(df.high, df.low, df.close, 14)
    return croise_haut(p, m) & (adx > 25), croise_bas(p, m) & (adx > 25)


def s_sar(df):
    s = sar(df.high, df.low)
    return (s > 0) & (s.shift() < 0), (s < 0) & (s.shift() > 0)


def s_heikin(df):
    hao, hac = heikin_ashi(df.open, df.high, df.low, df.close)
    haus, bas = hac > hao, hac < hao
    return haus & haus.shift(fill_value=False) & bas.shift(2, fill_value=False), bas & bas.shift(fill_value=False) & haus.shift(2, fill_value=False)


def s_aroon(df):
    up, dn = aroon(df.high, df.low, 25)
    return croise_haut(up, dn), croise_bas(up, dn)


def s_orb_londres(df):
    oh, ol, actif = _ouverture(df, 7 * 60, 7 * 60 + 30, 11 * 60)
    return front((df.close > oh) & actif), front((df.close < ol) & actif)


def s_orb_ny(df):
    oh, ol, actif = _ouverture(df, 13 * 60 + 30, 14 * 60, 17 * 60)
    return front((df.close > oh) & actif), front((df.close < ol) & actif)


def s_cassure_veille(df):
    pdh, pdl, _ = _niveaux_veille(df)
    m = _min_jour(df)
    fenetre = pd.Series((m >= 7 * 60) & (m < 17 * 60), index=df.index)
    return front((df.close > pdh) & fenetre), front((df.close < pdl) & fenetre)


def s_keltner(df):
    mid, a = ema(df.close, 20), atr(df.high, df.low, df.close, 10)
    return front(df.close > mid + 2 * a), front(df.close < mid - 2 * a)


def s_squeeze(df):
    c = df.close
    m, sd = c.rolling(20).mean(), c.rolling(20).std()
    largeur = 4 * sd / m
    serre = (largeur <= 1.25 * largeur.rolling(100).min()).rolling(3).max().fillna(0) > 0
    return front((c > m + 2 * sd) & serre), front((c < m - 2 * sd) & serre)


def s_roc12(df):
    roc = df.close / df.close.shift(12) - 1
    return croise_haut(roc, 0.001), croise_bas(roc, -0.001)


def s_cassure_volume(df):
    hh, ll = df.high.rolling(20).max().shift(), df.low.rolling(20).min().shift()
    fort = df.volume > 1.5 * df.volume.rolling(20).mean()
    return front((df.close > hh) & fort), front((df.close < ll) & fort)


def s_rsi14(df):
    r = rsi(df.close, 14)
    return croise_haut(r, 30.0), croise_bas(r, 70.0)


def s_rsi2(df):
    r, e = rsi(df.close, 2), ema(df.close, 200)
    return front((r < 10) & (df.close > e)), front((r > 90) & (df.close < e))


def s_bollinger_retour(df):
    c = df.close
    m, sd = c.rolling(20).mean(), c.rolling(20).std()
    hi, lo = m + 2 * sd, m - 2 * sd
    return (c.shift() < lo.shift()) & (c > lo), (c.shift() > hi.shift()) & (c < hi)


def s_stochastique(df):
    bas, haut = df.low.rolling(14).min(), df.high.rolling(14).max()
    k = (100 * (df.close - bas) / (haut - bas)).rolling(3).mean()
    d = k.rolling(3).mean()
    return croise_haut(k, d) & (k < 20), croise_bas(k, d) & (k > 80)


def s_cci20(df):
    x = cci(df.high, df.low, df.close, 20)
    return croise_haut(x, -100.0), croise_bas(x, 100.0)


def s_williams(df):
    bas, haut = df.low.rolling(14).min(), df.high.rolling(14).max()
    w = -100 * (haut - df.close) / (haut - bas)
    return croise_haut(w, -80.0), croise_bas(w, -20.0)


def s_vwap(df):
    j = _jour(df)
    tp = (df.high + df.low + df.close) / 3
    vwap = (tp * df.volume).groupby(j).cumsum() / df.volume.groupby(j).cumsum()
    dev = df.close - vwap
    sd = dev.rolling(48).std()
    return front(dev < -2 * sd), front(dev > 2 * sd)


def s_zscore50(df):
    c = df.close
    z = (c - c.rolling(50).mean()) / c.rolling(50).std()
    return front(z < -2), front(z > 2)


def s_mfi14(df):
    x = mfi(df.high, df.low, df.close, df.volume, 14)
    return croise_haut(x, 20.0), croise_bas(x, 80.0)


def s_avalement(df):
    o, h, l, c = df.open, df.high, df.low, df.close
    haussier = (c.shift() < o.shift()) & (c > o) & (c >= o.shift()) & (o <= c.shift()) & (l <= l.rolling(20).min().shift())
    baissier = (c.shift() > o.shift()) & (c < o) & (c <= o.shift()) & (o >= c.shift()) & (h >= h.rolling(20).max().shift())
    return haussier, baissier


def s_pivots(df):
    pdh, pdl, pdc = _niveaux_veille(df)
    p = (pdh + pdl + pdc) / 3
    r1, s1 = 2 * p - pdl, 2 * p - pdh
    m = _min_jour(df)
    fenetre = pd.Series((m >= 7 * 60) & (m < 17 * 60), index=df.index)
    return front((df.low <= s1) & (df.close > s1) & fenetre), front((df.high >= r1) & (df.close < r1) & fenetre)


def s_hasard(df):
    """Témoin : tirage fixé par l'horodatage (donc identique à chaque exécution)."""
    t = ((df.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(seconds=1)).values.astype(np.uint64)
    x = (t * np.uint64(11400714819323198485)) >> np.uint64(40)
    u = (x % np.uint64(1000)).astype(float) / 1000.0
    y = ((x >> np.uint64(10)) % np.uint64(2)).astype(int)
    fire = u < 1 / 60
    return pd.Series(fire & (y == 1), index=df.index), pd.Series(fire & (y == 0), index=df.index)


# (numéro, nom, famille, fonction, indicateur)
STRATEGIES = [
    (1, "EMA 9/21", TENDANCE, s_ema_9_21), (2, "Repli sur EMA 50", TENDANCE, s_repli_ema50), (3, "MACD 12-26-9", TENDANCE, s_macd),
    (4, "Supertrend 10x3", TENDANCE, s_supertrend), (5, "Donchian 48", TENDANCE, s_donchian48), (6, "Ichimoku nuage", TENDANCE, s_ichimoku),
    (7, "ADX/DI 14", TENDANCE, s_adx_di), (8, "Parabolic SAR", TENDANCE, s_sar), (9, "Heikin-Ashi", TENDANCE, s_heikin),
    (10, "Aroon 25", TENDANCE, s_aroon), (11, "Cassure ouverture Londres", TENDANCE, s_orb_londres),
    (12, "Cassure ouverture New York", TENDANCE, s_orb_ny), (13, "Cassure de la veille", TENDANCE, s_cassure_veille),
    (14, "Keltner 20x2", TENDANCE, s_keltner), (15, "Compression Bollinger", TENDANCE, s_squeeze), (16, "Momentum ROC 12", TENDANCE, s_roc12),
    (17, "Cassure avec volume", TENDANCE, s_cassure_volume),
    (18, "RSI 14", RETOUR, s_rsi14), (19, "RSI 2 Connors", RETOUR, s_rsi2), (20, "Retour Bollinger", RETOUR, s_bollinger_retour),
    (21, "Stochastique 14-3-3", RETOUR, s_stochastique), (22, "CCI 20", RETOUR, s_cci20), (23, "Williams %R 14", RETOUR, s_williams),
    (24, "VWAP 2 écarts-types", RETOUR, s_vwap), (25, "Z-score 50", RETOUR, s_zscore50), (26, "MFI 14", RETOUR, s_mfi14),
    (27, "Avalement", RETOUR, s_avalement), (28, "Pivots de la veille", RETOUR, s_pivots),
    (0, "Témoin hasard", TENDANCE, s_hasard),
]
