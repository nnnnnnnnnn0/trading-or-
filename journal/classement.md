# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-23 23:55 UTC (10 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Cassure avec volume | tendance | 17 | 1,7 | 53 % | 0,523 | 0,436 | 1,2 | 7,4 | 5,2 | 370 | — |
| 11 | Cassure ouverture Londres | tendance | 17 | 1,7 | 47 % | 0,322 | 0,232 | 0,7 | 3,9 | 1,7 | 197 | — |
| 12 | Cassure ouverture New York | tendance | 18 | 1,8 | 56 % | 0,274 | 0,213 | 0,7 | 3,8 | 2,2 | 191 | — |
| 2 | Repli sur EMA 50 | tendance | 36 | 3,6 | 50 % | 0,271 | 0,178 | 0,8 | 6,4 | 1,4 | 321 | 0,10 |
| 13 | Cassure de la veille | tendance | 14 | 1,4 | 43 % | 0,211 | 0,144 | 0,4 | 2,0 | 0,6 | 101 | — |
| 10 | Aroon 25 | tendance | 40 | 4,0 | 42 % | 0,174 | 0,085 | 0,4 | 3,4 | -1,9 | 170 | 0,05 |
| 6 | Ichimoku nuage | tendance | 44 | 4,4 | 45 % | 0,163 | 0,077 | 0,4 | 3,4 | -2,3 | 168 | 0,05 |
| 15 | Compression Bollinger | tendance | 22 | 2,2 | 45 % | 0,153 | 0,047 | 0,2 | 1,0 | -2,5 | 52 | — |
| 19 | RSI 2 Connors | retour | 56 | 5,6 | 62 % | 0,107 | 0,023 | 0,2 | 1,3 | -5,7 | 66 | 0,03 |
| 9 | Heikin-Ashi | tendance | 92 | 9,2 | 42 % | 0,062 | -0,023 | -0,2 | -2,1 | -13,9 | -107 | 0,01 |
| 18 | RSI 14 | retour | 39 | 3,9 | 56 % | 0,040 | -0,042 | -0,3 | -1,7 | -6,5 | -83 | 0,01 |
| 24 | VWAP 2 écarts-types | retour | 48 | 4,8 | 60 % | 0,043 | -0,046 | -0,4 | -2,2 | -8,6 | -111 | 0,01 |
| 16 | Momentum ROC 12 | tendance | 76 | 7,6 | 39 % | 0,021 | -0,064 | -0,5 | -4,9 | -14,6 | -245 | 0,01 |
| 20 | Retour Bollinger | retour | 80 | 8,0 | 57 % | 0,018 | -0,066 | -0,7 | -5,2 | -15,3 | -262 | 0,00 |
| 25 | Z-score 50 | retour | 55 | 5,5 | 55 % | 0,001 | -0,083 | -0,7 | -4,6 | -11,5 | -228 | 0,00 |
| 22 | CCI 20 | retour | 118 | 11,8 | 55 % | -0,002 | -0,088 | -1,1 | -10,4 | -25,7 | -522 | 0,00 |
| 5 | Donchian 48 | tendance | 46 | 4,6 | 39 % | -0,009 | -0,093 | -0,5 | -4,3 | -10,1 | -213 | 0,01 |
| 21 | Stochastique 14-3-3 | retour | 86 | 8,6 | 55 % | -0,015 | -0,104 | -1,1 | -9,0 | -20,5 | -448 | 0,00 |
| 27 | Avalement | retour | 23 | 2,3 | 52 % | -0,011 | -0,106 | -0,6 | -2,4 | -5,7 | -122 | — |
| 1 | EMA 9/21 | tendance | 44 | 4,4 | 39 % | -0,033 | -0,123 | -0,6 | -5,4 | -11,3 | -270 | 0,00 |
| 23 | Williams %R 14 | retour | 150 | 15,0 | 53 % | -0,038 | -0,127 | -1,8 | -19,1 | -39,1 | -953 | 0,00 |
| 4 | Supertrend 10x3 | tendance | 38 | 3,8 | 34 % | -0,060 | -0,151 | -0,7 | -5,8 | -11,0 | -288 | 0,00 |
| 26 | MFI 14 | retour | 23 | 2,3 | 48 % | -0,100 | -0,181 | -1,0 | -4,2 | -6,9 | -208 | — |
| 3 | MACD 12-26-9 | tendance | 67 | 6,7 | 40 % | -0,121 | -0,202 | -1,5 | -13,5 | -21,7 | -677 | 0,00 |
| 8 | Parabolic SAR | tendance | 67 | 6,7 | 36 % | -0,152 | -0,237 | -1,7 | -15,9 | -24,4 | -793 | 0,00 |
| 7 | ADX/DI 14 | tendance | 10 | 1,0 | 40 % | -0,169 | -0,261 | -0,8 | -2,6 | -4,0 | -130 | — |
| 0 | Témoin hasard | tendance | 22 | 2,2 | 32 % | -0,193 | -0,291 | -1,1 | -6,4 | -9,6 | -320 | — |
| 14 | Keltner 20x2 | tendance | 53 | 5,3 | 34 % | -0,245 | -0,333 | -2,2 | -17,6 | -24,6 | -882 | 0,00 |
| 28 | Pivots de la veille | retour | 8 | 0,8 | 25 % | -0,562 | -0,626 | -2,2 | -5,0 | -5,8 | -250 | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
