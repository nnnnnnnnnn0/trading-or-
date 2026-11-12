# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-11 23:55 UTC (2 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 15 | Compression Bollinger | tendance | 6 | 3,0 | 100 % | 1,617 | 1,492 | 6,1 | 9,0 | 7,8 | 448 | — |
| 17 | Cassure avec volume | tendance | 7 | 3,5 | 86 % | 1,412 | 1,307 | 3,1 | 9,1 | 8,0 | 457 | — |
| 11 | Cassure ouverture Londres | tendance | 3 | 1,5 | 67 % | 0,948 | 0,837 | 1,4 | 2,5 | 2,0 | 126 | — |
| 9 | Heikin-Ashi | tendance | 18 | 9,0 | 67 % | 0,778 | 0,678 | 2,1 | 12,2 | 9,5 | 610 | — |
| 1 | EMA 9/21 | tendance | 11 | 5,5 | 64 % | 0,627 | 0,507 | 1,2 | 5,6 | 3,6 | 279 | — |
| 6 | Ichimoku nuage | tendance | 9 | 4,5 | 56 % | 0,543 | 0,428 | 0,9 | 3,9 | 2,3 | 193 | — |
| 5 | Donchian 48 | tendance | 13 | 6,5 | 54 % | 0,530 | 0,425 | 1,1 | 5,5 | 3,5 | 276 | — |
| 4 | Supertrend 10x3 | tendance | 6 | 3,0 | 67 % | 0,541 | 0,420 | 0,8 | 2,5 | 1,4 | 126 | — |
| 13 | Cassure de la veille | tendance | 4 | 2,0 | 50 % | 0,352 | 0,282 | 0,4 | 1,1 | 0,7 | 56 | — |
| 16 | Momentum ROC 12 | tendance | 20 | 10,0 | 50 % | 0,325 | 0,213 | 0,7 | 4,3 | 0,9 | 213 | — |
| 12 | Cassure ouverture New York | tendance | 6 | 3,0 | 50 % | 0,245 | 0,165 | 0,3 | 1,0 | 0,3 | 49 | — |
| 14 | Keltner 20x2 | tendance | 12 | 6,0 | 50 % | 0,257 | 0,161 | 0,4 | 1,9 | 0,2 | 97 | — |
| 3 | MACD 12-26-9 | tendance | 15 | 7,5 | 47 % | 0,059 | -0,043 | -0,1 | -0,6 | -2,9 | -32 | — |
| 24 | VWAP 2 écarts-types | retour | 9 | 4,5 | 56 % | -0,028 | -0,142 | -0,5 | -1,3 | -2,8 | -64 | — |
| 19 | RSI 2 Connors | retour | 11 | 5,5 | 55 % | -0,045 | -0,159 | -0,6 | -1,7 | -3,6 | -87 | — |
| 7 | ADX/DI 14 | tendance | 4 | 2,0 | 50 % | -0,071 | -0,180 | -0,3 | -0,7 | -1,4 | -36 | — |
| 0 | Témoin hasard | tendance | 8 | 4,0 | 38 % | -0,086 | -0,209 | -0,4 | -1,7 | -3,2 | -84 | — |
| 2 | Repli sur EMA 50 | tendance | 7 | 3,5 | 29 % | -0,143 | -0,270 | -0,5 | -1,9 | -3,2 | -94 | — |
| 10 | Aroon 25 | tendance | 8 | 4,0 | 25 % | -0,152 | -0,279 | -0,6 | -2,2 | -3,8 | -112 | — |
| 18 | RSI 14 | retour | 17 | 8,5 | 35 % | -0,320 | -0,418 | -2,0 | -7,1 | -9,6 | -356 | — |
| 26 | MFI 14 | retour | 7 | 3,5 | 29 % | -0,348 | -0,436 | -1,4 | -3,1 | -4,0 | -153 | — |
| 8 | Parabolic SAR | tendance | 16 | 8,0 | 31 % | -0,351 | -0,458 | -1,7 | -7,3 | -9,9 | -366 | — |
| 23 | Williams %R 14 | retour | 37 | 18,5 | 32 % | -0,365 | -0,472 | -3,5 | -17,5 | -23,4 | -873 | 0,00 |
| 20 | Retour Bollinger | retour | 20 | 10,0 | 35 % | -0,387 | -0,487 | -2,6 | -9,7 | -12,7 | -487 | — |
| 21 | Stochastique 14-3-3 | retour | 24 | 12,0 | 33 % | -0,394 | -0,501 | -2,9 | -12,0 | -15,9 | -601 | — |
| 27 | Avalement | retour | 6 | 3,0 | 33 % | -0,417 | -0,537 | -1,4 | -3,2 | -4,3 | -161 | — |
| 25 | Z-score 50 | retour | 17 | 8,5 | 18 % | -0,517 | -0,613 | -3,7 | -10,4 | -12,9 | -521 | — |
| 22 | CCI 20 | retour | 25 | 12,5 | 20 % | -0,560 | -0,661 | -4,6 | -16,5 | -20,3 | -826 | — |
| 28 | Pivots de la veille | retour | 0 | 0 | — | — | — | — | — | — | — | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
