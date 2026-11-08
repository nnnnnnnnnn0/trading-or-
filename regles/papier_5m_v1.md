# Paper trading quotidien sur graphique 5 min : 28 stratégies + 1 témoin (règles figées le 8 nov 2026)

Chaque matin, le moteur rejoue la veille sur les barres 5 min de l'or au comptant (Dukascopy) et inscrit dans le journal les ordres que chaque stratégie **aurait pris**. Les signaux n'utilisent que le passé (vérifié par un test automatique). **Le paper trading est différé** : les ordres sont connus le lendemain matin, ce n'est pas un conseil de trade en direct.

Départ : lundi 9 novembre 2026 00:00 UTC. Aucune règle n'est modifiée après coup ; une stratégie peut être retirée du suivi, jamais retouchée.

## Règles communes
- Signal à la **clôture** d'une barre 5 min ; entrée à l'**ouverture** de la barre suivante, du lundi au vendredi, entre 07:00 et 20:00 UTC (heure d'été Paris : 09:00-22:00 ; hiver : 08:00-21:00). Barres sans volume ignorées.
- Un signal se déclenche quand sa condition devient vraie (pas à chaque barre). **Une seule position par stratégie** à la fois.
- ATR = moyenne des vraies amplitudes sur 14 barres au moment du signal. **Stop = 2 × ATR** (c'est 1 R). Famille *tendance* : objectif 4 × ATR (2 R), durée max 36 barres (3 h). Famille *retour à la moyenne* : objectif 1,5 × ATR (0,75 R), durée max 24 barres (2 h).
- Sortie forcée à 21:00 UTC (pas de nuit, pas de week-end). Si stop et objectif sont dans la même barre : stop. Stop gappé : exécuté à l'ouverture.
- Compte fictif de 10 000 $, risque de 50 $ (0,5 %) par trade : taille en onces = 50 $ / (2 × ATR).
- Frais : **base 0,02 % l'aller-retour** (écart de prix + glissement d'un courtier typique) ; **stress 0,05 %**. Les deux sont inscrits.

## Les 17 stratégies « tendance / cassure »
1. **EMA 9/21** : croisement de moyennes mobiles exponentielles.
2. **Repli sur EMA 50** : prix franchit à nouveau l'EMA 50 dans le sens de EMA 50 contre EMA 200.
3. **MACD (12,26,9)** : l'histogramme croise zéro.
4. **Supertrend (ATR 10, ×3)** : changement de sens.
5. **Donchian 48** : clôture au-delà du plus haut / plus bas des 48 barres précédentes.
6. **Ichimoku (9,26,52)** : clôture qui sort du nuage (au-dessus de l'achat, en dessous de la vente).
7. **ADX / DI (14)** : croisement +DI/−DI avec ADX > 25.
8. **Parabolic SAR (0,02 ; 0,2)** : changement de sens.
9. **Heikin-Ashi** : deuxième bougie consécutive de même couleur après une bougie de couleur opposée.
10. **Aroon 25** : croisement Aroon haut / Aroon bas.
11. **Cassure d'ouverture de Londres** : plus haut / plus bas de 07:00 à 07:30 UTC, cassure jusqu'à 11:00.
12. **Cassure d'ouverture de New York** : plus haut / plus bas de 13:30 à 14:00 UTC, cassure jusqu'à 17:00.
13. **Cassure de la veille** : clôture au-delà du plus haut / plus bas de la journée UTC précédente.
14. **Keltner (EMA 20 ± 2 × ATR 10)** : clôture hors du canal.
15. **Compression de Bollinger** : bandes (20, 2) proches de leur plus bas des 100 dernières barres (≤ 1,25 ×), puis clôture hors des bandes dans les 3 barres.
16. **Momentum ROC 12** : croise +0,10 % (achat) ou −0,10 % (vente).
17. **Cassure avec volume** : cassure du plus haut / bas de 20 barres avec un volume > 1,5 × sa moyenne sur 20 barres.

## Les 11 stratégies « retour à la moyenne »
18. **RSI 14** : croise 30 vers le haut (achat) / 70 vers le bas (vente).
19. **RSI 2 (Connors)** : RSI 2 < 10 au-dessus de l'EMA 200 (achat) ; > 90 en dessous (vente).
20. **Retour dans les bandes de Bollinger (20, 2)** : clôture qui revient à l'intérieur après être sortie.
21. **Stochastique (14,3,3)** : croisement %K / %D sous 20 (achat) ou au-dessus de 80 (vente).
22. **CCI 20** : croise −100 vers le haut (achat) / +100 vers le bas (vente).
23. **Williams %R 14** : croise −80 vers le haut (achat) / −20 vers le bas (vente).
24. **VWAP** : écart au VWAP du jour UTC supérieur à 2 écarts-types (48 barres) : achat sous, vente au-dessus.
25. **Z-score 50** : z < −2 (achat) / z > +2 (vente).
26. **MFI 14 (avec volume)** : croise 20 vers le haut (achat) / 80 vers le bas (vente).
27. **Avalement (chandelier)** : avalement haussier sur un plus bas de 20 barres (achat) ; baissier sur un plus haut de 20 barres (vente).
28. **Pivots de la veille** : rejet sur S1 (achat) ou R1 (vente), pivot classique de la veille UTC, entre 07:00 et 17:00 UTC.

## Témoin
**0. Hasard** : sens tiré au sort, environ 1 entrée sur 60 barres (tirage fixé par l'horodatage de la barre), mêmes sorties que la famille tendance. Il dit ce que le pur hasard donne avec ces frais et ces sorties.

## Comment lire les résultats
- Le journal est dans `journal/` : `ordres.csv` (tous les ordres, détail complet), `jours/AAAA-MM-JJ.md` (ordres de la journée avec heures de Paris, gagné / perdu), `classement.md` (cumul par stratégie).
- **Avec 28 stratégies en parallèle, quelques-unes paraîtront excellentes par chance.** Aucune conclusion avant au moins 100 trades par stratégie, un t ≥ 2, et un Deflated Sharpe ≥ 0,95 calculé avec 28 essais (le classement l'affiche). Compare toujours au témoin.
- Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
