"""Stratégie « Confluence Monte Carlo » v2 : règles dans regles/montecarlo_intraday_v2.md (figées avant le test).
Lancé une seule fois sur les 14 ans de barres 5 min de l'or.

  python scripts/backtests/backtest_montecarlo_v2.py   # -> resultats/montecarlo_intraday_v2.md

Réutilise les briques du backtest v1 (données, ATR/EMA horaires, fenêtre de variations de 15 min, mesures, Deflated Sharpe).
Précisions d'implémentation (choisies avant le test) : SMA 50 des clôtures de séance connues la veille ; volume relatif =
volume de la dernière heure civile terminée / moyenne de la même heure des 20 jours ouvrés précédents ; médiane d'ATR sur
les 1 200 dernières barres 1 h ; tout est lu sur des barres terminées à l'heure de décision.
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_compression as bc  # noqa: E402
import backtest_montecarlo as bm  # noqa: E402
import backtest_regime as br  # noqa: E402

NS, JOUR_NS = bm.NS, bm.JOUR_NS
ANCRAGE_H = 7
FENETRE, CHEMINS, PAS = 480, 2000, 40          # 480 variations de 15 min, 2 000 trajectoires de 40 pas (07:00 -> 17:00)
GRAINE = 2026
IDX2 = np.random.default_rng(GRAINE).integers(0, FENETRE, size=(CHEMINS, PAS))
PAS_DECISION = range(4, 39, 2)                  # 08:00, 08:30 … 16:30 UTC
STOP_A, D_MIN, D_MAX = 1.5, 1.0, 3.0
DUREE_MAX = 6 * 3600
MAX_PAR_JOUR = 2
Z_25, Z_05 = 0.6744897501960817, 1.6448536269514722
N_ESSAIS, CUMUL = 5, 358
FRAIS_BASE, FRAIS_STRESS = bm.FRAIS_BASE, bm.FRAIS_STRESS
SORTIE = br.RACINE / "resultats" / "montecarlo_intraday_v2.md"


# ------------------------------------------------------------------ préparation
def extras(df, P):
    """Tendance journalière, médiane d'ATR et volume relatif, tous connus à l'heure de décision."""
    a = df[df["volume"] > 0]
    seance = (a.index + pd.Timedelta(hours=2)).normalize()
    dc = a["close"].groupby(seance).last()
    ecart = dc - dc.rolling(50).mean()
    P.d_lab = bm._ns(dc.index)
    P.d_trend = np.nan_to_num(np.sign(ecart.to_numpy()), nan=0.0)
    P.atr_med = pd.Series(P.atr).rolling(1200, min_periods=600).median().to_numpy()
    hv = df["volume"].resample("1h").sum()
    t = pd.DataFrame({"j": hv.index.normalize(), "h": hv.index.hour, "v": hv.values.astype(float)})
    tab = t.pivot(index="j", columns="h", values="v").reindex(columns=range(24))
    tab = tab[tab.index.dayofweek < 5].where(lambda x: x > 0)
    P.rv_jours = bm._ns(tab.index)
    P.rv_vol = tab.to_numpy()
    P.rv_ref = tab.rolling(20, min_periods=15).mean().shift(1).to_numpy()
    return P


def preparer(df):
    return extras(df, bm.preparer(df))


# ------------------------------------------------------------------ cône Monte Carlo
def cone(fenetre, idx=IDX2):
    """Niveaux simulés (en log, par rapport au prix d'ancrage) : trajectoires triées pas par pas et médiane de chaque pas."""
    cum = np.cumsum(np.asarray(fenetre)[idx], axis=1)
    return np.sort(cum, axis=0), np.median(cum, axis=0)


def position_q(tri, m, x):
    """Part des trajectoires dont le niveau au pas m (1…40) est inférieur à x : 0 = bas du cône, 1 = haut."""
    return float(np.searchsorted(tri[:, m - 1], x, side="left")) / tri.shape[0]


def decisions(P):
    lignes = []
    for jour in P.jours:
        jour = int(jour)
        ta = jour + ANCRAGE_H * 3600 * NS
        ia = int(np.searchsorted(P.t, ta))
        if ia >= len(P.t) or P.t[ia] != ta or P.vol[ia] <= 0:
            continue
        k = int(np.searchsorted(P.r_fin, ta, side="right"))
        if k < FENETRE or ta - P.r_fin[k - FENETRE] > 10 * JOUR_NS:
            continue
        fen = P.r_val[k - FENETRE:k]
        sigma = float(fen.std(ddof=1))
        if not sigma > 0:
            continue
        tri, med = cone(fen)
        biais = float(np.sign(med[-1]))
        pa = float(P.o[ia])
        d = int(np.searchsorted(P.d_lab, jour, side="left")) - 1
        dtrend = float(P.d_trend[d]) if d >= 0 and jour - P.d_lab[d] <= 6 * JOUR_NS else 0.0
        row = int(np.searchsorted(P.rv_jours, jour))
        row_ok = row < len(P.rv_jours) and P.rv_jours[row] == jour
        for m in PAS_DECISION:
            T = ta + m * 15 * 60 * NS
            i0 = int(np.searchsorted(P.t, T))
            if i0 >= len(P.t) or P.t[i0] != T or P.vol[i0] <= 0:
                continue
            j = int(np.searchsorted(P.h_fin, T, side="right")) - 1
            if j < 200 or T - P.h_fin[j] > 2 * 3600 * NS or not (P.atr[j] > 0) or not np.isfinite(P.atr_med[j]):
                continue
            echeance = min(T + DUREE_MAX * NS, jour + bm.SORTIE_S * NS)
            i_dl = int(np.searchsorted(P.t, echeance))
            if i_dl >= len(P.t) or P.t[i_dl] - echeance > 30 * 60 * NS:
                continue
            x = math.log(float(P.o[i0]) / pa)
            rv = float("nan")
            if row_ok:
                hl = int((T // NS % 86400) // 3600) - 1
                v, r = P.rv_vol[row, hl], P.rv_ref[row, hl]
                if v > 0 and r > 0:
                    rv = float(v / r)
            lignes.append((T, jour, i0, i_dl, float(P.atr[j]), float(P.atr_med[j]), float(P.ema20[j]), float(P.ema100[j]), dtrend, biais,
                           position_q(tri, m, x), x / (sigma * math.sqrt(m)), rv, pa * math.exp(float(med[m - 1])), pa))
    s = pd.DataFrame(lignes, columns=["T", "jour", "i0", "i_dl", "A", "atr_med", "ema20", "ema100", "dtrend", "biais", "q", "z", "rv",
                                      "cible_mc", "cible_z"])
    s["date"] = pd.to_datetime(s["T"], unit="ns", utc=True)
    return s


def directions(s):
    """Sens de chaque variante (+1 achat, -1 vente, 0 rien) à chaque décision."""
    filtre = (s["A"] >= s["atr_med"]) & (s["rv"] >= 1.0)           # NaN -> faux
    tend_h = (s["dtrend"] > 0) & (s["ema20"] > s["ema100"])
    tend_b = (s["dtrend"] < 0) & (s["ema20"] < s["ema100"])
    ach_mc = (s["biais"] > 0) & (s["q"] > 0.05) & (s["q"] <= 0.25)
    ven_mc = (s["biais"] < 0) & (s["q"] >= 0.75) & (s["q"] < 0.95)
    ach_z = (s["z"] > -Z_05) & (s["z"] <= -Z_25)
    ven_z = (s["z"] >= Z_25) & (s["z"] < Z_05)

    def sens(h, b):
        return np.where(h, 1, np.where(b, -1, 0))

    return {"F": sens(tend_h & ach_mc & filtre, tend_b & ven_mc & filtre),
            "Fz": sens(tend_h & ach_z & filtre, tend_b & ven_z & filtre),
            "Fnt": sens(ach_mc & filtre, ven_mc & filtre),
            "Fnv": sens(tend_h & ach_mc, tend_b & ven_mc)}


def distances(P, s, sens, cle):
    """Distance à l'objectif (en dollars, dans le sens du trade), plafonnée à 3 A ; NaN (= pas de trade) si inférieure à 1 A."""
    a = s["A"].to_numpy()
    d = sens * (s[cle].to_numpy() - P.o[s["i0"].to_numpy()])
    d = np.minimum(d, D_MAX * a)
    d[(sens == 0) | (d < D_MIN * a)] = np.nan
    return d


# ------------------------------------------------------------------ simulation
def sortie(t, o, h, l, i0, i_dl, sens, stop_d, tgt_d):
    """Entrée à l'ouverture de i0 ; stop et objectif en dollars ; sortie à l'ouverture de i_dl. Stop prioritaire dans une même barre ;
    stop gappé : prix d'ouverture. Renvoie (prix, motif, fin en ns)."""
    entree = o[i0]
    stop, cible = entree - sens * stop_d, entree + sens * tgt_d
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


def simuler(P, s, sens, dist):
    """Une position à la fois, 2 trades par jour au plus ; 1 R = distance du stop (1,5 A)."""
    libre, par_jour, lignes = -1, {}, []
    T, J, I0, IDL, A = (s[c].to_numpy() for c in ("T", "jour", "i0", "i_dl", "A"))
    for k in range(len(s)):
        sg = int(sens[k])
        if sg == 0 or not np.isfinite(dist[k]) or T[k] < libre or par_jour.get(J[k], 0) >= MAX_PAR_JOUR:
            continue
        stop_d = STOP_A * float(A[k])
        px, motif, fin = sortie(P.t, P.o, P.h, P.l, int(I0[k]), int(IDL[k]), sg, stop_d, float(dist[k]))
        entree = float(P.o[I0[k]])
        brut = sg * (px - entree) / stop_d
        r = entree / stop_d
        lignes.append((s["date"].iloc[k], sg, entree, px, motif, stop_d, brut, brut - FRAIS_BASE * r, brut - FRAIS_STRESS * r))
        libre = fin
        par_jour[J[k]] = par_jour.get(J[k], 0) + 1
    return pd.DataFrame(lignes, columns=["date", "sens", "entree", "sortie", "motif", "A", "brut", "net", "stress"])


# ------------------------------------------------------------------ mesures
def mesures(tr, jours):
    m = bm.mesures(tr, jours)
    x = bm.serie_quotidienne(tr, jours)
    m["dsr5"], m["dsr358"] = bm.dsr(x.values, N_ESSAIS), bm.dsr(x.values, CUMUL)
    return m


def calibration_cone(P, s):
    """Information : là où D et H vont dans le même sens, rendement des 4 h suivantes (dans le sens de la tendance) selon la position
    dans le cône (q ramené dans le sens de la tendance : bas = repli profond contre la tendance)."""
    tend = np.where((s["dtrend"] > 0) & (s["ema20"] > s["ema100"]), 1, np.where((s["dtrend"] < 0) & (s["ema20"] < s["ema100"]), -1, 0))
    tf = s["T"].to_numpy() + 4 * 3600 * NS
    i_f = np.searchsorted(P.t, tf)
    i_c = np.minimum(i_f, len(P.t) - 1)
    ok = (tend != 0) & (i_f < len(P.t)) & (P.t[i_c] - tf <= 30 * 60 * NS)
    sg, e, f = tend[ok], P.o[s["i0"].to_numpy()[ok]], P.o[i_c[ok]]
    q = s["q"].to_numpy()[ok]
    return pd.DataFrame({"q": np.where(sg > 0, q, 1 - q), "bps": sg * np.log(f / e) * 1e4, "A": sg * (f - e) / s["A"].to_numpy()[ok]})


def tableau_calibration(c):
    bornes = [0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0001]
    noms = ["0-5 % (repli extrême)", "5-25 % (repli profond : zone d'achat de F)", "25-50 %", "50-75 %", "75-95 %", "95-100 % (déjà très étendu)"]
    lignes = []
    for i, nom in enumerate(noms):
        x = c[(c["q"] >= bornes[i]) & (c["q"] < bornes[i + 1])]
        if len(x):
            lignes.append("| %s | %d | %s | %s | %s |" % (nom, len(x), br.fr(x["bps"].mean(), 2), br.fr(x["A"].mean(), 3), br.pct((x["bps"] > 0).mean(), 0)))
    return lignes


# ------------------------------------------------------------------ rapport
def rapport(n_boot=10000, n_hasard=100):
    df = bc.lire_5m_complet()
    P = preparer(df)
    s = decisions(P)
    sens = directions(s)
    dist = {"F": distances(P, s, sens["F"], "cible_mc"), "Fnt": distances(P, s, sens["Fnt"], "cible_mc"),
            "Fnv": distances(P, s, sens["Fnv"], "cible_mc"), "Fz": distances(P, s, sens["Fz"], "cible_z")}
    trades = {k: simuler(P, s, sens[k], dist[k]) for k in ("F", "Fz", "Fnt", "Fnv")}
    # témoin : sens tiré au hasard (graine 2026) aux heures et avec les distances de F
    declenche = (sens["F"] != 0) & np.isfinite(dist["F"])
    d_abs = np.abs(dist["F"])
    rng = np.random.default_rng(GRAINE)
    trades["Hasard"] = simuler(P, s, np.where(declenche, rng.choice([-1, 1], size=len(s)), 0), d_abs)
    moy_hasard = []
    for g in range(1, n_hasard + 1):
        r = np.random.default_rng(10_000 + g)
        tr = simuler(P, s, np.where(declenche, r.choice([-1, 1], size=len(s)), 0), d_abs)
        if len(tr):
            moy_hasard.append(float(tr["net"].mean()))
    moy_hasard = np.array(moy_hasard)
    jours = P.jours[(P.jours >= s["T"].iloc[0] - s["T"].iloc[0] % JOUR_NS) & (P.jours <= s["T"].iloc[-1])]
    M = {k: mesures(v, jours) for k, v in trades.items()}
    mF, mZ, mH = M["F"], M["Fz"], M["Hasard"]
    ans = max(1e-9, (s["date"].iloc[-1] - s["date"].iloc[0]).days / 365.25)
    boot = bm.bootstrap_trades(trades["F"]["net"].values, n_boot)
    cal = calibration_cone(P, s)

    def sup(a, b):
        return bool(a > b)          # NaN -> faux

    crit = [
        ("Gain net moyen > 0 avec t ≥ 2 en développement (2012-2019)", mF["m_dev"] > 0 and mF["t_dev"] >= 2,
         "moyenne %s R, t = %s sur %d trades" % (br.fr(mF["m_dev"], 3), br.fr(mF["t_dev"], 1), mF["n_dev"])),
        ("Gain net moyen > 0 avec t ≥ 2 en validation (2020-2026)", mF["m_val"] > 0 and mF["t_val"] >= 2,
         "moyenne %s R, t = %s sur %d trades" % (br.fr(mF["m_val"], 3), br.fr(mF["t_val"], 1), mF["n_val"])),
        ("Au moins 100 trades et 60 % d'années positives", mF["n"] >= 100 and mF["ans_tot"] > 0 and mF["ans_pos"] / mF["ans_tot"] >= 0.6,
         "%d trades, %d années positives sur %d (années de 20 trades ou plus)" % (mF["n"], mF["ans_pos"], mF["ans_tot"])),
        ("Deflated Sharpe ≥ 0,95 (5 essais)", mF["dsr5"] >= 0.95, "DSR = %s (avec 358 essais : %s)" % (br.fr(mF["dsr5"], 2), br.fr(mF["dsr358"], 2))),
        ("Rendement annuel après impôts > 0", mF["apres"] > 0, "%s par an après impôts (%s avant impôts)" % (br.pct(mF["apres"], 1), br.pct(mF["avant"], 1))),
        ("F fait mieux que Fz (sans simulation) en développement et en validation", sup(mF["m_dev"], mZ["m_dev"]) and sup(mF["m_val"], mZ["m_val"]),
         "F %s / %s R contre Fz %s / %s R (dév. / valid.)" % (br.fr(mF["m_dev"], 3), br.fr(mF["m_val"], 3), br.fr(mZ["m_dev"], 3), br.fr(mZ["m_val"], 3))),
        ("F fait mieux que le témoin hasard en développement et en validation", sup(mF["m_dev"], mH["m_dev"]) and sup(mF["m_val"], mH["m_val"]),
         "F %s / %s R contre hasard %s / %s R (dév. / valid.)" % (br.fr(mF["m_dev"], 3), br.fr(mF["m_val"], 3), br.fr(mH["m_dev"], 3), br.fr(mH["m_val"], 3))),
        ("Gain net moyen > 0 avec les frais de stress (0,05 %)", mF["stress"] > 0, "%s R par trade avec frais de stress" % br.fr(mF["stress"], 3)),
    ]
    reussis = all(c[1] for c in crit)
    nb = len(crit)
    L = ["# Stratégie « Confluence Monte Carlo » v2 : résultats", "",
         "Règles figées avant le test : `regles/montecarlo_intraday_v2.md` (recherche et description complète). Lancé une seule fois, sans retouche. "
         "Or XAUUSD, barres 5 min Dukascopy 2012-2026 ; frais de base 0,02 % l'aller-retour (stress 0,05 %), risque 0,5 % du capital par trade (1 R = distance du stop, 1,5 ATR horaire). "
         "Développement 2012-2019, validation 2020-2026.", "",
         "## Verdict", "",
         ("**F passe les %d critères figés.** Cela reste un résultat de backtest : à confirmer en avant avant de lui faire confiance." % nb if reussis else
          "**F ne passe pas tous les critères figés (%d sur %d réussis) : elle n'est pas « solide » au sens que nous avions fixé.** Les chiffres sont publiés tels quels, sans retouche de la règle." % (
              sum(1 for c in crit if c[1]), nb)),
         "", "| Critère (figé avant le test) | Résultat | Détail |", "|---|---|---|"]
    for nom, ok, det in crit:
        L.append("| %s | %s | %s |" % (nom, "✔ réussi" if ok else "✘ échoué", det))
    L += ["", "## Les variantes", "",
          "Moyennes par trade en R (1 R = distance du stop). Brut = sans frais ; net = frais de base ; stress = frais 0,05 %. t = test de Newey-West sur le net.", "",
          "| Variante | Trades | par semaine | gagnants | brut | net | t | net (stress) | années positives |", "|---|---|---|---|---|---|---|---|---|",
          bm.ligne_variante("F complète (Monte Carlo + tendances + filtres)", mF, ans), bm.ligne_variante("Fz sans simulation (écart normalisé)", mZ, ans),
          bm.ligne_variante("Fnt sans tendances", M["Fnt"], ans), bm.ligne_variante("Fnv sans filtres volatilité/volume", M["Fnv"], ans),
          bm.ligne_variante("Témoin hasard (aux heures de F)", mH, ans), "",
          "| Variante | dév. : trades | dév. : net R | dév. : t | valid. : trades | valid. : net R | valid. : t | rend. annuel avant impôts | après impôts (31,4 %) | DSR (5 essais) | DSR (358 essais) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in ("F", "Fz", "Fnt", "Fnv", "Hasard"):
        m = M[k]
        L.append("| %s | %d | %s | %s | %d | %s | %s | %s | %s | %s | %s |" % (
            k, m["n_dev"], br.fr(m["m_dev"], 3), br.fr(m["t_dev"], 1), m["n_val"], br.fr(m["m_val"], 3), br.fr(m["t_val"], 1),
            br.pct(m["avant"], 1), br.pct(m["apres"], 1), br.fr(m["dsr5"], 2), br.fr(m["dsr358"], 2)))
    sorties = ", ".join("%s %d" % (k, v) for k, v in trades["F"]["motif"].value_counts().items()) if len(trades["F"]) else "aucun trade"
    L += ["", "Sorties de F : %s." % sorties,
          "Heures de décision évaluées : %d ; déclenchements (sens ≠ 0, distance à l'objectif valide) : F %d, Fz %d, Fnt %d, Fnv %d." % (
              len(s), int(((sens["F"] != 0) & np.isfinite(dist["F"])).sum()), int(((sens["Fz"] != 0) & np.isfinite(dist["Fz"])).sum()),
              int(((sens["Fnt"] != 0) & np.isfinite(dist["Fnt"])).sum()), int(((sens["Fnv"] != 0) & np.isfinite(dist["Fnv"])).sum())), ""]
    L += ["## F année par année", "", "| Année | Trades | net moyen (R) | total (R) |", "|---|---|---|---|"]
    if len(trades["F"]):
        for an, g in trades["F"].groupby(trades["F"]["date"].dt.year):
            L.append("| %d | %d | %s | %s |" % (an, len(g), br.fr(g["net"].mean(), 3), br.fr(g["net"].sum(), 1)))
    q05 = br.fr(float(np.quantile(moy_hasard, 0.05)), 3) if len(moy_hasard) else "n.d."
    q95 = br.fr(float(np.quantile(moy_hasard, 0.95)), 3) if len(moy_hasard) else "n.d."
    med = br.fr(float(np.median(moy_hasard)), 3) if len(moy_hasard) else "n.d."
    part = br.pct(float((moy_hasard >= mF["net"]).mean()), 0) if len(moy_hasard) and mF["n"] else "n.d."
    L += ["", "## Le témoin hasard", "",
          "Le témoin tire le sens au hasard aux mêmes heures que F, avec les mêmes stop et objectif (graine 2026) : net moyen %s R. "
          "Sur 100 autres tirages : médiane %s R, 90 %% des tirages entre %s et %s R ; %s des tirages font au moins aussi bien que F (%s R)." % (
              br.fr(mH["net"], 3), med, q05, q95, part, br.fr(mF["net"], 3)), "",
          "## Le repli dans le cône prédit-il quelque chose ? (information)", "",
          "Pour tous les moments où la tendance journalière et la tendance horaire vont dans le même sens : rendement des 4 heures suivantes, "
          "compté dans le sens de la tendance, selon la position du prix dans le cône Monte Carlo (en bas = repli profond contre la tendance). "
          "Les observations se chevauchent (une toutes les 30 min) : à lire comme une tendance générale, pas comme un test.", "",
          "| Position dans le cône | Cas | rendement moyen 4 h (points de base) | en ATR | part positive |", "|---|---|---|---|---|"] + tableau_calibration(cal) + [""]
    if boot:
        L += ["## Monte Carlo des résultats de F (information)", "",
              "10 000 rééchantillonnages au hasard (avec remise) des %d trades de F : probabilité que le total soit positif = %s ; "
              "total entre %s et %s R (5 %% à 95 %%) ; perte maximale médiane %s R (95 %% des cas sous %s R). "
              "Cela mesure la part de chance dans l'ordre des trades, pas la validité de la règle dans le futur." % (
                  mF["n"], br.pct(boot["p_pos"], 0), br.fr(boot["q05"], 1), br.fr(boot["q95"], 1), br.fr(boot["dd_med"], 1), br.fr(boot["dd_95"], 1)), ""]
    L += ["## À retenir", "",
          "- Essais cumulés dans ce dépôt : environ %d (dont les 5 variantes de ce test)." % CUMUL,
          "- Fz et le témoin hasard servent à savoir si la **simulation** apporte quelque chose en plus d'un simple écart normalisé et d'un tirage au sort (critères 5 et 6).",
          "- Aucun paramètre n'a été ajusté après ce test (fenêtre de 480 variations, 2 000 trajectoires, bornes 0,05 / 0,25, stop 1,5 A, objectif = médiane du cône entre 1 et 3 A).",
          "- Frais supposés : 0,02 % l'aller-retour (à remplacer par le vrai spread de ton courtier). Impôt : 31,4 % (flat tax 2026), sans conseil fiscal.", "",
          "Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.", ""]
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    rapport()
