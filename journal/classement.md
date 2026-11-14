# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-13 23:55 UTC (4 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | Cassure ouverture Londres | tendance | 6 | 1,5 | 67 % | 0,974 | 0,872 | 1,7 | 5,2 | 4,3 | 262 | — |
| 17 | Cassure avec volume | tendance | 12 | 3,0 | 67 % | 0,907 | 0,815 | 2,0 | 9,8 | 8,1 | 489 | — |
| 13 | Cassure de la veille | tendance | 5 | 1,2 | 60 % | 0,681 | 0,608 | 0,9 | 3,0 | 2,5 | 152 | — |
| 5 | Donchian 48 | tendance | 19 | 4,8 | 53 % | 0,520 | 0,424 | 1,3 | 8,1 | 5,3 | 403 | — |
| 15 | Compression Bollinger | tendance | 11 | 2,8 | 55 % | 0,428 | 0,309 | 0,7 | 3,4 | 1,4 | 170 | — |
| 2 | Repli sur EMA 50 | tendance | 14 | 3,5 | 57 % | 0,322 | 0,206 | 0,6 | 2,9 | 0,4 | 144 | — |
| 9 | Heikin-Ashi | tendance | 36 | 9,0 | 53 % | 0,233 | 0,138 | 0,6 | 5,0 | -0,1 | 249 | 0,08 |
| 16 | Momentum ROC 12 | tendance | 30 | 7,5 | 47 % | 0,226 | 0,127 | 0,5 | 3,8 | -0,7 | 191 | 0,06 |
| 6 | Ichimoku nuage | tendance | 15 | 3,8 | 53 % | 0,224 | 0,119 | 0,4 | 1,8 | -0,6 | 89 | — |
| 19 | RSI 2 Connors | retour | 22 | 5,5 | 68 % | 0,193 | 0,094 | 0,5 | 2,1 | -1,2 | 103 | — |
| 3 | MACD 12-26-9 | tendance | 25 | 6,2 | 52 % | 0,084 | -0,006 | -0,0 | -0,2 | -3,6 | -8 | — |
| 1 | EMA 9/21 | tendance | 18 | 4,5 | 44 % | 0,076 | -0,029 | -0,1 | -0,5 | -3,4 | -26 | — |
| 12 | Cassure ouverture New York | tendance | 9 | 2,2 | 44 % | -0,008 | -0,077 | -0,2 | -0,7 | -1,6 | -35 | — |
| 14 | Keltner 20x2 | tendance | 22 | 5,5 | 41 % | 0,020 | -0,077 | -0,3 | -1,7 | -4,9 | -85 | — |
| 28 | Pivots de la veille | retour | 2 | 0,5 | 50 % | -0,125 | -0,216 | nan | -0,4 | -0,7 | -22 | — |
| 7 | ADX/DI 14 | tendance | 6 | 1,5 | 50 % | -0,117 | -0,218 | -0,5 | -1,3 | -2,2 | -65 | — |
| 4 | Supertrend 10x3 | tendance | 16 | 4,0 | 31 % | -0,130 | -0,237 | -0,8 | -3,8 | -6,4 | -189 | — |
| 20 | Retour Bollinger | retour | 35 | 8,8 | 49 % | -0,163 | -0,254 | -1,7 | -8,9 | -13,7 | -445 | 0,00 |
| 22 | CCI 20 | retour | 49 | 12,2 | 41 % | -0,221 | -0,317 | -2,6 | -15,5 | -22,5 | -775 | 0,00 |
| 25 | Z-score 50 | retour | 26 | 6,5 | 38 % | -0,229 | -0,320 | -2,0 | -8,3 | -11,9 | -416 | — |
| 24 | VWAP 2 écarts-types | retour | 18 | 4,5 | 44 % | -0,222 | -0,331 | -1,6 | -6,0 | -8,9 | -298 | — |
| 10 | Aroon 25 | tendance | 15 | 3,8 | 27 % | -0,219 | -0,334 | -1,1 | -5,0 | -7,6 | -250 | — |
| 0 | Témoin hasard | tendance | 12 | 3,0 | 33 % | -0,223 | -0,335 | -0,9 | -4,0 | -6,0 | -201 | — |
| 8 | Parabolic SAR | tendance | 28 | 7,0 | 39 % | -0,244 | -0,338 | -1,7 | -9,5 | -13,4 | -473 | — |
| 23 | Williams %R 14 | retour | 68 | 17,0 | 41 % | -0,243 | -0,343 | -3,3 | -23,3 | -33,6 | -1167 | 0,00 |
| 21 | Stochastique 14-3-3 | retour | 38 | 9,5 | 42 % | -0,261 | -0,359 | -2,6 | -13,7 | -19,3 | -683 | 0,00 |
| 18 | RSI 14 | retour | 21 | 5,2 | 38 % | -0,283 | -0,373 | -2,0 | -7,8 | -10,7 | -392 | — |
| 26 | MFI 14 | retour | 14 | 3,5 | 29 % | -0,396 | -0,474 | -2,2 | -6,6 | -8,3 | -332 | — |
| 27 | Avalement | retour | 10 | 2,5 | 30 % | -0,475 | -0,590 | -2,2 | -5,9 | -7,6 | -295 | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
