# Stratégie intraday « Monte Carlo » v1 : règles figées avant le test (9 nov 2026)

**Interprétation retenue de « l'indicateur de Monte Carlo »** (il n'existe pas de version unique ; si tu pensais à un indicateur précis, donne-moi son nom ou la vidéo) : à chaque décision, on simule **1 000 trajectoires de prix** en re-tirant au hasard les variations des 15 dernières heures de bourse de l'or (méthode du bootstrap), et on mesure la **probabilité que l'objectif soit touché avant le stop**. Ce n'est pas une prévision magique : la simulation ne sait que ce que la dernière journée a montré (tendance et agitation récentes). On la combine avec trois autres signaux. Le Monte Carlo sert aussi à juger les résultats (rééchantillonnage des trades, voir plus bas).

## Données
Or au comptant XAUUSD, barres 5 min (Dukascopy), 2012 à la dernière séance ; jours et heures valides comme pour les autres tests (barres actives, volume non nul). Signaux calculés sur des barres de 15 minutes et de 1 heure agrégées ; stop et objectif contrôlés sur les barres 5 min.

## Règles (variante principale V1)
1. **Décisions** : chaque heure pile de 08:00 à 16:00 UTC, du lundi au vendredi. Une seule position à la fois.
2. **ATR de référence A** : ATR(14) des barres de 1 heure terminées (en dollars).
3. **Signal Monte Carlo** : fenêtre des 96 dernières variations de 15 min (barres actives, sans saut de plus de 30 min), 1 000 trajectoires de 32 pas (8 heures), tirage fixé (graine 2026). Pour l'achat : probabilité P↑ de toucher **+1,5 A avant −1,0 A** ; pour la vente : P↓ de toucher **−1,5 A avant +1,0 A**. Achat si P↑ ≥ 0,50 **et** P↑ − P↓ ≥ 0,15 ; vente si P↓ ≥ 0,50 **et** P↓ − P↑ ≥ 0,15. (Sans tendance, la probabilité « neutre » est d'environ 0,40.)
4. **Tendance** : moyenne mobile exponentielle 20 > 100 sur les clôtures 1 h pour acheter ; < pour vendre.
5. **Pas d'excès** : RSI(14) 1 h entre 40 et 70 pour acheter ; entre 30 et 60 pour vendre.
6. **Entrée** à l'ouverture de la barre 5 min de l'heure de décision. **Stop = 1,0 A, objectif = 1,5 A**, sortie au bout de 8 heures ou à 20:55 UTC au plus tard. Si stop et objectif sont dans la même barre : stop. Stop gappé : prix d'ouverture.
7. Risque de 0,5 % du capital par trade (1 R = A). Frais : base 0,02 % l'aller-retour, stress 0,05 %.

## Variantes (3) et témoin
- **V1** : Monte Carlo + tendance + RSI (règles ci-dessus).
- **V2** : Monte Carlo seul (sans tendance ni RSI).
- **V3** : tendance + RSI sans Monte Carlo (sens de la tendance) : **mesure si le Monte Carlo apporte quelque chose**.
- **Témoin hasard** : sens tiré au sort aux mêmes heures et mêmes sorties que V3.

## Critères pour dire « solide » (tous exigés, pour V1)
1. Gain net moyen par trade > 0 avec t (Newey-West) ≥ 2 en **développement (2012-2019)** et en **validation (2020-2026)**.
2. Au moins 60 % d'années positives (années avec au moins 20 trades) et au moins 100 trades.
3. Deflated Sharpe ≥ 0,95 avec 3 essais (aussi donné avec 350 essais).
4. Rendement annuel après impôts (31,4 % des plus-values nettes annuelles, moins-values reportées) > 0.
5. **V1 fait mieux que V3** (gain net moyen par trade plus élevé) en développement **et** en validation.

## Monte Carlo des résultats (information)
10 000 rééchantillonnages des trades de V1 : probabilité que le total soit positif, fourchette 5 %-95 % du total en R, et perte maximale médiane en R.

Si V1 échoue, on le publie tel quel, sans la retoucher. Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
