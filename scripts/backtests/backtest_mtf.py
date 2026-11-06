"""Backtest v1 de la stratégie « Alignement multi-échelles » sur l'or.

Étage 1 (jour)  : tendance MA20 > MA50 (ou <), calculée sur les jours déjà terminés ; pas d'ordre
                  si l'amplitude de la veille dépasse 2 fois sa moyenne sur 20 jours.
Étage 2 (1 h)   : repli d'au moins 3 bougies du mauvais côté de la MA20 horaire, sans casser le
                  plus bas (plus haut) des 24 bougies précédant le repli.
Étage 3 (1 h ou 5 min) : une bougie clôture au-delà de l'extrême des 6 bougies précédentes.
Entrée à l'ouverture de la bougie suivante, 8 h-20 h heure de Paris. Stop = extrême du repli, au
moins 1 ATR horaire, au plus 3 ATR (sinon pas d'ordre). Objectif 2 R. Sortie de sécurité :
après 6 h, si le gain est sous 0,5 R, on sort. Intraday : sortie à 21 h (Paris). Swing court : 72 h max.
"""
import bisect
import csv
import datetime as dt
import math
import random
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_or import metriques, fr, verdict  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent.parent
SORTIE = RACINE / "resultats" / ("backtest_mtf_histo.md" if "--histo" in sys.argv else "backtest_mtf_v1.md")
TIRAGES = {dt.timedelta(minutes=5): 100}
PARIS, NY = ZoneInfo("Europe/Paris"), ZoneInfo("America/New_York")
FRAIS_AR, FINANCEMENT = 0.0005, 0.00015
HEURE_MIN, HEURE_MAX = 8, 20          # heure d'entrée (Paris) : 8 h inclus, 20 h exclu
MIN_ATR, MAX_ATR = 1.0, 3.0
OBJECTIF_R, SECURITE_H, SECURITE_R = 2.0, 6, 0.5


class Serie:
    def __init__(self, lignes, pas_min):
        self.dur = dt.timedelta(minutes=pas_min)
        self.t = [l[0] for l in lignes]
        self.o, self.h, self.l, self.c = ([l[i] for l in lignes] for i in (1, 2, 3, 4))
        loc = [x.astimezone(PARIS) for x in self.t]
        self.ph = [x.hour for x in loc]
        self.pdate = [x.date() for x in loc]
        self.td = [(x.astimezone(NY) + dt.timedelta(hours=6)).date() for x in self.t]
        self.n = len(self.t)


def lire(chemin, pas_min):
    lignes = []
    with open(chemin, newline="") as f:
        lecteur = csv.reader(f)
        next(lecteur)
        for r in lecteur:
            v = [float(x) for x in r[1:5]]
            if v[0] == v[1] == v[2] == v[3]:
                continue  # bougie plate : pas de vraie cotation
            d = dt.datetime.strptime(r[0], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
            lignes.append([d] + v)
    return lignes[:-1]  # la dernière bougie est peut-être en cours


def lire_histo():
    """Historique 5 min (Dukascopy, or au comptant) -> lignes 5 min et lignes 1 h."""
    import gzip
    cinq, heures = [], {}
    for f in sorted((RACINE / "data" / "histo").glob("xauusd_5m_*.csv.gz")):
        with gzip.open(f, "rt") as g:
            lecteur = csv.reader(g)
            next(lecteur)
            for r in lecteur:
                v = [float(x) for x in r[1:5]]
                if v[0] == v[1] == v[2] == v[3]:
                    continue
                d = dt.datetime.strptime(r[0], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
                cinq.append([d] + v)
                k = d.replace(minute=0)
                b = heures.get(k)
                if b is None:
                    heures[k] = [k] + v
                else:
                    b[2], b[3], b[4] = max(b[2], v[1]), min(b[3], v[2]), v[3]
    return cinq[:-1], [heures[k] for k in sorted(heures)][:-1]


def filtre_jour(chemin):
    """date -> (tendance, volatilité ok), calculés avec les jours strictement avant."""
    d, cl, am = [], [], []
    with open(chemin, newline="") as f:
        lecteur = csv.reader(f)
        next(lecteur)
        for r in lecteur:
            h, b, c = float(r[2]), float(r[3]), float(r[4])
            d.append(dt.date.fromisoformat(r[0][:10]))
            cl.append(c)
            am.append(h - b)
    res = {}
    for i in range(51, len(d)):
        m20, m50 = sum(cl[i - 20:i]) / 20, sum(cl[i - 50:i]) / 50
        tendance = 1 if m20 > m50 else -1 if m20 < m50 else 0
        moy = sum(am[i - 21:i - 1]) / 20
        res[d[i]] = (tendance, am[i - 1] <= 2 * moy if moy > 0 else False)
    return res


def indicateurs_h(s):
    ma = [None] * s.n
    atr = [None] * s.n
    bas = [0] * s.n
    haut = [0] * s.n
    for i in range(s.n):
        if i >= 19:
            ma[i] = sum(s.c[i - 19:i + 1]) / 20
        if i >= 14:
            tr = [max(s.h[k] - s.l[k], abs(s.h[k] - s.c[k - 1]), abs(s.l[k] - s.c[k - 1]))
                  for k in range(i - 13, i + 1)]
            atr[i] = sum(tr) / 14
        if ma[i] is not None:
            bas[i] = bas[i - 1] + 1 if s.c[i] < ma[i] else 0
            haut[i] = haut[i - 1] + 1 if s.c[i] > ma[i] else 0
    return atr, bas, haut


def preparations(s, fj):
    """Pour chaque bougie horaire terminée : (sens, extrême du repli) ou None."""
    atr, bas, haut = indicateurs_h(s)
    prep = [None] * s.n
    for i in range(45, s.n):
        tend = fj.get(s.td[i], (0, False))[0]
        if tend > 0 and bas[i] >= 3 and i - bas[i] + 1 >= 24:
            a = i - bas[i] + 1
            if min(s.l[a:i + 1]) > min(s.l[a - 24:a]):
                prep[i] = (1, min(s.l[a:i + 1]))
        elif tend < 0 and haut[i] >= 3 and i - haut[i] + 1 >= 24:
            a = i - haut[i] + 1
            if max(s.h[a:i + 1]) < max(s.h[a - 24:a]):
                prep[i] = (-1, max(s.h[a:i + 1]))
    return atr, prep


def contexte(decl, h1, atr1, fj):
    """Pour chaque bougie de déclenchement k : (tendance, atr, indice de la prépa 1 h) ou None si l'ordre est interdit."""
    ctx = [None] * decl.n
    fin1 = [x + h1.dur for x in h1.t]
    same = decl is h1
    for k in range(60, decl.n - 1):
        e = k + 1
        if decl.t[e] - decl.t[k] != decl.dur or not (HEURE_MIN <= decl.ph[e] < HEURE_MAX):
            continue
        tend, vol_ok = fj.get(decl.td[k], (0, False))
        if tend == 0 or not vol_ok:
            continue
        if same:
            i = k - 1
            a = atr1[k]
        else:
            i = bisect.bisect_right(fin1, decl.t[k] + decl.dur) - 1
            if i < 0 or decl.t[k] + decl.dur - fin1[i] > dt.timedelta(hours=2):
                continue
            a = atr1[i]
        if a is None or a <= 0:
            continue
        ctx[k] = (tend, a, i)
    return ctx


def signal(decl, ctx, prep, k):
    """(sens, extrême) si la bougie k déclenche un ordre, sinon None."""
    if ctx[k] is None:
        return None
    tend, _, i = ctx[k]
    p = prep[i] if i >= 0 else None
    if p is None or p[0] != tend:
        return None
    sens, ext = p
    if sens > 0 and decl.c[k] > max(decl.h[k - 6:k]):
        return sens, min(ext, min(decl.l[k - 6:k + 1]) if decl.dur < dt.timedelta(hours=1) else decl.l[k])
    if sens < 0 and decl.c[k] < min(decl.l[k - 6:k]):
        return sens, max(ext, max(decl.h[k - 6:k + 1]) if decl.dur < dt.timedelta(hours=1) else decl.h[k])
    return None


def simuler(s, e, sens, entree, risque, variante, frais=1.0):
    """Entrée à l'ouverture de la bougie e ; sortie intrabougie. Résultat en R."""
    stop = entree - sens * risque
    objectif = entree + sens * OBJECTIF_R * risque
    limite = s.t[e] + dt.timedelta(hours=72)
    secu = s.t[e] + dt.timedelta(hours=SECURITE_H)
    secu_faite = False
    sortie = prix = None
    for k in range(e, s.n):
        if k > e:
            if variante == "intraday":
                fini = s.pdate[k] > s.pdate[e] or s.ph[k] >= 21
            else:
                fini = s.t[k] >= limite
            if fini:
                sortie, prix = k, s.o[k]
                break
            if (s.o[k] - stop) * sens <= 0:
                sortie, prix = k, s.o[k]
                break
        touche_stop = (s.l[k] <= stop) if sens > 0 else (s.h[k] >= stop)
        touche_obj = (s.h[k] >= objectif) if sens > 0 else (s.l[k] <= objectif)
        if touche_stop:
            sortie, prix = k, stop
            break
        if touche_obj:
            sortie, prix = k, objectif
            break
        if not secu_faite and s.t[k] + s.dur >= secu:
            secu_faite = True
            if (s.c[k] - entree) * sens < SECURITE_R * risque:
                sortie, prix = k, s.c[k]
                break
    if sortie is None:
        sortie, prix = s.n - 1, s.c[s.n - 1]
    jours = (s.pdate[sortie] - s.pdate[e]).days
    cout = (FRAIS_AR + FINANCEMENT * jours) * entree * frais / risque
    brut = sens * (prix - entree) / risque
    return {"R": brut - cout, "sortie": sortie, "jours": jours, "sens": sens, "entree": e}


def lancer(decl, ctx, prep, variante, a, b, frais=1.0):
    trades, libre, ratios = [], 0, []
    for k in range(a, b):
        if k < libre:
            continue
        sg = signal(decl, ctx, prep, k)
        if sg is None:
            continue
        sens, ext = sg
        e = k + 1
        entree = decl.o[e]
        atr = ctx[k][1]
        stop = min(ext, entree - atr) if sens > 0 else max(ext, entree + atr)
        risque = (entree - stop) * sens
        if risque <= 0 or risque > MAX_ATR * atr:
            continue
        t = simuler(decl, e, sens, entree, risque, variante, frais)
        t["ratio"] = risque / atr
        trades.append(t)
        libre = t["sortie"]
    return trades


def hasard(decl, ctx, variante, a, b, n_cibles, ratios, part_achats, aligne, tirages, rng):
    cand = [k for k in range(a, b) if ctx[k] is not None]
    if n_cibles == 0 or len(cand) < n_cibles or not ratios:
        return []
    moyennes = []
    for _ in range(tirages):
        libre, rs = 0, []
        for k in sorted(rng.sample(cand, n_cibles)):
            if k < libre:
                continue
            tend, atr, _ = ctx[k]
            sens = tend if aligne else (1 if rng.random() < part_achats else -1)
            risque = rng.choice(ratios) * atr
            t = simuler(decl, k + 1, sens, decl.o[k + 1], risque, variante)
            rs.append(t["R"])
            libre = t["sortie"]
        if rs:
            moyennes.append(sum(rs) / len(rs))
    return moyennes


def part(base, m):
    return (sum(1 for x in base if x >= m["moy"]) / len(base)) if base else None


def bloc(titre, decl, ctx, prep, variante, periodes, rng, tirages=500):
    tirages = TIRAGES.get(decl.dur, tirages)
    lignes = ["### " + titre, "",
              "| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    res = {}
    for nom, a, b in periodes:
        tr = lancer(decl, ctx, prep, variante, a, b)
        tr2 = lancer(decl, ctx, prep, variante, a, b, 2.0)
        m = metriques(tr, tr2)
        if m is None:
            lignes.append("| %s | 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |" % nom)
            res[nom] = (None, None)
            continue
        achats = sum(1 for t in tr if t["sens"] > 0) / len(tr)
        ratios = [t["ratio"] for t in tr]
        pa = part(hasard(decl, ctx, variante, a, b, len(tr), ratios, achats, False, tirages, rng), m)
        pb = part(hasard(decl, ctx, variante, a, b, len(tr), ratios, achats, True, tirages, rng), m)
        res[nom] = (m, pb, tr)
        f = lambda x: (fr(x * 100, 0) + " %") if x is not None else "n/a"
        lignes.append("| %s | %d | %s %% | %s ± %s | %s | %s | %s | %s | %s | %s |" % (
            nom, m["n"], fr(m["taux"] * 100, 0), fr(m["moy"]), fr(m["ic"]), fr(m["pf"]),
            fr(m["dd"], 1), fr(m["jours"], 1), fr(m["moy_x2"]), f(pa), f(pb)))
    return lignes, res


def main():
    fj = filtre_jour(RACINE / "data" / "or_ohlc_jour.csv")
    histo = "--histo" in sys.argv
    if histo:
        l5, l1 = lire_histo()
        h1, m5 = Serie(l1, 60), Serie(l5, 5)
    else:
        h1 = Serie(lire(RACINE / "data" / "or_ohlc_1h.csv", 60), 60)
        m5 = Serie(lire(RACINE / "data" / "or_ohlc_5m.csv", 5), 5)
    atr1, prep = preparations(h1, fj)
    rng = random.Random(2026)
    c1 = contexte(h1, h1, atr1, fj)
    c5 = contexte(m5, h1, atr1, fj)
    cp = int(h1.n * 0.7)
    per1 = [("Tout", 60, h1.n - 2), ("Développement (70 %)", 60, cp), ("Contrôle (30 %)", cp, h1.n - 2)]
    cp5 = int(m5.n * 0.7)
    per5 = [("Tout", 60, m5.n - 2), ("Développement (70 %)", 60, cp5), ("Contrôle (30 %)", cp5, m5.n - 2)] if histo else [("Tout", 60, m5.n - 2)]
    jeux = [("Déclenchement 1 h, intraday", h1, c1, "intraday", per1),
            ("Déclenchement 1 h, swing court (3 jours max)", h1, c1, "swing", per1),
            ("Déclenchement 5 min, intraday", m5, c5, "intraday", per5),
            ("Déclenchement 5 min, swing court (3 jours max)", m5, c5, "swing", per5)]
    sections, resume = [], []
    for titre, decl, ctx, var, per in jeux:
        lignes, res = bloc(titre, decl, ctx, prep, var, per, rng)
        if len(per) == 3:
            dev, tm = res["Développement (70 %)"], res["Contrôle (30 %)"]
            v = verdict(dev[0], tm[0], tm[1] if tm[0] else None)
            nc = tm[0]["n"] if tm[0] else 0
            moy = fr(tm[0]["moy"]) if tm[0] else "n/a"
        else:
            tt = res["Tout"]
            v = "Informatif seulement : 60 jours de données 5 min, trop peu d'ordres"
            nc = tt[0]["n"] if tt[0] else 0
            moy = fr(tt[0]["moy"]) if tt[0] else "n/a"
        lignes += ["", "**Verdict : " + v + ".**", ""]
        sections.append("\n".join(lignes))
        resume.append("| %s | %d | %s | %s |" % (titre, nc, moy, v))
    d1, d2 = h1.t[0].date(), h1.t[-1].date()
    e1, e2 = m5.t[0].date(), m5.t[-1].date()
    texte = [
        "# Backtest v1 : Alignement multi-échelles (or)", "",
        "Données : filtre de tendance sur %d jours (2006 à aujourd'hui), bougies 1 h du %s au %s (%d bougies), bougies 5 min du %s au %s (%d bougies). Source : %s. Une seule exécution, règles non ajustées après coup." % (len(fj), d1, d2, h1.n, e1, e2, m5.n, "or au comptant XAUUSD, prix vendeur (Dukascopy) pour 1 h et 5 min ; futures GC=F (Yahoo) pour le filtre journalier" if "--histo" in sys.argv else "futures GC=F (Yahoo Finance)"),
        "", "**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
        "## Résumé (période de contrôle pour le 1 h, ensemble des données pour le 5 min)", "",
        "| Version | Ordres | R moyen | Verdict |", "| --- | --- | --- | --- |"] + resume + ["", "## Détail", ""] + sections + [
        "## Hypothèses et limites", "",
        "- Futures GC=F, pas l'or au comptant de ton courtier : écarts de prix possibles, notamment à l'échéance des contrats.",
        "- Entrée à l'ouverture de la bougie suivante, stops et objectifs contrôlés dans la bougie (plus haut / plus bas). Stop et objectif dans la même bougie : stop. Ouverture au-delà du stop : sortie à l'ouverture.",
        "- Coûts estimés, pas ceux d'un courtier : 0,050 % du notionnel par aller-retour, 0,015 % par nuit calendaire. Colonne « frais ×2 » : coûts doublés. L'écart de prix (spread) réel d'un courtier peut être plus grand sur du court terme.",
        "- Calendrier d'annonces non utilisé : les ordres ne sont pas bloqués avant les annonces majeures (seul un filtre de volatilité de la veille existe).",
        "- Une position à la fois. Les tirages au hasard : 500 séries, même nombre d'ordres, mêmes stops (en multiples d'ATR) et mêmes sorties. « Dans la tendance » = direction de la tendance du jour, horaire aléatoire : c'est le témoin le plus exigeant, car il isole l'apport du repli et du déclenchement.",
        "- Version 5 min : seulement 60 jours disponibles, donc très peu d'ordres. Aucune conclusion possible ; les données 5 min s'accumulent désormais dans le dépôt.",
        "- Paramètres fixés avant le test (3 bougies, 24 h, 6 bougies, ATR 1 à 3, 2 R, 6 h) : aucun n'a été ajusté après avoir vu les résultats. Plus on teste de versions, plus un bon score par chance est probable.",
        "- Verdict « avantage probable » = R moyen positif en développement et en contrôle, borne basse de l'IC 95 % positive en contrôle, R moyen positif avec frais doublés et au plus 5 % de tirages aussi bons (témoin dans la tendance), avec au moins 30 ordres en contrôle.",
    ]
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text("\n".join(texte) + "\n", encoding="utf-8")
    print("\n".join(texte))


if __name__ == "__main__":
    main()
