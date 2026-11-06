"""Historique 5 min de l'or au comptant (XAUUSD, prix vendeur) depuis Dukascopy (gratuit, sans clé).
Reprise automatique : ne retélécharge que les jours manquants. Écrit un fichier de statut lisible.
Tourne dans GitHub Actions (le réseau y est ouvert)."""
import csv, datetime as dt, gzip, io, json, lzma, struct, sys, time, traceback, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent.parent
DOSSIER = RACINE / "data" / "histo"
DEBUT = dt.date(2012, 1, 1)
URL = "https://datafeed.dukascopy.com/datafeed/XAUUSD/%04d/%02d/%02d/BID_candles_min_1.bi5"


def telecharger(jour):
    url = URL % (jour.year, jour.month - 1, jour.day)
    for essai in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as f:
                return jour, f.read(), None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return jour, b"", None
            err = "HTTP %d" % e.code
        except Exception as e:
            err = type(e).__name__
        time.sleep(2 + 2 * essai)
    return jour, None, err


def decoder(jour, brut, echelle):
    if not brut:
        return []
    donnees = lzma.decompress(brut)
    debut = dt.datetime(jour.year, jour.month, jour.day, tzinfo=dt.timezone.utc)
    lignes = []
    for t, o, c, l, h, v in struct.iter_unpack(">IIIIIf", donnees):
        lignes.append((debut + dt.timedelta(seconds=t), o / echelle, h / echelle, l / echelle, c / echelle, v))
    return lignes


def agreger_5m(minutes):
    blocs = {}
    for t, o, h, l, c, v in sorted(minutes):
        k = t.replace(minute=t.minute - t.minute % 5, second=0)
        b = blocs.get(k)
        if b is None:
            blocs[k] = [o, h, l, c, v]
        else:
            b[1], b[2], b[3], b[4] = max(b[1], h), min(b[2], l), c, b[4] + v
    return blocs


def main():
    DOSSIER.mkdir(parents=True, exist_ok=True)
    statut = []
    existants = set()
    for f in DOSSIER.glob("xauusd_5m_*.csv.gz"):
        with gzip.open(f, "rt") as g:
            for r in csv.reader(g):
                if r and r[0] != "date_utc":
                    existants.add(r[0][:10])
    fin = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)
    manquants = [DEBUT + dt.timedelta(days=i) for i in range((fin - DEBUT).days + 1)]
    manquants = [j for j in manquants if j.weekday() != 5 and j.isoformat() not in existants]
    manquants = [j for j in manquants if j.isoformat() not in vides()]
    fichier_echecs = DOSSIER / "echecs.json"
    echecs = json.loads(fichier_echecs.read_text()) if fichier_echecs.exists() else {}
    manquants = [j for j in manquants if echecs.get(j.isoformat(), 0) < 15]  # abandon après 15 échecs
    tous = len(manquants)
    statut.append("jours à télécharger : %d (20 min max par exécution)" % len(manquants))
    manquants = manquants[-3000:]  # les plus récents d'abord ; les exécutions suivantes complètent
    # échelle des prix : testée sur le premier fichier non vide
    echelle = None
    nouveaux, erreurs, vus_vides = {}, 0, []
    t0 = time.time()
    def lots():
        with ThreadPoolExecutor(8) as ex:
            for i in range(0, len(manquants), 32):
                if time.time() - t0 > 1200:
                    statut.append("budget de 20 minutes atteint : le reste à la prochaine exécution")
                    return
                yield from ex.map(telecharger, manquants[i:i + 32])
    if True:
        for jour, brut, err in lots():
            if brut is None:
                erreurs += 1
                echecs[jour.isoformat()] = echecs.get(jour.isoformat(), 0) + 1
                if erreurs <= 3:
                    statut.append("erreur %s : %s" % (jour, err))
                continue
            if not brut:
                vus_vides.append(jour.isoformat())
                continue
            if echelle is None:
                brut_test = struct.unpack(">IIIIIf", lzma.decompress(brut)[:24])
                for e in (1000, 100, 10000, 1):
                    if 200 < brut_test[1] / e < 10000:
                        echelle = e
                        break
                statut.append("échelle des prix : %s (premier jour %s, premier prix %s)" % (echelle, jour, brut_test[1] / (echelle or 1)))
            m = decoder(jour, brut, echelle or 1000)
            if m:
                nouveaux[jour] = m
                if len(nouveaux) == 1:
                    statut.append("premier fichier : %s de %s à %s UTC, %d minutes" % (jour, m[0][0], m[-1][0], len(m)))
    par_annee = {}
    for jour, m in nouveaux.items():
        for k, b in agreger_5m(m).items():
            par_annee.setdefault(k.year, {})[k.strftime("%Y-%m-%d %H:%M")] = b
    for annee, blocs in par_annee.items():
        f = DOSSIER / ("xauusd_5m_%d.csv.gz" % annee)
        base = {}
        if f.exists():
            with gzip.open(f, "rt") as g:
                for r in list(csv.reader(g))[1:]:
                    base[r[0]] = [float(x) for x in r[1:]]
        base.update(blocs)
        with gzip.open(f, "wt", newline="") as g:
            w = csv.writer(g)
            w.writerow(["date_utc", "open", "high", "low", "close", "volume"])
            for k in sorted(base):
                w.writerow([k] + [round(x, 3) for x in base[k]])
    if vus_vides:
        with open(DOSSIER / "jours_vides.txt", "a") as f:
            f.write("\n".join(vus_vides) + "\n")
    for jour in list(nouveaux) + [dt.date.fromisoformat(x) for x in vus_vides]:
        echecs.pop(jour.isoformat(), None)
    fichier_echecs.write_text(json.dumps(echecs))
    reste = tous - len(nouveaux) - len(vus_vides)
    (DOSSIER / "reste.txt").write_text("%d\n" % reste)
    (DOSSIER / "ajoutes.txt").write_text("%d\n" % (len(nouveaux) + len(vus_vides)))
    statut.append("jours ajoutés : %d ; jours sans données : %d ; erreurs : %d ; reste à télécharger : %d" % (len(nouveaux), len(vus_vides), erreurs, reste))
    (DOSSIER / "statut.txt").write_text("\n".join(statut) + "\n")
    print("\n".join(statut))


def vides():
    f = DOSSIER / "jours_vides.txt"
    return set(f.read_text().split()) if f.exists() else set()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        DOSSIER.mkdir(parents=True, exist_ok=True)
        (DOSSIER / "statut.txt").write_text("ÉCHEC\n" + traceback.format_exc()[-1500:])
        print(traceback.format_exc())
