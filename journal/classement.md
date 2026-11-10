# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-09 23:55 UTC (1 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Cassure avec volume | tendance | 3 | 3,0 | 100 % | 2,000 | 1,870 | 154,0 | 5,6 | 5,0 | 281 | — |
| 15 | Compression Bollinger | tendance | 2 | 2,0 | 100 % | 2,000 | 1,844 | nan | 3,7 | 3,2 | 184 | — |
| 7 | ADX/DI 14 | tendance | 1 | 1,0 | 100 % | 1,500 | 1,423 | nan | 1,4 | 1,3 | 71 | — |
| 4 | Supertrend 10x3 | tendance | 3 | 3,0 | 67 % | 1,000 | 0,872 | 0,9 | 2,6 | 2,0 | 131 | — |
| 2 | Repli sur EMA 50 | tendance | 3 | 3,0 | 67 % | 1,000 | 0,871 | 0,9 | 2,6 | 2,0 | 131 | — |
| 1 | EMA 9/21 | tendance | 4 | 4,0 | 75 % | 0,868 | 0,758 | 1,1 | 3,0 | 2,4 | 152 | — |
| 6 | Ichimoku nuage | tendance | 5 | 5,0 | 60 % | 0,800 | 0,689 | 0,9 | 3,4 | 2,6 | 172 | — |
| 9 | Heikin-Ashi | tendance | 6 | 6,0 | 67 % | 0,709 | 0,607 | 1,1 | 3,6 | 2,7 | 182 | — |
| 8 | Parabolic SAR | tendance | 4 | 4,0 | 75 % | 0,556 | 0,455 | 0,8 | 1,8 | 1,2 | 91 | — |
| 5 | Donchian 48 | tendance | 4 | 4,0 | 50 % | 0,500 | 0,382 | 0,4 | 1,5 | 0,8 | 76 | — |
| 0 | Témoin hasard | tendance | 2 | 2,0 | 50 % | 0,500 | 0,368 | nan | 0,7 | 0,3 | 37 | — |
| 24 | VWAP 2 écarts-types | retour | 4 | 4,0 | 75 % | 0,313 | 0,202 | 0,5 | 0,8 | 0,1 | 40 | — |
| 16 | Momentum ROC 12 | tendance | 7 | 7,0 | 43 % | 0,214 | 0,098 | 0,2 | 0,7 | -0,5 | 34 | — |
| 3 | MACD 12-26-9 | tendance | 3 | 3,0 | 67 % | 0,148 | 0,060 | 0,1 | 0,2 | -0,2 | 9 | — |
| 14 | Keltner 20x2 | tendance | 3 | 3,0 | 33 % | -0,000 | -0,112 | -0,1 | -0,3 | -0,8 | -17 | — |
| 11 | Cassure ouverture Londres | tendance | 1 | 1,0 | 0 % | -0,107 | -0,207 | nan | -0,2 | -0,4 | -10 | — |
| 26 | MFI 14 | retour | 2 | 2,0 | 50 % | -0,125 | -0,215 | nan | -0,4 | -0,7 | -22 | — |
| 27 | Avalement | retour | 2 | 2,0 | 50 % | -0,125 | -0,226 | nan | -0,5 | -0,8 | -23 | — |
| 19 | RSI 2 Connors | retour | 6 | 6,0 | 50 % | -0,125 | -0,234 | -0,6 | -1,4 | -2,4 | -70 | — |
| 23 | Williams %R 14 | retour | 14 | 14,0 | 43 % | -0,191 | -0,295 | -1,3 | -4,1 | -6,3 | -207 | — |
| 20 | Retour Bollinger | retour | 7 | 7,0 | 43 % | -0,250 | -0,345 | -1,0 | -2,4 | -3,4 | -121 | — |
| 22 | CCI 20 | retour | 7 | 7,0 | 43 % | -0,250 | -0,347 | -1,0 | -2,4 | -3,4 | -121 | — |
| 21 | Stochastique 14-3-3 | retour | 11 | 11,0 | 36 % | -0,364 | -0,470 | -1,8 | -5,2 | -6,9 | -259 | — |
| 12 | Cassure ouverture New York | tendance | 3 | 3,0 | 33 % | -0,510 | -0,595 | -1,2 | -1,8 | -2,2 | -89 | — |
| 18 | RSI 14 | retour | 7 | 7,0 | 29 % | -0,500 | -0,603 | -1,8 | -4,2 | -5,3 | -211 | — |
| 25 | Z-score 50 | retour | 6 | 6,0 | 17 % | -0,614 | -0,726 | -2,6 | -4,4 | -5,4 | -218 | — |
| 13 | Cassure de la veille | tendance | 1 | 1,0 | 0 % | -1,000 | -1,103 | nan | -1,1 | -1,3 | -55 | — |
| 10 | Aroon 25 | tendance | 3 | 3,0 | 0 % | -1,000 | -1,121 | -47,9 | -3,4 | -3,9 | -168 | — |
| 28 | Pivots de la veille | retour | 0 | 0 | — | — | — | — | — | — | — | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
