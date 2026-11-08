"""Moteur de paper trading 5 min : rejoue les barres, inscrit les ordres de chaque stratégie, écrit le journal.

  python scripts/papier/moteur.py            # mode quotidien : journal/ (depuis le 9 nov 2026 00:00 UTC)
  python scripts/papier/moteur.py --histo    # rejoue tout l'historique 5 min -> resultats/papier_histo.md (une seule fois, 29 essais)

Le journal est recalculé en entier à chaque exécution (déterministe) : pas d'état caché, pas de doublon.
"""
import glob
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backtests"))
from strategies import RETOUR, STRATEGIES, TENDANCE  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent.parent
DEBUT_PAPIER = pd.Timestamp("2026-11-09 00:00", tz="UTC")
STOP_ATR = 2.0
OBJECTIF = {TENDANCE: 4.0, RETOUR: 1.5}
DUREE_MAX = {TENDANCE: 36, RETOUR: 24}
HEURE_DEBUT, HEURE_FIN, MIN_CLOTURE = 7 * 60, 20 * 60, 20 * 60 + 55
FRAIS_BASE, FRAIS_STRESS = 0.0002, 0.0005
RISQUE_USD = 50.0
NB_ESSAIS = 28


def charger(jours=None):
    morceaux = []
    for f in sorted(glob.glob(str(RACINE / "data" / "histo" / "xauusd_5m_*.csv.gz"))):
        morceaux.append(pd.read_csv(f))
    x = pd.concat(morceaux)
    x["t"] = pd.to_datetime(x["date_utc"], utc=True)
    x = x.drop_duplicates("t").set_index("t").sort_index()
    if jours:
        x = x[x.index >= x.index[-1].normalize() - pd.Timedelta(days=jours)]
    return x[["open", "high", "low", "close", "volume"]].astype(float)


def preparer(df):
    n = len(df)
    m = (df.index.hour * 60 + df.index.minute).values
    dow = df.index.dayofweek.values
    jour = df.index.normalize()
    cl = pd.Series(np.where(m == MIN_CLOTURE, np.arange(n), np.nan), index=df.index).groupby(jour).transform("max").values
    return {"n": n, "m": m, "dow": dow, "cl": cl}


def atr14(df):
    h, l, c = df.high, df.low, df.close
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(14).mean().values


def simuler(df, aux, atr, achat, vente, famille, debut=None):
    """Retourne la liste des ordres clos. Un signal à la clôture de la barre i entre à l'ouverture de i+1."""
    o, h, l, c, v = (df[k].values for k in ("open", "high", "low", "close", "volume"))
    n, m, dow, cl = aux["n"], aux["m"], aux["dow"], aux["cl"]
    ts = df.index
    dernier_jour = ts[-1].normalize()
    mult, duree = OBJECTIF[famille], DUREE_MAX[famille]
    sig_a, sig_v = achat.fillna(False).values, vente.fillna(False).values
    cands = np.nonzero(sig_a | sig_v)[0]
    ordres, libre = [], -1
    for i in cands:
        j = i + 1
        if j >= n or j <= libre or v[i] <= 0:
            continue
        if dow[j] > 4 or not (HEURE_DEBUT <= m[j] < HEURE_FIN) or not atr[i] > 0:
            continue
        cj = cl[j]
        if math.isnan(cj):
            if ts[j].normalize() != dernier_jour:
                continue                    # jour sans barre de 20:55 (données manquantes) : pas d'ordre
            cj = float(n + 10 ** 6)         # jour en cours : la clôture n'est pas encore connue
        if debut is not None and ts[j] < debut:
            continue
        sg = 1 if sig_a[i] and not sig_v[i] else (-1 if sig_v[i] and not sig_a[i] else 0)
        if sg == 0:
            continue
        a = atr[i]
        entree = o[j]
        d = STOP_ATR * a
        stop, cible = entree - sg * d, entree + sg * mult * a
        fin_regle = int(min(j + duree - 1, cj))
        fin = min(fin_regle, n - 1)
        hh, ll, oo = h[j:fin + 1], l[j:fin + 1], o[j:fin + 1]
        if sg > 0:
            s_hit, t_hit = ll <= stop, hh >= cible
        else:
            s_hit, t_hit = hh >= stop, ll <= cible
        si = int(np.argmax(s_hit)) if s_hit.any() else None
        ti = int(np.argmax(t_hit)) if t_hit.any() else None
        if si is not None and (ti is None or si <= ti):
            k = si
            px = stop if k == 0 else (min(stop, oo[k]) if sg > 0 else max(stop, oo[k]))
            motif = "stop"
        elif ti is not None:
            k, px, motif = ti, cible, "objectif"
        elif fin_regle <= n - 1:
            k, px = len(hh) - 1, c[fin]
            motif = "clôture 21h" if fin == int(cj) and fin < j + duree - 1 else "durée max"
        else:
            continue            # ordre encore ouvert à la fin des données : sera inscrit quand il sera clos
        sortie = j + k
        libre = sortie
        taille = RISQUE_USD / d
        brut_usd = sg * (px - entree) * taille
        ordres.append({"entree_ts": ts[j], "sens": "achat" if sg > 0 else "vente", "entree": entree, "stop": stop, "objectif": cible,
                       "sortie_ts": ts[sortie], "sortie": px, "motif": motif, "duree_min": int((sortie - j + 1) * 5), "taille_oz": taille,
                       "R_brut": sg * (px - entree) / d, "R_net": sg * (px - entree) / d - FRAIS_BASE * entree / d,
                       "R_stress": sg * (px - entree) / d - FRAIS_STRESS * entree / d,
                       "gain_usd_brut": brut_usd, "frais_usd": FRAIS_BASE * entree * taille, "gain_usd_net": brut_usd - FRAIS_BASE * entree * taille})
    return ordres


def tout_simuler(df, debut=None):
    aux, atr = preparer(df), atr14(df)
    rows = []
    for num, nom, famille, f in STRATEGIES:
        achat, vente = f(df)
        for o in simuler(df, aux, atr, achat, vente, famille, debut):
            o.update({"num": num, "strategie": nom, "famille": famille})
            rows.append(o)
    cols = ["num", "strategie", "famille", "sens", "entree_ts", "entree", "stop", "objectif", "sortie_ts", "sortie", "motif", "duree_min", "taille_oz",
            "R_brut", "R_net", "R_stress", "gain_usd_brut", "frais_usd", "gain_usd_net"]
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows)[cols].sort_values(["entree_ts", "num"]).reset_index(drop=True)


def fr(x, d=2):
    return ("{:." + str(d) + "f}").format(x).replace(".", ",")


def t_stat(x):
    x = np.asarray(x, dtype=float)
    return x.mean() / (x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 2 and x.std() > 0 else float("nan")


def resume(ordres, jours):
    """Tableau par stratégie (Markdown) pour un ensemble d'ordres."""
    import backtest_regime as br
    L = ["| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    lignes = []
    for num, nom, famille, _ in STRATEGIES:
        x = ordres[ordres["num"] == num]
        n = len(x)
        if n == 0:
            lignes.append((-9, "| %d | %s | %s | 0 | 0 | — | — | — | — | — | — | — | — |" % (num, nom, famille)))
            continue
        r = x["R_net"].values
        dsr = br.deflated_sharpe(r, NB_ESSAIS, 1 / math.sqrt(n - 1)) if n >= 30 else float("nan")
        lignes.append((r.mean(), "| %d | %s | %s | %d | %s | %s %% | %s | %s | %s | %s | %s | %s | %s |" % (
            num, nom, famille, n, fr(n / max(jours, 1), 1), fr((r > 0).mean() * 100, 0), fr(x["R_brut"].mean(), 3), fr(r.mean(), 3), fr(t_stat(r), 1), fr(r.sum(), 1),
            fr(x["R_stress"].sum(), 1), fr(x["gain_usd_net"].sum(), 0), "—" if math.isnan(dsr) else fr(dsr, 2))))
    L += [l for _, l in sorted(lignes, key=lambda z: -z[0])]
    return L


def ecrire_journal(ordres, df):
    jdir = RACINE / "journal"
    (jdir / "jours").mkdir(parents=True, exist_ok=True)
    o = ordres.copy()
    o.to_csv(jdir / "ordres.csv", index=False, float_format="%.4f", date_format="%Y-%m-%d %H:%M")
    jours_bourse = max(1, int(np.busday_count(DEBUT_PAPIER.date(), (df.index[-1] + pd.Timedelta(seconds=1)).date())))
    fin_donnees = df.index[-1]
    periode = ("Du %s au %s UTC (%d jours de bourse)." % (DEBUT_PAPIER.strftime("%Y-%m-%d"), fin_donnees.strftime("%Y-%m-%d %H:%M"), jours_bourse)
               if fin_donnees >= DEBUT_PAPIER else "Départ le %s UTC : les données du premier jour n'ont pas encore été téléchargées." % DEBUT_PAPIER.strftime("%Y-%m-%d"))
    cl = ["# Classement cumulé des stratégies (paper trading 5 min)", "",
          "%s **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0)." % periode, "",
          "R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.", ""]
    cl += resume(o, jours_bourse) if len(o) else ["Aucun ordre clos pour l'instant."]
    cl += ["", "Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile."]
    (jdir / "classement.md").write_text("\n".join(cl) + "\n", encoding="utf-8")
    if len(o):
        o["jour"] = o["entree_ts"].dt.strftime("%Y-%m-%d")
        for jour, x in o.groupby("jour"):
            L = ["# Ordres du %s (paper trading 5 min)" % jour, "",
                 "Heures de Paris. R = risque du trade ; gain net = après frais de base (0,02 %). Compte fictif de 10 000 $, risque de 50 $ par ordre.", "",
                 "| N° | Stratégie | Sens | Entrée (Paris) | Prix | Stop | Objectif | Sortie (Paris) | Prix | Motif | Durée | Taille | R net | Gain net $ |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
            for _, r in x.iterrows():
                L.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %d min | %s oz | %s | %s |" % (
                    r.num, r.strategie, r.sens, r.entree_ts.tz_convert("Europe/Paris").strftime("%H:%M"), fr(r.entree, 2), fr(r.stop, 2), fr(r.objectif, 2),
                    r.sortie_ts.tz_convert("Europe/Paris").strftime("%H:%M"), fr(r.sortie, 2), r.motif, r.duree_min, fr(r.taille_oz, 2), fr(r.R_net, 2), fr(r.gain_usd_net, 1)))
            g, p = x[x["R_net"] > 0], x[x["R_net"] <= 0]
            L += ["", "**Bilan du jour (hors témoin) :** %d ordres, %d gagnants, %d perdants, R net %s, gain net %s $." % (
                len(x[x.num != 0]), len(g[g.num != 0]), len(p[p.num != 0]), fr(x[x.num != 0]["R_net"].sum(), 2), fr(x[x.num != 0]["gain_usd_net"].sum(), 1)),
                  "Témoin hasard : %d ordres, R net %s." % (len(x[x.num == 0]), fr(x[x.num == 0]["R_net"].sum(), 2)), ""]
            par = x[x.num != 0].groupby(["num", "strategie"])[["R_net", "gain_usd_net"]].sum().reset_index().sort_values("R_net", ascending=False)
            L += ["**Par stratégie (R net / gain net $) :** " + " ; ".join("%s %s / %s" % (r.strategie, fr(r.R_net, 2), fr(r.gain_usd_net, 0)) for r in par.itertuples()), ""]
            (jdir / "jours" / ("%s.md" % jour)).write_text("\n".join(L) + "\n", encoding="utf-8")


def mode_quotidien():
    df = charger(jours=None)
    debut_donnees = DEBUT_PAPIER - pd.Timedelta(days=14)
    df = df[df.index >= debut_donnees]            # 14 jours de chauffe pour les indicateurs, déterministe
    ordres = tout_simuler(df, debut=DEBUT_PAPIER)
    ecrire_journal(ordres, df)
    print("Ordres clos : %d ; données jusqu'au %s UTC" % (len(ordres), df.index[-1]))


def mode_histo():
    import backtest_regime as br
    df = charger()
    ordres = tout_simuler(df)
    jours = int(np.busday_count(df.index[0].date(), df.index[-1].date()))
    L = ["# Paper trading 5 min : les 28 stratégies rejouées sur tout l'historique", "",
         "Règles figées dans `regles/papier_5m_v1.md` avant ce calcul, jamais ajustées. Or au comptant 5 min du %s au %s, **%d jours de bourse**. Exécuté **une seule fois** (29 essais comptés dans le projet, avec le témoin). Même moteur que le suivi quotidien." % (
             df.index[0].date(), df.index[-1].date(), jours), "",
         "R net = après frais de base (0,02 % l'aller-retour) ; R stress = frais de 0,05 %. Le Deflated Sharpe tient compte des 28 essais.", ""]
    L += resume(ordres, jours)
    moit = df.index[len(df) // 2]
    L += ["", "### Première moitié contre seconde moitié (R net moyen par ordre)", "", "| N° | Stratégie | 1re moitié (ordres / R net moyen) | 2e moitié (ordres / R net moyen) |", "| --- | --- | --- | --- |"]
    for num, nom, famille, _ in STRATEGIES:
        x = ordres[ordres["num"] == num]
        a, b = x[x["entree_ts"] < moit]["R_net"], x[x["entree_ts"] >= moit]["R_net"]
        L.append("| %d | %s | %d / %s | %d / %s |" % (num, nom, len(a), fr(a.mean(), 3) if len(a) else "—", len(b), fr(b.mean(), 3) if len(b) else "—"))
    t = ordres[ordres["num"] != 0]
    L += ["", "Parmi les 28 stratégies : %d ont un R net moyen positif, dont %d avec t ≥ 2 ; avec 28 essais, environ 1 à 2 stratégies passent t ≥ 2 par pur hasard. Témoin hasard : R net moyen %s (%d ordres)." % (
        sum(1 for num in range(1, 29) if len(ordres[ordres.num == num]) and ordres[ordres.num == num]["R_net"].mean() > 0),
        sum(1 for num in range(1, 29) if len(ordres[ordres.num == num]) > 2 and t_stat(ordres[ordres.num == num]["R_net"]) >= 2),
        fr(ordres[ordres.num == 0]["R_net"].mean(), 3), len(ordres[ordres.num == 0])),
        "", "Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile."]
    out = RACINE / "resultats" / "papier_histo.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    mode_histo() if "--histo" in sys.argv else mode_quotidien()
