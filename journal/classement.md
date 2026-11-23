# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-22 23:55 UTC (10 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Cassure avec volume | tendance | 17 | 1,7 | 53 % | 0,523 | 0,436 | 1,2 | 7,4 | 5,2 | 370 | — |
| 11 | Cassure ouverture Londres | tendance | 16 | 1,6 | 50 % | 0,382 | 0,291 | 0,8 | 4,7 | 2,5 | 233 | — |
| 6 | Ichimoku nuage | tendance | 35 | 3,5 | 51 % | 0,342 | 0,254 | 1,1 | 8,9 | 4,3 | 444 | 0,17 |
| 13 | Cassure de la veille | tendance | 13 | 1,3 | 46 % | 0,304 | 0,237 | 0,6 | 3,1 | 1,8 | 154 | — |
| 12 | Cassure ouverture New York | tendance | 17 | 1,7 | 53 % | 0,280 | 0,216 | 0,7 | 3,7 | 2,1 | 184 | — |
| 2 | Repli sur EMA 50 | tendance | 32 | 3,2 | 47 % | 0,228 | 0,134 | 0,5 | 4,3 | -0,2 | 214 | 0,06 |
| 15 | Compression Bollinger | tendance | 21 | 2,1 | 48 % | 0,208 | 0,103 | 0,3 | 2,2 | -1,2 | 108 | — |
| 9 | Heikin-Ashi | tendance | 82 | 8,2 | 45 % | 0,153 | 0,067 | 0,5 | 5,5 | -5,1 | 276 | 0,06 |
| 19 | RSI 2 Connors | retour | 51 | 5,1 | 65 % | 0,147 | 0,063 | 0,5 | 3,2 | -3,2 | 160 | 0,07 |
| 10 | Aroon 25 | tendance | 35 | 3,5 | 40 % | 0,111 | 0,019 | 0,1 | 0,7 | -4,2 | 33 | 0,02 |
| 16 | Momentum ROC 12 | tendance | 69 | 6,9 | 39 % | 0,034 | -0,053 | -0,4 | -3,7 | -12,7 | -184 | 0,01 |
| 18 | RSI 14 | retour | 37 | 3,7 | 57 % | 0,022 | -0,062 | -0,4 | -2,3 | -6,9 | -115 | 0,01 |
| 5 | Donchian 48 | tendance | 41 | 4,1 | 39 % | 0,021 | -0,065 | -0,3 | -2,7 | -8,0 | -134 | 0,01 |
| 22 | CCI 20 | retour | 110 | 11,0 | 55 % | 0,004 | -0,083 | -1,0 | -9,2 | -23,6 | -458 | 0,00 |
| 20 | Retour Bollinger | retour | 72 | 7,2 | 57 % | 0,001 | -0,084 | -0,8 | -6,0 | -15,2 | -302 | 0,00 |
| 25 | Z-score 50 | retour | 50 | 5,0 | 54 % | -0,004 | -0,089 | -0,8 | -4,5 | -10,9 | -224 | 0,00 |
| 27 | Avalement | retour | 20 | 2,0 | 55 % | 0,000 | -0,096 | -0,5 | -1,9 | -4,8 | -96 | — |
| 1 | EMA 9/21 | tendance | 38 | 3,8 | 39 % | -0,012 | -0,104 | -0,5 | -4,0 | -9,2 | -198 | 0,01 |
| 24 | VWAP 2 écarts-types | retour | 41 | 4,1 | 56 % | -0,018 | -0,109 | -0,8 | -4,5 | -10,0 | -223 | 0,00 |
| 21 | Stochastique 14-3-3 | retour | 80 | 8,0 | 55 % | -0,019 | -0,109 | -1,1 | -8,8 | -19,7 | -438 | 0,00 |
| 4 | Supertrend 10x3 | tendance | 34 | 3,4 | 35 % | -0,022 | -0,114 | -0,5 | -3,9 | -8,6 | -193 | 0,01 |
| 23 | Williams %R 14 | retour | 137 | 13,7 | 52 % | -0,063 | -0,153 | -2,1 | -21,0 | -39,5 | -1048 | 0,00 |
| 3 | MACD 12-26-9 | tendance | 61 | 6,1 | 39 % | -0,120 | -0,202 | -1,4 | -12,3 | -19,9 | -616 | 0,00 |
| 26 | MFI 14 | retour | 22 | 2,2 | 45 % | -0,139 | -0,220 | -1,2 | -4,8 | -7,5 | -242 | — |
| 0 | Témoin hasard | tendance | 17 | 1,7 | 35 % | -0,132 | -0,233 | -0,7 | -4,0 | -6,5 | -198 | — |
| 8 | Parabolic SAR | tendance | 61 | 6,1 | 34 % | -0,183 | -0,269 | -1,9 | -16,4 | -24,2 | -820 | 0,00 |
| 14 | Keltner 20x2 | tendance | 48 | 4,8 | 33 % | -0,251 | -0,341 | -2,1 | -16,4 | -22,9 | -819 | 0,00 |
| 7 | ADX/DI 14 | tendance | 8 | 0,8 | 38 % | -0,338 | -0,437 | -1,2 | -3,5 | -4,7 | -175 | — |
| 28 | Pivots de la veille | retour | 7 | 0,7 | 29 % | -0,500 | -0,562 | -1,8 | -3,9 | -4,6 | -197 | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
