#!/usr/bin/env python3
"""Backtest des règles v1 sur l'or, à partir des CLÔTURES quotidiennes (data/or_quotidien.csv).

Hypothèses (toutes déclarées dans le rapport) :
- signal calculé sur la clôture du jour J, entrée à la clôture de J+1 (pas d'ouverture disponible) ;
- stops contrôlés sur les clôtures seulement, exécutés au cours de clôture (les trous de cours coûtent) ;
- un stop et un objectif franchis le même jour comptent comme stop ;
- une position à la fois par règle ;
- coûts : estimations, pas ceux d'un courtier réel.
Les règles ne sont PAS ajustées ici : voir regles/strategies_or.md.
"""
import csv
import datetime
import math
import random
import statistics
import sys
from pathlib import Path

DONNEES = Path("data/or_quotidien.csv")
SORTIE = Path("resultats/backtest_v1.md")
FRAIS_ALLER_RETOUR = 0.0005   # 0,05 % du notionnel (estimation)
FINANCEMENT_NUIT = 0.00015    # 0,015 % par nuit calendaire (estimation)
DEBUT_MIN = 150               # historique minimal avant le premier signal
REGLES = ("repli", "cassure", "compression")
NOMS = {"repli": "Repli dans la tendance", "cassure": "Cassure de 20 jours",
        "compression": "Compression puis cassure"}


def charger(chemin):
    dates, c = [], []
    with open(chemin, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            dates.append(datetime.date.fromisoformat(ligne["date"]))
            c.append(float(ligne["close"]))
    return dates, c


def indicateurs(c):
    n = len(c)
    ind = {k: [None] * n for k in ("m20", "m50", "vol", "bw", "bas", "haut")}
    for i in range(n):
        if i >= 19:
            w = c[i - 19:i + 1]
            mu = sum(w) / 20
            sd = statistics.pstdev(w)
            ind["m20"][i], ind["bas"][i], ind["haut"][i] = mu, mu - 2 * sd, mu + 2 * sd
            ind["bw"][i] = (4 * sd) / mu
        if i >= 49:
            ind["m50"][i] = sum(c[i - 49:i + 1]) / 50
        if i >= 14:
            ind["vol"][i] = sum(abs(c[k] - c[k - 1]) for k in range(i - 13, i + 1)) / 14
    return ind


def detecter(regle, j, c, ind):
    """Retourne +1 (achat), -1 (vente) ou 0 (pas de signal) à la clôture j."""
    if regle == "repli":
        if j < 51 or not ind["vol"][j]:
            return 0
        if ind["m20"][j] > ind["m50"][j] and c[j - 1] >= ind["m20"][j - 1] and c[j] < ind["m20"][j]:
            return 1
        return 0
    if regle == "cassure":
        if j < 21:
            return 0
        precedentes = c[j - 20:j]
        if c[j] > max(precedentes):
            return 1
        if c[j] < min(precedentes):
            return -1
        return 0
    if regle == "compression":
        if j < 149:
            return 0
        recentes, anterieures = ind["bw"][j - 5:j], ind["bw"][j - 126:j]
        if min(recentes) > min(anterieures):
            return 0
        if c[j] > ind["haut"][j]:
            return 1
        if c[j] < ind["bas"][j]:
            return -1
    return 0


def stop_regle(regle, j, sens, c, ind):
    if regle == "repli":
        v = ind["vol"][j]
        return c[j] - 2 * v if v else None
    if regle == "cassure":
        w = c[j - 9:j + 1]
        return min(w) if sens > 0 else max(w)
    return ind["bas"][j] if sens > 0 else ind["haut"][j]


def simuler(regle, j, sens, stop, c, dates, ind, frais=1.0):
    """Entrée à la clôture de j+1 ; sortie selon la règle. Résultat en multiples de R."""
    n = len(c)
    e = j + 1
    if e >= n - 1 or stop is None:
        return None
    entree = c[e]
    if regle == "repli":
        stop = entree - sens * 2 * ind["vol"][j]  # stop mesuré depuis l'entrée réelle
    risque = (entree - stop) * sens
    plancher = 0.5 * (ind["vol"][j] or 0)
    if risque <= 0 or risque < plancher:
        return None  # risque quasi nul : l'ordre serait démesuré, on l'écarte
    objectif = None
    if regle == "repli":
        objectif = entree + sens * 3 * risque
    elif regle == "compression":
        objectif = entree + sens * 2 * risque
    sortie = prix = None
    for t in range(e + 1, n):
        px = c[t]
        if (px - stop) * sens <= 0:
            sortie, prix = t, px
            break
        if objectif is not None and (px - objectif) * sens >= 0:
            sortie, prix = t, objectif
            break
        if regle == "repli" and px < ind["m50"][t]:
            sortie, prix = t, px
            break
        if regle == "cassure":
            w = c[t - 10:t]
            if (sens > 0 and px < min(w)) or (sens < 0 and px > max(w)):
                sortie, prix = t, px
                break
        if regle == "compression" and t - e >= 10:
            sortie, prix = t, px
            break
    if sortie is None:
        sortie, prix = n - 1, c[n - 1]
    nuits = (dates[sortie] - dates[e]).days
    cout = (FRAIS_ALLER_RETOUR + FINANCEMENT_NUIT * nuits) * entree * frais / risque
    brut = sens * (prix - entree) / risque
    return {"R": brut - cout, "brut": brut, "sortie": sortie, "jours": nuits, "sens": sens, "entree": e}


def lancer(regle, c, dates, ind, debut, fin, frais=1.0):
    trades, libre = [], 0
    for j in range(max(debut, DEBUT_MIN), fin):
        if j < libre:
            continue
        sens = detecter(regle, j, c, ind)
        if not sens:
            continue
        t = simuler(regle, j, sens, stop_regle(regle, j, sens, c, ind), c, dates, ind, frais)
        if t:
            trades.append(t)
            libre = t["sortie"]
    return trades


def hasard(regle, c, dates, ind, debut, fin, n_cibles, part_achats, tirages, rng):
    """Moyennes de R pour des entrées tirées au hasard avec les mêmes stops et sorties."""
    candidats = list(range(max(debut, DEBUT_MIN), fin - 1))
    if n_cibles == 0 or len(candidats) < n_cibles:
        return []
    moyennes = []
    for _ in range(tirages):
        libre, rs = 0, []
        for j in sorted(rng.sample(candidats, n_cibles)):
            if j < libre:
                continue
            sens = 1 if (regle == "repli" or rng.random() < part_achats) else -1
            t = simuler(regle, j, sens, stop_regle(regle, j, sens, c, ind), c, dates, ind)
            if t:
                rs.append(t["R"])
                libre = t["sortie"]
        if rs:
            moyennes.append(sum(rs) / len(rs))
    return moyennes


def metriques(trades, trades_x2=None):
    r = [t["R"] for t in trades]
    n = len(r)
    if n == 0:
        return None
    m = sum(r) / n
    sd = statistics.stdev(r) if n > 1 else 0.0
    ic = 1.96 * sd / math.sqrt(n) if n > 1 else float("nan")
    gains = sum(x for x in r if x > 0)
    pertes = -sum(x for x in r if x <= 0)
    cum = pic = dd = 0.0
    serie = pire = 0
    for x in r:
        cum += x
        pic = max(pic, cum)
        dd = min(dd, cum - pic)
        serie = serie + 1 if x <= 0 else 0
        pire = max(pire, serie)
    m2 = (sum(t["R"] for t in trades_x2) / len(trades_x2)) if trades_x2 else float("nan")
    return {"n": n, "taux": sum(1 for x in r if x > 0) / n, "moy": m, "ic": ic,
            "pf": gains / pertes if pertes > 0 else float("inf"), "dd": dd, "serie": pire,
            "jours": sum(t["jours"] for t in trades) / n, "moy_x2": m2, "total": cum}


def fr(x, d=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    if x == float("inf"):
        return "infini"
    return ("{:." + str(d) + "f}").format(x).replace(".", ",")


def verdict(dev, test, part_hasard):
    if test is None or test["n"] < 30:
        return "Échantillon insuffisant : moins de 30 ordres en période de contrôle"
    if (dev and dev["moy"] > 0 and test["moy"] > 0 and test["moy"] - test["ic"] > 0
            and test["moy_x2"] > 0 and part_hasard is not None and part_hasard <= 0.05):
        return "Avantage probable"
    if test["moy"] > 0 and dev and dev["moy"] > 0:
        return "Non démontré : positif mais incertain"
    return "Absent ou instable"


def main():
    dates, c = charger(DONNEES)
    n = len(c)
    ind = indicateurs(c)
    coupure = int(n * 0.7)
    periodes = [("Tout", DEBUT_MIN, n - 1), ("Développement (70 %)", DEBUT_MIN, coupure),
                ("Contrôle (30 %)", coupure, n - 1)]
    rng = random.Random(2026)
    sections, resume = [], []
    for regle in REGLES:
        lignes = ["### " + NOMS[regle], "",
                  "| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Pire série | Durée moy. (jours) | R moyen, frais ×2 | Part des tirages au hasard qui font aussi bien |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        res = {}
        for nom, a, b in periodes:
            tr = lancer(regle, c, dates, ind, a, b)
            tr2 = lancer(regle, c, dates, ind, a, b, frais=2.0)
            m = metriques(tr, tr2)
            res[nom] = (m, tr)
            if m is None:
                lignes.append("| %s | 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |" % nom)
                continue
            achats = sum(1 for t in tr if t["sens"] > 0) / len(tr)
            base = hasard(regle, c, dates, ind, a, b, len(tr), achats, 1000, rng)
            part = (sum(1 for x in base if x >= m["moy"]) / len(base)) if base else None
            res[nom] = (m, tr, part)
            lignes.append("| %s | %d | %s %% | %s ± %s | %s | %s | %d | %s | %s | %s |" % (
                nom, m["n"], fr(m["taux"] * 100, 0), fr(m["moy"]), fr(m["ic"]), fr(m["pf"]),
                fr(m["dd"], 1), m["serie"], fr(m["jours"], 1), fr(m["moy_x2"]),
                (fr(part * 100, 0) + " %") if part is not None else "n/a"))
        dev = res["Développement (70 %)"][0]
        tm = res["Contrôle (30 %)"]
        v = verdict(dev, tm[0], tm[2] if len(tm) > 2 else None)
        lignes += ["", "**Verdict : " + v + ".**", ""]
        tout = res["Tout"][1]
        for sens, nom in ((1, "achats"), (-1, "ventes")):
            sous = [t for t in tout if t["sens"] == sens]
            if sous:
                lignes.append("- Exploratoire, %s seulement : %d ordres, R moyen %s." % (
                    nom, len(sous), fr(sum(t["R"] for t in sous) / len(sous))))
        sections.append("\n".join(lignes) + "\n")
        resume.append("| %s | %s | %s | %s |" % (NOMS[regle], tm[0]["n"] if tm[0] else 0,
                                               fr(tm[0]["moy"]) if tm[0] else "n/a", v))
    rendement = c[-1] / c[0] - 1
    annees = (dates[-1] - dates[0]).days / 365.25
    annualise = (c[-1] / c[0]) ** (1 / annees) - 1
    texte = "\n".join([
        "# Backtest v1 : règles de l'or",
        "",
        "Données : %d clôtures quotidiennes du %s au %s (data/or_quotidien.csv). Une seule exécution, règles non ajustées après coup." % (
            n, dates[0].isoformat(), dates[-1].isoformat()),
        "",
        "**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**",
        "",
        "## Résumé (période de contrôle)", "",
        "| Règle | Ordres | R moyen | Verdict |", "| --- | --- | --- | --- |", *resume, "",
        "Référence : garder l'or sur toute la période = %s %% au total, soit %s %% par an (hors coûts de détention)." % (
            fr(rendement * 100, 0), fr(annualise * 100, 1)), "",
        "## Détail par règle", "", *sections,
        "## Hypothèses et limites", "",
        "- Données de clôture seulement : pas de plus haut ni de plus bas. Entrée à la clôture de J+1 (pas d'ouverture disponible) ; stops contrôlés sur les clôtures et exécutés au cours de clôture ; stop et objectif le même jour : stop.",
        "- Coûts estimés, pas ceux d'un courtier : %s %% du notionnel par aller-retour, %s %% par nuit calendaire de financement. Colonne « frais ×2 » = ces coûts doublés." % (
            fr(FRAIS_ALLER_RETOUR * 100, 3), fr(FINANCEMENT_NUIT * 100, 3)),
        "- Une position à la fois par règle. Durée non plafonnée pour le repli et la cassure (sortie par règle) ; 10 jours pour la compression.",
        "- La règle « suite d'un événement macro » n'est pas testée : elle exige le plus haut et le plus bas de la séance et un calendrier d'annonces.",
        "- Tirages au hasard : 1 000 séries de dates aléatoires par période, même nombre d'ordres, même proportion d'achats, mêmes stops et sorties, graine fixe. Un faible pourcentage signifie que la règle bat presque tous les tirages.",
        "- Trois règles testées, plus des découpages exploratoires achats/ventes : plus on teste, plus un bon résultat par chance est probable. Ne retenir un « avantage probable » qu'avec prudence.",
        "- L'or a beaucoup monté sur la période : les achats profitent de cette hausse, d'où l'importance de la comparaison au hasard.",
        "- Verdict « avantage probable » = R moyen positif en développement et en contrôle, borne basse de l'IC 95 % positive en contrôle, R moyen positif avec frais doublés, et au plus 5 % de tirages au hasard aussi bons ; « échantillon insuffisant » sous 30 ordres en contrôle.",
        ""])
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text(texte, encoding="utf-8")
    print(texte)


if __name__ == "__main__":
    sys.exit(main())
