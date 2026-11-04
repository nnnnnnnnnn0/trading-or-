# Backtest v1 : règles de l'or

Données : 4024 clôtures quotidiennes du 2011-06-01 au 2026-11-02 (data/or_quotidien.csv). Une seule exécution, règles non ajustées après coup.

**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

## Résumé (période de contrôle)

| Règle | Ordres | R moyen | Verdict |
| --- | --- | --- | --- |
| Repli dans la tendance | 25 | 0,53 | Échantillon insuffisant : moins de 30 ordres en période de contrôle |
| Cassure de 20 jours | 48 | 0,15 | Absent ou instable |
| Compression puis cassure | 11 | 0,06 | Échantillon insuffisant : moins de 30 ordres en période de contrôle |

Référence : garder l'or sur toute la période = 154 % au total, soit 6,2 % par an (hors coûts de détention).

## Détail par règle

### Repli dans la tendance

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Pire série | Durée moy. (jours) | R moyen, frais ×2 | Part des tirages au hasard qui font aussi bien |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 77 | 40 % | 0,11 ± 0,37 | 1,20 | -12,4 | 7 | 10,9 | -0,03 | 19 % |
| Développement (70 %) | 53 | 34 % | -0,08 ± 0,44 | 0,88 | -12,4 | 7 | 8,8 | -0,22 | 38 % |
| Contrôle (30 %) | 25 | 56 % | 0,53 ± 0,62 | 2,69 | -2,2 | 4 | 16,2 | 0,38 | 16 % |

**Verdict : Échantillon insuffisant : moins de 30 ordres en période de contrôle.**

- Exploratoire, achats seulement : 77 ordres, R moyen 0,11.

### Cassure de 20 jours

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Pire série | Durée moy. (jours) | R moyen, frais ×2 | Part des tirages au hasard qui font aussi bien |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 161 | 35 % | -0,07 ± 0,18 | 0,84 | -20,1 | 8 | 22,0 | -0,20 | 43 % |
| Développement (70 %) | 113 | 33 % | -0,17 ± 0,19 | 0,65 | -19,9 | 8 | 21,8 | -0,30 | 44 % |
| Contrôle (30 %) | 48 | 40 % | 0,15 ± 0,40 | 1,37 | -5,8 | 6 | 22,4 | 0,03 | 42 % |

**Verdict : Absent ou instable.**

- Exploratoire, achats seulement : 82 ordres, R moyen -0,00.
- Exploratoire, ventes seulement : 79 ordres, R moyen -0,15.

### Compression puis cassure

| Période | Ordres | Réussite | R moyen (± IC 95 %) | Facteur de profit | Perte max (R) | Pire série | Durée moy. (jours) | R moyen, frais ×2 | Part des tirages au hasard qui font aussi bien |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 31 | 45 % | -0,02 ± 0,29 | 0,95 | -6,0 | 5 | 13,0 | -0,09 | 28 % |
| Développement (70 %) | 20 | 40 % | -0,06 ± 0,40 | 0,84 | -4,6 | 5 | 12,8 | -0,14 | 37 % |
| Contrôle (30 %) | 11 | 55 % | 0,06 ± 0,40 | 1,27 | -2,0 | 2 | 13,4 | 0,00 | 35 % |

**Verdict : Échantillon insuffisant : moins de 30 ordres en période de contrôle.**

- Exploratoire, achats seulement : 13 ordres, R moyen -0,18.
- Exploratoire, ventes seulement : 18 ordres, R moyen 0,11.

## Hypothèses et limites

- Données de clôture seulement : pas de plus haut ni de plus bas. Entrée à la clôture de J+1 (pas d'ouverture disponible) ; stops contrôlés sur les clôtures et exécutés au cours de clôture ; stop et objectif le même jour : stop.
- Coûts estimés, pas ceux d'un courtier : 0,050 % du notionnel par aller-retour, 0,015 % par nuit calendaire de financement. Colonne « frais ×2 » = ces coûts doublés.
- Une position à la fois par règle. Durée non plafonnée pour le repli et la cassure (sortie par règle) ; 10 jours pour la compression.
- La règle « suite d'un événement macro » n'est pas testée : elle exige le plus haut et le plus bas de la séance et un calendrier d'annonces.
- Tirages au hasard : 1 000 séries de dates aléatoires par période, même nombre d'ordres, même proportion d'achats, mêmes stops et sorties, graine fixe. Un faible pourcentage signifie que la règle bat presque tous les tirages.
- Trois règles testées, plus des découpages exploratoires achats/ventes : plus on teste, plus un bon résultat par chance est probable. Ne retenir un « avantage probable » qu'avec prudence.
- L'or a beaucoup monté sur la période : les achats profitent de cette hausse, d'où l'importance de la comparaison au hasard.
- Verdict « avantage probable » = R moyen positif en développement et en contrôle, borne basse de l'IC 95 % positive en contrôle, R moyen positif avec frais doublés, et au plus 5 % de tirages au hasard aussi bons ; « échantillon insuffisant » sous 30 ordres en contrôle.
