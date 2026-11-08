"""Que s'est-il passé quand les trades ont gagné ? Recherche de conditions, avec garde-fous contre le surajustement.

Méthode (fixée avant de regarder les résultats) :
  - trades de Compression Or (variante A) et de Nuit Or (variante A) ; 60 % premiers trades = développement, 40 % derniers = contrôle ;
  - conditions candidates : seuils aux quintiles du développement pour les mesures, valeurs pour les catégories (connues avant l'entrée) ;
  - sélection sur le développement SEULEMENT : meilleure condition, puis meilleure 2e condition en plus (t le plus élevé, au moins 60 puis 40 trades) ;
  - jugement unique sur le contrôle + test de permutation : la même méthode appliquée à des résultats mélangés (300 fois) dit ce que le hasard produit.

  python scripts/backtests/analyse_gagnants.py   # -> resultats/analyse_gagnants.md
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_compression as bc  # noqa: E402
import backtest_nuit as bn  # noqa: E402
import backtest_regime as br  # noqa: E402

NUM = ["vol_pct", "trend63", "dist200", "ret1", "ret5", "rng_atr"]
CAT = ["dow", "dxy63", "taux63"]
NOMS = {"vol_pct": "volatilité (rang sur 1 an)", "trend63": "tendance 3 mois", "dist200": "écart à la moyenne 200 j", "ret1": "variation de la veille",
        "ret5": "variation sur 5 jours", "rng_atr": "amplitude de la veille / ATR", "dow": "jour de la semaine (0 = lundi)", "dxy63": "dollar sur 3 mois (−1 baisse, +1 hausse)",
        "taux63": "taux réels sur 3 mois (−1 baisse, +1 hausse)", "sens": "sens (+1 achat, −1 vente)", "session": "session d'entrée", "comp": "type de compression", "nuits": "nuits tenues"}
N_PERM = 300


def features_jour(d):
    c = pd.Series(d.c)
    atr = pd.Series(d.atr)
    rel = atr / c
    f = pd.DataFrame({
        "vol_pct": rel.rolling(252).apply(lambda x: (x[-1] >= x).mean(), raw=True),
        "trend63": c / c.shift(63) - 1, "dist200": c / c.rolling(200).mean() - 1,
        "ret1": c / c.shift(1) - 1, "ret5": c / c.shift(5) - 1, "rng_atr": pd.Series(d.r) / atr})
    dates = pd.to_datetime(d.label, unit="D")
    g, dxy, tx = br.charger()
    for nom, s in (("dxy63", dxy), ("taux63", tx)):
        sg = np.sign(s.diff(63)).shift(1)
        f[nom] = sg.reindex(dates, method="ffill").values
    f["date_label"] = dates
    return f


def table_compression(d, f):
    tr, _, _ = bc.lancer(d, "A")
    rows = f.iloc[tr["j"].values].reset_index(drop=True)
    out = rows[NUM + ["dxy63", "taux63"]].copy()
    out["dow"] = pd.to_datetime(d.label[tr["j"].values + 1], unit="D").dayofweek
    out["sens"] = tr["sens"].values
    h = tr["date"].dt.hour.values
    out["session"] = np.where((h >= 22) | (h < 7), 0, np.where(h < 13, 1, 2))     # 0 Asie, 1 Londres, 2 New York
    j = tr["j"].values
    out["comp"] = [int(d.r[x] <= d.r[x - 3:x].min()) + 2 * int(d.h[x] < d.h[x - 1] and d.l[x] > d.l[x - 1]) + 4 * int(d.r[x] < 0.7 * d.atr[x - 1]) for x in j]
    out["date"] = tr["date"].values
    out["y"] = tr["net"].values
    return out, ["sens", "session", "comp"], (1.0, "R")


def table_nuit(d, f):
    seg = br.segments(br.lire_5m())
    y = bn.trades(seg, 0.0005, 0.00015)
    entree = seg.index.values.astype("datetime64[D]").astype(np.int64)
    idx = np.searchsorted(d.label, entree, side="left") - 1
    ok = idx >= 260
    out = f.iloc[idx[ok]][NUM + ["dxy63", "taux63"]].reset_index(drop=True)
    out["dow"] = seg.index[ok].dayofweek
    out["nuits"] = seg["nuits"].values[ok]
    out["date"] = seg.index[ok].values
    out["y"] = y.values[ok]
    return out, ["nuits"], (100.0, "% par trade")


def regles(F, dev, num, cat):
    noms, masks = [], []
    for c in num:
        for q in np.nanquantile(F.loc[dev, c], [0.2, 0.4, 0.6, 0.8]):
            noms.append("%s ≤ %.3g" % (NOMS[c], q)); masks.append((F[c] <= q).values)
            noms.append("%s > %.3g" % (NOMS[c], q)); masks.append((F[c] > q).values)
    for c in cat:
        for v in sorted(F[c].dropna().unique()):
            noms.append("%s = %g" % (NOMS[c], v)); masks.append((F[c] == v).values)
    return noms, np.array(masks).T.astype(float)


def t_stats(y, M, w, minn):
    Mw = M * w[:, None]
    n = Mw.sum(0)
    s, s2 = Mw.T @ y, Mw.T @ (y * y)
    m = s / np.maximum(n, 1)
    v = np.maximum((s2 - n * m * m) / np.maximum(n - 1, 1), 1e-18)
    t = m / np.sqrt(v / np.maximum(n, 1))
    t[n < minn] = -np.inf
    return t


def choisir(y, M, dev):
    w = dev.astype(float)
    t1 = t_stats(y, M, w, 60)
    r1 = int(np.argmax(t1))
    M2 = M * M[:, [r1]]
    t2 = t_stats(y, M2, w, 40)
    t2[r1] = -np.inf
    r2 = int(np.argmax(t2))
    return r1, r2, M[:, r1] * M[:, r2]


def stats_masque(y, masque, part):
    z = y[(masque > 0) & part]
    if len(z) < 3:
        return len(z), float("nan"), float("nan")
    return len(z), z.mean(), z.mean() / (z.std(ddof=1) / np.sqrt(len(z)))


def analyser(nom, T, cat_extra, ech, rng):
    echelle, unite = ech
    F = T.drop(columns=["date", "y"])
    y = T["y"].values
    n = len(T)
    coupe = int(n * 0.6)
    dev = np.arange(n) < coupe
    ctl = ~dev
    num = [c for c in NUM]
    cat = CAT + cat_extra
    noms, M = regles(F, dev, num, cat)
    R = len(noms)
    gagnants = y > 0
    L = ["## %s" % nom, "",
         "%d trades du %s au %s ; développement %d, contrôle %d. Rendement net moyen sans condition : développement %s, contrôle %s (unité : %s)." % (
             n, str(T["date"].iloc[0])[:10], str(T["date"].iloc[-1])[:10], dev.sum(), ctl.sum(),
             br.fr(y[dev].mean() * echelle, 3), br.fr(y[ctl].mean() * echelle, 3), unite), ""]
    # profil des gagnants (développement)
    L += ["**Gagnants contre perdants (développement seulement), écart standardisé des mesures :**", ""]
    diffs = []
    for c in NUM:
        a, b = F.loc[dev & gagnants, c], F.loc[dev & ~gagnants, c]
        sd = F.loc[dev, c].std()
        if sd > 0:
            diffs.append((abs(a.mean() - b.mean()) / sd, c, (a.mean() - b.mean()) / sd))
    for _, c, dd in sorted(diffs, reverse=True)[:4]:
        L.append("- %s : %s (écart standardisé %s)" % (NOMS[c], "plus élevé chez les gagnants" if dd > 0 else "plus bas chez les gagnants", br.fr(dd, 2)))
    L.append("")
    # meilleures conditions simples
    t1 = t_stats(y, M, dev.astype(float), 60)
    top = np.argsort(-t1)[:5]
    L += ["**Cinq meilleures conditions simples sur le développement, et ce qu'elles donnent ensuite sur le contrôle :**", "",
          "| Condition | Développement (trades / moy. / t) | Contrôle (trades / moy. / t) |", "| --- | --- | --- |"]
    for r in top:
        a, b = stats_masque(y, M[:, r], dev), stats_masque(y, M[:, r], ctl)
        L.append("| %s | %d / %s / %s | %d / %s / %s |" % (noms[r], a[0], br.fr(a[1] * echelle, 3), br.fr(a[2], 1), b[0], br.fr(b[1] * echelle, 3), br.fr(b[2], 1)))
    # sélection à deux conditions + permutation
    r1, r2, masque = choisir(y, M, dev)
    a, b = stats_masque(y, masque, dev), stats_masque(y, masque, ctl)
    obs_t = b[2]
    hasard = []
    for _ in range(N_PERM):
        yp = y.copy()
        yp[dev] = rng.permutation(y[dev])
        yp[ctl] = rng.permutation(y[ctl])
        _, _, mk = choisir(yp, M, dev)
        hasard.append(stats_masque(yp, mk, ctl)[2])
    hasard = np.array([h for h in hasard if not np.isnan(h)])
    p = (np.sum(hasard >= obs_t) + 1) / (len(hasard) + 1) if not np.isnan(obs_t) else float("nan")
    semaines = (pd.Timestamp(T["date"].iloc[-1]) - pd.Timestamp(T["date"].iloc[0])).days / 7
    L += ["", "**Règle choisie sur le développement (2 conditions) :** %s **et** %s" % (noms[r1], noms[r2]), "",
          "- Développement : %d trades, moyenne %s, t = %s." % (a[0], br.fr(a[1] * echelle, 3), br.fr(a[2], 1)),
          "- **Contrôle : %d trades, moyenne %s, t = %s.** Fréquence : %s trades par semaine." % (b[0], br.fr(b[1] * echelle, 3), br.fr(b[2], 1), br.fr((masque > 0).sum() / semaines, 2)),
          "- Test de permutation : avec la même méthode sur des résultats mélangés, le t sur le contrôle dépasse celui-ci dans %s de cas (médiane du hasard : t = %s). Environ %d conditions candidates, %d combinaisons possibles." % (
              br.pct(p, 0), br.fr(float(np.median(hasard)), 1), R, R * R // 2)]
    garde = (not np.isnan(b[1])) and b[1] > 0 and b[2] >= 2 and p <= 0.05 and (masque > 0).sum() >= 100
    L += ["", "**Verdict : %s**" % ("la règle survit au contrôle et au hasard (à confirmer en paper trading, pas une preuve)." if garde else
                                    "la règle ne survit pas : ce que l'on voit chez les gagnants du développement ne se retrouve pas sur le contrôle plus que le hasard ne le ferait."), ""]
    return L


def rapport():
    df = bc.lire_5m_complet()
    d = bc.Donnees(df)
    f = features_jour(d)
    rng = np.random.default_rng(2026)
    txt = ["# Analyse des trades gagnants : y a-t-il des conditions qui rendent la stratégie gagnante ?", "",
           "Méthode fixée avant de regarder (voir `scripts/backtests/analyse_gagnants.py`) : conditions cherchées sur les 60 % premiers trades, jugées une fois sur les 40 % derniers, comparées au hasard par permutation. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", ""]
    for nom, (T, cat, ech) in (("Compression Or (variante A)", table_compression(d, f)), ("Nuit Or (variante A)", table_nuit(d, f))):
        T = T.dropna(subset=NUM).reset_index(drop=True)
        txt += analyser(nom, T, cat, ech, rng)
    txt += ["## Limites", "",
            "- Le contrôle n'est pas vierge : les résultats globaux de ces stratégies avaient déjà été vus avant. Le vrai test sans biais est le paper trading à partir de maintenant.",
            "- Seules les stratégies avec assez de trades sont analysées. Le Régime or (une quinzaine de changements par an) n'en a pas assez ; les anciennes études intraday sont supprimées du dépôt.",
            "- Les conditions étudiées sont celles listées ici ; d'autres (heure d'été, annonces, saisons) n'ont pas été cherchées pour limiter le nombre d'essais."]
    out = br.RACINE / "resultats" / "analyse_gagnants.md"
    out.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))


if __name__ == "__main__":
    rapport()
