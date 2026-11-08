"""Stratégie « Régime or » v1 : backtest, test de l'hypothèse H1 (nuit / jour), signal du jour.

Les règles sont celles de regles/strategie_regime_v1.md, figées avant tout test : aucun paramètre n'est ajusté.

  python scripts/backtests/backtest_regime.py            # rapport complet -> resultats/regime_v1.md
  python scripts/backtests/backtest_regime.py --signal   # position conseillée à la dernière clôture
"""
import csv
import datetime as dt
import gzip
import math
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent.parent
DATA = RACINE / "data"
SORTIE = RACINE / "resultats" / "regime_v1.md"

FRAIS_COTE = 0.00025      # 0,025 % par côté = 0,05 % l'aller-retour
FINANCEMENT = 0.00015     # 0,015 % par nuit calendaire, sur l'exposition tenue (achat ou vente)
VOL_CIBLE, LEVIER_MAX = 0.10, 1.5
SEUIL, ATR_MULT = 0.5, 3.0
HORIZONS = (21, 63, 252)
VARIANTES = {"V1 principale (0,7 tendance + 0,3 macro)": (0.7, 0.3),
             "V2 tendance seule": (1.0, 0.0),
             "V3 pondération 0,5 / 0,5": (0.5, 0.5)}


# ---------------------------------------------------------------- données
def lire_prix(fichier):
    d = pd.read_csv(DATA / fichier)
    d["date"] = pd.to_datetime(d["date_utc"].str[:10])
    d = d.drop_duplicates("date", keep="last").set_index("date").sort_index()
    return d[["open", "high", "low", "close"]].astype(float)


def charger():
    """Or (OHLC), dollar et taux réels alignés sur les dates de l'or. La séance du jour non terminée est retirée."""
    g = lire_prix("or_jour.csv")
    g = g[(g["close"] > 0) & (g["high"] >= g["low"])]
    if g.index[-1].date() >= dt.datetime.now(dt.timezone.utc).date():
        g = g.iloc[:-1]
    dxy = lire_prix("dollar_dxy.csv")["close"].reindex(g.index).ffill(limit=5)
    taux = lire_prix("taux_reels_10ans.csv")["close"].reindex(g.index).ffill(limit=5)
    return g, dxy, taux


# ---------------------------------------------------------------- stratégie
def scores(c, dxy, taux):
    """Tendance T, macro M (dollar et taux réels de la veille : pas de regard dans le futur)."""
    t = sum(np.sign(c.pct_change(n)) for n in HORIZONS) / len(HORIZONS)
    dx, tr = dxy.shift(1), taux.shift(1)
    m = (-np.sign(tr.diff(63)) - np.sign(dx.diff(63))) / 2
    return t, m


def jours_de_decision(index):
    """Vrai pour la dernière séance de chaque semaine (clôture du vendredi, ou du dernier jour ouvré)."""
    sem = index.isocalendar()
    cle = sem["year"].astype(int) * 100 + sem["week"].astype(int)
    suiv = np.append(cle.values[1:], -1)
    return cle.values != suiv


def positions(g, direction, decision):
    """Exposition tenue de la clôture t à la clôture t+1. Direction et taille fixées à la décision ; sortie de sécurité si le
    cours clôture au-delà de ATR_MULT x ATR(14) contre la position (retour au rééquilibrage suivant)."""
    c, h, l = g["close"], g["high"], g["low"]
    n = len(g)
    r = c.pct_change()
    vol = (r.rolling(20).std() * math.sqrt(252)).values
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().values
    cv = c.values
    pos = np.zeros(n)
    expo, stop, sens = 0.0, None, 0
    for t in range(n):
        if decision[t]:
            d = direction[t]
            if d != 0 and not math.isnan(d) and not math.isnan(vol[t]) and vol[t] > 0 and not math.isnan(atr[t]):
                sens = int(d)
                expo = sens * min(LEVIER_MAX, VOL_CIBLE / vol[t])
                stop = cv[t] - sens * ATR_MULT * atr[t]
            else:
                sens, expo, stop = 0, 0.0, None
        elif sens != 0 and ((sens > 0 and cv[t] < stop) or (sens < 0 and cv[t] > stop)):
            expo, sens = 0.0, 0
        pos[t] = expo
    return pos


def rendements(pos, c, dates):
    """Rendement net quotidien de la position tenue de t à t+1 (frais sur les changements, financement par nuit)."""
    cv = c.values
    suiv = np.zeros(len(cv))
    suiv[:-1] = cv[1:] / cv[:-1] - 1
    nuits = np.zeros(len(cv))
    nuits[:-1] = (dates[1:] - dates[:-1]).astype(int)
    prev = np.concatenate([[0.0], pos[:-1]])
    return pos * suiv - np.abs(pos - prev) * FRAIS_COTE - np.abs(pos) * FINANCEMENT * nuits


def direction_variante(t, m, w_t, w_m):
    if w_m == 0:
        return np.sign(t).values
    s = w_t * t + w_m * m
    return np.where(s >= SEUIL, 1.0, np.where(s <= -SEUIL, -1.0, 0.0)) * (~s.isna()).values.astype(float)


# ---------------------------------------------------------------- mesures
def stats(x):
    x = np.asarray(x, dtype=float)
    sd = x.std()
    eq = np.cumprod(1 + x)
    dd = (eq / np.maximum.accumulate(eq) - 1).min() if len(x) else 0.0
    return {"ann": x.mean() * 252, "vol": sd * math.sqrt(252), "sharpe": x.mean() / sd * math.sqrt(252) if sd > 0 else 0.0, "dd": dd}


def p_decalage(pos, c, dates, a, b, vrai, rng, n=1000):
    """Part de décalages circulaires aléatoires de la même série d'expositions qui rapportent au moins autant."""
    L = b - a
    cnt = 0
    for _ in range(n):
        k = int(rng.integers(63, L - 63))
        q = pos.copy()
        q[a:b] = np.roll(pos[a:b], k)
        if rendements(q, c, dates)[a:b].mean() >= vrai:
            cnt += 1
    return cnt / n


def deflated_sharpe(x, n_essais, ecart_sr):
    """Deflated Sharpe Ratio (Bailey & López de Prado). x : rendements quotidiens ; ecart_sr : écart-type des Sharpe quotidiens des essais
    (n_essais >= 2)."""
    x = np.asarray(x, dtype=float)
    T = len(x)
    sr = x.mean() / x.std()
    z = (x - x.mean()) / x.std()
    skew, kurt = (z ** 3).mean(), (z ** 4).mean()
    nd, g = NormalDist(), 0.5772156649
    sr0 = ecart_sr * ((1 - g) * nd.inv_cdf(1 - 1 / n_essais) + g * nd.inv_cdf(1 - 1 / (n_essais * math.e)))
    den = math.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4 * sr * sr))
    return nd.cdf((sr - sr0) * math.sqrt(T - 1) / den)


def fr(x, d=2):
    return ("{:." + str(d) + "f}").format(x).replace(".", ",")


def pct(x, d=1):
    return fr(x * 100, d) + " %"


# ---------------------------------------------------------------- module A
def module_a():
    g, dxy, taux = charger()
    c = g["close"]
    dates = g.index.values.astype("datetime64[D]")
    t, m = scores(c, dxy, taux)
    decision = jours_de_decision(g.index)
    ok = (~t.isna() & ~m.isna()).values
    debut = int(np.argmax(ok)) + 1
    n = len(c)
    fin = n - 1  # la dernière clôture n'a pas de rendement suivant
    res, rets = {}, {}
    for nom, (wt, wm) in VARIANTES.items():
        pos = positions(g, direction_variante(t, m, wt, wm), decision)
        res[nom] = pos
        rets[nom] = rendements(pos, c, dates)
    bh = np.zeros(n)
    bh[:-1] = c.values[1:] / c.values[:-1] - 1
    bornes = np.linspace(debut, fin, 5).astype(int)
    # Dispersion des Sharpe quotidiens des essais : inconnue pour les ~250 essais du projet, donc on prend l'écart-type d'un Sharpe
    # sous l'hypothèse « aucun talent » (1 / racine(T-1)), choix prudent et identique pour 3 et 250 essais.
    ecart_sr = 1 / math.sqrt(fin - debut - 1)
    rng = np.random.default_rng(2026)
    out = {"g": g, "debut": debut, "fin": fin, "bornes": bornes, "bh": bh, "rets": rets, "pos": res, "dates": dates,
           "t": t, "m": m, "ecart_sr": ecart_sr, "lignes": [], "verdicts": {}}
    sb = stats(bh[debut:fin])
    out["sb"] = sb
    for nom, r in rets.items():
        s = stats(r[debut:fin])
        pos = res[nom]
        blocs = [stats(r[a:b])["ann"] for a, b in zip(bornes[:-1], bornes[1:])]
        p = p_decalage(pos, c, dates, debut, fin, r[debut:fin].mean(), rng)
        dsr3, dsr250 = deflated_sharpe(r[debut:fin], 3, ecart_sr), deflated_sharpe(r[debut:fin], 250, ecart_sr)
        p_ = pos[debut:fin]
        long_, court = (p_ > 0).mean(), (p_ < 0).mean()
        chang = (np.sign(p_[1:]) != np.sign(p_[:-1])).sum() / ((fin - debut) / 252)
        ach = r[debut:fin][pos[debut:fin] > 0].sum() / ((fin - debut) / 252) * 100
        ven = r[debut:fin][pos[debut:fin] < 0].sum() / ((fin - debut) / 252) * 100
        c1, c2 = s["sharpe"] >= sb["sharpe"] - 0.1, abs(s["dd"]) <= 0.6 * abs(sb["dd"])
        c3, c4, c5 = sum(1 for b in blocs if b > 0) >= 3, p <= 0.05, dsr3 >= 0.95
        manque = [txt for ok_, txt in ((c1, "Sharpe trop bas face à garder l'or"), (c2, "perte maximale pas assez réduite"),
                                       (c3, "pas positive dans 3 blocs sur 4"), (c4, "pas meilleure que le hasard"),
                                       (c5, "Deflated Sharpe < 0,95")) if not ok_]
        out["verdicts"][nom] = manque
        out["lignes"].append((nom, s, blocs, p, dsr3, dsr250, long_, court, chang, ach, ven))
    return out


# ---------------------------------------------------------------- module B (H1)
def lire_5m():
    morceaux = []
    for f in sorted((DATA / "histo").glob("xauusd_5m_*.csv.gz")):
        with gzip.open(f, "rt") as g:
            morceaux.append(pd.read_csv(g, usecols=["date_utc", "open"]))
    if not morceaux:
        return None
    d = pd.concat(morceaux)
    d["t"] = pd.to_datetime(d["date_utc"], utc=True)
    return d.drop_duplicates("t").set_index("t").sort_index()["open"]


def segments(ouvertures, h1=13, h2=21):
    """Par date UTC : rendement « séance américaine » (h1 -> h2) et « hors séance américaine » (h2 -> h1 du lendemain)."""
    o = ouvertures
    jours = sorted(set(o.index.date))
    prix = {}
    for j in jours:
        for h in (h1, h2):
            t0 = pd.Timestamp(dt.datetime(j.year, j.month, j.day, h, 0), tz="UTC")
            w = o.loc[t0:t0 + pd.Timedelta(minutes=30)]
            if len(w):
                prix[(j, h)] = float(w.iloc[0])
    lignes = []
    for i, j in enumerate(jours[:-1]):
        a, b, c_ = prix.get((j, h1)), prix.get((j, h2)), prix.get((jours[i + 1], h1))
        if a and b and c_ and (jours[i + 1] - j).days <= 4:
            lignes.append((pd.Timestamp(j), b / a - 1, c_ / b - 1, (jours[i + 1] - j).days))
    return pd.DataFrame(lignes, columns=["date", "us", "hors_us", "nuits"]).set_index("date")


def nw_t(x, lag=5):
    x = np.asarray(x, dtype=float)
    n = len(x)
    u = x - x.mean()
    s = u @ u / n
    for k in range(1, lag + 1):
        s += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return x.mean() / math.sqrt(s / n) if s > 0 else float("nan")


def module_b():
    o = lire_5m()
    if o is None:
        return None
    s = segments(o)
    if len(s) < 200:
        return {"n": len(s)}
    coupe = int(len(s) * 0.6)
    s["diff"] = s["hors_us"] - s["us"]
    parts = {"Développement (60 %)": s.iloc[:coupe], "Contrôle (40 %)": s.iloc[coupe:]}
    lignes = []
    for nom, x in parts.items():
        lignes.append((nom, len(x), x["us"].mean(), x["hors_us"].mean(), x["diff"].mean(), nw_t(x["diff"])))
    par_an = s.groupby(s.index.year)[["us", "hors_us"]].mean()
    coh = float((par_an["hors_us"] > par_an["us"]).mean())
    ok = all(l[4] > 0 and l[5] >= 2 for l in lignes) and coh >= 0.7
    return {"n": len(s), "lignes": lignes, "par_an": par_an, "coh": coh, "ok": ok, "debut": s.index[0].date(), "fin": s.index[-1].date(),
            "annees": sorted(set(s.index.year))}


# ---------------------------------------------------------------- rapport
def rapport():
    a = module_a()
    g, bornes, debut, fin = a["g"], a["bornes"], a["debut"], a["fin"]
    sb = a["sb"]
    txt = ["# Stratégie Régime or v1 : résultats", "",
           "Règles : `regles/strategie_regime_v1.md`, figées avant le test. Rien n'a été ajusté après coup. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
           "## Module A : régime journalier (tendance + macro, taille par la volatilité)", "",
           "Données : or GC=F du %s au %s (%d séances testées, hors période de chauffe), dollar DXY, taux réels américains 10 ans (US Treasury). Frais : %s par aller-retour, financement %s par nuit. Dollar et taux réels pris avec un jour de retard." % (
               g.index[debut].date(), g.index[fin].date(), fin - debut, "0,05 %", "0,015 %"), "",
           "Référence « garder l'or » : rendement annuel %s, volatilité %s, Sharpe %s, perte maximale %s." % (pct(sb["ann"]), pct(sb["vol"]), fr(sb["sharpe"]), pct(sb["dd"], 0)), "",
           "| Variante | Rendement annuel | Volatilité | Sharpe | Perte max | Rendement annuel par bloc | Hasard | Deflated Sharpe (3 essais / 250) | Temps achat / vente | Changements de sens par an | Contribution achats / ventes (points par an) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for nom, s, blocs, p, d3, d250, lg, ct, ch, ach, ven in a["lignes"]:
        txt.append("| %s | %s | %s | %s | %s | %s | %s | %s / %s | %s / %s | %s | %s / %s |" % (
            nom, pct(s["ann"]), pct(s["vol"]), fr(s["sharpe"]), pct(s["dd"], 0), " / ".join(fr(b * 100, 0) for b in blocs),
            fr(p * 100, 0) + " %", fr(d3, 2), fr(d250, 2), pct(lg, 0), pct(ct, 0), fr(ch, 1), fr(ach, 1), fr(ven, 1)))
    dates_blocs = [str(g.index[b].date())[:4] for b in bornes]
    txt += ["", "Blocs égaux : " + " | ".join("%s-%s" % (dates_blocs[i], dates_blocs[i + 1]) for i in range(4)) + ". « Hasard » = part de 1 000 décalages aléatoires de la même série d'expositions qui rapportent au moins autant.", ""]
    v1 = list(a["verdicts"].items())[0]
    txt += ["### Verdict (variante principale V1)", ""]
    if not v1[1]:
        txt.append("**Tous les critères sont remplis.** Cela fait de V1 un candidat pour le paper trading en conditions réelles, pas une preuve.")
    else:
        txt.append("**Critères non remplis : " + " ; ".join(v1[1]) + ".** La stratégie n'est pas retenue en l'état ; elle n'est pas retouchée pour la faire passer.")
    txt += ["", "Autres variantes (robustesse, mêmes critères) : " + " ; ".join("%s : %s" % (k.split(" ")[0], "tous remplis" if not v else "non remplis (%d critère(s))" % len(v)) for k, v in list(a["verdicts"].items())[1:]) + ".", ""]
    r1 = list(a["rets"].values())[0]
    ann = pd.DataFrame({"V1": r1, "Garder l'or": a["bh"]}, index=g.index).iloc[debut:fin]
    an = ann.groupby(ann.index.year).apply(lambda x: (1 + x).prod() - 1)
    txt += ["### Rendement par année (V1 contre garder l'or)", "", "| Année | V1 | Garder l'or |", "| --- | --- | --- |"]
    for y, row in an.iterrows():
        txt.append("| %d | %s | %s |" % (y, pct(row["V1"], 0), pct(row["Garder l'or"], 0)))
    b = module_b()
    txt += ["", "## Module B : hypothèse H1, « l'or monte surtout hors séance américaine (13 h à 21 h UTC) »", ""]
    if b is None or "lignes" not in b:
        txt.append("Pas assez de données 5 min pour conclure (%s jours). Le téléchargement de l'historique doit d'abord se terminer." % (0 if b is None else b["n"]))
    else:
        txt += ["Données 5 min (Dukascopy, or au comptant) : %d jours du %s au %s ; années présentes : %s." % (b["n"], b["debut"], b["fin"], ", ".join(str(y) for y in b["annees"])), "",
                "| Période | Jours | Séance américaine (rendement moyen) | Hors séance américaine | Différence | t |", "| --- | --- | --- | --- | --- | --- |"]
        for nom, n_, us, hu, d, t_ in b["lignes"]:
            txt.append("| %s | %d | %s | %s | %s | %s |" % (nom, n_, pct(us, 3), pct(hu, 3), pct(d, 3), fr(t_, 1)))
        txt += ["", "Années où « hors séance » > « séance américaine » : %s." % pct(b["coh"], 0), "",
                "**H1 %s** (critère : différence positive en développement et en contrôle avec t ≥ 2, et au moins 70 %% des années)." % ("confirmée" if b["ok"] else "non confirmée")]
    txt += ["", "## Limites", "",
            "- Signal et exécution à la clôture du vendredi ; la sortie de sécurité est exécutée à la clôture, sans glissement de prix.",
            "- Frais et financement estimés, identiques achat et vente ; pas d'écart de prix de courtier ; futures GC=F.",
            "- Heures UTC fixes pour H1 : l'ouverture américaine se décale d'une heure selon l'heure d'été.",
            "- Environ 250 essais ont été faits dans ce projet avant cette stratégie (voir Deflated Sharpe à 250). Cette stratégie, elle, vient de la littérature et n'a que 3 variantes.",
            "- Aucune stratégie ne garantit un gain ; le suivi de tendance connaît de longues périodes sans gain."]
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))


def signal():
    g, dxy, taux = charger()
    t, m = scores(g["close"], dxy, taux)
    s = 0.7 * t + 0.3 * m
    i = len(g) - 1
    r = g["close"].pct_change()
    vol = float(r.rolling(20).std().iloc[i] * math.sqrt(252))
    tr = pd.concat([g["high"] - g["low"], (g["high"] - g["close"].shift()).abs(), (g["low"] - g["close"].shift()).abs()], axis=1).max(axis=1)
    atr = float(tr.rolling(14).mean().iloc[i])
    sc = float(s.iloc[i])
    d = 1 if sc >= SEUIL else -1 if sc <= -SEUIL else 0
    expo = d * min(LEVIER_MAX, VOL_CIBLE / vol)
    px = float(g["close"].iloc[i])
    print("Dernière clôture : %s, or %.1f" % (g.index[i].date(), px))
    print("Tendance T = %.2f ; macro M = %.2f ; score S = %.2f" % (float(t.iloc[i]), float(m.iloc[i]), sc))
    print("Direction : %s ; exposition conseillée %.2f x le capital (volatilité 20 j : %.1f %%)" % ({1: "ACHAT", -1: "VENTE", 0: "À PLAT"}[d], expo, vol * 100))
    if d:
        print("Sortie de sécurité si clôture %s %.1f. Décision et taille ne se revoient qu'à la clôture du vendredi." % ("sous" if d > 0 else "au-dessus de", px - d * ATR_MULT * atr))
    print("Paper trading uniquement : ceci n'est pas un conseil en investissement.")


if __name__ == "__main__":
    signal() if "--signal" in sys.argv else rapport()
