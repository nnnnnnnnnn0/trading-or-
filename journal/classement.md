# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-12 23:55 UTC (3 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Cassure avec volume | tendance | 10 | 3,3 | 80 % | 1,288 | 1,196 | 3,0 | 12,0 | 10,6 | 598 | — |
| 15 | Compression Bollinger | tendance | 7 | 2,3 | 86 % | 1,243 | 1,119 | 2,6 | 7,8 | 6,5 | 392 | — |
| 11 | Cassure ouverture Londres | tendance | 4 | 1,3 | 75 % | 1,211 | 1,110 | 2,2 | 4,4 | 3,8 | 222 | — |
| 13 | Cassure de la veille | tendance | 5 | 1,7 | 60 % | 0,681 | 0,608 | 0,9 | 3,0 | 2,5 | 152 | — |
| 5 | Donchian 48 | tendance | 17 | 5,7 | 59 % | 0,699 | 0,606 | 1,8 | 10,3 | 7,9 | 515 | — |
| 9 | Heikin-Ashi | tendance | 25 | 8,3 | 64 % | 0,611 | 0,519 | 2,0 | 13,0 | 9,5 | 649 | — |
| 1 | EMA 9/21 | tendance | 13 | 4,3 | 62 % | 0,489 | 0,375 | 1,0 | 4,9 | 2,6 | 244 | — |
| 6 | Ichimoku nuage | tendance | 10 | 3,3 | 50 % | 0,388 | 0,275 | 0,6 | 2,7 | 1,0 | 137 | — |
| 16 | Momentum ROC 12 | tendance | 23 | 7,7 | 52 % | 0,371 | 0,265 | 0,9 | 6,1 | 2,5 | 305 | — |
| 4 | Supertrend 10x3 | tendance | 9 | 3,0 | 56 % | 0,361 | 0,253 | 0,5 | 2,3 | 0,8 | 114 | — |
| 14 | Keltner 20x2 | tendance | 18 | 6,0 | 50 % | 0,247 | 0,153 | 0,5 | 2,8 | 0,2 | 138 | — |
| 2 | Repli sur EMA 50 | tendance | 9 | 3,0 | 44 % | 0,215 | 0,089 | 0,2 | 0,8 | -0,9 | 40 | — |
| 12 | Cassure ouverture New York | tendance | 8 | 2,7 | 50 % | 0,116 | 0,046 | 0,1 | 0,4 | -0,5 | 18 | — |
| 19 | RSI 2 Connors | retour | 17 | 5,7 | 59 % | 0,029 | -0,074 | -0,3 | -1,3 | -3,9 | -63 | — |
| 3 | MACD 12-26-9 | tendance | 20 | 6,7 | 45 % | -0,006 | -0,098 | -0,4 | -2,0 | -4,7 | -98 | — |
| 10 | Aroon 25 | tendance | 10 | 3,3 | 30 % | 0,002 | -0,118 | -0,3 | -1,2 | -3,0 | -59 | — |
| 24 | VWAP 2 écarts-types | retour | 11 | 3,7 | 55 % | -0,045 | -0,161 | -0,6 | -1,8 | -3,7 | -89 | — |
| 0 | Témoin hasard | tendance | 10 | 3,3 | 40 % | -0,067 | -0,180 | -0,4 | -1,8 | -3,5 | -90 | — |
| 28 | Pivots de la veille | retour | 2 | 0,7 | 50 % | -0,125 | -0,216 | nan | -0,4 | -0,7 | -22 | — |
| 7 | ADX/DI 14 | tendance | 5 | 1,7 | 40 % | -0,257 | -0,364 | -0,7 | -1,8 | -2,6 | -91 | — |
| 18 | RSI 14 | retour | 21 | 7,0 | 38 % | -0,283 | -0,373 | -2,0 | -7,8 | -10,7 | -392 | — |
| 20 | Retour Bollinger | retour | 29 | 9,7 | 41 % | -0,291 | -0,382 | -2,4 | -11,1 | -15,0 | -554 | — |
| 21 | Stochastique 14-3-3 | retour | 33 | 11,0 | 39 % | -0,308 | -0,406 | -2,7 | -13,4 | -18,3 | -670 | 0,00 |
| 26 | MFI 14 | retour | 13 | 4,3 | 31 % | -0,350 | -0,428 | -1,9 | -5,6 | -7,1 | -278 | — |
| 23 | Williams %R 14 | retour | 52 | 17,3 | 35 % | -0,346 | -0,448 | -3,9 | -23,3 | -31,3 | -1166 | 0,00 |
| 22 | CCI 20 | retour | 36 | 12,0 | 31 % | -0,377 | -0,475 | -3,5 | -17,1 | -22,4 | -855 | 0,00 |
| 8 | Parabolic SAR | tendance | 23 | 7,7 | 30 % | -0,414 | -0,510 | -2,5 | -11,7 | -15,0 | -586 | — |
| 25 | Z-score 50 | retour | 21 | 7,0 | 24 % | -0,442 | -0,533 | -3,2 | -11,2 | -14,1 | -560 | — |
| 27 | Avalement | retour | 7 | 2,3 | 29 % | -0,500 | -0,620 | -1,9 | -4,3 | -5,6 | -217 | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
