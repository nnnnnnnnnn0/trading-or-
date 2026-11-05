# Backtest v1 : Alignement multi-échelles (or)

Données : filtre de tendance sur 4991 jours (2006 à aujourd'hui), bougies 1 h du 2024-12-06 au 2026-11-04 (7574 bougies), bougies 5 min du 2024-12-06 au 2026-11-04 (90849 bougies). Source : or au comptant XAUUSD, prix vendeur (Dukascopy) pour 1 h et 5 min ; futures GC=F (Yahoo) pour le filtre journalier. Une seule exécution, règles non ajustées après coup.

**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

## Résumé (période de contrôle pour le 1 h, ensemble des données pour le 5 min)

| Version | Ordres | R moyen | Verdict |
| --- | --- | --- | --- |
| Déclenchement 1 h, intraday | 8 | -0,37 | Échantillon insuffisant : moins de 30 ordres en période de contrôle |
| Déclenchement 1 h, swing court (3 jours max) | 8 | -0,17 | Échantillon insuffisant : moins de 30 ordres en période de contrôle |
| Déclenchement 5 min, intraday | 54 | -0,24 | Absent ou instable |
| Déclenchement 5 min, swing court (3 jours max) | 54 | -0,22 | Absent ou instable |

## Détail

### Déclenchement 1 h, intraday

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 21 | 33 % | -0,21 ± 0,38 | 0,57 | -6,3 | 0,0 | -0,29 | 74 % | 82 % |
| Développement (70 %) | 13 | 38 % | -0,12 ± 0,56 | 0,77 | -3,4 | 0,0 | -0,20 | 64 % | 63 % |
| Contrôle (30 %) | 8 | 25 % | -0,37 ± 0,40 | 0,21 | -3,0 | 0,0 | -0,44 | 91 % | 88 % |

**Verdict : Échantillon insuffisant : moins de 30 ordres en période de contrôle.**

### Déclenchement 1 h, swing court (3 jours max)

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 21 | 29 % | 0,06 ± 0,53 | 1,12 | -5,1 | 0,3 | -0,03 | 25 % | 37 % |
| Développement (70 %) | 13 | 38 % | 0,20 ± 0,76 | 1,38 | -2,9 | 0,3 | 0,11 | 23 % | 22 % |
| Contrôle (30 %) | 8 | 12 % | -0,17 ± 0,63 | 0,58 | -2,2 | 0,2 | -0,25 | 66 % | 66 % |

**Verdict : Échantillon insuffisant : moins de 30 ordres en période de contrôle.**

### Déclenchement 5 min, intraday

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 147 | 36 % | -0,15 ± 0,18 | 0,72 | -30,2 | 0,0 | -0,31 | 67 % | 77 % |
| Développement (70 %) | 93 | 38 % | -0,10 ± 0,23 | 0,81 | -17,1 | 0,1 | -0,28 | 52 % | 55 % |
| Contrôle (30 %) | 54 | 33 % | -0,24 ± 0,27 | 0,57 | -17,4 | 0,0 | -0,36 | 84 % | 93 % |

**Verdict : Absent ou instable.**

### Déclenchement 5 min, swing court (3 jours max)

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 147 | 33 % | -0,16 ± 0,20 | 0,74 | -29,7 | 0,3 | -0,32 | 45 % | 65 % |
| Développement (70 %) | 93 | 37 % | -0,12 ± 0,26 | 0,81 | -18,5 | 0,4 | -0,30 | 65 % | 54 % |
| Contrôle (30 %) | 54 | 28 % | -0,22 ± 0,31 | 0,64 | -19,0 | 0,3 | -0,35 | 85 % | 77 % |

**Verdict : Absent ou instable.**

## Hypothèses et limites

- Futures GC=F, pas l'or au comptant de ton courtier : écarts de prix possibles, notamment à l'échéance des contrats.
- Entrée à l'ouverture de la bougie suivante, stops et objectifs contrôlés dans la bougie (plus haut / plus bas). Stop et objectif dans la même bougie : stop. Ouverture au-delà du stop : sortie à l'ouverture.
- Coûts estimés, pas ceux d'un courtier : 0,050 % du notionnel par aller-retour, 0,015 % par nuit calendaire. Colonne « frais ×2 » : coûts doublés. L'écart de prix (spread) réel d'un courtier peut être plus grand sur du court terme.
- Calendrier d'annonces non utilisé : les ordres ne sont pas bloqués avant les annonces majeures (seul un filtre de volatilité de la veille existe).
- Une position à la fois. Les tirages au hasard : 500 séries, même nombre d'ordres, mêmes stops (en multiples d'ATR) et mêmes sorties. « Dans la tendance » = direction de la tendance du jour, horaire aléatoire : c'est le témoin le plus exigeant, car il isole l'apport du repli et du déclenchement.
- Version 5 min : seulement 60 jours disponibles, donc très peu d'ordres. Aucune conclusion possible ; les données 5 min s'accumulent désormais dans le dépôt.
- Paramètres fixés avant le test (3 bougies, 24 h, 6 bougies, ATR 1 à 3, 2 R, 6 h) : aucun n'a été ajusté après avoir vu les résultats. Plus on teste de versions, plus un bon score par chance est probable.
- Verdict « avantage probable » = R moyen positif en développement et en contrôle, borne basse de l'IC 95 % positive en contrôle, R moyen positif avec frais doublés et au plus 5 % de tirages aussi bons (témoin dans la tendance), avec au moins 30 ordres en contrôle.
