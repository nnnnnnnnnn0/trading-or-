# Recherche de récurrences sur l'or (v1)

Données : 5041 jours de bourse (2006-10-20 à 2026-11-04), futures GC=F et facteurs. Exploration : 2007-10-19 à 2021-02-18 (70 %). Contrôle fermé jusqu'à la fin : 2021-02-19 à 2026-11-04.

**112 essais comptés** (56 hypothèses x 2 horizons). Avec autant d'essais, le seuil de Bonferroni est |t| ≈ 3.5 ; au seuil usuel de 2, environ 6 essais « marchent » par pur hasard.

**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

## 1. Meilleurs candidats en exploration (|t| ≥ 2,5 : 4 sur 112)

| Condition | Horizon | Jours | Rendement moyen | Écart vs. tous les jours | t |
| --- | --- | --- | --- | --- | --- |
| taux 10 ans, forte hausse | 3 j | 478 | -0.20 % | -0.35 % | -3.3 |
| dollar > +1 écart-type | 1 j | 523 | -0.11 % | -0.17 % | -2.9 |
| taux 10 ans, forte baisse | 3 j | 499 | 0.37 % | +0.32 % | 2.7 |
| taux 10 ans, forte baisse | 1 j | 499 | 0.17 % | +0.17 % | 2.6 |
| premier vendredi du mois | 1 j | 149 | 0.21 % | +0.19 % | 1.9 |
| premier vendredi du mois | 3 j | 149 | 0.40 % | +0.32 % | 1.9 |
| taux 10 ans, forte hausse | 1 j | 478 | -0.06 % | -0.11 % | -1.8 |
| plus haut 20j | 1 j | 496 | 0.10 % | +0.08 % | 1.5 |
| mois = 1 | 1 j | 282 | 0.12 % | +0.10 % | 1.5 |
| plus haut 55j | 1 j | 335 | 0.11 % | +0.09 % | 1.5 |
| clôture proche du plus bas du jour | 1 j | 744 | 0.09 % | +0.07 % | 1.4 |
| VIX z > 1,5 | 1 j | 393 | 0.13 % | +0.11 % | 1.4 |
| mois = 1 | 3 j | 282 | 0.30 % | +0.22 % | 1.4 |
| jour = lundi | 3 j | 630 | 0.02 % | -0.10 % | -1.3 |
| mois = 3 | 3 j | 282 | -0.14 % | -0.26 % | -1.3 |

## 2. Contrôle sur la période fermée (30 %)

| Condition | Horizon | Sens | Écart exploration | Écart contrôle | t contrôle | Années cohérentes | Net de frais | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| taux 10 ans, forte hausse | 3 j | vente | -0.35 % | +0.15 % | 0.9 | 60 % | -0.20 % | Rejeté |
| dollar > +1 écart-type | 1 j | vente | -0.17 % | -0.09 % | -1.0 | 65 % | +0.04 % | Rejeté |
| taux 10 ans, forte baisse | 3 j | achat | +0.32 % | +0.05 % | 0.4 | 85 % | +0.00 % | Rejeté |
| taux 10 ans, forte baisse | 1 j | achat | +0.17 % | +0.09 % | 1.1 | 80 % | +0.04 % | Rejeté |

## Conclusion

**Aucune récurrence ne passe le contrôle.** Les meilleurs candidats d'exploration ne se confirment pas sur la période fermée : c'est l'attendu d'un marché liquide, et cela évite une fausse stratégie.

## Limites

- Données journalières seulement : les récurrences intraday (heure de la journée, séances Asie / Europe / États-Unis) seront testées avec l'historique 5 min, quand il sera complet.
- Rendements bruts clôture à clôture, frais comptés à 0,05 % par aller-retour ; pas de financement de nuit.
- Facteurs décalés par leurs heures de clôture : léger flou possible.
- Le calendrier des annonces n'existe que depuis novembre 2026 : l'effet des annonces n'est pas testable (sauf « premier vendredi du mois », proxy de l'emploi américain).
