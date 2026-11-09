# Stratégie « Continuation Monte Carlo » v3 (intraday) : règles figées avant le test (9 nov 2026)

## D'où vient cette idée (à lire avant les résultats)
Le tableau d'information de la v2 (`resultats/montecarlo_intraday_v2.md`, « Le repli dans le cône prédit-il quelque chose ? ») montrait que, quand les tendances journalière et horaire sont alignées, les 4 heures suivantes rapportaient davantage lorsque le prix était **au-dessus** du quart bas du cône que dans la zone de repli (5-25 %) que la v2 achetait. La v3 teste donc le **complément** de la v2 : suivre la tendance sans attendre de repli.

**Attention : cette idée vient de l'observation des mêmes données 2012-2026.** La séparation développement / validation ci-dessous n'est donc **pas** une validation indépendante pour cette hypothèse. Un résultat positif ne vaudrait que comme piste à confirmer en avant (paper trading) ; un résultat négatif est, lui, parfaitement informatif.

## Reprise de la v2 (inchangé, voir `regles/montecarlo_intraday_v2.md`)
Données, jours valides, ancrage 07:00 UTC, cône Monte Carlo (480 variations de 15 min, 2 000 trajectoires de 40 pas, graine 2026), position q dans le cône, biais Monte Carlo, tendances D (journalière) et H (horaire), filtre de volatilité, filtre de volume relatif, décisions toutes les 30 min de 08:00 à 16:30 UTC, une position à la fois, 2 trades au maximum par jour, frais de base 0,02 % et de stress 0,05 %, risque 0,5 % par trade, 1 R = distance du stop.

## Règles (variante principale C)
1. **Achat** : D haussière **et** H haussière **et** biais Monte Carlo haussier **et q > 0,25** (le prix n'est pas dans la zone de repli) **et** filtre de volatilité **et** filtre de volume. **Vente** : D et H baissières, biais baissier, **q < 0,75**, mêmes filtres.
2. Entrée à l'ouverture de la barre 5 min de la décision. **Stop à 1,5 A** (A = ATR(14) des barres 1 h terminées). **Pas d'objectif.**
3. **Sortie dans le temps : ouverture de la barre 5 min située 4 heures après l'entrée** (même horizon que le tableau d'information). Stop gappé : prix d'ouverture.

## Variantes (3) et témoin
- **C** : complète.
- **Ct** : sans le cône (tendances D et H alignées + filtres, pas de biais Monte Carlo ni de q). **Mesure si le cône apporte quelque chose en plus de la tendance.**
- **Cnv** : C sans filtres de volatilité ni de volume.
- **Témoin hasard** : sens tiré au sort (graine 2026) aux mêmes heures que C, mêmes stop et sortie.

## Critères pour dire « solide » (tous exigés, pour C)
1. Gain net moyen par trade > 0 avec t (Newey-West) ≥ 2 en développement (2012-2019) **et** en validation (2020-2026), **en gardant en tête que ce partage n'est pas indépendant pour cette idée**.
2. Au moins 100 trades et 60 % d'années positives (années avec au moins 20 trades).
3. Deflated Sharpe ≥ 0,95 avec **4 essais** (aussi donné avec 362 essais cumulés dans le dépôt).
4. Rendement annuel après impôts (31,4 %) > 0.
5. **C fait mieux que Ct** (gain net moyen par trade) en développement et en validation.
6. **C fait mieux que le témoin hasard** en développement et en validation.
7. Gain net moyen avec les frais de stress (0,05 %) > 0 sur l'ensemble.

Même si tout est réussi, ce ne sera pas une validation : l'idée vient de ces données. Paramètres fixés avant le test et non ajustés ensuite. Test lancé une seule fois.

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
