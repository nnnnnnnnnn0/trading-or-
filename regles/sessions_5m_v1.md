# 24 stratégies « sessions » à 2-3 ordres par semaine ou plus, testées sur 14 ans : règles figées (8 nov 2026)

Demande : tester plus de 20 stratégies avec au moins 2 à 3 ordres par semaine sur les 14 ans, et savoir si l'une est profitable (après frais et après impôts). Pour que « il y en a une qui gagne » ait un sens, les 24 règles sont **fixées avant le test** et lancées **une seule fois**, avec une période de **développement (2012-2019)** et une période de **validation (2020-2026)** jugées séparément. Ce ne sont pas des indicateurs : ce sont des règles sur le comportement de l'or par session de la journée (autre famille que les 28 stratégies du paper trading).

## Principe commun
- Or au comptant XAUUSD, barres 5 min (Dukascopy), 2012-01-01 à la dernière séance ; lundi à vendredi. Heures UTC fixes (l'heure d'été décale Londres et New York d'une heure, ignoré).
- Repères de prix = ouverture de la barre 5 min à l'heure indiquée. Asie 22:00 (veille) → 07:00 ; Londres 07:00 → 13:30 ; New York 13:30 → 20:55 ; points intermédiaires 08:00, 14:30, 16:00, 18:30. Un rendement de session = prix de fin / prix de début − 1.
- Un trade par jour par stratégie, entrée à l'ouverture de la barre indiquée, sortie à l'ouverture de la barre de sortie, **stop de sécurité à 1 × ATR journalier(14)** (ATR des séances 22:00-22:00 terminées). Stop gappé exécuté au pire prix.
- Frais : base **0,02 %** l'aller-retour, stress **0,05 %**. Pas de financement (trades du jour, sans levier, exposition 1 fois le capital).
- Impôt (information) : 31,4 % des plus-values nettes annuelles, moins-values reportées (taux 2026 du prélèvement forfaitaire en France ; hypothèse, pas un conseil fiscal). Rendement 1 fois le capital, réinvesti.

## Les 24 stratégies (entrée → sortie ; sens)
1. **Asie suivie** : 07:00 → 13:30 ; dans le sens du rendement Asie (22:00-07:00). 2. **Asie inversée** : sens contraire.
3. **Londres suivie** : 13:30 → 18:30 ; sens du rendement Londres (07:00-13:30). 4. **Londres inversée**.
5. **New York matin suivi** : 16:00 → 20:55 ; sens du rendement 13:30-16:00. 6. **New York matin inversé**.
7. **Veille suivie** : 07:00 → 18:30 ; sens du rendement 24 h (07:00 de la veille à 07:00). 8. **Veille inversée**.
9. **Tendance 5 jours suivie** : 07:00 → 18:30 ; sens du rendement sur 5 jours. 10. **Tendance 5 jours inversée**.
11. **Tendance 20 jours suivie** : 07:00 → 18:30 ; sens du rendement sur 20 jours. 12. **Tendance 20 jours inversée**.
13. **1re heure de Londres suivie** : 08:00 → 13:30 ; sens du rendement 07:00-08:00. 14. **inversée**.
15. **1re heure de New York suivie** : 14:30 → 18:30 ; sens du rendement 13:30-14:30. 16. **inversée**.
17. **Asie + Londres alignées** : 13:30 → 18:30 ; seulement si Asie et Londres ont le même signe, dans ce sens.
18. **Londres renverse l'Asie** : 13:30 → 18:30 ; seulement si Asie et Londres ont des signes opposés, dans le sens de Londres.
19. **Clôture de la veille en haut / en bas du rang (suivie)** : 07:00 → 18:30 ; position de la clôture de la séance précédente dans son amplitude : ≥ 0,8 achat, ≤ 0,2 vente, sinon rien. 20. **inversée**.
21. **Fin de New York suivie** : 18:30 → 20:55 ; sens du rendement 13:30-18:30. 22. **inversée**.
23. **Londres suivie si tendance 20 jours d'accord** : comme 3, seulement si le sens de Londres = sens de la tendance 20 jours.
24. **Asie suivie si tendance 20 jours d'accord** : comme 1, seulement si le sens de l'Asie = sens de la tendance 20 jours.
Témoin : **Londres → New York au hasard** (sens tiré au sort, mêmes sorties que 3).

## Critères pour dire « profitable » (tous exigés, pour une stratégie)
1. Gain net moyen par trade > 0 avec t (Newey-West) ≥ 2 en **développement** (2012-2019) **et** en **validation** (2020-2026).
2. Au moins 60 % d'années positives, au moins 2 ordres par semaine en moyenne.
3. Deflated Sharpe ≥ 0,95 sur toute la période avec **24 essais** (aussi donné avec **330 essais**, total approximatif du projet).
4. Rendement annuel après impôts > 0.

Si aucune ne passe, on le publie tel quel. Une stratégie qui passe serait seulement candidate au paper trading en direct, pas une preuve. Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
