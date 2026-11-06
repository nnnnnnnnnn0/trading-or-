# Stratégies intraday de l'or, achat et vente (v1)

Données : 13742 bougies 1 h (2024-06-13 à 2026-11-05), futures GC=F. Développement : jusqu'au 2025-11-19. Contrôle (ouvert une seule fois) : du 2025-11-19 à 2026-11-05.

**39 essais comptés** (15 stratégies, 24 heures). Aucun réglage : valeurs standard. À plat chaque soir (20 h UTC), jamais de nuit.

**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

**Attention : seulement 2,4 ans de données horaires** (l'historique 5 min plus long est encore en cours de téléchargement). Tout résultat ici est une hypothèse à confirmer, pas une preuve.

Critères de « candidat » (mode achat + vente) : au moins 30 ordres en contrôle, rendement moyen par ordre positif en développement et en contrôle, aussi avec frais doublés, t ≥ 2, au plus 1 % de hasard (sens des ordres tiré au sort).

| Stratégie | Mode | Ordres (contrôle) | Rendement moyen par ordre, développement | Rendement moyen par ordre, contrôle | t contrôle | Hasard | Réussite contrôle | Sharpe contrôle | Rendement moyen, frais ×2 | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cassure de la plage asiatique (0-7 h UTC) | achat + vente | 199 | 0,025 % | 0,056 % | 1,0 | 4 % | 49 % | 0,80 | 0,006 % | À surveiller |
| Cassure de la plage asiatique (0-7 h UTC) | achat seulement | 109 | 0,083 % | -0,063 % | -0,8 | 58 % | 48 % | -0,78 | -0,113 % | Rejeté |
| Cassure de la plage asiatique (0-7 h UTC) | vente seulement | 90 | -0,060 % | 0,199 % | 1,8 | 1 % | 51 % | 1,70 | 0,149 % | Rejeté |
| Cassure de la première heure américaine (13 h UTC) | achat + vente | 194 | -0,033 % | -0,053 % | -1,2 | 51 % | 41 % | -1,07 | -0,103 % | Rejeté |
| Cassure de la première heure américaine (13 h UTC) | achat seulement | 104 | -0,006 % | -0,145 % | -3,2 | 97 % | 37 % | -2,58 | -0,195 % | Rejeté |
| Cassure de la première heure américaine (13 h UTC) | vente seulement | 90 | -0,068 % | 0,053 % | 0,7 | 9 % | 46 % | 0,63 | 0,003 % | Rejeté |
| Cassure du plus haut / plus bas de la veille | achat + vente | 172 | 0,041 % | 0,003 % | 0,0 | 23 % | 48 % | 0,03 | -0,047 % | Rejeté |
| Cassure du plus haut / plus bas de la veille | achat seulement | 93 | 0,123 % | -0,114 % | -1,3 | 79 % | 44 % | -1,24 | -0,164 % | Rejeté |
| Cassure du plus haut / plus bas de la veille | vente seulement | 79 | -0,098 % | 0,140 % | 1,2 | 8 % | 53 % | 0,97 | 0,090 % | Rejeté |
| RSI 14 1 h, retour à la moyenne (30/70) | achat + vente | 86 | -0,127 % | 0,021 % | 0,1 | 31 % | 45 % | 0,13 | -0,029 % | Rejeté |
| RSI 14 1 h, retour à la moyenne (30/70) | achat seulement | 42 | 0,032 % | -0,189 % | -1,0 | 72 % | 36 % | -0,83 | -0,239 % | Rejeté |
| RSI 14 1 h, retour à la moyenne (30/70) | vente seulement | 44 | -0,218 % | 0,222 % | 1,3 | 10 % | 55 % | 1,06 | 0,172 % | Rejeté |
| Bollinger 20-2 1 h, retour à la moyenne | achat + vente | 154 | -0,102 % | -0,028 % | -0,4 | 36 % | 56 % | -0,39 | -0,078 % | Rejeté |
| Bollinger 20-2 1 h, retour à la moyenne | achat seulement | 74 | -0,032 % | -0,163 % | -1,2 | 83 % | 54 % | -1,30 | -0,213 % | Rejeté |
| Bollinger 20-2 1 h, retour à la moyenne | vente seulement | 80 | -0,164 % | 0,097 % | 1,3 | 3 % | 57 % | 1,24 | 0,047 % | Rejeté |
| Bollinger 20-2 1 h, cassure | achat + vente | 154 | 0,002 % | -0,072 % | -0,9 | 64 % | 38 % | -0,99 | -0,122 % | Rejeté |
| Bollinger 20-2 1 h, cassure | achat seulement | 80 | 0,064 % | -0,197 % | -2,6 | 98 % | 36 % | -2,45 | -0,247 % | Rejeté |
| Bollinger 20-2 1 h, cassure | vente seulement | 74 | -0,068 % | 0,063 % | 0,5 | 16 % | 41 % | 0,51 | 0,013 % | Rejeté |
| Moyennes EMA 20 / 50 (1 h) | achat + vente | 302 | 0,014 % | -0,021 % | -0,4 | 30 % | 46 % | -0,30 | -0,071 % | Rejeté |
| Moyennes EMA 20 / 50 (1 h) | achat seulement | 147 | 0,056 % | -0,075 % | -1,1 | 63 % | 46 % | -0,92 | -0,125 % | Rejeté |
| Moyennes EMA 20 / 50 (1 h) | vente seulement | 155 | -0,047 % | 0,030 % | 0,3 | 22 % | 46 % | 0,27 | -0,020 % | Rejeté |
| MACD 12-26-9 (1 h) | achat + vente | 434 | 0,005 % | 0,002 % | 0,0 | 11 % | 41 % | 0,04 | -0,048 % | Rejeté |
| MACD 12-26-9 (1 h) | achat seulement | 219 | 0,046 % | -0,036 % | -0,7 | 41 % | 42 % | -0,62 | -0,086 % | Rejeté |
| MACD 12-26-9 (1 h) | vente seulement | 215 | -0,038 % | 0,039 % | 0,6 | 8 % | 41 % | 0,56 | -0,011 % | Rejeté |
| Stochastique 14-3-3 (1 h) | achat + vente | 152 | -0,127 % | -0,073 % | -1,1 | 61 % | 41 % | -0,92 | -0,123 % | Rejeté |
| Stochastique 14-3-3 (1 h) | achat seulement | 63 | -0,062 % | -0,223 % | -2,3 | 91 % | 33 % | -1,60 | -0,273 % | Rejeté |
| Stochastique 14-3-3 (1 h) | vente seulement | 89 | -0,157 % | 0,033 % | 0,3 | 18 % | 47 % | 0,33 | -0,017 % | Rejeté |
| Donchian 24 h / sortie 12 h | achat + vente | 140 | -0,020 % | -0,013 % | -0,2 | 31 % | 50 % | -0,17 | -0,063 % | Rejeté |
| Donchian 24 h / sortie 12 h | achat seulement | 77 | 0,051 % | -0,168 % | -1,7 | 90 % | 49 % | -1,65 | -0,218 % | Rejeté |
| Donchian 24 h / sortie 12 h | vente seulement | 63 | -0,133 % | 0,176 % | 1,4 | 3 % | 51 % | 1,37 | 0,126 % | Rejeté |
| SuperTrend 10-3 (1 h) | achat + vente | 311 | 0,013 % | -0,067 % | -1,1 | 60 % | 43 % | -0,86 | -0,117 % | Rejeté |
| SuperTrend 10-3 (1 h) | achat seulement | 149 | 0,057 % | -0,122 % | -1,5 | 81 % | 44 % | -1,32 | -0,172 % | Rejeté |
| SuperTrend 10-3 (1 h) | vente seulement | 162 | -0,042 % | -0,017 % | -0,2 | 38 % | 41 % | -0,15 | -0,067 % | Rejeté |
| Ichimoku 1 h (cours / nuage) | achat + vente | 359 | -0,009 % | -0,043 % | -1,0 | 43 % | 38 % | -0,79 | -0,093 % | Rejeté |
| Ichimoku 1 h (cours / nuage) | achat seulement | 175 | 0,026 % | -0,055 % | -0,9 | 50 % | 41 % | -0,81 | -0,105 % | Rejeté |
| Ichimoku 1 h (cours / nuage) | vente seulement | 184 | -0,059 % | -0,033 % | -0,5 | 40 % | 35 % | -0,38 | -0,083 % | Rejeté |
| Momentum 6 h | achat + vente | 742 | -0,039 % | -0,053 % | -2,1 | 56 % | 32 % | -1,87 | -0,103 % | Rejeté |
| Momentum 6 h | achat seulement | 369 | -0,015 % | -0,075 % | -2,6 | 78 % | 34 % | -2,12 | -0,125 % | Rejeté |
| Momentum 6 h | vente seulement | 373 | -0,065 % | -0,030 % | -0,8 | 30 % | 29 % | -0,71 | -0,080 % | Rejeté |
| Direction de la première heure de Londres (7 h UTC) | achat + vente | 237 | -0,047 % | -0,056 % | -0,7 | 52 % | 47 % | -0,64 | -0,106 % | Rejeté |
| Direction de la première heure de Londres (7 h UTC) | achat seulement | 108 | 0,023 % | -0,139 % | -1,1 | 76 % | 50 % | -1,04 | -0,189 % | Rejeté |
| Direction de la première heure de Londres (7 h UTC) | vente seulement | 129 | -0,126 % | 0,014 % | 0,1 | 27 % | 45 % | 0,12 | -0,036 % | Rejeté |

## Heures de la journée (rendement moyen d'une bougie 1 h, en %, UTC)

| Heure UTC | Développement | t | Contrôle | t |
| --- | --- | --- | --- | --- |
| 7 h | 0,030 | 2,5 | -0,019 | -1,0 |
| 4 h | -0,018 | -1,7 | -0,018 | -0,7 |
| 19 h | 0,015 | 1,7 | 0,026 | 1,3 |
| 20 h | 0,016 | 1,7 | -0,021 | -0,7 |
| 10 h | 0,015 | 1,5 | 0,035 | 1,6 |

Les heures les plus marquées en développement sont à comparer au contrôle : un effet réel garde le même sens. Un effet d'une heure (quelques millièmes de %) reste inférieur aux frais d'un aller-retour (0,05 %).

## Conclusion

**Aucune stratégie intraday n'est retenue comme candidate.**

À surveiller (au plus 5 % de hasard, mais pas assez nets) : Cassure de la plage asiatique (0-7 h UTC).

## Limites

- 2,4 ans seulement : une seule configuration de marché (hausse forte de l'or). Résultats fragiles.
- Exécution à la clôture de la bougie du signal, frais estimés 0,05 % l'aller-retour, pas d'écart de prix réel de courtier, pas de dérapage (slippage).
- Futures GC=F, pas l'or au comptant ; heures UTC, donc la relation avec l'ouverture de Londres ou de New York change avec l'heure d'été.
- 39 essais : avec un seuil à 5 %, environ 2 paraissent bons par hasard. Une confirmation en paper trading reste nécessaire.
