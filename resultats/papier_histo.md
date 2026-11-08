# Paper trading 5 min : les 28 stratégies rejouées sur tout l'historique

Règles figées dans `regles/papier_5m_v1.md` avant ce calcul, jamais ajustées. Or au comptant 5 min du 2012-01-01 au 2026-11-06, **3874 jours de bourse**. Exécuté **une seule fois** (29 essais comptés dans le projet, avec le témoin). Même moteur que le suivi quotidien.

R net = après frais de base (0,02 % l'aller-retour) ; R stress = frais de 0,05 %. Le Deflated Sharpe tient compte des 28 essais.

| N° | Stratégie | Famille | Ordres | Par jour de bourse | Gagnants | R brut moyen (sans frais) | R net moyen | t | R net cumulé | R stress cumulé | Gain net $ | Deflated Sharpe (28 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 12 | Cassure ouverture New York | tendance | 5088 | 1,3 | 41 % | 0,029 | -0,071 | -4,3 | -361,3 | -1121,8 | -18067 | 0,00 |
| 13 | Cassure de la veille | tendance | 5984 | 1,5 | 38 % | 0,032 | -0,102 | -6,1 | -608,8 | -1805,7 | -30438 | 0,00 |
| 8 | Parabolic SAR | tendance | 25866 | 6,7 | 38 % | 0,017 | -0,129 | -16,5 | -3328,7 | -8963,3 | -166434 | 0,00 |
| 3 | MACD 12-26-9 | tendance | 23699 | 6,1 | 38 % | 0,013 | -0,131 | -16,3 | -3107,8 | -8231,3 | -155391 | 0,00 |
| 11 | Cassure ouverture Londres | tendance | 6301 | 1,6 | 37 % | 0,030 | -0,137 | -8,3 | -862,4 | -2438,6 | -43121 | 0,00 |
| 25 | Z-score 50 | retour | 19122 | 4,9 | 56 % | 0,003 | -0,139 | -22,7 | -2657,7 | -6716,7 | -132886 | 0,00 |
| 19 | RSI 2 Connors | retour | 20700 | 5,3 | 55 % | 0,012 | -0,140 | -24,3 | -2903,4 | -7625,3 | -145172 | 0,00 |
| 24 | VWAP 2 écarts-types | retour | 18850 | 4,9 | 56 % | 0,006 | -0,141 | -23,0 | -2655,6 | -6820,9 | -132780 | 0,00 |
| 18 | RSI 14 | retour | 13307 | 3,4 | 54 % | -0,017 | -0,144 | -20,0 | -1921,5 | -4458,4 | -96075 | 0,00 |
| 21 | Stochastique 14-3-3 | retour | 28367 | 7,3 | 55 % | 0,003 | -0,145 | -29,3 | -4111,1 | -10393,2 | -205557 | 0,00 |
| 26 | MFI 14 | retour | 8897 | 2,3 | 55 % | -0,002 | -0,146 | -16,6 | -1302,1 | -3233,5 | -65105 | 0,00 |
| 20 | Retour Bollinger | retour | 29037 | 7,5 | 55 % | -0,002 | -0,146 | -29,7 | -4250,7 | -10542,3 | -212536 | 0,00 |
| 0 | Témoin hasard | tendance | 8389 | 2,2 | 38 % | 0,004 | -0,147 | -10,9 | -1229,0 | -3119,0 | -61450 | 0,00 |
| 9 | Heikin-Ashi | tendance | 30070 | 7,8 | 37 % | -0,002 | -0,147 | -20,4 | -4413,1 | -10941,8 | -220655 | 0,00 |
| 22 | CCI 20 | retour | 39663 | 10,2 | 55 % | -0,002 | -0,148 | -35,5 | -5865,6 | -14561,2 | -293278 | 0,00 |
| 27 | Avalement | retour | 4747 | 1,2 | 55 % | 0,004 | -0,151 | -12,5 | -715,4 | -1820,0 | -35770 | 0,00 |
| 2 | Repli sur EMA 50 | tendance | 12629 | 3,3 | 37 % | 0,002 | -0,151 | -13,5 | -1910,3 | -4814,8 | -95517 | 0,00 |
| 6 | Ichimoku nuage | tendance | 16486 | 4,3 | 37 % | 0,001 | -0,152 | -15,3 | -2504,9 | -6281,1 | -125246 | 0,00 |
| 17 | Cassure avec volume | tendance | 12049 | 3,1 | 35 % | -0,007 | -0,155 | -12,9 | -1864,3 | -4525,3 | -93215 | 0,00 |
| 5 | Donchian 48 | tendance | 15731 | 4,1 | 36 % | -0,014 | -0,155 | -15,2 | -2442,1 | -5776,1 | -122104 | 0,00 |
| 1 | EMA 9/21 | tendance | 17109 | 4,4 | 37 % | -0,003 | -0,156 | -16,1 | -2666,0 | -6584,5 | -133302 | 0,00 |
| 10 | Aroon 25 | tendance | 16237 | 4,2 | 38 % | -0,003 | -0,156 | -15,8 | -2535,1 | -6272,5 | -126755 | 0,00 |
| 28 | Pivots de la veille | retour | 6292 | 1,6 | 54 % | -0,028 | -0,157 | -14,8 | -988,5 | -2209,6 | -49423 | 0,00 |
| 23 | Williams %R 14 | retour | 48938 | 12,6 | 55 % | -0,009 | -0,158 | -41,7 | -7717,3 | -18599,5 | -385866 | 0,00 |
| 16 | Momentum ROC 12 | tendance | 25461 | 6,6 | 36 % | -0,020 | -0,160 | -20,4 | -4084,4 | -9433,0 | -204220 | 0,00 |
| 14 | Keltner 20x2 | tendance | 16227 | 4,2 | 36 % | -0,021 | -0,170 | -16,9 | -2758,0 | -6392,4 | -137899 | 0,00 |
| 7 | ADX/DI 14 | tendance | 6406 | 1,7 | 36 % | -0,036 | -0,176 | -11,3 | -1127,1 | -2468,6 | -56353 | 0,00 |
| 4 | Supertrend 10x3 | tendance | 14363 | 3,7 | 36 % | -0,028 | -0,181 | -17,0 | -2595,3 | -5891,8 | -129763 | 0,00 |
| 15 | Compression Bollinger | tendance | 4677 | 1,2 | 36 % | 0,002 | -0,192 | -10,2 | -897,8 | -2256,4 | -44890 | 0,00 |

### Première moitié contre seconde moitié (R net moyen par ordre)

| N° | Stratégie | 1re moitié (ordres / R net moyen) | 2e moitié (ordres / R net moyen) |
| --- | --- | --- | --- |
| 1 | EMA 9/21 | 8639 / -0,162 | 8470 / -0,150 |
| 2 | Repli sur EMA 50 | 6320 / -0,177 | 6309 / -0,125 |
| 3 | MACD 12-26-9 | 11962 / -0,120 | 11737 / -0,143 |
| 4 | Supertrend 10x3 | 7172 / -0,190 | 7191 / -0,171 |
| 5 | Donchian 48 | 7854 / -0,154 | 7877 / -0,156 |
| 6 | Ichimoku nuage | 8289 / -0,154 | 8197 / -0,150 |
| 7 | ADX/DI 14 | 3363 / -0,164 | 3043 / -0,189 |
| 8 | Parabolic SAR | 12868 / -0,128 | 12998 / -0,129 |
| 9 | Heikin-Ashi | 15192 / -0,143 | 14878 / -0,150 |
| 10 | Aroon 25 | 8303 / -0,159 | 7934 / -0,153 |
| 11 | Cassure ouverture Londres | 3101 / -0,115 | 3200 / -0,158 |
| 12 | Cassure ouverture New York | 2552 / -0,074 | 2536 / -0,068 |
| 13 | Cassure de la veille | 2902 / -0,104 | 3082 / -0,099 |
| 14 | Keltner 20x2 | 8391 / -0,177 | 7836 / -0,162 |
| 15 | Compression Bollinger | 2190 / -0,136 | 2487 / -0,241 |
| 16 | Momentum ROC 12 | 12709 / -0,153 | 12752 / -0,168 |
| 17 | Cassure avec volume | 6363 / -0,159 | 5686 / -0,150 |
| 18 | RSI 14 | 6893 / -0,153 | 6414 / -0,135 |
| 19 | RSI 2 Connors | 10360 / -0,154 | 10340 / -0,127 |
| 20 | Retour Bollinger | 14807 / -0,156 | 14230 / -0,136 |
| 21 | Stochastique 14-3-3 | 13481 / -0,161 | 14886 / -0,130 |
| 22 | CCI 20 | 19701 / -0,157 | 19962 / -0,139 |
| 23 | Williams %R 14 | 24495 / -0,174 | 24443 / -0,141 |
| 24 | VWAP 2 écarts-types | 9680 / -0,150 | 9170 / -0,131 |
| 25 | Z-score 50 | 9775 / -0,156 | 9347 / -0,121 |
| 26 | MFI 14 | 4128 / -0,160 | 4769 / -0,134 |
| 27 | Avalement | 2002 / -0,186 | 2745 / -0,125 |
| 28 | Pivots de la veille | 3048 / -0,172 | 3244 / -0,143 |
| 0 | Témoin hasard | 4198 / -0,135 | 4191 / -0,158 |

Parmi les 28 stratégies : 0 ont un R net moyen positif, dont 0 avec t ≥ 2 ; avec 28 essais, environ 1 à 2 stratégies passent t ≥ 2 par pur hasard. Témoin hasard : R net moyen -0,147 (8389 ordres).

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
