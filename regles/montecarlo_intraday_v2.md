# Stratégie « Confluence Monte Carlo » v2 : règles figées avant le test (9 nov 2026)

## Ce que dit la recherche (résumé, sources en bas)

- **Il n'existe pas « un » indicateur Monte Carlo.** Sur TradingView il y en a une dizaine (LuxAlgo *Expected Move*, ChartPrime *Future Moves*, DW *Range Forecast*, *Monte Carlo CT*, BackQuant *Seasonality*, *Markov + Monte Carlo EV*, *Price Probabilities*…). Tous font la même chose : à partir de l'historique récent (volatilité, parfois dérive), ils simulent des centaines ou milliers de trajectoires et dessinent un **cône** (médiane, bandes 25-75 %, 5-95 %) ou une probabilité d'atteindre un niveau.
- **Aucun auteur ne donne de règle chiffrée ni de backtest.** Tous disent de ne pas l'utiliser seul, mais en **confluence** avec d'autres signaux.
- **Usages recommandés** : (1) un biais de direction (*Monte Carlo CT* : probabilité de hausse > 50 % ; ChartPrime : direction la plus probable) ; (2) **acheter les replis vers la bande basse du cône quand la prévision est haussière**, avec la **médiane comme objectif** (*Monte Carlo CT*, BackQuant « acheter la peur ») ; (3) un stop au-delà de la bande interne ; (4) des filtres : **volume relatif et momentum** (*Monte Carlo CT*), **tendance par moyenne mobile** (LuxAlgo), saisonnalité (BackQuant) ; (5) une graine fixe (pas de « repaint ») et un horizon de simulation égal à la durée de détention.
- **Limite connue** : la simulation tire dans le passé récent, elle ne contient donc pas plus d'information que la volatilité et la dérive de la fenêtre. Le test v1 l'a confirmé : probabilités annoncées de 13 % à 67 %, réussites réelles de 31 % à 35 %. D'où une règle de cette v2 : **le Monte Carlo doit battre la même stratégie sans simulation** (variante Fz).
- **Littérature** : « momentum intrajournalier » (Gao, Han, Li, Zhou) : le rendement de la première demi-heure prédit celui de la dernière (SPY 1993-2013, R² ≈ 1,6 %), **plus fort quand la volatilité et le volume sont élevés**. Cela justifie les filtres de volatilité et de volume ci-dessous (et ils réduisent le poids des frais, qui sont fixes en % alors que le stop s'élargit avec la volatilité).

Sources : TradingView (pages des indicateurs LuxAlgo `oebxZpF2`, ChartPrime `LGueefJE`, DW `ujVS2XfG`, Monte Carlo CT `9q1VcIPG`, BackQuant `D7rwZNa7`, Markov+EV `8JcjlIbR`, Price Probabilities `HLpRcHqT`) ; Gao, Han, Li, Zhou, *Market Intraday Momentum* (document de travail) ; backtrex.com *Monte Carlo simulation for trading strategies* (rééchantillonnage des trades, bonnes pratiques).

## Données
Or XAUUSD, barres 5 min Dukascopy 2012 à la dernière séance ; jours valides, barres actives et garde-fous comme en v1 (`regles/montecarlo_intraday_v1.md`). Séance journalière = 22:00 UTC → 22:00 UTC.

## Définitions
- **A** : ATR(14), lissage de Wilder, des barres 1 h terminées.
- **Ancrage** : chaque jour valide du lundi au vendredi, à **07:00 UTC** (ouverture de Londres). Prix d'ancrage P_A = ouverture de la barre 5 min de 07:00.
- **Cône Monte Carlo** (calculé une fois par jour à 07:00, avec seulement des données antérieures) : fenêtre des **480 dernières variations de 15 min** (≈ 5 séances ; barres actives, sans saut de plus de 30 min, fin ≤ 07:00), **2 000 trajectoires de 40 pas** (jusqu'à 17:00), tirage avec remise, graine 2026 (tirages partagés d'un jour à l'autre). Pour chaque pas m, on garde la distribution des niveaux simulés (en log par rapport à P_A).
- **À la décision T = 07:00 + m × 15 min** : x = ln(P_T / P_A) avec P_T = ouverture de la barre 5 min de T. **q** = part des trajectoires dont le niveau au pas m est inférieur à x (position du prix dans le cône : q bas = le prix est dans le bas du cône). **M_m** = médiane des niveaux simulés au pas m.
- **Biais Monte Carlo** : haussier si la médiane du cône au pas 40 est > 0, baissier si < 0.
- **Tendance journalière D** : dernière clôture de séance terminée > moyenne simple des 50 dernières clôtures de séance → haussière ; < → baissière.
- **Tendance horaire H** : EMA 20 > EMA 100 des clôtures 1 h → haussière ; < → baissière.
- **Filtre de volatilité** : A ≥ médiane de A sur les 1 200 dernières barres 1 h (≈ 50 jours).
- **Filtre de volume relatif** : volume (ticks) de la dernière heure civile terminée ÷ moyenne du volume de cette même heure sur les 20 jours ouvrés valides précédents ≥ 1,0.

## Règles (variante principale F)
1. **Décisions** : toutes les 30 min, de 08:00 à 16:30 UTC, du lundi au vendredi. Une position à la fois, **2 trades au maximum par jour**.
2. **Achat** : D haussière **et** H haussière **et** biais Monte Carlo haussier **et** 0,05 < q ≤ 0,25 (repli dans le quart bas du cône, sans être dans l'extrême qui signale un changement de régime) **et** filtre de volatilité **et** filtre de volume. **Vente** : symétrique (D, H baissières, biais baissier, 0,75 ≤ q < 0,95, mêmes filtres).
3. **Entrée** à l'ouverture de la barre 5 min de T.
4. **Stop** à 1,5 A. **Objectif** : le niveau de la médiane du cône au pas m (P_A × exp(M_m)). Distance d = objectif − entrée (dans le sens du trade) ; **pas de trade si d < 1,0 A**, d plafonnée à 3,0 A.
5. **Sortie dans le temps** : ouverture de la barre à min(T + 6 h, 20:55 UTC). Stop et objectif dans la même barre : stop. Stop gappé : prix d'ouverture.
6. **Risque** 0,5 % du capital par trade ; **1 R = distance du stop (1,5 A)**. Frais de base 0,02 % l'aller-retour, stress 0,05 % (en % du prix d'entrée).

## Variantes (4) et témoin
- **F** : complète (règles ci-dessus).
- **Fz** : sans simulation. Le cône est remplacé par la gaussienne simple : z = x / (σ√m), σ = écart-type des 480 variations. Biais = D et H seulement (pas de biais Monte Carlo). Achat si −1,645 < z ≤ −0,674 ; vente si 0,674 ≤ z < 1,645 ; objectif = retour au prix d'ancrage P_A. Mêmes filtres, stop, bornes de d, sorties. **Mesure si la simulation apporte quelque chose de plus qu'un écart normalisé par la volatilité.**
- **Fnt** : F sans D ni H (biais Monte Carlo seul).
- **Fnv** : F sans filtres de volatilité et de volume.
- **Témoin hasard** : sens tiré au sort (graine 2026) aux mêmes heures et avec les mêmes stop et objectif que F.

## Critères pour dire « solide » (tous exigés, pour F)
1. Gain net moyen par trade > 0 avec t (Newey-West) ≥ 2 en **développement (2012-2019)** et en **validation (2020-2026)**.
2. Au moins 100 trades et 60 % d'années positives (années avec au moins 20 trades).
3. Deflated Sharpe ≥ 0,95 avec **5 essais** (aussi donné avec 358 essais cumulés dans le dépôt).
4. Rendement annuel après impôts (31,4 % des plus-values nettes annuelles, moins-values reportées) > 0.
5. **F fait mieux que Fz** (gain net moyen par trade) en développement et en validation.
6. **F fait mieux que le témoin hasard** en développement et en validation.
7. Gain net moyen par trade **avec les frais de stress (0,05 %) > 0** sur l'ensemble de la période.

## Informations (aucune décision n'en dépend)
- 10 000 rééchantillonnages des trades de F (probabilité de total > 0, fourchette 5-95 %, perte maximale médiane et à 95 %) et 100 autres tirages du témoin hasard.
- **Le repli dans le cône prédit-il quelque chose ?** Pour tous les moments où D et H sont dans le même sens : rendement des 4 heures suivantes, dans le sens de la tendance, par tranche de position dans le cône (q ramené dans le sens de la tendance : bas = repli profond contre la tendance).

## Règles de conduite
Les paramètres ci-dessus sont fixés **avant** le test, choisis à partir de la recherche et de l'échec de v1 (frais trop lourds par rapport au stop, probabilités peu informatives), pas ajustés sur des résultats de v2. Test lancé une seule fois ; si F échoue, on le publie tel quel. Essais cumulés dans le dépôt après ce test : environ 358.

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
