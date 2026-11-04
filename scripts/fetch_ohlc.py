"""Télécharge l'or (futures GC=F) avec ouverture/plus haut/plus bas/clôture/volume.
Source : Yahoo Finance (sans clé). Tourne dans GitHub Actions. Un échec n'arrête pas le reste."""
import csv, json, sys, datetime, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
JEUX = [("1d", "max", "data/or_ohlc_jour.csv"),
        ("1h", "730d", "data/or_ohlc_1h.csv"),
        ("5m", "60d", "data/or_ohlc_5m.csv")]


def convertir(obj):
    r = obj["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    lignes = []
    for i, t in enumerate(r.get("timestamp") or []):
        v = [q[k][i] for k in ("open", "high", "low", "close", "volume")]
        if None in v[:4]:
            continue
        d = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
        lignes.append([d] + [round(x, 2) for x in v[:4]] + [v[4] or 0])
    return lignes


def telecharger(intervalle, plage):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=%s&interval=%s" % (plage, intervalle))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as f:
        return json.load(f)


def main():
    for inter, plage, sortie in JEUX:
        try:
            lignes = convertir(telecharger(inter, plage))
            if len(lignes) < 10:
                raise ValueError("trop peu de lignes")
            with open(RACINE / sortie, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["date_utc", "open", "high", "low", "close", "volume"])
                w.writerows(lignes)
            print("OK", sortie, len(lignes), lignes[0][0], lignes[-1][0])
        except Exception as e:
            print("ÉCHEC", sortie, type(e).__name__, str(e)[:120])


if __name__ == "__main__":
    main()
