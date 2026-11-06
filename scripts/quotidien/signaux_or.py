#!/usr/bin/env python3
"""Signaux de niveau A sur l'or, calculés sur les CLÔTURES quotidiennes seulement.

Limites assumées : pas de plus haut ni de plus bas, donc la volatilité est
approchée par la moyenne des écarts de clôture à clôture sur 14 jours
(sous-estime la vraie ATR). Les niveaux sont indicatifs : l'entrée réelle se
fait à l'ouverture suivante, et il faut les vérifier sur le graphique.
Règles figées : voir regles/strategies_or.md. Aucune règle ne se modifie ici.
"""
import csv
import datetime
import statistics
import sys
from pathlib import Path

DONNEES = Path("data/or_quotidien.csv")
DOSSIER = Path("rapports")


def charger(chemin):
    dates, clotures = [], []
    with open(chemin, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            dates.append(ligne["date"])
            clotures.append(float(ligne["close"]))
    return dates, clotures


def moyenne(c, n):
    return sum(c[-n:]) / n if len(c) >= n else None


def volatilite(c, n=14):
    if len(c) < n + 1:
        return None
    return sum(abs(c[i] - c[i - 1]) for i in range(len(c) - n, len(c))) / n


def bandes(c, n=20, k=2.0):
    if len(c) < n:
        return None
    fenetre = c[-n:]
    milieu = sum(fenetre) / n
    ecart = statistics.pstdev(fenetre)
    return milieu - k * ecart, milieu, milieu + k * ecart


def largeur_bandes(c):
    b = bandes(c)
    if b is None or b[1] == 0:
        return None
    return (b[2] - b[0]) / b[1]


def repli_tendance(c):
    """Moyenne 20 j au-dessus de la 50 j, première clôture sous la 20 j : achat."""
    if len(c) < 52:
        return None
    m20, m50, m20_veille = moyenne(c, 20), moyenne(c, 50), moyenne(c[:-1], 20)
    v = volatilite(c)
    if v is None or v == 0:
        return None
    if m20 > m50 and c[-2] >= m20_veille and c[-1] < m20:
        entree = c[-1]
        stop = entree - 2 * v
        return {"strategie": "Repli dans la tendance", "sens": "Long", "entree": entree, "stop": stop,
                "objectif": entree + 3 * (entree - stop),
                "sortie": "clôture sous la moyenne 50 jours (%.2f), ou objectif 3R" % m50}
    return None


def cassure_20(c):
    """Clôture hors de l'étendue des 20 clôtures précédentes."""
    if len(c) < 22:
        return None
    precedentes = c[-21:-1]
    entree = c[-1]
    if entree > max(precedentes):
        return {"strategie": "Cassure de 20 jours", "sens": "Long", "entree": entree, "stop": min(c[-10:]),
                "objectif": None, "sortie": "stop suiveur : clôture sous le plus bas des 10 derniers jours"}
    if entree < min(precedentes):
        return {"strategie": "Cassure de 20 jours", "sens": "Short", "entree": entree, "stop": max(c[-10:]),
                "objectif": None, "sortie": "stop suiveur : clôture au-dessus du plus haut des 10 derniers jours"}
    return None


def compression(c):
    """Largeur des bandes au plus bas de ~6 mois dans les 5 derniers jours, puis clôture hors des bandes."""
    if len(c) < 150:
        return None
    largeurs = []
    for fin in range(len(c) - 126, len(c) + 1):
        w = largeur_bandes(c[:fin])
        if w is None:
            return None
        largeurs.append(w)
    anterieures, recentes = largeurs[:-1], largeurs[-6:-1]
    if min(recentes) > min(anterieures):
        return None
    bas, _, haut = bandes(c)
    entree = c[-1]
    if entree > haut:
        risque = entree - bas
        return {"strategie": "Compression puis cassure", "sens": "Long", "entree": entree, "stop": bas,
                "objectif": entree + 2 * risque, "sortie": "objectif 2R ou 10 jours maximum"}
    if entree < bas:
        risque = haut - entree
        return {"strategie": "Compression puis cassure", "sens": "Short", "entree": entree, "stop": haut,
                "objectif": entree - 2 * risque, "sortie": "objectif 2R ou 10 jours maximum"}
    return None


def tous_les_signaux(c):
    resultats = []
    for fonction in (repli_tendance, cassure_20, compression):
        signal = fonction(c)
        if signal:
            resultats.append(signal)
    return resultats


def rapport(dates, c, signaux):
    m20, m50, v = moyenne(c, 20), moyenne(c, 50), volatilite(c)
    jour = dates[-1]
    var1 = (c[-1] / c[-2] - 1) * 100 if len(c) > 1 else 0.0
    var5 = (c[-1] / c[-6] - 1) * 100 if len(c) > 5 else 0.0
    lignes = ["# Bilan automatique de l'or : données au " + jour, "",
              "Source : clôtures quotidiennes Alpha Vantage (XAU/USD). Calcul automatique, sans analyse de l'actualité.", "",
              "## État du marché", "",
              "- Dernière clôture : %.2f $ (%+.2f %% sur 1 jour, %+.2f %% sur 5 jours)" % (c[-1], var1, var5)]
    if m20 is not None and m50 is not None:
        lignes.append("- Moyenne 20 jours : %.2f, moyenne 50 jours : %.2f (%s)" % (
            m20, m50, "tendance haussière" if m20 > m50 else "tendance baissière ou neutre"))
    if v is not None:
        lignes.append("- Volatilité approchée (14 jours, clôture à clôture) : %.2f $" % v)
    lignes += ["", "## Signaux de niveau A", ""]
    if not signaux:
        lignes.append("Aucun signal valide aujourd'hui. Ne pas trader est une décision valable.")
    for s in signaux:
        lignes += ["### %s : %s" % (s["strategie"], s["sens"]), "",
                   "- Niveau d'entrée indicatif (dernière clôture) : %.2f" % s["entree"],
                   "- Stop : %.2f" % s["stop"]]
        if s["objectif"] is not None:
            lignes.append("- Objectif : %.2f" % s["objectif"])
        lignes += ["- Sortie : " + s["sortie"], ""]
    lignes += ["", "## À faire à la main", "",
               "- Stratégie « suite d'un événement macro » : non calculée ici (elle exige le plus haut et le plus bas de la séance). Voir data/annonces.csv.",
               "- Vérifier chaque niveau sur le graphique TradingView avant d'enregistrer un ordre dans le journal.",
               "- Les prix ci-dessus sont indicatifs ; l'entrée réelle se fait à l'ouverture suivante.", "",
               "Paper trading : aucun argent réel. Ce n'est ni un conseil en investissement ni une prévision."]
    return "\n".join(lignes) + "\n"


def main():
    if not DONNEES.exists():
        raise SystemExit("data/or_quotidien.csv est absent : lance d'abord scripts/fetch_or.py")
    dates, c = charger(DONNEES)
    if len(c) < 60:
        raise SystemExit("Pas assez de données : " + str(len(c)))
    texte = rapport(dates, c, tous_les_signaux(c))
    retard = (datetime.date.today() - datetime.date.fromisoformat(dates[-1])).days
    if retard > 4:
        texte = "> ATTENTION : la dernière donnée a %d jours ; le rapport peut être périmé.\n\n" % retard + texte
    DOSSIER.mkdir(exist_ok=True)
    chemin = DOSSIER / (dates[-1] + ".md")
    chemin.write_text(texte, encoding="utf-8")
    print("Rapport écrit :", chemin)


if __name__ == "__main__":
    sys.exit(main())
