# Backtest d'indicateurs sur l'or (v1)

Données : 4756 jours (2006-10-20 à 2026-11-05), futures GC=F. Développement (70 %) : 2008-04-25 à 2021-06-28. Contrôle (30 %) : 2021-06-29 à 2026-11-05.

**34 essais comptés** (17 stratégies, 2 modes). Aucun paramètre n'a été ajusté : valeurs standard.

**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

Référence : garder l'or en contrôle = Sharpe 0,94, rendement annuel 17,7 %.

## Résultats

Sharpe = rendement / risque annualisé (au-dessus de 0,5 c'est bien, au-dessus de 1 c'est rare). « Hasard » = part de 1 000 décalages aléatoires de la même série de positions qui font au moins aussi bien : c'est le test qui neutralise la tendance haussière de l'or. Frais ×2 : Sharpe avec frais doublés.

| Indicateur | Mode | Sharpe développement | Rendement annuel contrôle | Sharpe contrôle | t contrôle | Hasard | Sharpe contrôle, frais ×2 | Perte max contrôle | Entrées contrôle | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RSI 14, retour à la moyenne (30/70) | achat + vente | 0,19 | -1,7 % | -0,13 | -0,3 | 42 % | -0,15 | -40 % | 21 | Rejeté |
| RSI 14, retour à la moyenne (30/70) | achat seulement | 0,37 | 5,2 % | 0,86 | 2,0 | 1 % | 0,85 | -9 % | 8 | À surveiller |
| RSI 2 de Connors + tendance MA200 | achat + vente | -0,32 | -1,8 % | -0,25 | -0,5 | 82 % | -0,30 | -19 % | 43 | Rejeté |
| RSI 2 de Connors + tendance MA200 | achat seulement | 0,13 | -0,9 % | -0,13 | -0,3 | 84 % | -0,17 | -16 % | 30 | Rejeté |
| MACD 12-26-9 (croisement) | achat + vente | 0,08 | -7,2 % | -0,38 | -0,9 | 80 % | -0,44 | -53 % | 113 | Rejeté |
| MACD 12-26-9 (croisement) | achat seulement | 0,33 | 5,2 % | 0,38 | 0,9 | 79 % | 0,34 | -21 % | 56 | Rejeté |
| Bollinger 20-2, retour à la moyenne | achat + vente | 0,26 | -1,6 % | -0,11 | -0,3 | 40 % | -0,14 | -35 % | 43 | Rejeté |
| Bollinger 20-2, retour à la moyenne | achat seulement | 0,40 | 3,7 % | 0,47 | 1,2 | 40 % | 0,45 | -12 % | 15 | Rejeté |
| Bollinger 20-2, cassure | achat + vente | -0,33 | 0,9 % | 0,06 | 0,1 | 57 % | 0,03 | -18 % | 43 | Rejeté |
| Bollinger 20-2, cassure | achat seulement | -0,01 | 4,8 % | 0,40 | 1,0 | 56 % | 0,38 | -13 % | 28 | Rejeté |
| Stochastique 14-3-3 (zones 20/80) | achat + vente | -0,14 | 0,2 % | 0,01 | 0,0 | 37 % | -0,01 | -52 % | 48 | Rejeté |
| Stochastique 14-3-3 (zones 20/80) | achat seulement | 0,26 | 7,8 % | 0,77 | 2,0 | 28 % | 0,75 | -19 % | 24 | Rejeté |
| SuperTrend 10-3 | achat + vente | 0,08 | -0,1 % | -0,01 | -0,0 | 44 % | -0,02 | -34 % | 39 | Rejeté |
| SuperTrend 10-3 | achat seulement | 0,35 | 8,8 % | 0,64 | 1,6 | 47 % | 0,63 | -16 % | 19 | Rejeté |
| ADX 14 > 25 + sens MA20/MA50 | achat + vente | -0,11 | -1,0 % | -0,07 | -0,2 | 75 % | -0,09 | -28 % | 36 | Rejeté |
| ADX 14 > 25 + sens MA20/MA50 | achat seulement | 0,12 | 4,9 % | 0,39 | 1,0 | 45 % | 0,37 | -15 % | 21 | Rejeté |
| Croix dorée MA50 / MA200 | achat + vente | 0,11 | 6,4 % | 0,34 | 0,8 | 53 % | 0,33 | -44 % | 11 | Rejeté |
| Croix dorée MA50 / MA200 | achat seulement | 0,33 | 12,0 % | 0,72 | 1,7 | 54 % | 0,71 | -27 % | 5 | Rejeté |
| Ichimoku (cours / nuage) | achat + vente | -0,17 | 11,6 % | 0,64 | 1,6 | 10 % | 0,61 | -23 % | 73 | Rejeté |
| Ichimoku (cours / nuage) | achat seulement | 0,15 | 15,0 % | 0,99 | 2,5 | 6 % | 0,96 | -17 % | 38 | Rejeté |
| Momentum ROC 12 jours | achat + vente | -0,12 | -0,0 % | -0,00 | -0,0 | 49 % | -0,09 | -49 % | 180 | Rejeté |
| Momentum ROC 12 jours | achat seulement | 0,20 | 8,8 % | 0,61 | 1,5 | 50 % | 0,55 | -15 % | 89 | Rejeté |
| Donchian 20 / sortie 10 (tortues) | achat + vente | -0,11 | 4,0 % | 0,24 | 0,6 | 47 % | 0,22 | -18 % | 39 | Rejeté |
| Donchian 20 / sortie 10 (tortues) | achat seulement | 0,27 | 6,9 % | 0,50 | 1,3 | 61 % | 0,48 | -15 % | 24 | Rejeté |
| CCI 20 (±100) | achat + vente | -0,33 | 2,1 % | 0,12 | 0,3 | 48 % | 0,09 | -31 % | 69 | Rejeté |
| CCI 20 (±100) | achat seulement | 0,03 | 4,4 % | 0,33 | 0,8 | 75 % | 0,30 | -15 % | 38 | Rejeté |
| Williams %R 14, retour à la moyenne | achat + vente | -0,09 | 3,4 % | 0,21 | 0,5 | 22 % | 0,15 | -27 % | 99 | Rejeté |
| Williams %R 14, retour à la moyenne | achat seulement | 0,10 | 9,1 % | 0,86 | 2,0 | 16 % | 0,81 | -15 % | 53 | Rejeté |
| Canal de Keltner 20-10-2 (cassure) | achat + vente | -0,33 | -0,6 % | -0,05 | -0,1 | 78 % | -0,07 | -22 % | 29 | Rejeté |
| Canal de Keltner 20-10-2 (cassure) | achat seulement | 0,09 | 3,2 % | 0,29 | 0,7 | 56 % | 0,27 | -13 % | 19 | Rejeté |
| SAR parabolique 0,02-0,2 | achat + vente | 0,12 | -1,5 % | -0,08 | -0,2 | 60 % | -0,14 | -43 % | 115 | Rejeté |
| SAR parabolique 0,02-0,2 | achat seulement | 0,36 | 8,1 % | 0,58 | 1,4 | 53 % | 0,54 | -30 % | 57 | Rejeté |
| Momentum 12 mois (252 jours) | achat + vente | -0,16 | 8,9 % | 0,47 | 1,1 | 50 % | 0,45 | -43 % | 38 | Rejeté |
| Momentum 12 mois (252 jours) | achat seulement | 0,14 | 13,3 % | 0,76 | 1,8 | 48 % | 0,75 | -27 % | 19 | Rejeté |

## Conclusion

**Aucune stratégie n'obtient « avantage probable ».**

À surveiller (au plus 5 % de hasard, mais 34 essais : au moins 1 à 2 sont attendus par hasard) : RSI 14, retour à la moyenne (30/70) (achat seulement).

## Limites

- Signal et exécution à la même clôture : légèrement optimiste. Données journalières seulement.
- Frais 0,05 % l'aller-retour, sans financement de nuit ni écart de prix réel.
- Le mode « achat seulement » profite de la hausse de l'or sur la période : seul le test de hasard le corrige.
- 34 essais : avec un seuil à 5 %, environ 2 paraissent bons par chance.
- Paramètres standard non optimisés : une version optimisée serait plus belle sur le passé et pire dans le futur.
