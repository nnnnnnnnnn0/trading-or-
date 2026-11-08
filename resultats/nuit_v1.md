# Stratégie Nuit or v1 : résultats

Règles : `regles/strategie_nuit_v1.md`, figées avant le test. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

Achat à 21 h UTC, vente à 13 h UTC le jour de bourse suivant, or au comptant 5 min, 4649 trades du 2012-01-01 au 2026-11-05. Gain brut moyen par trade (sans frais) : 0,042 %.

| Variante | Gain net moyen par trade | t | Rendement annuel | Sharpe | Trades gagnants | Perte max (cumulée) | Développement (moy. / t) | Contrôle (moy. / t) | Blocs (moy. par trade) | Années positives | Deflated Sharpe (2 / 250 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A (frais de base) | -0,026 % | -2,8 | -6,5 % | -0,64 | 42 % | -160 % | -0,039 % / -3,5 | -0,006 % / -0,4 | -0,082 % ; -0,012 % ; -0,034 % ; 0,025 % | 33 % | 0,00 / 0,00 |
| B (frais réduits de moitié) | 0,008 % | 0,9 | 2,0 % | 0,19 | 45 % | -64 % | -0,005 % / -0,5 | 0,028 % / 1,8 | -0,049 % ; 0,022 % ; 0,000 % ; 0,058 % | 53 % | 0,62 / 0,02 |

### Verdict (variante A)

**Critères non remplis : gain net positif avec t ≥ 2 en développement et en contrôle ; positif dans moins de 3 blocs sur 4 ; moins de 70 % d'années positives ; Deflated Sharpe < 0,95.** La stratégie n'est pas retenue ; elle n'est pas retouchée pour la faire passer.

Frais aller-retour qui annuleraient le gain brut (financement de 0,015 % par nuit inclus, 1,17 nuits en moyenne) : 0,024 %. Frais de base : 0,050 %.

### Gain net moyen par année (variante A)

| Année | Gain net moyen par trade |
| --- | --- |
| 2012 | -0,055 % |
| 2013 | -0,136 % |
| 2014 | -0,061 % |
| 2015 | -0,060 % |
| 2016 | 0,034 % |
| 2017 | -0,022 % |
| 2018 | -0,038 % |
| 2019 | -0,019 % |
| 2020 | 0,008 % |
| 2021 | -0,034 % |
| 2022 | -0,086 % |
| 2023 | -0,017 % |
| 2024 | 0,015 % |
| 2025 | 0,059 % |
| 2026 | 0,033 % |

## Limites

- Heures UTC fixes : l'ouverture américaine se décale d'une heure selon l'heure d'été.
- Entrée et sortie aux prix d'ouverture de barres 5 min, sans glissement ; or au comptant ; frais estimés, pas ceux d'un courtier précis.
- Cette règle vient d'un résultat vu sur les mêmes données (H1) : le test est moins indépendant qu'il n'en a l'air.
