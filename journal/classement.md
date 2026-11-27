# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-26 23:55 UTC (13 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | Cassure avec volume | tendance | 17 | 1,3 | 53 % | 0,523 | 0,436 | 1,2 | 7,4 | 5,2 | 370 | — |
| 2 | Repli sur EMA 50 | tendance | 44 | 3,4 | 50 % | 0,323 | 0,235 | 1,1 | 10,4 | 4,6 | 518 | 0,18 |
| 12 | Cassure ouverture New York | tendance | 21 | 1,6 | 52 % | 0,268 | 0,208 | 0,7 | 4,4 | 2,5 | 219 | — |
| 11 | Cassure ouverture Londres | tendance | 24 | 1,8 | 46 % | 0,186 | 0,100 | 0,4 | 2,4 | -0,7 | 120 | — |
| 13 | Cassure de la veille | tendance | 16 | 1,2 | 44 % | 0,156 | 0,091 | 0,3 | 1,4 | -0,1 | 72 | — |
| 6 | Ichimoku nuage | tendance | 54 | 4,2 | 44 % | 0,170 | 0,085 | 0,5 | 4,6 | -2,3 | 229 | 0,05 |
| 4 | Supertrend 10x3 | tendance | 47 | 3,6 | 40 % | 0,140 | 0,052 | 0,3 | 2,4 | -3,8 | 122 | 0,04 |
| 15 | Compression Bollinger | tendance | 30 | 2,3 | 43 % | 0,157 | 0,050 | 0,2 | 1,5 | -3,4 | 74 | 0,03 |
| 19 | RSI 2 Connors | retour | 66 | 5,1 | 62 % | 0,125 | 0,043 | 0,4 | 2,8 | -5,3 | 142 | 0,06 |
| 1 | EMA 9/21 | tendance | 52 | 4,0 | 42 % | 0,082 | -0,003 | -0,0 | -0,2 | -6,9 | -9 | 0,02 |
| 9 | Heikin-Ashi | tendance | 113 | 8,7 | 42 % | 0,064 | -0,018 | -0,1 | -2,0 | -15,8 | -100 | 0,01 |
| 0 | Témoin hasard | tendance | 32 | 2,5 | 44 % | 0,051 | -0,036 | -0,2 | -1,1 | -5,3 | -57 | 0,01 |
| 16 | Momentum ROC 12 | tendance | 91 | 7,0 | 41 % | 0,043 | -0,038 | -0,3 | -3,5 | -14,7 | -175 | 0,01 |
| 10 | Aroon 25 | tendance | 53 | 4,1 | 38 % | 0,046 | -0,039 | -0,2 | -2,1 | -8,9 | -103 | 0,01 |
| 24 | VWAP 2 écarts-types | retour | 59 | 4,5 | 59 % | 0,035 | -0,056 | -0,5 | -3,3 | -11,3 | -165 | 0,00 |
| 5 | Donchian 48 | tendance | 60 | 4,6 | 38 % | 0,011 | -0,070 | -0,4 | -4,2 | -11,4 | -209 | 0,01 |
| 25 | Z-score 50 | retour | 71 | 5,5 | 55 % | -0,003 | -0,083 | -0,8 | -5,9 | -14,4 | -295 | 0,00 |
| 20 | Retour Bollinger | retour | 96 | 7,4 | 56 % | -0,007 | -0,089 | -1,0 | -8,5 | -20,3 | -427 | 0,00 |
| 18 | RSI 14 | retour | 53 | 4,1 | 53 % | -0,032 | -0,106 | -0,9 | -5,6 | -11,5 | -281 | 0,00 |
| 7 | ADX/DI 14 | tendance | 15 | 1,2 | 47 % | -0,037 | -0,118 | -0,4 | -1,8 | -3,6 | -88 | — |
| 27 | Avalement | retour | 26 | 2,0 | 50 % | -0,033 | -0,128 | -0,8 | -3,3 | -7,0 | -166 | — |
| 22 | CCI 20 | retour | 146 | 11,2 | 52 % | -0,046 | -0,129 | -1,8 | -18,8 | -37,0 | -939 | 0,00 |
| 21 | Stochastique 14-3-3 | retour | 107 | 8,2 | 51 % | -0,059 | -0,145 | -1,8 | -15,5 | -29,3 | -774 | 0,00 |
| 23 | Williams %R 14 | retour | 185 | 14,2 | 51 % | -0,065 | -0,149 | -2,4 | -27,6 | -50,9 | -1378 | 0,00 |
| 26 | MFI 14 | retour | 28 | 2,2 | 46 % | -0,107 | -0,189 | -1,2 | -5,3 | -8,7 | -264 | — |
| 14 | Keltner 20x2 | tendance | 65 | 5,0 | 37 % | -0,114 | -0,199 | -1,3 | -12,9 | -21,1 | -645 | 0,00 |
| 3 | MACD 12-26-9 | tendance | 83 | 6,4 | 39 % | -0,122 | -0,200 | -1,6 | -16,6 | -26,3 | -829 | 0,00 |
| 8 | Parabolic SAR | tendance | 86 | 6,6 | 36 % | -0,153 | -0,234 | -1,9 | -20,1 | -30,5 | -1005 | 0,00 |
| 28 | Pivots de la veille | retour | 11 | 0,8 | 27 % | -0,475 | -0,533 | -2,2 | -5,9 | -6,8 | -293 | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
