# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-16 23:55 UTC (5 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Cassure avec volume | tendance | 12 | 2,4 | 67 % | 0,907 | 0,815 | 2,0 | 9,8 | 8,1 | 489 | — |
| 11 | Cassure ouverture Londres | tendance | 8 | 1,6 | 62 % | 0,716 | 0,618 | 1,4 | 4,9 | 3,8 | 247 | — |
| 13 | Cassure de la veille | tendance | 8 | 1,6 | 50 % | 0,370 | 0,303 | 0,6 | 2,4 | 1,6 | 121 | — |
| 9 | Heikin-Ashi | tendance | 45 | 9,0 | 56 % | 0,341 | 0,246 | 1,3 | 11,1 | 4,7 | 554 | 0,21 |
| 5 | Donchian 48 | tendance | 23 | 4,6 | 48 % | 0,305 | 0,211 | 0,7 | 4,8 | 1,6 | 242 | — |
| 6 | Ichimoku nuage | tendance | 21 | 4,2 | 52 % | 0,239 | 0,141 | 0,5 | 3,0 | -0,1 | 149 | — |
| 15 | Compression Bollinger | tendance | 13 | 2,6 | 46 % | 0,208 | 0,092 | 0,2 | 1,2 | -1,1 | 60 | — |
| 2 | Repli sur EMA 50 | tendance | 18 | 3,6 | 50 % | 0,197 | 0,085 | 0,3 | 1,5 | -1,5 | 77 | — |
| 16 | Momentum ROC 12 | tendance | 36 | 7,2 | 44 % | 0,157 | 0,062 | 0,3 | 2,2 | -2,9 | 111 | 0,04 |
| 19 | RSI 2 Connors | retour | 27 | 5,4 | 59 % | 0,047 | -0,049 | -0,3 | -1,3 | -5,2 | -66 | — |
| 3 | MACD 12-26-9 | tendance | 30 | 6,0 | 50 % | 0,033 | -0,056 | -0,3 | -1,7 | -5,7 | -84 | 0,01 |
| 10 | Aroon 25 | tendance | 20 | 4,0 | 35 % | 0,011 | -0,098 | -0,3 | -2,0 | -5,3 | -98 | — |
| 20 | Retour Bollinger | retour | 42 | 8,4 | 57 % | -0,011 | -0,102 | -0,8 | -4,3 | -10,0 | -214 | 0,00 |
| 1 | EMA 9/21 | tendance | 24 | 4,8 | 42 % | -0,053 | -0,153 | -0,6 | -3,7 | -7,3 | -183 | — |
| 12 | Cassure ouverture New York | tendance | 12 | 2,4 | 42 % | -0,090 | -0,158 | -0,5 | -1,9 | -3,1 | -95 | — |
| 22 | CCI 20 | retour | 59 | 11,8 | 49 % | -0,070 | -0,165 | -1,5 | -9,8 | -18,2 | -488 | 0,00 |
| 23 | Williams %R 14 | retour | 81 | 16,2 | 48 % | -0,115 | -0,216 | -2,3 | -17,5 | -29,7 | -874 | 0,00 |
| 25 | Z-score 50 | retour | 29 | 5,8 | 45 % | -0,128 | -0,218 | -1,4 | -6,3 | -10,3 | -317 | — |
| 24 | VWAP 2 écarts-types | retour | 20 | 4,0 | 50 % | -0,125 | -0,231 | -1,1 | -4,6 | -7,8 | -231 | — |
| 14 | Keltner 20x2 | tendance | 26 | 5,2 | 35 % | -0,137 | -0,233 | -1,0 | -6,1 | -9,8 | -303 | — |
| 21 | Stochastique 14-3-3 | retour | 44 | 8,8 | 48 % | -0,149 | -0,247 | -1,9 | -10,9 | -17,3 | -543 | 0,00 |
| 4 | Supertrend 10x3 | tendance | 20 | 4,0 | 30 % | -0,179 | -0,281 | -1,1 | -5,6 | -8,7 | -281 | — |
| 18 | RSI 14 | retour | 23 | 4,6 | 43 % | -0,193 | -0,285 | -1,6 | -6,6 | -9,7 | -328 | — |
| 8 | Parabolic SAR | tendance | 32 | 6,4 | 38 % | -0,212 | -0,305 | -1,7 | -9,8 | -14,3 | -489 | 0,00 |
| 26 | MFI 14 | retour | 16 | 3,2 | 38 % | -0,253 | -0,333 | -1,6 | -5,3 | -7,2 | -266 | — |
| 7 | ADX/DI 14 | tendance | 7 | 1,4 | 43 % | -0,243 | -0,351 | -0,9 | -2,5 | -3,6 | -123 | — |
| 27 | Avalement | retour | 12 | 2,4 | 42 % | -0,271 | -0,385 | -1,5 | -4,6 | -6,7 | -231 | — |
| 0 | Témoin hasard | tendance | 14 | 2,8 | 29 % | -0,334 | -0,440 | -1,4 | -6,2 | -8,4 | -308 | — |
| 28 | Pivots de la veille | retour | 3 | 0,6 | 33 % | -0,417 | -0,500 | -0,9 | -1,5 | -1,9 | -75 | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
