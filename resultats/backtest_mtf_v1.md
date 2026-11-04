# Backtest v1 : Alignement multi-échelles (or)

Données : filtre de tendance sur 4990 jours (2006 à aujourd'hui), bougies 1 h du 2024-06-13 au 2026-11-04 (13656 bougies), bougies 5 min du 2026-08-26 au 2026-11-04 (13489 bougies). Source : futures GC=F (Yahoo Finance). Une seule exécution, règles non ajustées après coup.

**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

## Résumé (période de contrôle pour le 1 h, ensemble des données pour le 5 min)

| Version | Ordres | R moyen | Verdict |
| --- | --- | --- | --- |
| Déclenchement 1 h, intraday | 16 | -0,27 | Échantillon insuffisant : moins de 30 ordres en période de contrôle |
| Déclenchement 1 h, swing court (3 jours max) | 16 | -0,12 | Échantillon insuffisant : moins de 30 ordres en période de contrôle |
| Déclenchement 5 min, intraday | 32 | -0,16 | Informatif seulement : 60 jours de données 5 min, trop peu d'ordres |
| Déclenchement 5 min, swing court (3 jours max) | 29 | -0,19 | Informatif seulement : 60 jours de données 5 min, trop peu d'ordres |

## Détail

### Déclenchement 1 h, intraday

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 39 | 41 % | -0,06 ± 0,29 | 0,86 | -6,4 | 0,0 | -0,13 | 38 % | 47 % |
| Développement (70 %) | 23 | 43 % | 0,10 ± 0,44 | 1,24 | -4,4 | 0,0 | 0,01 | 20 % | 17 % |
| Contrôle (30 %) | 16 | 38 % | -0,27 ± 0,32 | 0,33 | -4,6 | 0,0 | -0,34 | 89 % | 84 % |

**Verdict : Échantillon insuffisant : moins de 30 ordres en période de contrôle.**

### Déclenchement 1 h, swing court (3 jours max)

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 39 | 36 % | 0,05 ± 0,36 | 1,11 | -4,8 | 0,3 | -0,04 | 21 % | 30 % |
| Développement (70 %) | 23 | 39 % | 0,16 ± 0,52 | 1,35 | -4,8 | 0,4 | 0,07 | 21 % | 19 % |
| Contrôle (30 %) | 16 | 31 % | -0,12 ± 0,46 | 0,69 | -3,9 | 0,1 | -0,19 | 60 % | 54 % |

**Verdict : Échantillon insuffisant : moins de 30 ordres en période de contrôle.**

### Déclenchement 5 min, intraday

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 32 | 38 % | -0,16 ± 0,41 | 0,74 | -8,5 | 0,0 | -0,29 | 56 % | 56 % |

**Verdict : Informatif seulement : 60 jours de données 5 min, trop peu d'ordres.**

### Déclenchement 5 min, swing court (3 jours max)

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Durée moy. (jours) | R moyen, frais ×2 | Hasard, direction libre | Hasard, dans la tendance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 29 | 34 % | -0,19 ± 0,45 | 0,72 | -8,9 | 0,2 | -0,32 | 54 % | 57 % |

**Verdict : Informatif seulement : 60 jours de données 5 min, trop peu d'ordres.**

## Hypothèses et limites

- Futures GC=F, pas l'or au comptant de ton courtier : écarts de prix possibles, notamment à l'échéance des contrats.
- Entrée à l'ouverture de la bougie suivante, stops et objectifs contrôlés dans la bougie (plus haut / plus bas). Stop et objectif dans la même bougie : stop. Ouverture au-delà du stop : sortie à l'ouverture.
- Coûts estimés, pas ceux d'un courtier : 0,050 % du notionnel par aller-retour, 0,015 % par nuit calendaire. Colonne « frais ×2 » : coûts doublés. L'écart de prix (spread) réel d'un courtier peut être plus grand sur du court terme.
- Calendrier d'annonces non utilisé : les ordres ne sont pas bloqués avant les annonces majeures (seul un filtre de volatilité de la veille existe).
- Une position à la fois. Les tirages au hasard : 500 séries, même nombre d'ordres, mêmes stops (en multiples d'ATR) et mêmes sorties. « Dans la tendance » = direction de la tendance du jour, horaire aléatoire : c'est le témoin le plus exigeant, car il isole l'apport du repli et du déclenchement.
- Version 5 min : seulement 60 jours disponibles, donc très peu d'ordres. Aucune conclusion possible ; les données 5 min s'accumulent désormais dans le dépôt.
- Paramètres fixés avant le test (3 bougies, 24 h, 6 bougies, ATR 1 à 3, 2 R, 6 h) : aucun n'a été ajusté après avoir vu les résultats. Plus on teste de versions, plus un bon score par chance est probable.
- Verdict « avantage probable » = R moyen positif en développement et en contrôle, borne basse de l'IC 95 % positive en contrôle, R moyen positif avec frais doublés et au plus 5 % de tirages aussi bons (témoin dans la tendance), avec au moins 30 ordres en contrôle.
