"""Télécharge les facteurs qui influencent l'or (dollar, taux, argent, peur, actions, pétrole)
et le calendrier des annonces économiques de la semaine. Tourne dans GitHub Actions.
Chaque source est indépendante : un échec n'arrête pas les autres."""
import csv, json, urllib.request
from pathlib import Path

from fetch_ohlc import RACINE, convertir, fusionner, telecharger

FACTEURS = [("dollar_dxy", "DX-Y.NYB"), ("taux_10ans", "^TNX"), ("taux_5ans", "^FVX"),
            ("taux_13sem", "^IRX"), ("argent", "SI=F"), ("vix", "^VIX"),
            ("sp500", "^GSPC"), ("petrole_wti", "CL=F"), ("etf_or_gld", "GLD")]
CALENDRIER = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FICHIER_CAL = RACINE / "data" / "calendrier.csv"


def facteurs():
    for nom, symbole in FACTEURS:
        try:
            lignes = fusionner(RACINE / "data" / ("facteur_%s.csv" % nom),
                               convertir(telecharger("1d", "max", symbole)))
            if len(lignes) < 100:
                raise ValueError("trop peu de lignes")
            with open(RACINE / "data" / ("facteur_%s.csv" % nom), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["date_utc", "open", "high", "low", "close", "volume"])
                w.writerows(lignes)
            print("OK", nom, len(lignes), lignes[0][0], lignes[-1][0])
        except Exception as e:
            print("ÉCHEC", nom, type(e).__name__, str(e)[:120])


def calendrier():
    try:
        req = urllib.request.Request(CALENDRIER, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as f:
            donnees = json.load(f)
        base = {}
        if FICHIER_CAL.exists():
            with open(FICHIER_CAL, newline="", encoding="utf-8") as f:
                for r in list(csv.reader(f))[1:]:
                    base[(r[0], r[1], r[3])] = r
        for e in donnees:
            ligne = [e.get("date", ""), e.get("country", ""), e.get("impact", ""),
                     e.get("title", ""), e.get("forecast", ""), e.get("previous", "")]
            base[(ligne[0], ligne[1], ligne[3])] = ligne
        with open(FICHIER_CAL, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", "pays", "impact", "evenement", "prevision", "precedent"])
            w.writerows(base[k] for k in sorted(base))
        print("OK calendrier", len(base))
    except Exception as e:
        print("ÉCHEC calendrier", type(e).__name__, str(e)[:120])


if __name__ == "__main__":
    facteurs()
    calendrier()
