#!/usr/bin/env python3
"""Récupère l'historique quotidien de l'or (XAU/USD) chez Alpha Vantage.

La clé API est lue dans la variable d'environnement ALPHAVANTAGE_API_KEY
(secret GitHub). Elle n'est jamais écrite dans un fichier ni affichée.
Sortie : data/or_quotidien.csv (date, close), trié par date croissante.
Hypothèse à vérifier : les samedis et dimanches sont retirés.
"""
import csv
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SORTIE = Path("data/or_quotidien.csv")


def convertir(objet):
    """Transforme la réponse JSON en liste (date, close), jours ouvrés, ordre croissant."""
    if "data" not in objet:
        message = objet.get("Information") or objet.get("Note") or objet.get("Error Message") or "réponse inattendue"
        raise SystemExit("Alpha Vantage : " + str(message)[:200])
    lignes = []
    for ligne in objet["data"]:
        try:
            jour = datetime.date.fromisoformat(ligne["date"])
            prix = float(ligne["price"])
        except (KeyError, ValueError):
            continue
        if jour.weekday() >= 5:
            continue
        lignes.append((jour.isoformat(), prix))
    lignes.sort()
    return lignes


def main():
    cle = os.environ.get("ALPHAVANTAGE_API_KEY", "")
    if not cle:
        raise SystemExit("ALPHAVANTAGE_API_KEY est absente : ajoute-la dans les secrets du dépôt.")
    parametres = urllib.parse.urlencode({
        "function": "GOLD_SILVER_HISTORY", "symbol": "GOLD",
        "interval": "daily", "datatype": "json", "apikey": cle,
    })
    try:
        with urllib.request.urlopen("https://www.alphavantage.co/query?" + parametres, timeout=60) as reponse:
            objet = json.loads(reponse.read().decode("utf-8"))
    except Exception as erreur:  # on n'affiche jamais l'URL (elle contient la clé)
        raise SystemExit("Échec du téléchargement : " + type(erreur).__name__)
    lignes = convertir(objet)
    if len(lignes) < 200:
        raise SystemExit("Trop peu de données reçues : " + str(len(lignes)))
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.writer(f)
        ecrivain.writerow(["date", "close"])
        ecrivain.writerows(lignes)
    print("OK :", len(lignes), "jours, dernier :", lignes[-1][0])


if __name__ == "__main__":
    sys.exit(main())
