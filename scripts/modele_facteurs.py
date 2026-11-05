"""Modèle multi-facteurs v1 : probabilité que l'or monte le lendemain (clôture à clôture).

Règles figées avant le test : 16 facteurs ; 2 modèles (régression logistique, petits arbres) ;
réentraînement tous les 63 jours sur tout le passé, premier test après 5 ans de données ;
position seulement si p >= 0,55 (achat) ou p <= 0,45 (vente), tenue 1 jour ; frais 0,05 % par ordre.
Aucun paramètre n'est ajusté après avoir vu les résultats."""
import datetime as dt
import math
import random
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_or import metriques, fr  # noqa: E402

warnings.filterwarnings("ignore")
RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "resultats" / "modele_facteurs_v1.md"
FRAIS = 0.0005
SEUIL = 0.05
PAS, DEPART = 63, 1250


def serie(nom, fichier):
    df = pd.read_csv(RACINE / "data" / fichier)
    df["date"] = pd.to_datetime(df["date_utc"].str[:10])
    return df.drop_duplicates("date", keep="last").set_index("date")["close"].rename(nom)


def construire():
    or_ = pd.read_csv(RACINE / "data" / "or_ohlc_jour.csv")
    or_["date"] = pd.to_datetime(or_["date_utc"].str[:10])
    or_ = or_.drop_duplicates("date", keep="last").set_index("date")["close"].rename("or")
    if or_.index[-1].date() >= dt.datetime.now(dt.timezone.utc).date():
        or_ = or_.iloc[:-1]  # séance du jour pas terminée
    noms = {"dxy": "facteur_dollar_dxy.csv", "t10": "facteur_taux_10ans.csv", "t5": "facteur_taux_5ans.csv",
            "ag": "facteur_argent.csv", "vix": "facteur_vix.csv", "spx": "facteur_sp500.csv",
            "wti": "facteur_petrole_wti.csv"}
    d = pd.concat([or_] + [serie(k, f) for k, f in noms.items()], axis=1).loc[or_.index[0]:or_.index[-1]]
    d = d.dropna(subset=["or"]).ffill(limit=3)
    d = d[d["or"] > 0]
    lr = lambda s, n: np.log(s / s.shift(n))
    zd = lambda s, n: s.diff(n) / s.diff().rolling(60).std()
    f = pd.DataFrame(index=d.index)
    f["or_1j"], f["or_5j"], f["or_20j"] = lr(d["or"], 1), lr(d["or"], 5), lr(d["or"], 20)
    f["dist_ma20"] = d["or"] / d["or"].rolling(20).mean() - 1
    f["dist_ma50"] = d["or"] / d["or"].rolling(50).mean() - 1
    f["vol_20j"] = lr(d["or"], 1).rolling(20).std()
    f["dollar_1j"], f["dollar_5j"] = lr(d["dxy"], 1), lr(d["dxy"], 5)
    f["taux10_1j"], f["taux10_5j"] = zd(d["t10"], 1), zd(d["t10"], 5)
    f["pente_5j"] = zd(d["t10"] - d["t5"], 5)
    f["argent_1j"], f["argent_5j"] = lr(d["ag"], 1), lr(d["ag"], 5)
    f["vix_z"] = (d["vix"] - d["vix"].rolling(60).mean()) / d["vix"].rolling(60).std()
    f["vix_1j"] = lr(d["vix"], 1)
    f["sp500_5j"], f["petrole_5j"] = lr(d["spx"], 5), lr(d["wti"], 5)
    f = f.replace([np.inf, -np.inf], np.nan)
    suivant = d["or"].shift(-1) / d["or"] - 1
    return f, suivant


def modeles():
    return {"Régression logistique": lambda: LogisticRegression(C=0.1, max_iter=500),
            "Petits arbres": lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05,
                                                                     l2_regularization=1.0, random_state=0)}


def marche_avant(X, r, fabrique):
    y = (r > 0).astype(int).values
    idx = np.where(~X.isna().any(axis=1) & r.notna())[0]
    proba = pd.Series(np.nan, index=X.index)
    base = pd.Series(np.nan, index=X.index)
    pos = idx[idx >= DEPART] if len(idx) else idx
    debut = idx[DEPART] if len(idx) > DEPART else None
    if debut is None:
        return proba, base
    for s in range(debut, len(X), PAS):
        tr = idx[idx < s]
        te = [i for i in range(s, min(s + PAS, len(X))) if i in set(idx)]
        if not te or len(tr) < DEPART:
            continue
        sc = StandardScaler().fit(X.iloc[tr])
        m = fabrique().fit(sc.transform(X.iloc[tr]), y[tr])
        proba.iloc[te] = m.predict_proba(sc.transform(X.iloc[te]))[:, 1]
        base.iloc[te] = y[tr].mean()
    return proba, base


def trades_de(p, r, frais=1.0):
    t = []
    for i in np.where(p.notna() & r.notna())[0]:
        if p.iloc[i] >= 0.5 + SEUIL:
            sens = 1
        elif p.iloc[i] <= 0.5 - SEUIL:
            sens = -1
        else:
            continue
        t.append({"R": (sens * r.iloc[i] - FRAIS * frais) * 100, "jours": 1, "sens": sens, "i": i})
    return t


def hasard(p, r, a, b, n, part_achats, rng, tirages=2000):
    idx = [i for i in range(a, b) if not math.isnan(r.iloc[i]) and not math.isnan(p.iloc[i])]
    if len(idx) < n or n == 0:
        return []
    out = []
    for _ in range(tirages):
        ch = rng.sample(idx, n)
        out.append(sum(((1 if rng.random() < part_achats else -1) * r.iloc[i] - FRAIS) * 100 for i in ch) / n)
    return out


def evaluer(nom, p, base, r, rng):
    ok = p.notna() & r.notna()
    pos = np.where(ok)[0]
    coupe = pos[int(len(pos) * 0.7)]
    pers = [("Tout", pos[0], pos[-1] + 1), ("Premiers 70 % (information)", pos[0], coupe),
            ("Derniers 30 % (contrôle)", coupe, pos[-1] + 1)]
    lignes = ["### " + nom, "",
              "| Période | Jours | Précision | AUC | Brier (modèle / constante) | Ordres | Réussite | Rendement moyen par ordre (± IC 95 %) | Frais ×2 | Part des tirages au hasard aussi bons |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    res = {}
    for nm, a, b in pers:
        sel = ok.copy()
        sel.iloc[:a] = False
        sel.iloc[b:] = False
        pp, rr, bb = p[sel], r[sel], base[sel]
        y = (rr > 0).astype(int)
        auc = roc_auc_score(y, pp)
        prec = ((pp > 0.5).astype(int) == y).mean()
        brier, brier0 = ((pp - y) ** 2).mean(), ((bb - y) ** 2).mean()
        ps = p.where(sel)
        tr, tr2 = trades_de(ps, r.where(sel)), trades_de(ps, r.where(sel), 2.0)
        m = metriques(tr, tr2)
        if m is None:
            lignes.append("| %s | %d | %s %% | %s | %s / %s | 0 | n/a | n/a | n/a | n/a |" % (
                nm, len(y), fr(prec * 100, 1), fr(auc, 3), fr(brier, 4), fr(brier0, 4)))
            res[nm] = (None, None)
            continue
        achats = sum(1 for t in tr if t["sens"] > 0) / len(tr)
        base_h = hasard(p, r, a, b, len(tr), achats, rng)
        part = sum(1 for x in base_h if x >= m["moy"]) / len(base_h) if base_h else None
        res[nm] = (m, part, auc)
        lignes.append("| %s | %d | %s %% | %s | %s / %s | %d | %s %% | %s %% ± %s | %s %% | %s |" % (
            nm, len(y), fr(prec * 100, 1), fr(auc, 3), fr(brier, 4), fr(brier0, 4), m["n"], fr(m["taux"] * 100, 0),
            fr(m["moy"], 3), fr(m["ic"], 3), fr(m["moy_x2"], 3), (fr(part * 100, 0) + " %") if part is not None else "n/a"))
    dev, ctl = res["Premiers 70 % (information)"], res["Derniers 30 % (contrôle)"]
    if ctl[0] is None or ctl[0]["n"] < 30:
        v = "Échantillon insuffisant"
    elif (dev[0] and dev[0]["moy"] > 0 and ctl[0]["moy"] > 0 and ctl[0]["moy"] - ctl[0]["ic"] > 0
          and ctl[0]["moy_x2"] > 0 and ctl[1] is not None and ctl[1] <= 0.025):
        v = "Avantage probable (seuil de 2,5 % car 2 modèles testés)"
    elif ctl[0]["moy"] > 0 and dev[0] and dev[0]["moy"] > 0:
        v = "Non démontré : positif mais incertain"
    else:
        v = "Absent ou instable"
    par_an = {}
    for t in trades_de(p, r):
        par_an.setdefault(p.index[t["i"]].year, []).append(t["R"])
    an = " · ".join("%d : %s %%" % (k, fr(sum(v_) / len(v_), 2)) for k, v_ in sorted(par_an.items()))
    lignes += ["", "**Verdict : " + v + ".**", "", "Rendement moyen par ordre, année par année : " + an, ""]
    return lignes, v, ctl


def main():
    X, r = construire()
    rng = random.Random(2026)
    tout, resume = [], []
    derniere = {}
    for nom, fab in modeles().items():
        p, base = marche_avant(X, r, fab)
        lignes, v, ctl = evaluer(nom, p, base, r, rng)
        tout.append("\n".join(lignes))
        resume.append("| %s | %s | %s | %s |" % (nom, fr(ctl[2], 3) if ctl[0] else "n/a",
                                              fr(ctl[0]["moy"], 3) + " %" if ctl[0] else "n/a", v))
        ok = np.where(~X.isna().any(axis=1) & r.notna())[0]
        sc = StandardScaler().fit(X.iloc[ok])
        m = fab().fit(sc.transform(X.iloc[ok]), (r.iloc[ok] > 0).astype(int))
        derniere[nom] = (m.predict_proba(sc.transform(X.iloc[[-1]]))[0, 1], X.index[-1].date())
        if nom.startswith("Régression"):
            coefs = sorted(zip(X.columns, m.coef_[0]), key=lambda z: -abs(z[1]))[:6]
            cf = ", ".join("%s (%s)" % (k, fr(c, 3)) for k, c in coefs)
    if "--journal" in sys.argv:
        chemin = RACINE / "journal" / "predictions_modele.csv"
        deja = chemin.read_text().splitlines() if chemin.exists() else ["date_cloture,p_logistique,p_arbres"]
        jour = str(X.index[-1].date())
        if not any(l.startswith(jour) for l in deja[1:]):
            deja.append("%s,%.4f,%.4f" % (jour, derniere["Régression logistique"][0], derniere["Petits arbres"][0]))
            chemin.write_text("\n".join(deja) + "\n")
    j0 = X.index[0].date()
    n_test = int(((~X.isna().any(axis=1)) & r.notna()).sum()) - DEPART
    texte = ["# Modèle multi-facteurs v1 : l'or le lendemain", "",
             "Données : %d jours de bourse (%s à %s), 16 facteurs (or, dollar, taux, argent, VIX, S&P 500, pétrole). Test strictement chronologique : réentraînement tous les %d jours, toujours évalué sur des jours que le modèle n'a jamais vus. Environ %d jours testés." % (len(X), j0, X.index[-1].date(), PAS, n_test),
             "", "**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
             "## Résumé (derniers 30 % de la période testée)", "",
             "| Modèle | AUC (0,5 = hasard) | Rendement moyen par ordre | Verdict |", "| --- | --- | --- | --- |"] + resume + [
             "", "## Détail", ""] + tout + [
             "## Probabilité pour la prochaine séance (information, pas un conseil)", ""] + [
             "- %s : %s %% de chances que l'or monte après la clôture du %s." % (k, fr(v[0] * 100, 0), v[1]) for k, v in derniere.items()] + [
             "", "Facteurs les plus pesants dans la régression (valeurs standardisées) : " + cf + ".", "",
             "## Hypothèses et limites", "",
             "- Futures GC=F, clôture à clôture. Les heures de clôture des facteurs diffèrent légèrement (VIX, taux, actions) : léger décalage possible.",
             "- Frais comptés à chaque ordre (0,05 % aller-retour, sans économie quand la position se poursuit dans le même sens) : estimation prudente. Pas de financement de nuit ni d'écart de prix réel de courtier.",
             "- Règles figées : 16 facteurs, 2 modèles, seuil 55 % / 45 %, entrée à la clôture, sortie à la clôture suivante. Aucun réglage après coup. Deux modèles testés : seuil de 2,5 % au lieu de 5 % pour parler d'avantage probable.",
             "- Un signal quotidien n'est pas un trade « fiable » : même un bon modèle se trompe souvent. L'AUC proche de 0,5 signifie qu'il ne fait pas mieux que le hasard.",
             "- Mauvaise nouvelle fréquente : la précision d'un modèle journalier sur l'or dépasse rarement 52 %. Elle ne couvre alors pas les frais."]
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text("\n".join(texte) + "\n", encoding="utf-8")
    print("\n".join(texte))


if __name__ == "__main__":
    main()
