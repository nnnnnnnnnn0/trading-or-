"""Recherche de récurrences sur l'or (données journalières GC=F, 2006 à aujourd'hui).

Méthode (fixée avant de regarder) :
- ~55 hypothèses x 2 horizons (1 jour, 3 jours) = ~110 essais, tous comptés.
- Exploration sur les 70 % anciens uniquement. Les 30 % récents restent fermés.
- Passage en contrôle seulement si |t| >= 2,5 en exploration (t corrigé de l'autocorrélation).
- Verdict final sur le contrôle : même sens, |t| >= 2 (p < 5 %), sens stable dans au moins 65 % des années,
  gain moyen > frais (0,05 %). Les essais multiples sont rappelés : le seuil de Bonferroni vaut |t| ~ 3,5."""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent.parent
SORTIE = RACINE / "resultats" / "recurrences_v1.md"
FRAIS = 0.05  # en %


def lire(f, nom):
    d = pd.read_csv(RACINE / "data" / f)
    d["date"] = pd.to_datetime(d["date_utc"].str[:10])
    return d.drop_duplicates("date", keep="last").set_index("date").rename(columns=lambda c: c)


def construire():
    g = lire("or_ohlc_jour.csv", "or")
    g = g[g["close"] > 0]
    import datetime as dt
    if g.index[-1].date() >= dt.datetime.now(dt.timezone.utc).date():
        g = g.iloc[:-1]
    c, o, h, l = g["close"], g["open"], g["high"], g["low"]
    f = {}
    for k, fich in (("dxy", "facteur_dollar_dxy.csv"), ("vix", "facteur_vix.csv"), ("t10", "facteur_taux_10ans.csv"),
                    ("ag", "facteur_argent.csv")):
        f[k] = lire(fich, k)["close"].reindex(g.index).ffill(limit=3)
    r1 = c.pct_change()
    sig = r1.rolling(60).std()
    M = {}
    for i, n in enumerate(["lundi", "mardi", "mercredi", "jeudi", "vendredi"]):
        M["jour = " + n] = g.index.dayofweek == i
    for m in range(1, 13):
        M["mois = %d" % m] = g.index.month == m
    ym = pd.Series(g.index.to_period("M"), index=g.index)
    rang = g.groupby(ym).cumcount()
    rang_inv = g.groupby(ym).cumcount(ascending=False)
    M["3 premiers jours du mois"] = (rang < 3).values
    M["3 derniers jours du mois"] = (rang_inv < 3).values
    M["premier vendredi du mois"] = ((g.index.dayofweek == 4) & (g.index.day <= 7))
    for n in (1, 5, 20):
        rn = c.pct_change(n)
        M["rendement %dj > 0" % n] = (rn > 0).values
        M["rendement %dj < 0" % n] = (rn < 0).values
    M["jour > +2 écarts-types"] = (r1 > 2 * sig).values
    M["jour < -2 écarts-types"] = (r1 < -2 * sig).values
    M["jour > +1 écart-type"] = (r1 > sig).values
    M["jour < -1 écart-type"] = (r1 < -sig).values
    m50, m200, m20 = c.rolling(50).mean(), c.rolling(200).mean(), c.rolling(20).mean()
    M["cours > MA200"], M["cours < MA200"] = (c > m200).values, (c < m200).values
    M["MA20 > MA50"], M["MA20 < MA50"] = (m20 > m50).values, (m20 < m50).values
    for n in (20, 55):
        M["plus haut %dj" % n] = (c >= c.shift(1).rolling(n).max()).values
        M["plus bas %dj" % n] = (c <= c.shift(1).rolling(n).min()).values
    vol = r1.rolling(20).std()
    pct = vol.rolling(250).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)
    M["volatilité dans les 20 % bas"], M["volatilité dans les 20 % hauts"] = (pct < 0.2).values, (pct > 0.8).values
    d = c.diff()
    rsi = 100 - 100 / (1 + d.clip(lower=0).rolling(14).mean() / (-d.clip(upper=0)).rolling(14).mean())
    M["RSI14 < 30"], M["RSI14 > 70"] = (rsi < 30).values, (rsi > 70).values
    for k, nom in (("dxy", "dollar"), ("ag", "argent")):
        rk = f[k].pct_change()
        sk = rk.rolling(60).std()
        M["%s > +1 écart-type" % nom], M["%s < -1 écart-type" % nom] = (rk > sk).values, (rk < -sk).values
    vz = (f["vix"] - f["vix"].rolling(60).mean()) / f["vix"].rolling(60).std()
    M["VIX z > 1,5"], M["VIX z < -1"] = (vz > 1.5).values, (vz < -1).values
    dt10 = f["t10"].diff()
    zt = dt10 / dt10.rolling(60).std()
    M["taux 10 ans, forte hausse"], M["taux 10 ans, forte baisse"] = (zt > 1).values, (zt < -1).values
    gap = o / c.shift(1) - 1
    M["écart d'ouverture > +0,5 écart-type"], M["écart d'ouverture < -0,5 écart-type"] = (gap > 0.5 * sig).values, (gap < -0.5 * sig).values
    M["3 hausses de suite"] = ((r1 > 0) & (r1.shift(1) > 0) & (r1.shift(2) > 0)).values
    M["3 baisses de suite"] = ((r1 < 0) & (r1.shift(1) < 0) & (r1.shift(2) < 0)).values
    pos = (c - l) / (h - l)
    M["clôture proche du plus haut du jour"], M["clôture proche du plus bas du jour"] = (pos > 0.8).values, (pos < 0.2).values
    return g, c, {k: pd.Series(np.asarray(v, dtype=bool), index=g.index) for k, v in M.items()}


def nw_t(y, x, lag):
    """t de Newey-West de la pente de y sur le masque x (0/1)."""
    ok = ~np.isnan(y)
    y, x = y[ok], x[ok].astype(float)
    n = len(y)
    if x.sum() < 20 or x.sum() > n - 20:
        return float("nan"), float("nan")
    X = np.column_stack([np.ones(n), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ b
    u = X * e[:, None]
    S = u.T @ u / n
    for k in range(1, lag + 1):
        G = u[k:].T @ u[:-k] / n
        S += (1 - k / (lag + 1)) * (G + G.T)
    A = np.linalg.inv(X.T @ X / n)
    V = A @ S @ A / n
    return b[1], b[1] / math.sqrt(V[1, 1])


def main():
    g, c, M = construire()
    rets = {h: (c.shift(-h) / c - 1) * 100 for h in (1, 3)}
    idx = np.arange(len(c))
    debut = 250
    coupe = int(debut + (len(c) - debut) * 0.7)
    dev, ctl = slice(debut, coupe), slice(coupe, len(c) - 1)
    lignes = []
    for nom, mk in M.items():
        for h in (1, 3):
            y = rets[h].values
            exc, t = nw_t(y[dev], mk.values[dev], h)
            if math.isnan(t):
                continue
            moy = np.nanmean(y[dev][mk.values[dev]])
            lignes.append((nom, h, int(mk.values[dev].sum()), moy, exc, t))
    N = len(lignes)
    lignes.sort(key=lambda z: -abs(z[5]))
    retenues = [z for z in lignes if abs(z[5]) >= 2.5]
    bonf = abs(__import__("statistics").NormalDist().inv_cdf(1 - 0.05 / N / 2))
    sortie = ["# Recherche de récurrences sur l'or (v1)", "",
              "Données : %d jours de bourse (%s à %s), futures GC=F et facteurs. Exploration : %s à %s (70 %%). Contrôle fermé jusqu'à la fin : %s à %s." % (
                  len(c), c.index[0].date(), c.index[-1].date(), c.index[debut].date(), c.index[coupe - 1].date(), c.index[coupe].date(), c.index[-1].date()),
              "", "**%d essais comptés** (%d hypothèses x 2 horizons). Avec autant d'essais, le seuil de Bonferroni est |t| ≈ %.1f ; au seuil usuel de 2, environ %d essais « marchent » par pur hasard." % (N, N // 2, bonf, round(N * 0.05)),
              "", "**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
              "## 1. Meilleurs candidats en exploration (|t| ≥ 2,5 : %d sur %d)" % (len(retenues), N), "",
              "| Condition | Horizon | Jours | Rendement moyen | Écart vs. tous les jours | t |", "| --- | --- | --- | --- | --- | --- |"]
    for nom, h, n, moy, exc, t in lignes[:15]:
        sortie.append("| %s | %d j | %d | %.2f %% | %+.2f %% | %.1f |" % (nom, h, n, moy, exc, t))
    sortie += ["", "## 2. Contrôle sur la période fermée (30 %)", ""]
    sortie += ["| Condition | Horizon | Sens | Écart exploration | Écart contrôle | t contrôle | Années cohérentes | Net de frais | Verdict |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    survivants = []
    for nom, h, n, moy, exc, t in retenues:
        mk = M[nom].values
        y = rets[h].values
        exc2, t2 = nw_t(y[ctl], mk[ctl], h)
        sens = 1 if exc > 0 else -1
        ans = pd.Series(sens * y, index=c.index)[mk]
        ans = ans[~ans.isna()]
        par_an = ans.groupby(ans.index.year).mean()
        part = (par_an > 0).mean() if len(par_an) else float("nan")
        net = sens * exc2 - FRAIS if not math.isnan(exc2) else float("nan")
        ok = (not math.isnan(t2)) and exc2 * exc > 0 and abs(t2) >= 2 and part >= 0.65 and net > 0
        v = "À surveiller" if ok else "Rejeté"
        if ok:
            survivants.append(nom + " (%d j)" % h)
        sortie.append("| %s | %d j | %s | %+.2f %% | %+.2f %% | %.1f | %s %% | %+.2f %% | %s |" % (
            nom, h, "achat" if sens > 0 else "vente", exc, exc2, t2, "n/a" if math.isnan(part) else "%d" % round(part * 100), net, v))
    sortie += ["", "## Conclusion", ""]
    if survivants:
        sortie.append("Récurrences qui passent tous les filtres : " + ", ".join(survivants) + ". Elles restent **à confirmer en conditions réelles** (paper trading) : %d essais ont été faits, un résultat chanceux reste possible." % N)
    else:
        sortie.append("**Aucune récurrence ne passe le contrôle.** Les meilleurs candidats d'exploration ne se confirment pas sur la période fermée : c'est l'attendu d'un marché liquide, et cela évite une fausse stratégie.")
    sortie += ["", "## Limites", "",
               "- Données journalières seulement : les récurrences intraday (heure de la journée, séances Asie / Europe / États-Unis) seront testées avec l'historique 5 min, quand il sera complet.",
               "- Rendements bruts clôture à clôture, frais comptés à 0,05 % par aller-retour ; pas de financement de nuit.",
               "- Facteurs décalés par leurs heures de clôture : léger flou possible.",
               "- Le calendrier des annonces n'existe que depuis novembre 2026 : l'effet des annonces n'est pas testable (sauf « premier vendredi du mois », proxy de l'emploi américain)."]
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text("\n".join(sortie) + "\n", encoding="utf-8")
    print("\n".join(sortie))


if __name__ == "__main__":
    main()
