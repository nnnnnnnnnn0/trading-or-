# Classement cumulé des stratégies (paper trading 5 min)

Du 2026-11-09 au 2026-11-10 23:55 UTC (1 jours de bourse). **Aucune conclusion avant au moins 100 ordres par stratégie, t ≥ 2 et Deflated Sharpe ≥ 0,95.** Avec 28 stratégies, quelques-unes sembleront bonnes par chance : compare toujours au **témoin hasard** (n° 0).

R = risque d'un trade (2 × ATR). « R net » = après frais de base (0,02 %) ; « R stress » = frais de 0,05 %. Compte fictif de 10 000 $, risque 50 $ par ordre.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 15 | Compression Bollinger | tendance | 5 | 5,0 | 100 % | 1,734 | 1,607 | 6,0 | 8,0 | 7,1 | 402 | — |
| 17 | Cassure avec volume | tendance | 5 | 5,0 | 80 % | 1,400 | 1,294 | 2,2 | 6,5 | 5,7 | 323 | — |
| 11 | Cassure ouverture Londres | tendance | 2 | 2,0 | 50 % | 0,946 | 0,843 | nan | 1,7 | 1,4 | 84 | — |
| 9 | Heikin-Ashi | tendance | 11 | 11,0 | 73 % | 0,912 | 0,821 | 2,2 | 9,0 | 7,5 | 452 | — |
| 7 | ADX/DI 14 | tendance | 2 | 2,0 | 100 % | 0,857 | 0,760 | nan | 1,5 | 1,2 | 76 | — |
| 6 | Ichimoku nuage | tendance | 7 | 7,0 | 57 % | 0,714 | 0,601 | 1,0 | 4,2 | 3,0 | 210 | — |
| 1 | EMA 9/21 | tendance | 8 | 8,0 | 62 % | 0,684 | 0,572 | 1,1 | 4,6 | 3,2 | 229 | — |
| 2 | Repli sur EMA 50 | tendance | 4 | 4,0 | 50 % | 0,500 | 0,374 | 0,4 | 1,5 | 0,7 | 75 | — |
| 4 | Supertrend 10x3 | tendance | 5 | 5,0 | 60 % | 0,443 | 0,321 | 0,5 | 1,6 | 0,7 | 80 | — |
| 16 | Momentum ROC 12 | tendance | 14 | 14,0 | 50 % | 0,324 | 0,221 | 0,6 | 3,1 | 0,9 | 155 | — |
| 5 | Donchian 48 | tendance | 8 | 8,0 | 38 % | 0,200 | 0,101 | 0,2 | 0,8 | -0,4 | 40 | — |
| 0 | Témoin hasard | tendance | 5 | 5,0 | 40 % | 0,200 | 0,078 | 0,1 | 0,4 | -0,5 | 20 | — |
| 24 | VWAP 2 écarts-types | retour | 6 | 6,0 | 67 % | 0,167 | 0,054 | 0,1 | 0,3 | -0,7 | 16 | — |
| 3 | MACD 12-26-9 | tendance | 8 | 8,0 | 50 % | 0,049 | -0,036 | -0,1 | -0,3 | -1,3 | -15 | — |
| 8 | Parabolic SAR | tendance | 10 | 10,0 | 50 % | 0,039 | -0,057 | -0,2 | -0,6 | -2,0 | -29 | — |
| 13 | Cassure de la veille | tendance | 3 | 3,0 | 33 % | -0,000 | -0,068 | -0,1 | -0,2 | -0,5 | -10 | — |
| 19 | RSI 2 Connors | retour | 9 | 9,0 | 56 % | -0,028 | -0,140 | -0,4 | -1,3 | -2,8 | -63 | — |
| 14 | Keltner 20x2 | tendance | 7 | 7,0 | 29 % | -0,057 | -0,143 | -0,3 | -1,0 | -1,9 | -50 | — |
| 26 | MFI 14 | retour | 5 | 5,0 | 40 % | -0,087 | -0,168 | -0,4 | -0,8 | -1,4 | -42 | — |
| 12 | Cassure ouverture New York | tendance | 5 | 5,0 | 40 % | -0,106 | -0,183 | -0,3 | -0,9 | -1,5 | -46 | — |
| 27 | Avalement | retour | 4 | 4,0 | 50 % | -0,125 | -0,235 | -0,5 | -0,9 | -1,6 | -47 | — |
| 18 | RSI 14 | retour | 11 | 11,0 | 36 % | -0,267 | -0,358 | -1,4 | -3,9 | -5,4 | -197 | — |
| 23 | Williams %R 14 | retour | 24 | 24,0 | 33 % | -0,338 | -0,435 | -2,6 | -10,4 | -13,9 | -522 | — |
| 21 | Stochastique 14-3-3 | retour | 16 | 16,0 | 38 % | -0,344 | -0,447 | -2,0 | -7,1 | -9,6 | -357 | — |
| 10 | Aroon 25 | tendance | 6 | 6,0 | 17 % | -0,369 | -0,491 | -1,0 | -2,9 | -4,0 | -147 | — |
| 22 | CCI 20 | retour | 14 | 14,0 | 29 % | -0,424 | -0,512 | -2,3 | -7,2 | -9,0 | -359 | — |
| 20 | Retour Bollinger | retour | 13 | 13,0 | 31 % | -0,462 | -0,551 | -2,3 | -7,2 | -8,9 | -358 | — |
| 25 | Z-score 50 | retour | 11 | 11,0 | 18 % | -0,493 | -0,582 | -2,8 | -6,4 | -7,9 | -320 | — |
| 28 | Pivots de la veille | retour | 0 | 0 | — | — | — | — | — | — | — | — |

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
