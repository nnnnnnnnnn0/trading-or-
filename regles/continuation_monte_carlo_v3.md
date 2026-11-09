# Stratégie « Continuation Monte Carlo » v3 : règles figées avant le test (9 nov 2026)

## D'où vient l'idée, et ce que ce test vaut
Le test v2 (`resultats/montecarlo_intraday_v2.md`) a montré, à titre d'information, que lorsque la tendance journalière et la tendance horaire vont dans le même sens, les 4 heures suivantes rapportent en moyenne +1,1 à +1,5 point de base si le prix est au milieu ou en haut du cône Monte Carlo, contre +0,1 dans la zone de repli (là où la v2 achetait) et −2,0 en cas de repli extrême. D'où l'hypothèse de cette v3 : **entrer dans le sens de la tendance, sans attendre de repli**.

**Cette hypothèse a été trouvée en regardant les mêmes données que celles du test.** Ce backtest n'est donc **pas indépendant** : un bon résultat ne vaudrait que comme piste à confirmer en avant (paper trading), jamais comme preuve. Pour compenser, les critères sont stricts et les 9 stratégies testées sont comptées comme essais (Deflated Sharpe).

Autre point de départ : 1,4 point de base par 4 heures est inférieur aux frais d'un aller-retour (2 points de base). Garder la position plus longtemps dilue les frais fixes, mais ajoute des frais de financement la nuit. C'est ce que le test des trois durées mesure.

## Données et définitions
Identiques à la v2 (`regles/montecarlo_intraday_v2.md`) : or XAUUSD, barres 5 min Dukascopy 2012-2026, jours valides, A = ATR(14) horaire (Wilder), cône Monte Carlo ancré à 07:00 UTC (480 variations de 15 min, 2 000 trajectoires, graine 2026), tendance journalière D (clôture de séance > moyenne simple 50 séances), tendance horaire H (EMA 20 > EMA 100), filtre de volatilité (A ≥ médiane sur 1 200 barres 1 h), filtre de volume relatif (≥ 1,0).
Nouveauté : la position du prix dans le cône est lue dans le **sens de la tendance** : q' = q si la tendance est haussière, 1 − q si elle est baissière ; z' = z (haussière) ou −z (baissière). q' haut = le prix est du bon côté du cône.

## Règles
1. **Une seule décision par jour : 08:00 UTC**, du lundi au vendredi, jours valides. La tendance **t** vaut +1 si D et H sont haussières, −1 si D et H sont baissières, 0 sinon.
2. **Entrée à l'ouverture de la barre 5 min de 08:00**, dans le sens de la tendance, si la position précédente est terminée (une seule position à la fois, pas de renfort).
3. **Stop** à 3,0 × A × √(nombre de jours de bourse de détention) ; pas d'objectif ; stop gappé : prix d'ouverture. 1 R = distance du stop.
4. **Trois durées** : **H0** sortie à l'ouverture de la barre de 20:55 UTC du jour même ; **H2** à 20:55 UTC du 3e jour de bourse (entrée comprise) ; **H4** à 20:55 UTC du 5e jour de bourse. (Le stop de H0 est donc 3,0 A, celui de H2 3,0 A × √3, celui de H4 3,0 A × √5.)
5. **Frais** : base 0,02 % l'aller-retour + financement 0,015 % par nuit calendaire ; stress 0,05 % + 0,03 % par nuit (en % du prix d'entrée). Risque 0,5 % du capital par trade.

## Variantes (pour chacune des 3 durées : 9 stratégies, comptées comme 9 essais)
- **C (complète)** : t ≠ 0, **biais Monte Carlo dans le sens de la tendance** (médiane du cône au pas 40 du même signe que t), **q' > 0,25**, filtres de volatilité et de volume.
- **Cz (sans simulation)** : t ≠ 0, **z' > −0,674** (quart bas d'une gaussienne sans dérive), mêmes filtres.
- **Ct (tendance seule)** : t ≠ 0, aucun autre filtre. Référence : « suivre la tendance, point ».
- **Hasard** : sens tiré au sort (graine 2026) aux mêmes jours que C, mêmes stop et durée.

## Critères pour dire « solide » (appliqués à C, pour chacune des 3 durées)
1. Gain net moyen par trade > 0 avec t (Newey-West) ≥ 2 en **développement (2012-2019)** et en **validation (2020-2026)**.
2. Au moins 100 trades et 60 % d'années positives (années avec au moins 12 trades).
3. Deflated Sharpe ≥ 0,95 avec **9 essais** (aussi donné avec 367 essais cumulés dans le dépôt).
4. Rendement annuel après impôts (31,4 %, plus-values nettes annuelles, moins-values reportées, rendement attribué à la date de sortie) > 0.
5. **C fait mieux que Cz, que Ct et que le hasard** (gain net moyen par trade) en développement **et** en validation.
6. Gain net moyen par trade avec les frais de stress > 0 sur l'ensemble de la période.

## Informations (aucune décision n'en dépend)
Rendement de « garder l'or » sur la même période (avant et après impôts) ; 10 000 rééchantillonnages des trades de chaque C ; 100 autres tirages du hasard par durée ; résultats année par année.

## Règles de conduite
Tous les paramètres sont fixés ci-dessus avant le test (stop 3 A √jours, 08:00, q' > 0,25, durées 0/2/4 jours), sans ajustement après coup. Test lancé une seule fois ; publié tel quel. Une éventuelle réussite ne serait qu'une piste : la suite logique serait de la suivre en paper trading, sans toucher aux règles. Essais cumulés dans le dépôt après ce test : environ 367.

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
