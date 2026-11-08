"""Indicateurs techniques sur barres 5 min (pandas). Tous n'utilisent que le passé."""
import numpy as np
import pandas as pd


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def sma(s, n):
    return s.rolling(n).mean()


def vraie_amplitude(h, l, c):
    cp = c.shift()
    return pd.concat([h - l, (h - cp).abs(), (l - cp).abs()], axis=1).max(axis=1)


def atr(h, l, c, n=14):
    return vraie_amplitude(h, l, c).rolling(n).mean()


def rsi(c, n):
    d = c.diff()
    haut = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    bas = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + haut / bas)


def croise_haut(a, b):
    b = b if isinstance(b, pd.Series) else pd.Series(b, index=a.index)
    return (a > b) & (a.shift() <= b.shift())


def croise_bas(a, b):
    b = b if isinstance(b, pd.Series) else pd.Series(b, index=a.index)
    return (a < b) & (a.shift() >= b.shift())


def front(cond):
    """Vrai seulement à la barre où la condition devient vraie."""
    cond = cond.fillna(False).astype(bool)
    return cond & ~cond.shift(fill_value=False)


def supertrend(h, l, c, n=10, mult=3.0):
    """Retourne +1 (haussier) / -1 (baissier) pour chaque barre."""
    a = atr(h, l, c, n).values
    hl2 = ((h + l) / 2).values
    cv = c.values
    hb, lb = hl2 + mult * a, hl2 - mult * a
    N = len(cv)
    fh, fl, sens = np.full(N, np.nan), np.full(N, np.nan), np.zeros(N)
    for i in range(N):
        if np.isnan(a[i]):
            continue
        if i == 0 or np.isnan(fh[i - 1]):
            fh[i], fl[i], sens[i] = hb[i], lb[i], 1
            continue
        fh[i] = hb[i] if (hb[i] < fh[i - 1] or cv[i - 1] > fh[i - 1]) else fh[i - 1]
        fl[i] = lb[i] if (lb[i] > fl[i - 1] or cv[i - 1] < fl[i - 1]) else fl[i - 1]
        if sens[i - 1] <= 0 and cv[i] > fh[i - 1]:
            sens[i] = 1
        elif sens[i - 1] >= 0 and cv[i] < fl[i - 1]:
            sens[i] = -1
        else:
            sens[i] = sens[i - 1] if sens[i - 1] != 0 else 1
    return pd.Series(sens, index=c.index)


def sar(h, l, pas=0.02, maxi=0.2):
    """Parabolic SAR : retourne +1 / -1 (sens de la tendance)."""
    hv, lv = h.values, l.values
    N = len(hv)
    sens = np.zeros(N)
    if N < 2:
        return pd.Series(sens, index=h.index)
    haussier, af, ep, sr = True, pas, hv[0], lv[0]
    sens[0] = 1
    for i in range(1, N):
        sr = sr + af * (ep - sr)
        if haussier:
            sr = min(sr, lv[i - 1], lv[i - 2] if i > 1 else lv[i - 1])
            if lv[i] < sr:
                haussier, sr, ep, af = False, ep, lv[i], pas
            elif hv[i] > ep:
                ep, af = hv[i], min(af + pas, maxi)
        else:
            sr = max(sr, hv[i - 1], hv[i - 2] if i > 1 else hv[i - 1])
            if hv[i] > sr:
                haussier, sr, ep, af = True, ep, hv[i], pas
            elif lv[i] < ep:
                ep, af = lv[i], min(af + pas, maxi)
        sens[i] = 1 if haussier else -1
    return pd.Series(sens, index=h.index)


def heikin_ashi(o, h, l, c):
    hac = (o + h + l + c) / 4
    hao = np.zeros(len(c))
    ov, cv = o.values, hac.values
    if len(ov):
        hao[0] = (ov[0] + c.values[0]) / 2
    for i in range(1, len(ov)):
        hao[i] = (hao[i - 1] + cv[i - 1]) / 2
    return pd.Series(hao, index=c.index), hac


def adx_di(h, l, c, n=14):
    haut, bas = h.diff(), -l.diff()
    plus = pd.Series(np.where((haut > bas) & (haut > 0), haut, 0.0), index=c.index)
    moins = pd.Series(np.where((bas > haut) & (bas > 0), bas, 0.0), index=c.index)
    tr = vraie_amplitude(h, l, c)
    a = tr.ewm(alpha=1 / n, adjust=False).mean()
    pdi = 100 * plus.ewm(alpha=1 / n, adjust=False).mean() / a
    mdi = 100 * moins.ewm(alpha=1 / n, adjust=False).mean() / a
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi)
    return pdi, mdi, dx.ewm(alpha=1 / n, adjust=False).mean()


def aroon(h, l, n=25):
    haut = h.rolling(n + 1).apply(lambda x: n - np.argmax(x[::-1]), raw=True)
    bas = l.rolling(n + 1).apply(lambda x: n - np.argmin(x[::-1]), raw=True)
    return 100 * (n - haut) / n, 100 * (n - bas) / n


def cci(h, l, c, n=20):
    tp = (h + l + c) / 3
    m = tp.rolling(n).mean()
    dm = tp.rolling(n).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return (tp - m) / (0.015 * dm)


def mfi(h, l, c, v, n=14):
    tp = (h + l + c) / 3
    flux = tp * v
    plus = flux.where(tp > tp.shift(), 0.0).rolling(n).sum()
    moins = flux.where(tp < tp.shift(), 0.0).rolling(n).sum()
    return 100 - 100 / (1 + plus / moins)
