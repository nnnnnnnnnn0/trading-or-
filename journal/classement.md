# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-19 23:55 UTC (8 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Cassure avec volume | tendance | 15 | 1,9 | 60 % | 0,726 | 0,636 | 1,7 | 9,5 | 7,5 | 477 | — |
| 6 | Ichimoku nuage | tendance | 30 | 3,8 | 53 % | 0,365 | 0,271 | 1,1 | 8,1 | 3,9 | 407 | 0,17 |
| 11 | Cassure ouverture Londres | tendance | 14 | 1,8 | 50 % | 0,365 | 0,268 | 0,7 | 3,7 | 1,7 | 187 | — |
| 12 | Cassure ouverture New York | tendance | 15 | 1,9 | 53 % | 0,328 | 0,261 | 0,7 | 3,9 | 2,4 | 196 | — |
| 13 | Cassure de la veille | tendance | 11 | 1,4 | 45 % | 0,269 | 0,198 | 0,5 | 2,2 | 1,0 | 109 | — |
| 9 | Heikin-Ashi | tendance | 74 | 9,2 | 47 % | 0,208 | 0,118 | 0,8 | 8,7 | -1,4 | 435 | 0,10 |
| 2 | Repli sur EMA 50 | tendance | 28 | 3,5 | 46 % | 0,189 | 0,089 | 0,3 | 2,5 | -1,7 | 125 | — |
| 15 | Compression Bollinger | tendance | 19 | 2,4 | 47 % | 0,177 | 0,069 | 0,2 | 1,3 | -1,8 | 65 | — |
| 19 | RSI 2 Connors | retour | 43 | 5,4 | 63 % | 0,116 | 0,025 | 0,2 | 1,1 | -4,8 | 53 | 0,03 |
| 16 | Momentum ROC 12 | tendance | 59 | 7,4 | 42 % | 0,101 | 0,008 | 0,0 | 0,5 | -7,8 | 23 | 0,02 |
| 10 | Aroon 25 | tendance | 31 | 3,9 | 39 % | 0,098 | -0,001 | -0,0 | -0,0 | -4,6 | -1 | 0,02 |
| 5 | Donchian 48 | tendance | 37 | 4,6 | 38 % | 0,033 | -0,058 | -0,3 | -2,1 | -7,2 | -107 | 0,01 |
| 20 | Retour Bollinger | retour | 63 | 7,9 | 57 % | 0,005 | -0,085 | -0,8 | -5,4 | -13,8 | -268 | 0,00 |
| 21 | Stochastique 14-3-3 | retour | 75 | 9,4 | 55 % | -0,034 | -0,127 | -1,3 | -9,5 | -20,0 | -477 | 0,00 |
| 18 | RSI 14 | retour | 34 | 4,2 | 53 % | -0,042 | -0,130 | -0,9 | -4,4 | -8,9 | -221 | 0,00 |
| 22 | CCI 20 | retour | 97 | 12,1 | 53 % | -0,041 | -0,134 | -1,5 | -13,0 | -26,5 | -651 | 0,00 |
| 25 | Z-score 50 | retour | 45 | 5,6 | 51 % | -0,049 | -0,139 | -1,1 | -6,3 | -12,3 | -313 | 0,00 |
| 24 | VWAP 2 écarts-types | retour | 35 | 4,4 | 54 % | -0,050 | -0,147 | -1,0 | -5,1 | -10,2 | -257 | 0,00 |
| 4 | Supertrend 10x3 | tendance | 30 | 3,8 | 33 % | -0,052 | -0,150 | -0,6 | -4,5 | -8,9 | -226 | 0,01 |
| 1 | EMA 9/21 | tendance | 34 | 4,2 | 38 % | -0,067 | -0,163 | -0,8 | -5,6 | -10,5 | -278 | 0,00 |
| 3 | MACD 12-26-9 | tendance | 53 | 6,6 | 42 % | -0,078 | -0,166 | -1,0 | -8,8 | -15,8 | -439 | 0,00 |
| 23 | Williams %R 14 | retour | 124 | 15,5 | 50 % | -0,092 | -0,186 | -2,4 | -23,1 | -40,7 | -1154 | 0,00 |
| 26 | MFI 14 | retour | 22 | 2,8 | 45 % | -0,139 | -0,220 | -1,2 | -4,8 | -7,5 | -242 | — |
| 27 | Avalement | retour | 17 | 2,1 | 47 % | -0,132 | -0,236 | -1,1 | -4,0 | -6,6 | -200 | — |
| 8 | Parabolic SAR | tendance | 54 | 6,8 | 33 % | -0,220 | -0,310 | -2,1 | -16,7 | -24,0 | -836 | 0,00 |
| 14 | Keltner 20x2 | tendance | 43 | 5,4 | 33 % | -0,249 | -0,344 | -2,0 | -14,8 | -20,9 | -739 | 0,00 |
| 7 | ADX/DI 14 | tendance | 7 | 0,9 | 43 % | -0,243 | -0,351 | -0,9 | -2,5 | -3,6 | -123 | — |
| 0 | Témoin hasard | tendance | 16 | 2,0 | 31 % | -0,266 | -0,370 | -1,2 | -5,9 | -8,4 | -296 | — |
| 28 | Pivots de la veille | retour | 5 | 0,6 | 20 % | -0,650 | -0,721 | -2,1 | -3,6 | -4,1 | -180 | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
