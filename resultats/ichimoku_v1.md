# Ichimoku combiné à d'autres signaux (v1)

Données : 4756 jours (2006-10-20 à 2026-11-05), futures GC=F, dollar et taux. 4 blocs de durée égale : 2008-2013 | 2013-2017 | 2017-2022 | 2022-2026.

**34 essais comptés ici, plus 34 au backtest précédent (soit 68 au total).** Paramètres standard, aucun réglage.

**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

**Précaution** : la période 2021-2026 avait déjà été vue pour l'Ichimoku seul, donc plus de contrôle vierge. Un résultat n'est retenu que s'il est positif dans au moins 3 blocs sur 4, bat le hasard (au plus 1 %), a t ≥ 2,5 et reste positif avec frais doublés. Même alors, il n'est qu'un **candidat à confirmer en paper trading**.

Référence : garder l'or sur toute la période = Sharpe 0,56, rendement annuel 10,4 %.

| Stratégie | Mode | Sharpe | Rendement annuel | t | Hasard | Rendement annuel par bloc | Sharpe frais ×2 | Entrées | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tenkan > Kijun (confirmation TK) | achat + vente | -0,08 | -1,2 % | -0,3 | 69 % | -10 / -5 / 1 / 9 | -0,12 | 214 | Rejeté |
| Tenkan > Kijun (confirmation TK) | achat seulement | 0,32 | 3,9 % | 1,4 | 47 % | 2 / -5 / 5 / 13 | 0,30 | 105 | Rejeté |
| Chikou libre (cours > cours d'il y a 26 j) | achat + vente | 0,08 | 1,4 % | 0,3 | 37 % | -8 / -1 / -1 / 16 | 0,04 | 273 | Rejeté |
| Chikou libre (cours > cours d'il y a 26 j) | achat seulement | 0,43 | 5,4 % | 1,8 | 25 % | 5 / -5 / 4 / 17 | 0,40 | 143 | Rejeté |
| Nuage futur de la bonne couleur | achat + vente | 0,10 | 1,6 % | 0,4 | 38 % | -10 / 0 / 2 / 14 | 0,06 | 197 | Rejeté |
| Nuage futur de la bonne couleur | achat seulement | 0,45 | 5,8 % | 1,9 | 25 % | 6 / -4 / 5 / 16 | 0,43 | 103 | Rejeté |
| ADX 14 > 25 (tendance forte) | achat + vente | -0,22 | -2,9 % | -0,9 | 93 % | -9 / -1 / 1 / -2 | -0,24 | 101 | Rejeté |
| ADX 14 > 25 (tendance forte) | achat seulement | 0,14 | 1,4 % | 0,6 | 67 % | 0 / -3 / 3 / 5 | 0,12 | 62 | Rejeté |
| RSI 14 du bon côté de 50 | achat + vente | 0,10 | 1,6 % | 0,4 | 31 % | -11 / 3 / -2 / 16 | 0,04 | 337 | Rejeté |
| RSI 14 du bon côté de 50 | achat seulement | 0,50 | 6,0 % | 2,2 | 12 % | 5 / -1 / 4 / 17 | 0,46 | 174 | Rejeté |
| RSI 14 pas en excès (< 70 / > 30) | achat + vente | 0,10 | 1,6 % | 0,4 | 31 % | -8 / -3 / -2 / 19 | 0,03 | 382 | Rejeté |
| RSI 14 pas en excès (< 70 / > 30) | achat seulement | 0,46 | 5,4 % | 1,9 | 20 % | 3 / -4 / 4 / 19 | 0,41 | 222 | Rejeté |
| MACD du bon côté de son signal | achat + vente | 0,04 | 0,5 % | 0,2 | 43 % | -3 / 2 / -3 / 6 | -0,02 | 269 | Rejeté |
| MACD du bon côté de son signal | achat seulement | 0,32 | 3,2 % | 1,4 | 33 % | 5 / -1 / 1 / 8 | 0,28 | 142 | Rejeté |
| Dollar sous / sur sa MA50 (veille) | achat + vente | -0,06 | -0,8 % | -0,2 | 54 % | -6 / -1 / -8 / 12 | -0,10 | 250 | Rejeté |
| Dollar sous / sur sa MA50 (veille) | achat seulement | 0,27 | 2,8 % | 1,2 | 49 % | 7 / -5 / -2 / 11 | 0,23 | 132 | Rejeté |
| Taux 10 ans sous / sur leur MA50 (veille) | achat + vente | 0,28 | 3,6 % | 1,2 | 8 % | -0 / 2 / 2 / 11 | 0,22 | 254 | Rejeté |
| Taux 10 ans sous / sur leur MA50 (veille) | achat seulement | 0,48 | 4,7 % | 2,0 | 12 % | 6 / -2 / 4 / 11 | 0,44 | 144 | Rejeté |
| Volatilité hors des 20 % les plus hauts | achat + vente | 0,35 | 5,0 % | 1,5 | 6 % | 1 / 3 / 6 / 10 | 0,30 | 258 | Rejeté |
| Volatilité hors des 20 % les plus hauts | achat seulement | 0,55 | 6,0 % | 2,2 | 11 % | 9 / -3 / 8 / 10 | 0,52 | 131 | Rejeté |
| Triple confirmation (TK + Chikou + nuage futur) | achat + vente | -0,00 | -0,0 % | -0,0 | 55 % | -9 / -4 / 2 / 11 | -0,04 | 203 | Rejeté |
| Triple confirmation (TK + Chikou + nuage futur) | achat seulement | 0,40 | 4,6 % | 1,7 | 27 % | 3 / -4 / 5 / 14 | 0,38 | 103 | Rejeté |
| Triple confirmation + ADX > 25 | achat + vente | -0,23 | -2,9 % | -1,0 | 93 % | -8 / -3 / 2 / -2 | -0,25 | 101 | Rejeté |
| Triple confirmation + ADX > 25 | achat seulement | 0,11 | 1,0 % | 0,5 | 68 % | -0 / -2 / 3 / 3 | 0,09 | 58 | Rejeté |
| Triple confirmation + dollar | achat + vente | -0,03 | -0,3 % | -0,1 | 54 % | -1 / -3 / -5 / 7 | -0,07 | 196 | Rejeté |
| Triple confirmation + dollar | achat seulement | 0,40 | 3,7 % | 1,8 | 20 % | 9 / -4 / -0 / 10 | 0,37 | 105 | Rejeté |
| Sortie sur la Kijun (au lieu du nuage) | achat + vente | -0,03 | -0,6 % | -0,1 | 50 % | -10 / 2 / -3 / 8 | -0,13 | 576 | Rejeté |
| Sortie sur la Kijun (au lieu du nuage) | achat seulement | 0,31 | 4,0 % | 1,3 | 42 % | 5 / -2 / 1 / 11 | 0,24 | 313 | Rejeté |
| Entrée sur repli vers la Kijun | achat + vente | 0,22 | 3,6 % | 1,0 | 25 % | 1 / -4 / -1 / 18 | 0,21 | 79 | Rejeté |
| Entrée sur repli vers la Kijun | achat seulement | 0,54 | 6,7 % | 2,3 | 13 % | 9 / -5 / 5 / 17 | 0,53 | 37 | Rejeté |
| Croisement TK au-dessus / sous le nuage | achat + vente | 0,26 | 3,4 % | 1,1 | 13 % | -1 / -1 / 3 / 12 | 0,24 | 82 | Rejeté |
| Croisement TK au-dessus / sous le nuage | achat seulement | 0,44 | 4,7 % | 1,9 | 12 % | 4 / -3 / 4 / 14 | 0,43 | 44 | Rejeté |
| RÉFÉRENCE : Ichimoku seul (cours / nuage) | achat + vente | 0,08 | 1,4 % | 0,3 | 38 % | -9 / -1 / -1 / 16 | 0,04 | 247 | Référence |
| RÉFÉRENCE : Ichimoku seul (cours / nuage) | achat seulement | 0,44 | 5,8 % | 1,9 | 29 % | 6 / -5 / 4 / 18 | 0,41 | 127 | Référence |

## Conclusion

**Aucune combinaison ne passe le filtre strict.**

## Limites

- Signal et exécution à la même clôture ; frais 0,05 % l'aller-retour, sans financement de nuit.
- Dollar et taux de la veille pour éviter le regard dans le futur (clôtures décalées).
- 68 essais au total : plusieurs résultats flatteurs sont attendus par pur hasard. Seule la confirmation en conditions réelles (paper trading) compte.
- Le mode « achat seulement » profite de la hausse de l'or ; le test de hasard le corrige en partie.
