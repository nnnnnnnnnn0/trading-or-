# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-17 23:55 UTC (6 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Cassure avec volume | tendance | 13 | 2,2 | 62 % | 0,760 | 0,668 | 1,6 | 8,7 | 6,9 | 434 | — |
| 11 | Cassure ouverture Londres | tendance | 10 | 1,7 | 60 % | 0,673 | 0,570 | 1,3 | 5,7 | 4,2 | 285 | — |
| 13 | Cassure de la veille | tendance | 8 | 1,3 | 50 % | 0,370 | 0,303 | 0,6 | 2,4 | 1,6 | 121 | — |
| 6 | Ichimoku nuage | tendance | 25 | 4,2 | 52 % | 0,316 | 0,218 | 0,8 | 5,4 | 1,7 | 272 | — |
| 9 | Heikin-Ashi | tendance | 56 | 9,3 | 52 % | 0,261 | 0,164 | 0,9 | 9,2 | 1,1 | 460 | 0,13 |
| 15 | Compression Bollinger | tendance | 15 | 2,5 | 47 % | 0,247 | 0,130 | 0,4 | 1,9 | -0,7 | 97 | — |
| 5 | Donchian 48 | tendance | 28 | 4,7 | 43 % | 0,179 | 0,082 | 0,3 | 2,3 | -1,7 | 115 | — |
| 12 | Cassure ouverture New York | tendance | 13 | 2,2 | 46 % | 0,070 | 0,003 | 0,0 | 0,0 | -1,3 | 2 | — |
| 2 | Repli sur EMA 50 | tendance | 23 | 3,8 | 43 % | 0,067 | -0,039 | -0,1 | -0,9 | -4,5 | -44 | — |
| 3 | MACD 12-26-9 | tendance | 38 | 6,3 | 47 % | 0,025 | -0,068 | -0,4 | -2,6 | -7,8 | -129 | 0,01 |
| 16 | Momentum ROC 12 | tendance | 47 | 7,8 | 38 % | 0,022 | -0,077 | -0,4 | -3,6 | -10,5 | -180 | 0,01 |
| 20 | Retour Bollinger | retour | 50 | 8,3 | 58 % | 0,006 | -0,088 | -0,7 | -4,4 | -11,5 | -221 | 0,00 |
| 19 | RSI 2 Connors | retour | 33 | 5,5 | 55 % | -0,023 | -0,119 | -0,8 | -3,9 | -8,7 | -196 | 0,00 |
| 25 | Z-score 50 | retour | 35 | 5,8 | 51 % | -0,028 | -0,120 | -0,9 | -4,2 | -9,1 | -211 | 0,00 |
| 1 | EMA 9/21 | tendance | 29 | 4,8 | 41 % | -0,032 | -0,131 | -0,6 | -3,8 | -8,1 | -190 | — |
| 10 | Aroon 25 | tendance | 24 | 4,0 | 33 % | -0,032 | -0,139 | -0,5 | -3,3 | -7,2 | -167 | — |
| 24 | VWAP 2 écarts-types | retour | 26 | 4,3 | 54 % | -0,058 | -0,162 | -0,9 | -4,2 | -8,3 | -210 | — |
| 4 | Supertrend 10x3 | tendance | 24 | 4,0 | 33 % | -0,065 | -0,169 | -0,7 | -4,1 | -7,8 | -203 | — |
| 22 | CCI 20 | retour | 72 | 12,0 | 50 % | -0,073 | -0,170 | -1,7 | -12,2 | -22,8 | -612 | 0,00 |
| 23 | Williams %R 14 | retour | 96 | 16,0 | 50 % | -0,089 | -0,189 | -2,2 | -18,2 | -32,6 | -909 | 0,00 |
| 21 | Stochastique 14-3-3 | retour | 53 | 8,8 | 51 % | -0,095 | -0,195 | -1,6 | -10,3 | -18,2 | -515 | 0,00 |
| 18 | RSI 14 | retour | 27 | 4,5 | 48 % | -0,118 | -0,211 | -1,2 | -5,7 | -9,4 | -284 | — |
| 8 | Parabolic SAR | tendance | 39 | 6,5 | 38 % | -0,147 | -0,242 | -1,4 | -9,4 | -14,9 | -471 | 0,00 |
| 14 | Keltner 20x2 | tendance | 33 | 5,5 | 30 % | -0,229 | -0,328 | -1,6 | -10,8 | -15,7 | -542 | 0,00 |
| 7 | ADX/DI 14 | tendance | 7 | 1,2 | 43 % | -0,243 | -0,351 | -0,9 | -2,5 | -3,6 | -123 | — |
| 26 | MFI 14 | retour | 19 | 3,2 | 37 % | -0,279 | -0,363 | -1,9 | -6,9 | -9,3 | -345 | — |
| 0 | Témoin hasard | tendance | 16 | 2,7 | 31 % | -0,266 | -0,370 | -1,2 | -5,9 | -8,4 | -296 | — |
| 27 | Avalement | retour | 13 | 2,2 | 38 % | -0,327 | -0,442 | -1,8 | -5,7 | -8,0 | -287 | — |
| 28 | Pivots de la veille | retour | 3 | 0,5 | 33 % | -0,417 | -0,500 | -0,9 | -1,5 | -1,9 | -75 | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
