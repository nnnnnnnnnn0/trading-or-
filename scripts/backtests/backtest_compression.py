"""Stratégie « Compression Or » v1 : règles dans regles/strategie_compression_v1.md (figées avant le test).

  python scripts/backtests/backtest_compression.py   # -> resultats/compression_v1.md
"""
import glob
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_regime as br  # noqa: E402

FRAIS_AR, FRAIS_NUIT = 0.0005, 0.00015
RISQUE = 0.005          # 1 R = 0,5 % du capital
MIN_BARRES, MIN_ACTIVES = 200, 100


class Donnees:
    """Barres 5 min regroupées en jours de séance (22 h UTC à 22 h UTC)."""

    def __init__(self, df):
        self.ts = df.index.values
        self.O, self.H, self.L, self.C = (df[c].values for c in ("open", "high", "low", "close"))
        lab = ((df.index + pd.Timedelta(hours=2)).normalize()).values.astype("datetime64[D]").astype(np.int64)
        actives = (df["volume"].values > 0).astype(int)
        jours, debuts, comptes = np.unique(lab, return_index=True, return_counts=True)
        fins = debuts + comptes
        act = np.add.reduceat(actives, debuts)
        ok = (comptes >= MIN_BARRES) & (act >= MIN_ACTIVES)
        self.label = jours[ok]
        self.s, self.e = debuts[ok], fins[ok]
        n = len(self.label)
        self.h = np.array([self.H[a:b].max() for a, b in zip(self.s, self.e)])
        self.l = np.array([self.L[a:b].min() for a, b in zip(self.s, self.e)])
        self.c = np.array([self.C[b - 1] for b in self.e])
        self.r = self.h - self.l
        cp = np.concatenate([[np.nan], self.c[:-1]])
        self.tr = np.nanmax(np.vstack([self.r, np.abs(self.h - cp), np.abs(self.l - cp)]), axis=0)
        self.atr = pd.Series(self.tr).rolling(14).mean().values
        self.n = n

    def comprime(self, j):
        """Le jour j (indice) est-il comprimé ? (règle 1)"""
        if j < 17:
            return False
        c1 = self.r[j] <= self.r[j - 3:j].min()
        c2 = self.h[j] < self.h[j - 1] and self.l[j] > self.l[j - 1]
        c3 = self.r[j] < 0.7 * self.atr[j - 1]
        return bool(c1 or c2 or c3)


def jour_date(ts):
    return ts.astype("datetime64[D]").astype(np.int64)


def simuler(d, j, sens):
    """Trade pour la séance j+1 d'après le jour j. sens : 0 achat et vente, +1 achat seul, -1 vente seule. None si pas de trade."""
    k = j + 1
    if k + 0 >= d.n:
        return None
    a, b = d.s[k], d.e[k]
    achat, vente = d.h[j], d.l[j]
    atr = d.atr[j]
    if not atr > 0:
        return None
    ib = np.nonzero(d.H[a:b] >= achat)[0] if sens >= 0 else np.array([], dtype=int)
    iv = np.nonzero(d.L[a:b] <= vente)[0] if sens <= 0 else np.array([], dtype=int)
    fb = ib[0] if len(ib) else None
    fv = iv[0] if len(iv) else None
    if fb is None and fv is None:
        return None
    if fb is not None and fv is not None and fb == fv:
        return {"conflit": True}
    if fv is None or (fb is not None and fb < fv):
        sg, i, niveau = 1, a + fb, achat
        entree = max(niveau, d.O[i])
    else:
        sg, i, niveau = -1, a + fv, vente
        entree = min(niveau, d.O[i])
    stop, cible = entree - sg * atr, entree + sg * 2 * atr
    fin_j = min(k + 2, d.n - 1)
    fin = d.e[fin_j]
    h, l, o = d.H[i:fin], d.L[i:fin], d.O[i:fin]
    if sg > 0:
        s_hit, t_hit = l <= stop, h >= cible
    else:
        s_hit, t_hit = h >= stop, l <= cible
    t_hit[0] = False
    si = np.argmax(s_hit) if s_hit.any() else None
    ti = np.argmax(t_hit) if t_hit.any() else None
    if si is not None and (ti is None or si <= ti):
        m = si
        px = stop if m == 0 else (min(stop, o[m]) if sg > 0 else max(stop, o[m]))
        type_ = "stop"
    elif ti is not None:
        m, px, type_ = ti, cible, "objectif"
    else:
        m, px, type_ = len(h) - 1, d.C[fin - 1], "temps"
    sortie = i + m
    nuits = int(jour_date(d.ts[sortie]) - jour_date(d.ts[i]))
    brut = sg * (px - entree) / atr
    frais = (FRAIS_AR + FRAIS_NUIT * nuits) * entree / atr
    return {"conflit": False, "j": j, "date": pd.Timestamp(d.ts[i]), "sens": sg, "brut": brut, "net": brut - frais, "type": type_, "sortie_idx": sortie,
            "debut_prochaine": d.e[min(fin_j, d.n - 1)]}


def lancer(d, variante, filtre="compresse"):
    """variante 'A' ou 'B'. filtre 'compresse' (règles) ou 'normal' (contrôle : jours non comprimés, sans contrainte de position unique)."""
    trades, conflits, ignores = [], 0, 0
    libre = 0
    for j in range(64, d.n - 1):
        comp = d.comprime(j)
        if (filtre == "compresse") != comp:
            continue
        if filtre == "compresse" and d.s[j + 1] < libre:
            ignores += 1
            continue
        sens = 0
        if variante == "B":
            sens = 1 if d.c[j] > d.c[j - 63] else -1
        t = simuler(d, j, sens)
        if t is None:
            continue
        if t["conflit"]:
            conflits += 1
            continue
        libre = t["sortie_idx"] + 1
        trades.append(t)
    return pd.DataFrame(trades), conflits, ignores


def lire_5m_complet():
    morceaux = [pd.read_csv(f) for f in sorted(glob.glob(str(br.DATA / "histo" / "xauusd_5m_*.csv.gz")))]
    x = pd.concat(morceaux)
    x["t"] = pd.to_datetime(x["date_utc"], utc=True)
    return x.drop_duplicates("t").set_index("t").sort_index()


def mesures(x):
    x = np.asarray(x, dtype=float)
    return {"moy": x.mean(), "t": br.nw_t(x, 3), "gagnants": (x > 0).mean()}


def ligne(nom, tr, conflits, ignores, annees, ecart_fn):
    x = tr["net"].values
    n = len(x)
    coupe = int(n * 0.6)
    dev, ctl = mesures(x[:coupe]), mesures(x[coupe:])
    bornes = np.linspace(0, n, 5).astype(int)
    blocs = [x[a:b].mean() for a, b in zip(bornes[:-1], bornes[1:])]
    par_an = tr.groupby(tr["date"].dt.year)["net"].agg(["mean", "size"])
    par_an = par_an[par_an["size"] >= 5]
    pos_an = (par_an["mean"] > 0).mean() if len(par_an) else 0.0
    ecart = ecart_fn(n)
    d2, d250 = br.deflated_sharpe(x, 2, ecart), br.deflated_sharpe(x, 250, ecart)
    m = mesures(x)
    manque = [t for ok, t in ((n >= 100, "moins de 100 trades"),
                              (dev["moy"] > 0 and ctl["moy"] > 0 and dev["t"] >= 2 and ctl["t"] >= 2, "gain net positif avec t ≥ 2 en développement et en contrôle"),
                              (sum(b > 0 for b in blocs) >= 3, "positif dans moins de 3 blocs sur 4"),
                              (pos_an >= 0.6, "moins de 60 % d'années positives"), (d2 >= 0.95, "Deflated Sharpe < 0,95")) if not ok]
    cap = x.sum() * RISQUE / annees
    types = tr["type"].value_counts(normalize=True)
    cols = [nom, str(n), br.fr(n / annees / 52, 1), br.fr(tr["brut"].mean(), 3) + " R", br.fr(m["moy"], 3) + " R", br.fr(m["t"], 1), br.pct(m["gagnants"], 0),
            br.pct(cap), "%s / %s" % (br.fr(dev["moy"], 3), br.fr(dev["t"], 1)), "%s / %s" % (br.fr(ctl["moy"], 3), br.fr(ctl["t"], 1)),
            " ; ".join(br.fr(b, 2) for b in blocs), br.pct(pos_an, 0), "%s / %s" % (br.fr(d2), br.fr(d250)),
            "%s / %s / %s" % (br.pct(types.get("objectif", 0), 0), br.pct(types.get("stop", 0), 0), br.pct(types.get("temps", 0), 0)),
            "%d / %d" % ((tr["sens"] > 0).sum(), (tr["sens"] < 0).sum())]
    return "| " + " | ".join(cols) + " |", manque, par_an["mean"]


def rapport():
    df = lire_5m_complet()
    d = Donnees(df)
    annees = (pd.Timestamp(d.ts[-1]) - pd.Timestamp(d.ts[0])).days / 365.25
    ecart_fn = lambda n: 1 / math.sqrt(n - 1)
    txt = ["# Stratégie Compression Or v1 : résultats", "",
           "Règles : `regles/strategie_compression_v1.md`, figées avant le test. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
           "Or au comptant 5 min, %d jours de séance valides du %s au %s. Un R = le risque d'un trade (1 × ATR) = 0,5 %% du capital. Frais de base : 0,05 %% l'aller-retour + 0,015 %% par nuit." % (
               d.n, pd.Timestamp(d.label[0] * 86400e9).date() if False else pd.Timestamp(int(d.label[0]), unit="D").date(), pd.Timestamp(int(d.label[-1]), unit="D").date()), "",
           "| Variante | Trades | Par semaine | Gain brut moyen | Gain net moyen | t | Gagnants | Rendement annuel (capital) | Développement (moy. R / t) | Contrôle (moy. R / t) | Blocs (moy. R) | Années positives | Deflated Sharpe (2 / 250 essais) | Objectif / stop / temps | Achats / ventes |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    verdicts, annuel = {}, {}
    for v in ("A", "B"):
        tr, conflits, ignores = lancer(d, v)
        l, manque, pa = ligne(v + (" (achat et vente)" if v == "A" else " (sens de la tendance)"), tr, conflits, ignores, annees, ecart_fn)
        txt.append(l)
        verdicts[v] = (manque, conflits, ignores)
        annuel[v] = pa
        if v == "A":
            tr_a = tr
    ctl_rows = []
    for v in ("A", "B"):
        tr, _, _ = lancer(d, v, "normal")
        ctl_rows.append((v, len(tr), tr["net"].mean(), br.nw_t(tr["net"].values, 3), tr["brut"].mean()))
    txt += ["", "### Verdict", ""]
    ok = [v for v, (m, _, _) in verdicts.items() if not m]
    if ok:
        txt.append("**Critères remplis par la variante %s.** Candidate pour du paper trading en conditions réelles, pas une preuve." % " et ".join(ok))
    else:
        for v, (m, c, i) in verdicts.items():
            txt.append("- Variante %s : critères non remplis : %s." % (v, " ; ".join(m)))
        txt += ["", "**La stratégie n'est pas retenue ; elle n'est pas retouchée pour la faire passer.**"]
    txt += ["", "Trades ignorés : %s (position déjà ouverte) et %s (deux niveaux touchés dans la même barre)." % (
        " / ".join("%s : %d" % (v, verdicts[v][2]) for v in verdicts), " / ".join("%s : %d" % (v, verdicts[v][1]) for v in verdicts)), "",
        "### Contrôle : même mécanique les jours NON comprimés (information)", "",
        "| Variante | Trades | Gain brut moyen | Gain net moyen | t |", "| --- | --- | --- | --- | --- |"]
    txt += ["| %s | %d | %s R | %s R | %s |" % (v, n, br.fr(b, 3), br.fr(m_, 3), br.fr(t_, 1)) for v, n, m_, t_, b in ctl_rows]
    txt += ["", "Si le contrôle fait aussi bien que les règles, la compression n'apporte rien : on ne ferait que profiter (ou souffrir) d'une cassure générale.", "",
            "### Gain net moyen par année (R, variante A)", "", "| Année | Gain net moyen (R) |", "| --- | --- |"]
    txt += ["| %d | %s |" % (y, br.fr(m_, 3)) for y, m_ in annuel["A"].items()]
    txt += ["", "## Limites", "",
            "- Exécution des ordres stop supposée au niveau (ou à l'ouverture en cas de gap), sans glissement ; or au comptant ; frais estimés.",
            "- Dans la barre d'entrée, seul le stop est vérifié ; stop et objectif dans une même barre 5 min : stop compté (hypothèse prudente).",
            "- Environ 255 essais ont été faits dans ce projet avant cette stratégie ; le Deflated Sharpe à 250 essais est donné par honnêteté.",
            "- Heures UTC fixes pour le jour de séance ; la séance de New York se décale d'une heure selon l'heure d'été."]
    out = br.RACINE / "resultats" / "compression_v1.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))


if __name__ == "__main__":
    rapport()
