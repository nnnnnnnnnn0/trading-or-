# Analyse des trades gagnants : y a-t-il des conditions qui rendent la stratégie gagnante ?

Méthode fixée avant de regarder (voir `scripts/backtests/analyse_gagnants.py`) : conditions cherchées sur les 60 % premiers trades, jugées une fois sur les 40 % derniers, comparées au hasard par permutation. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

## Compression Or (variante A)

807 trades du 2013-01-15 au 2026-10-27 ; développement 484, contrôle 323. Rendement net moyen sans condition : développement -0,023, contrôle -0,044 (unité : R).

**Gagnants contre perdants (développement seulement), écart standardisé des mesures :**

- volatilité (rang sur 1 an) : plus bas chez les gagnants (écart standardisé -0,12)
- variation sur 5 jours : plus élevé chez les gagnants (écart standardisé 0,09)
- variation de la veille : plus bas chez les gagnants (écart standardisé -0,05)
- écart à la moyenne 200 j : plus bas chez les gagnants (écart standardisé -0,04)

**Cinq meilleures conditions simples sur le développement, et ce qu'elles donnent ensuite sur le contrôle :**

| Condition | Développement (trades / moy. / t) | Contrôle (trades / moy. / t) |
| --- | --- | --- |
| type de compression = 1 | 76 / 0,164 / 1,3 | 56 / -0,093 / -0,7 |
| variation sur 5 jours > -0.00343 | 290 / 0,036 / 0,6 | 203 / 0,024 / 0,3 |
| variation de la veille ≤ -0.00071 | 194 / 0,045 / 0,6 | 106 / -0,119 / -1,3 |
| jour de la semaine (0 = lundi) = 0 | 99 / 0,060 / 0,6 | 65 / 0,076 / 0,6 |
| jour de la semaine (0 = lundi) = 2 | 88 / 0,057 / 0,5 | 60 / -0,185 / -1,5 |

**Règle choisie sur le développement (2 conditions) :** type de compression = 1 **et** écart à la moyenne 200 j > -0.0125

- Développement : 52 trades, moyenne 0,263, t = 1,7.
- **Contrôle : 46 trades, moyenne -0,109, t = -0,7.** Fréquence : 0,14 trades par semaine.
- Test de permutation : avec la même méthode sur des résultats mélangés, le t sur le contrôle dépasse celui-ci dans 65 % de cas (médiane du hasard : t = -0,3). Environ 71 conditions candidates, 2520 combinaisons possibles.

**Verdict : la règle ne survit pas : ce que l'on voit chez les gagnants du développement ne se retrouve pas sur le contrôle plus que le hasard ne le ferait.**

## Nuit Or (variante A)

4327 trades du 2013-01-10 au 2026-11-05 ; développement 2596, contrôle 1731. Rendement net moyen sans condition : développement -0,037, contrôle -0,003 (unité : % par trade).

**Gagnants contre perdants (développement seulement), écart standardisé des mesures :**

- variation de la veille : plus élevé chez les gagnants (écart standardisé 0,04)
- variation sur 5 jours : plus bas chez les gagnants (écart standardisé -0,03)
- volatilité (rang sur 1 an) : plus élevé chez les gagnants (écart standardisé 0,03)
- amplitude de la veille / ATR : plus élevé chez les gagnants (écart standardisé 0,03)

**Cinq meilleures conditions simples sur le développement, et ce qu'elles donnent ensuite sur le contrôle :**

| Condition | Développement (trades / moy. / t) | Contrôle (trades / moy. / t) |
| --- | --- | --- |
| variation de la veille > 0.00654 | 519 / 0,016 / 0,6 | 447 / -0,057 / -1,4 |
| écart à la moyenne 200 j > 0.0737 | 518 / 0,004 / 0,1 | 753 / 0,020 / 0,6 |
| jour de la semaine (0 = lundi) = 1 | 432 / 0,002 / 0,1 | 289 / 0,058 / 1,2 |
| jour de la semaine (0 = lundi) = 3 | 433 / -0,008 / -0,3 | 289 / 0,026 / 0,5 |
| tendance 3 mois > 0.0614 | 519 / -0,011 / -0,4 | 657 / -0,003 / -0,1 |

**Règle choisie sur le développement (2 conditions) :** variation de la veille > 0.00654 **et** volatilité (rang sur 1 an) ≤ 0.341

- Développement : 173 trades, moyenne 0,066, t = 2,1.
- **Contrôle : 128 trades, moyenne -0,019, t = -0,4.** Fréquence : 0,42 trades par semaine.
- Test de permutation : avec la même méthode sur des résultats mélangés, le t sur le contrôle dépasse celui-ci dans 66 % de cas (médiane du hasard : t = 0,1). Environ 62 conditions candidates, 1922 combinaisons possibles.

**Verdict : la règle ne survit pas : ce que l'on voit chez les gagnants du développement ne se retrouve pas sur le contrôle plus que le hasard ne le ferait.**

## Limites

- Le contrôle n'est pas vierge : les résultats globaux de ces stratégies avaient déjà été vus avant. Le vrai test sans biais est le paper trading à partir de maintenant.
- Seules les stratégies avec assez de trades sont analysées. Le Régime or (une quinzaine de changements par an) n'en a pas assez ; les anciennes études intraday sont supprimées du dépôt.
- Les conditions étudiées sont celles listées ici ; d'autres (heure d'été, annonces, saisons) n'ont pas été cherchées pour limiter le nombre d'essais.
