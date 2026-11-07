"""Données journalières pour la stratégie Régime or : or (GC=F), dollar (DXY) et taux réels américains 10 ans.
Sources gratuites sans clé : Yahoo Finance (or, dollar) et US Treasury (taux réels). Tourne dans GitHub Actions.
Un échec sur une source n'arrête pas les autres ; l'historique déjà enregistré est conservé."""
import csv
import datetime as dt
import json
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote

RACINE = Path(__file__).resolve().parent.parent.parent
DATA = RACINE / "data"
ENTETE = ["date_utc", "open", "high", "low", "close", "volume"]


def http(url, essais=3, delai=60):
    err = None
    for i in range(essais):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=delai) as f:
                return f.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(3 * (i + 1))
    raise err


def convertir_yahoo(objet):
    r = objet["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    lignes = []
    for i, t in enumerate(r.get("timestamp") or []):
        v = [q[k][i] for k in ("open", "high", "low", "close", "volume")]
        if None in v[:4]:
            continue
        d = dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
        lignes.append([d] + [round(x, 4) for x in v[:4]] + [v[4] or 0])
    return lignes


def lignes_treasury(texte):
    """CSV du Trésor américain (Date MM/DD/YYYY, colonnes « 5 YR », « 10 YR »...) -> lignes au format commun, taux réel 10 ans."""
    lecteur = csv.reader(texte.splitlines())
    tete = next(lecteur)
    k = tete.index("10 YR")
    out = []
    for r in lecteur:
        if len(r) > k and r[k].strip() not in ("", "N/A"):
            d = dt.datetime.strptime(r[0], "%m/%d/%Y").strftime("%Y-%m-%d")
            v = round(float(r[k]), 4)
            out.append([d + " 00:00", v, v, v, v, 0])
    return out


def fusionner(chemin, nouvelles):
    base = {}
    if chemin.exists():
        with open(chemin, newline="") as f:
            for r in list(csv.reader(f))[1:]:
                if len(r) == 6:
                    base[r[0][:10]] = [r[0]] + [float(x) for x in r[1:]]
    for r in nouvelles:
        base[r[0][:10]] = r  # une ligne par date (la plus récente l'emporte)
    return [base[k] for k in sorted(base)]


def ecrire(chemin, lignes):
    with open(chemin, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(ENTETE)
        w.writerows(lignes)


def yahoo(symbole, fichier):
    debut = int(time.time()) - 21 * 366 * 86400
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=1d" % (quote(symbole), debut, int(time.time()))
    lignes = fusionner(DATA / fichier, convertir_yahoo(json.loads(http(url))))
    if len(lignes) < 1000:
        raise ValueError("trop peu de lignes")
    ecrire(DATA / fichier, lignes)
    print("OK", fichier, len(lignes), lignes[0][0], lignes[-1][0])


def taux_reels():
    annee_fin = dt.date.today().year
    nouvelles = []
    for a in range(2003, annee_fin + 1):
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/%d/all"
               "?type=daily_treasury_real_yield_curve&field_tdr_date_value=%d&page&_format=csv" % (a, a))
        nouvelles += lignes_treasury(http(url))
    lignes = fusionner(DATA / "taux_reels_10ans.csv", nouvelles)
    if len(lignes) < 1000:
        raise ValueError("trop peu de lignes")
    ecrire(DATA / "taux_reels_10ans.csv", lignes)
    print("OK taux_reels_10ans.csv", len(lignes), lignes[0][0], lignes[-1][0])


def main():
    for nom, f in (("or", lambda: yahoo("GC=F", "or_jour.csv")), ("dollar", lambda: yahoo("DX-Y.NYB", "dollar_dxy.csv")),
                   ("taux réels", taux_reels)):
        try:
            f()
        except Exception as e:  # noqa: BLE001
            print("ÉCHEC", nom, type(e).__name__, str(e)[:150])


if __name__ == "__main__":
    main()
