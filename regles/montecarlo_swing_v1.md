# Stratégie « Monte Carlo swing » v1 (5 séances) : règles figées avant le test (9 nov 2026)

## Pourquoi
Les tests intraday (v1, v2, v3) butent sur les frais : le gain moyen brut par trade est de l'ordre de quelques points de base, comme les frais. En détenant plusieurs jours, les mêmes frais pèsent beaucoup moins par rapport au mouvement attendu. On teste donc l'idée « tendance + cône Monte Carlo » sur **5 séances** (les indicateurs Monte Carlo cités dans `regles/montecarlo_intraday_v2.md` sont décrits comme plus adaptés au court et moyen terme qu'au scalp ; l'horizon de simulation doit être égal à la durée de détention).

## Données
Or XAUUSD, barres 5 min Dukascopy 2012-2026, regroupées en **séances de 22:00 UTC à 22:00 UTC** (étiquette = date de la fin de séance ; barres actives, volume non nul). Séance valide : au moins 200 barres et 100 barres actives. Lundi-vendredi. Open = première barre active, close = dernière, high/low = extrêmes.

## Définitions (à la clôture de la séance d, avec seulement le passé)
- **ATRj** : ATR(14), lissage de Wilder, des séances.
- **SMA50** : moyenne simple des 50 dernières clôtures de séance.
- **Cône Monte Carlo** : fenêtre des **120 dernières variations de clôture à clôture** (séances consécutives, écart d'étiquettes ≤ 5 jours), **2 000 trajectoires de 5 pas**, tirage avec remise, graine 2026. **P_up = part des trajectoires dont le rendement cumulé après 5 pas est > 0** (la « probabilité de hausse » des indicateurs *Monte Carlo CT* et ChartPrime).

## Règles (variante principale S1)
1. Décision à la clôture de chaque séance **si aucune position n'est ouverte**.
2. **Achat** si clôture > SMA50 **et** P_up ≥ 0,55. **Vente** si clôture < SMA50 **et** P_up ≤ 0,45 (bornes de la zone de confiance « modérée » de *Monte Carlo CT*).
3. **Entrée à l'ouverture de la séance suivante.** **Stop à 2,5 ATRj** de l'entrée, contrôlé avec le plus haut / plus bas de chaque séance de détention (stop gappé : prix d'ouverture de la séance). **Pas d'objectif.**
4. **Sortie à la clôture de la 5e séance** de détention (entrée = séance 1) si le stop n'a pas été touché. Nouvelle décision possible à cette même clôture.
5. Frais en % du prix d'entrée : **base 0,05 % aller-retour + 0,015 % par nuit** ; **stress 0,10 % + 0,03 % par nuit**. Nuits = nombre de jours calendaires entre l'étiquette de la séance d'entrée et celle de la séance de sortie (les week-ends comptent). Les ventes paient le financement comme les achats.
6. Position à **1 × le capital** (sans levier) pendant la détention ; rendement du trade = (sortie − entrée)/entrée dans le sens du trade, moins les frais. Pour les rendements annuels, le rendement net de chaque trade est réparti à parts égales sur les séances détenues ; impôt de 31,4 % des plus-values nettes de l'année, moins-values reportées.

## Variantes (4) et témoin
- **S1** : tendance + Monte Carlo.
- **S2** : tendance seule (clôture > SMA50 → achat ; < → vente), sans simulation.
- **S3** : Monte Carlo seul (P_up ≥ 0,55 achat ; ≤ 0,45 vente), sans tendance.
- **S4** : S1 en achat seulement.
- **Témoin hasard** : sens tiré au sort (graine 2026) aux jours de signal de S1, mêmes stop et sortie.

## Critères pour dire « solide » (tous exigés, pour S1)
1. Gain net moyen par trade (en % du prix) > 0 avec t (Newey-West) ≥ 2 en **développement (2012-2019)** et en **validation (2020-2026)**.
2. Au moins 100 trades et 60 % d'années positives (années avec au moins 10 trades).
3. Deflated Sharpe ≥ 0,95 avec **5 essais** (aussi donné avec 367 essais cumulés dans le dépôt).
4. Rendement annuel après impôts > 0.
5. **S1 fait mieux que S2** (gain net moyen par trade) en développement et en validation (le Monte Carlo apporte quelque chose en plus de la tendance).
6. **S1 fait mieux que le témoin hasard** en développement et en validation.
7. Gain net moyen par trade avec les frais de stress > 0 sur l'ensemble.

## Informations (aucune décision n'en dépend)
- Rendement annuel de l'or acheté et gardé sur la même période (avant et après impôts), part du temps investi de chaque variante.
- 10 000 rééchantillonnages des trades de S1 ; 100 autres tirages du témoin.
- **La probabilité P_up annoncée prédit-elle quelque chose ?** Pour toutes les séances : rendement des 5 séances suivantes par tranche de P_up.

Paramètres fixés avant le test, non ajustés ensuite. Test lancé une seule fois. Essais cumulés après les deux tests : environ 367.

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
