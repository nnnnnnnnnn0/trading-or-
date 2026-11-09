"""Stratégie intraday « Monte Carlo » v1 : règles dans regles/montecarlo_intraday_v1.md (figées avant le test).
Lancé une seule fois sur les 14 ans de barres 5 min de l'or.

  python scripts/backtests/backtest_montecarlo.py   # -> resultats/montecarlo_intraday_v1.md

Précisions d'implémentation (non écrites dans les règles, choisies avant le test, sans toucher aux paramètres) :
  - ATR(14) et RSI(14) au lissage de Wilder (alpha = 1/14) sur les barres de 1 h actives ;
  - EMA 20 / 100 : lissage exponentiel standard (span) sur les clôtures 1 h ;
  - tous les signaux sont lus sur des barres TERMINÉES à l'heure de décision (rien du futur) ;
  - le prix de départ de la simulation est l'ouverture de la barre 5 min de la décision (= prix d'entrée) ;
  - sortie « heure » : ouverture de la première barre à l'échéance min(décision + 8 h, 20:55 UTC) ;
  - garde-fous de données : jour valide (>= 200 barres dont >= 100 avec volume), dernière barre 1 h
    datant de moins de 2 h, fenêtre de 96 variations datant de moins de 6 jours.
"""
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_compression as bc  # noqa: E402
import backtest_regime as br  # noqa: E402
import backtest_sessions as bs  # noqa: E402

HEURES = range(8, 17)                   # décisions 08:00 … 16:00 UTC
FENETRE, CHEMINS, PAS = 96, 1000, 32    # 96 variations de 15 min, 1 000 trajectoires de 32 pas (8 h)
GRAINE = 2026
CIBLE_A, STOP_A = 1.5, 1.0
SEUIL_P, SEUIL_ECART = 500, 150         # en millièmes : P >= 0,50 et écart >= 0,15
DUREE_MAX = 8 * 3600
SORTIE_S = 20 * 3600 + 55 * 60          # 20:55 UTC
FRAIS_BASE, FRAIS_STRESS = 0.0002, 0.0005
RISQUE = 0.005
N_ESSAIS_PRECEDENTS = 350
SEPARATION = pd.Timestamp("2020-01-01", tz="UTC")
MIN_BARRES, MIN_ACTIVES = 200, 100
NS = 10 ** 9
JOUR_NS = 86400 * NS
SORTIE = br.RACINE / "resultats" / "montecarlo_intraday_v1.md"
IDX = np.random.default_rng(GRAINE).integers(0, FENETRE, size=(CHEMINS, PAS))   # tirages partagés, fixés une fois pour toutes


# ------------------------------------------------------------------ préparation des données
def _ns(index):
    return index.values.astype("datetime64[ns]").astype(np.int64)


def preparer(df):
    """df : barres 5 min (index UTC, open/high/low/close/volume). Renvoie les tableaux nécessaires."""
    actif = df["volume"] > 0
    jour = df.index.normalize()
    n_barres = df["close"].groupby(jour).size()
    n_actives = actif.groupby(jour).sum()
    ok = (n_barres >= MIN_BARRES) & (n_actives >= MIN_ACTIVES)
    jours = _ns(ok.index[ok.values])
    jours = jours[((jours // JOUR_NS) + 3) % 7 < 5]            # 1970-01-01 était un jeudi : lundi = 0
    P = SimpleNamespace(
        t=_ns(df.index), o=df["open"].to_numpy(float), h=df["high"].to_numpy(float),
        l=df["low"].to_numpy(float), c=df["close"].to_numpy(float), vol=df["volume"].to_numpy(float), jours=jours)
    a = df[actif]
    h1 = a.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    c = h1["close"]
    pc = c.shift(1)
    tr = pd.concat([h1["high"] - h1["low"], (h1["high"] - pc).abs(), (h1["low"] - pc).abs()], axis=1).max(axis=1)
    P.atr = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean().to_numpy()
    P.ema20 = c.ewm(span=20, adjust=False).mean().to_numpy()
    P.ema100 = c.ewm(span=100, adjust=False).mean().to_numpy()
    d = c.diff()
    mu = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    md = (-d).clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rsi = 100 - 100 / (1 + mu / md.replace(0, np.nan))
    rsi[(md == 0) & (mu > 0)] = 100.0
    P.rsi = rsi.to_numpy()
    P.h_fin = _ns(h1.index) + 3600 * NS                         # une barre 1 h est connue à sa fin
    q = a["close"].resample("15min").last().dropna()
    t15, c15 = _ns(q.index), q.to_numpy(float)
    r, dt = np.diff(np.log(c15)), np.diff(t15)
    bon = dt <= 30 * 60 * NS                                    # on écarte les variations qui enjambent un trou
    P.r_val = r[bon]
    P.r_fin = t15[1:][bon] + 15 * 60 * NS
    return P


# ------------------------------------------------------------------ signal Monte Carlo
def proba_mc(fenetre, p0, a, idx=IDX):
    """Probabilités (en millièmes de chemins) d'atteindre +1,5 A avant -1,0 A (hausse) et -1,5 A avant +1,0 A (baisse),
    en re-tirant au hasard (avec remise) les variations de `fenetre`."""
    cum = np.cumsum(np.asarray(fenetre)[idx], axis=1)
    sans = PAS + 1

    def premier(masque):
        i = masque.argmax(axis=1)
        i[~masque.any(axis=1)] = sans
        return i

    u_c, u_s = math.log1p(CIBLE_A * a / p0), math.log1p(STOP_A * a / p0)
    d_c, d_s = math.log1p(-CIBLE_A * a / p0), math.log1p(-STOP_A * a / p0)
    f_uc, f_ds = premier(cum >= u_c), premier(cum <= d_s)
    f_dc, f_us = premier(cum <= d_c), premier(cum >= u_s)
    return int((f_uc < f_ds).sum() * 1000 // len(cum)), int((f_dc < f_us).sum() * 1000 // len(cum))


def decisions(P):
    """Une ligne par heure de décision valide, avec tous les signaux calculés à partir du passé seulement."""
    lignes = []
    for jour in P.jours:
        for h in HEURES:
            T = int(jour) + h * 3600 * NS
            i0 = int(np.searchsorted(P.t, T))
            if i0 >= len(P.t) or P.t[i0] != T or P.vol[i0] <= 0:
                continue
            j = int(np.searchsorted(P.h_fin, T, side="right")) - 1
            if j < 200 or T - P.h_fin[j] > 2 * 3600 * NS or not (P.atr[j] > 0):
                continue
            k = int(np.searchsorted(P.r_fin, T, side="right"))
            if k < FENETRE or T - P.r_fin[k - FENETRE] > 6 * JOUR_NS:
                continue
            echeance = min(T + DUREE_MAX * NS, int(jour) + SORTIE_S * NS)
            i_dl = int(np.searchsorted(P.t, echeance))
            if i_dl >= len(P.t) or P.t[i_dl] - echeance > 30 * 60 * NS:
                continue
            a, p0 = float(P.atr[j]), float(P.o[i0])
            pup, pdn = proba_mc(P.r_val[k - FENETRE:k], p0, a)
            lignes.append((T, i0, i_dl, a, float(P.rsi[j]), float(P.ema20[j]), float(P.ema100[j]), pup, pdn))
    s = pd.DataFrame(lignes, columns=["T", "i0", "i_dl", "A", "rsi", "ema20", "ema100", "pup", "pdn"])
    s["date"] = pd.to_datetime(s["T"], unit="ns", utc=True)
    return s


def directions(s):
    """Sens (+1 achat, -1 vente, 0 rien) de chaque variante pour chaque heure de décision."""
    tend_h, tend_b = s["ema20"] > s["ema100"], s["ema20"] < s["ema100"]
    ach = tend_h & (s["rsi"] >= 40) & (s["rsi"] <= 70)
    ven = tend_b & (s["rsi"] >= 30) & (s["rsi"] <= 60)
    mc_h = (s["pup"] >= SEUIL_P) & (s["pup"] - s["pdn"] >= SEUIL_ECART)
    mc_b = (s["pdn"] >= SEUIL_P) & (s["pdn"] - s["pup"] >= SEUIL_ECART)

    def sens(h, b):
        return np.where(h, 1, np.where(b, -1, 0))

    return {"V1": sens(mc_h & ach, mc_b & ven), "V2": sens(mc_h, mc_b), "V3": sens(ach, ven)}


# ------------------------------------------------------------------ simulation d'un trade
def une_sortie(t, o, h, l, i0, i_dl, sens, a):
    """Entrée à l'ouverture de la barre i0, stop 1,0 A, objectif 1,5 A, sortie à l'ouverture de la barre i_dl.
    Stop prioritaire dans une même barre ; stop gappé : prix d'ouverture. Renvoie (prix, motif, fin en ns)."""
    entree = o[i0]
    stop, cible = entree - sens * STOP_A * a, entree + sens * CIBLE_A * a
    lo, hi, op = l[i0:i_dl], h[i0:i_dl], o[i0:i_dl]
    if sens > 0:
        m_s, m_c = lo <= stop, hi >= cible
    else:
        m_s, m_c = hi >= stop, lo <= cible
    js = int(m_s.argmax()) if m_s.any() else None
    jc = int(m_c.argmax()) if m_c.any() else None
    if js is not None and (jc is None or js <= jc):
        px = stop if js == 0 else (min(stop, op[js]) if sens > 0 else max(stop, op[js]))
        return float(px), "stop", int(t[i0 + js]) + 300 * NS
    if jc is not None:
        return float(cible), "cible", int(t[i0 + jc]) + 300 * NS
    return float(o[i_dl]), "heure", int(t[i_dl])


def simuler(P, s, sens):
    """Une seule position à la fois ; frais en % du prix d'entrée, convertis en R (1 R = A)."""
    libre = -1
    T, I0, IDL, A = s["T"].to_numpy(), s["i0"].to_numpy(), s["i_dl"].to_numpy(), s["A"].to_numpy()
    lignes = []
    for k in range(len(s)):
        sg = int(sens[k])
        if sg == 0 or T[k] < libre:
            continue
        px, motif, fin = une_sortie(P.t, P.o, P.h, P.l, int(I0[k]), int(IDL[k]), sg, float(A[k]))
        entree = float(P.o[I0[k]])
        brut = sg * (px - entree) / float(A[k])
        r = entree / float(A[k])
        lignes.append((s["date"].iloc[k], sg, entree, px, motif, float(A[k]), brut, brut - FRAIS_BASE * r, brut - FRAIS_STRESS * r))
        libre = fin
    return pd.DataFrame(lignes, columns=["date", "sens", "entree", "sortie", "motif", "A", "brut", "net", "stress"])


# ------------------------------------------------------------------ mesures
def serie_quotidienne(tr, jours, col="net"):
    """Rendement quotidien du compte (risque 0,5 % par trade) sur tous les jours valides ouvrés."""
    jours = pd.DatetimeIndex(pd.to_datetime(jours, unit="ns", utc=True))
    x = pd.Series(0.0, index=jours)
    if len(tr):
        par_jour = (tr[col] * RISQUE).groupby(tr["date"].dt.normalize()).sum()
        x.loc[par_jour.index.intersection(x.index)] += par_jour.reindex(par_jour.index.intersection(x.index)).values
    return x


def rendements_annuels(x):
    """(avant impôts, après impôts) en rendement annuel composé ; impôt de 31,4 % des plus-values nettes de l'année."""
    ans = max(1e-9, (x.index[-1] - x.index[0]).days / 365.25)
    avant = float(np.prod(1 + x.values)) ** (1 / ans) - 1
    apres = float(bs.apres_impots(x.index, x.values)) ** (1 / ans) - 1
    return avant, apres


def dsr(x, n_essais):
    x = np.asarray(x, dtype=float)
    if len(x) < 30 or x.std() == 0:
        return float("nan")
    return br.deflated_sharpe(x, n_essais, 1 / math.sqrt(len(x) - 1))


def annees(tr):
    if not len(tr):
        return 0, 0
    g = tr.groupby(tr["date"].dt.year)["net"].agg(["size", "sum"])
    g = g[g["size"] >= 20]
    return int((g["sum"] > 0).sum()), len(g)


def moy_t(x):
    x = np.asarray(x, dtype=float)
    if len(x) < 5:
        return float("nan"), float("nan")
    return float(x.mean()), br.nw_t(x, 3)


def decoupe(tr):
    dev = tr[tr["date"] < SEPARATION]
    val = tr[tr["date"] >= SEPARATION]
    return dev, val


def mesures(tr, jours):
    dev, val = decoupe(tr)
    x = serie_quotidienne(tr, jours)
    avant, apres = rendements_annuels(x) if len(x) > 1 else (float("nan"), float("nan"))
    ap, na = annees(tr)
    m_dev, t_dev = moy_t(dev["net"])
    m_val, t_val = moy_t(val["net"])
    m_tot, t_tot = moy_t(tr["net"])
    return {
        "n": len(tr), "gagnants": float((tr["net"] > 0).mean()) if len(tr) else float("nan"),
        "brut": float(tr["brut"].mean()) if len(tr) else float("nan"), "net": m_tot, "t": t_tot,
        "stress": float(tr["stress"].mean()) if len(tr) else float("nan"),
        "n_dev": len(dev), "m_dev": m_dev, "t_dev": t_dev, "n_val": len(val), "m_val": m_val, "t_val": t_val,
        "ans_pos": ap, "ans_tot": na, "avant": avant, "apres": apres,
        "dsr3": dsr(x.values, 3), "dsr350": dsr(x.values, N_ESSAIS_PRECEDENTS),
        "somme_net": float(tr["net"].sum()),
    }


def bootstrap_trades(net, n_boot=10000, graine=GRAINE):
    """Rééchantillonne (avec remise) les trades de V1 : probabilité que le total soit positif, fourchette du total, perte maximale médiane."""
    net = np.asarray(net, dtype=float)
    n = len(net)
    if n < 10:
        return None
    rng = np.random.default_rng(graine)
    totaux, dds = [], []
    lot = max(1, min(n_boot, 2_000_000 // n))
    fait = 0
    while fait < n_boot:
        m = min(lot, n_boot - fait)
        cs = np.cumsum(net[rng.integers(0, n, size=(m, n))], axis=1)
        pic = np.maximum(np.maximum.accumulate(cs, axis=1), 0.0)
        totaux.append(cs[:, -1])
        dds.append((pic - cs).max(axis=1))
        fait += m
    tot, dd = np.concatenate(totaux), np.concatenate(dds)
    return {"p_pos": float((tot > 0).mean()), "q05": float(np.quantile(tot, 0.05)), "q95": float(np.quantile(tot, 0.95)),
            "dd_med": float(np.median(dd)), "dd_95": float(np.quantile(dd, 0.95))}


def calibration(P, s):
    """Information : la probabilité Monte Carlo annoncée se vérifie-t-elle ? Pour chaque heure de décision, un trade
    d'achat (resp. de vente) hypothétique, sans contrainte de position ; réalisé = objectif touché avant le stop."""
    obs = []
    A = s["A"].to_numpy()
    for sg, col in ((1, "pup"), (-1, "pdn")):
        p = s[col].to_numpy() / 1000.0
        for k in range(len(s)):
            _, motif, _ = une_sortie(P.t, P.o, P.h, P.l, int(s["i0"].iat[k]), int(s["i_dl"].iat[k]), sg, float(A[k]))
            obs.append((p[k], float(motif == "cible"), (s["T"].iat[k] // NS % 86400) // 3600))
    return pd.DataFrame(obs, columns=["p", "reel", "heure"])


def tableau_calibration(c):
    bornes = [0, 0.2, 0.3, 0.4, 0.5, 0.6, 1.01]
    noms = ["< 20 %", "20-30 %", "30-40 %", "40-50 %", "50-60 %", "≥ 60 %"]
    lignes = []
    for i, nom in enumerate(noms):
        x = c[(c["p"] >= bornes[i]) & (c["p"] < bornes[i + 1])]
        if len(x):
            lignes.append("| %s | %d | %s | %s |" % (nom, len(x), br.pct(x["p"].mean()), br.pct(x["reel"].mean())))
    corr = float(np.corrcoef(c["p"].rank(), c["reel"].rank())[0, 1]) if len(c) > 10 and c["reel"].std() > 0 else float("nan")
    return lignes, corr


# ------------------------------------------------------------------ rapport
def ligne_variante(nom, m, ans):
    return "| %s | %d | %s | %s | %s | %s | %s | %s | %s |" % (
        nom, m["n"], br.fr(m["n"] / ans / 52, 1), br.pct(m["gagnants"], 0), br.fr(m["brut"], 3), br.fr(m["net"], 3),
        br.fr(m["t"], 1), br.fr(m["stress"], 3), "%d/%d" % (m["ans_pos"], m["ans_tot"]))


def rapport(n_boot=10000, n_hasard=100):
    df = bc.lire_5m_complet()
    P = preparer(df)
    s = decisions(P)
    sens = directions(s)
    jours_valides = P.jours[(P.jours >= s["T"].iloc[0] - s["T"].iloc[0] % JOUR_NS) & (P.jours <= s["T"].iloc[-1])]
    trades = {k: simuler(P, s, v) for k, v in sens.items()}
    # témoin : sens tiré au hasard (graine 2026) aux mêmes heures que V3
    rng = np.random.default_rng(GRAINE)
    hasard = np.where(sens["V3"] != 0, rng.choice([-1, 1], size=len(s)), 0)
    trades["Hasard"] = simuler(P, s, hasard)
    M = {k: mesures(v, jours_valides) for k, v in trades.items()}
    m1, m3 = M["V1"], M["V3"]
    ans = max(1e-9, (s["date"].iloc[-1] - s["date"].iloc[0]).days / 365.25)
    # information : 100 autres tirages du témoin
    moy_hasard = []
    for g in range(1, n_hasard + 1):
        r = np.random.default_rng(10_000 + g)
        tr = simuler(P, s, np.where(sens["V3"] != 0, r.choice([-1, 1], size=len(s)), 0))
        if len(tr):
            moy_hasard.append(float(tr["net"].mean()))
    moy_hasard = np.array(moy_hasard)
    boot = bootstrap_trades(trades["V1"]["net"].values, n_boot)
    cal = calibration(P, s)
    cal_tab, cal_corr = tableau_calibration(cal)
    cal_tab_m, cal_corr_m = tableau_calibration(cal[cal["heure"] <= 12])

    crit = [
        ("Gain net moyen > 0 avec t ≥ 2 en développement (2012-2019)", m1["m_dev"] > 0 and m1["t_dev"] >= 2,
         "moyenne %s R, t = %s sur %d trades" % (br.fr(m1["m_dev"], 3), br.fr(m1["t_dev"], 1), m1["n_dev"])),
        ("Gain net moyen > 0 avec t ≥ 2 en validation (2020-2026)", m1["m_val"] > 0 and m1["t_val"] >= 2,
         "moyenne %s R, t = %s sur %d trades" % (br.fr(m1["m_val"], 3), br.fr(m1["t_val"], 1), m1["n_val"])),
        ("Au moins 100 trades et 60 % d'années positives", m1["n"] >= 100 and m1["ans_tot"] > 0 and m1["ans_pos"] / m1["ans_tot"] >= 0.6,
         "%d trades, %d années positives sur %d" % (m1["n"], m1["ans_pos"], m1["ans_tot"])),
        ("Deflated Sharpe ≥ 0,95 (3 essais)", m1["dsr3"] >= 0.95, "DSR = %s (avec 350 essais : %s)" % (br.fr(m1["dsr3"], 2), br.fr(m1["dsr350"], 2))),
        ("Rendement annuel après impôts > 0", m1["apres"] > 0, "%s par an après impôts (%s avant impôts)" % (br.pct(m1["apres"], 1), br.pct(m1["avant"], 1))),
        ("V1 fait mieux que V3 (sans Monte Carlo) en développement et en validation",
         m1["m_dev"] > m3["m_dev"] and m1["m_val"] > m3["m_val"],
         "V1 %s / %s R contre V3 %s / %s R (dév. / valid.)" % (br.fr(m1["m_dev"], 3), br.fr(m1["m_val"], 3), br.fr(m3["m_dev"], 3), br.fr(m3["m_val"], 3))),
    ]
    reussis = all(c[1] for c in crit)

    L = ["# Stratégie intraday « Monte Carlo » v1 : résultats", "",
         "Règles figées avant le test : `regles/montecarlo_intraday_v1.md`. Lancé une seule fois, sans retouche. "
         "Or XAUUSD, barres 5 min Dukascopy 2012-2026 ; frais de base 0,02 % l'aller-retour (stress 0,05 %), risque 0,5 % du capital par trade (1 R = 1 ATR horaire). "
         "Développement 2012-2019, validation 2020-2026.", "",
         "## Verdict", "",
         ("**V1 passe les 6 critères figés.** Cela reste un résultat de backtest : à confirmer en avant avant de lui faire confiance."
          if reussis else
          "**V1 ne passe pas tous les critères figés : elle n'est pas « solide » au sens que nous avions fixé.** Les chiffres ci-dessous sont publiés tels quels, sans retouche de la règle."),
         "", "| Critère (figé avant le test) | Résultat | Détail |", "|---|---|---|"]
    for nom, ok, det in crit:
        L.append("| %s | %s | %s |" % (nom, "✔ réussi" if ok else "✘ échoué", det))
    L += ["", "## Les quatre variantes", "",
          "Moyennes par trade en R (1 R = risque pris). Brut = sans frais ; net = frais de base ; stress = frais 0,05 %. t = test de Newey-West sur le net.", "",
          "| Variante | Trades | par semaine | gagnants | brut | net | t | net (stress) | années positives |", "|---|---|---|---|---|---|---|---|---|",
          ligne_variante("V1 Monte Carlo + tendance + RSI", m1, ans), ligne_variante("V2 Monte Carlo seul", M["V2"], ans),
          ligne_variante("V3 tendance + RSI (sans Monte Carlo)", m3, ans), ligne_variante("Témoin hasard (aux heures de V3)", M["Hasard"], ans), "",
          "| Variante | dév. : trades | dév. : net R | dév. : t | valid. : trades | valid. : net R | valid. : t | rend. annuel avant impôts | après impôts (31,4 %) | DSR (3 essais) | DSR (350 essais) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nom, k in (("V1", "V1"), ("V2", "V2"), ("V3", "V3"), ("Hasard", "Hasard")):
        m = M[k]
        L.append("| %s | %d | %s | %s | %d | %s | %s | %s | %s | %s | %s |" % (
            nom, m["n_dev"], br.fr(m["m_dev"], 3), br.fr(m["t_dev"], 1), m["n_val"], br.fr(m["m_val"], 3), br.fr(m["t_val"], 1),
            br.pct(m["avant"], 1), br.pct(m["apres"], 1), br.fr(m["dsr3"], 2), br.fr(m["dsr350"], 2)))
    L += ["", "Sorties de V1 : " + ", ".join("%s %d" % (k, v) for k, v in trades["V1"]["motif"].value_counts().items()) + ".",
          "Heures de décision évaluées : %d ; signaux d'achat/vente à l'heure : V1 %d, V2 %d, V3 %d." % (
              len(s), int((sens["V1"] != 0).sum()), int((sens["V2"] != 0).sum()), int((sens["V3"] != 0).sum())), ""]
    L += ["## V1 année par année", "", "| Année | Trades | net moyen (R) | total (R) |", "|---|---|---|---|"]
    if len(trades["V1"]):
        for an, g in trades["V1"].groupby(trades["V1"]["date"].dt.year):
            L.append("| %d | %d | %s | %s |" % (an, len(g), br.fr(g["net"].mean(), 3), br.fr(g["net"].sum(), 1)))
    L += ["", "## Le témoin hasard", "",
          "Le témoin tire le sens au hasard aux mêmes heures que V3 (graine 2026) : net moyen %s R. Sur 100 autres tirages : médiane %s R, "
          "90 %% des tirages entre %s et %s R ; %s des tirages font au moins aussi bien que V3 (%s R)." % (
              br.fr(M["Hasard"]["net"], 3), br.fr(float(np.median(moy_hasard)), 3) if len(moy_hasard) else "n.d.",
              br.fr(float(np.quantile(moy_hasard, 0.05)), 3) if len(moy_hasard) else "n.d.",
              br.fr(float(np.quantile(moy_hasard, 0.95)), 3) if len(moy_hasard) else "n.d.",
              br.pct(float((moy_hasard >= m3["net"]).mean()), 0) if len(moy_hasard) else "n.d.", br.fr(m3["net"], 3)), ""]
    L += ["## Le Monte Carlo prédit-il quelque chose ? (information)", "",
          "Pour chaque heure de décision (achat et vente hypothétiques, sans limite de position) : probabilité annoncée par la simulation contre fréquence réelle "
          "« objectif touché avant le stop » (échéance 8 h ou 20:55 UTC ; pour les décisions de 13 h à 16 h l'échéance est plus courte que les 8 h simulées, ce qui biaise vers le bas).", "",
          "| Probabilité annoncée | Cas | Annoncé en moyenne | Réalisé |", "|---|---|---|---|"] + cal_tab + [
          "", "Corrélation de rang entre probabilité annoncée et réussite réelle : %s (décisions de 08 h à 12 h seulement, échéance complète de 8 h : %s)." % (
              br.fr(cal_corr, 3), br.fr(cal_corr_m, 3)), ""]
    if boot:
        L += ["## Monte Carlo des résultats de V1 (information)", "",
              "10 000 rééchantillonnages au hasard (avec remise) des %d trades de V1 : probabilité que le total soit positif = %s ; "
              "total entre %s et %s R (5 %% à 95 %%) ; perte maximale médiane %s R (95 %% des cas sous %s R). "
              "Cela mesure la part de chance dans l'ordre des trades, pas la validité de la règle dans le futur." % (
                  m1["n"], br.pct(boot["p_pos"], 0), br.fr(boot["q05"], 1), br.fr(boot["q95"], 1), br.fr(boot["dd_med"], 1), br.fr(boot["dd_95"], 1)), ""]
    L += ["## À retenir", "",
          "- Nombre d'essais cumulés dans ce dépôt : environ %d + 3 variantes de cette stratégie." % N_ESSAIS_PRECEDENTS,
          "- Le témoin hasard et V3 servent à savoir si le Monte Carlo **apporte** quelque chose en plus de la tendance : voir le critère 6.",
          "- Les paramètres (seuils 0,50 / 0,15, stop 1,0 A, objectif 1,5 A, fenêtre de 96 variations) n'ont pas été ajustés après ce test.",
          "- Frais supposés : 0,02 % l'aller-retour (à remplacer par le vrai spread de ton courtier). Impôt : 31,4 % (flat tax 2026), sans conseil fiscal.", "",
          "Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.", ""]
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    rapport()
