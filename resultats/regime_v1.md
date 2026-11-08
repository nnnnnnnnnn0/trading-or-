# Stratégie Régime or v1 : résultats

Règles : `regles/strategie_regime_v1.md`, figées avant le test. Rien n'a été ajusté après coup. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

## Module A : régime journalier (tendance + macro, taille par la volatilité)

Données : or GC=F du 2006-10-26 au 2026-11-06 (5037 séances testées, hors période de chauffe), dollar DXY, taux réels américains 10 ans (US Treasury). Frais : 0,05 % par aller-retour, financement 0,015 % par nuit. Dollar et taux réels pris avec un jour de retard.

Référence « garder l'or » : rendement annuel 11,3 %, volatilité 18,4 %, Sharpe 0,62, perte maximale -44 %.

| Variante | Rendement annuel | Volatilité | Sharpe | Perte max | Rendement annuel par bloc | Hasard | Deflated Sharpe (3 essais / 250) | Temps achat / vente | Changements de sens par an | Contribution achats / ventes (points par an) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V1 principale (0,7 tendance + 0,3 macro) | -0,3 % | 9,0 % | -0,03 | -57 % | 9 / -7 / -4 / 1 | 26 % | 0,16 / 0,00 | 39 % / 23 % | 15,3 | 3,1 / -3,2 |
| V2 tendance seule | -0,9 % | 11,0 % | -0,08 | -63 % | 4 / -8 / -4 / 3 | 32 % | 0,11 / 0,00 | 63 % / 35 % | 10,8 | 2,9 / -3,8 |
| V3 pondération 0,5 / 0,5 | -0,3 % | 9,0 % | -0,04 | -57 % | 9 / -7 / -4 / 1 | 27 % | 0,16 / 0,00 | 39 % / 23 % | 15,3 | 3,0 / -3,2 |

Blocs égaux : 2006-2011 | 2011-2016 | 2016-2021 | 2021-2026. « Hasard » = part de 1 000 décalages aléatoires de la même série d'expositions qui rapportent au moins autant.

### Verdict (variante principale V1)

**Critères non remplis : Sharpe trop bas face à garder l'or ; perte maximale pas assez réduite ; pas positive dans 3 blocs sur 4 ; pas meilleure que le hasard ; Deflated Sharpe < 0,95.** La stratégie n'est pas retenue en l'état ; elle n'est pas retouchée pour la faire passer.

Autres variantes (robustesse, mêmes critères) : V2 : non remplis (5 critère(s)) ; V3 : non remplis (5 critère(s)).

### Rendement par année (V1 contre garder l'or)

| Année | V1 | Garder l'or |
| --- | --- | --- |
| 2006 | 0 % | 6 % |
| 2007 | 19 % | 35 % |
| 2008 | 1 % | 3 % |
| 2009 | 4 % | 27 % |
| 2010 | 9 % | 27 % |
| 2011 | 15 % | 12 % |
| 2012 | -8 % | 6 % |
| 2013 | 2 % | -27 % |
| 2014 | -15 % | -3 % |
| 2015 | -8 % | -9 % |
| 2016 | -8 % | 8 % |
| 2017 | -17 % | 13 % |
| 2018 | -1 % | -2 % |
| 2019 | 9 % | 19 % |
| 2020 | 4 % | 28 % |
| 2021 | -17 % | -8 % |
| 2022 | -4 % | 3 % |
| 2023 | -9 % | 12 % |
| 2024 | 12 % | 29 % |
| 2025 | 11 % | 62 % |
| 2026 | -3 % | -6 % |

## Module B : hypothèse H1, « l'or monte surtout hors séance américaine (13 h à 21 h UTC) »

Données 5 min (Dukascopy, or au comptant) : 4649 jours du 2012-01-01 au 2026-11-05 ; années présentes : 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026.

| Période | Jours | Séance américaine (rendement moyen) | Hors séance américaine | Différence | t |
| --- | --- | --- | --- | --- | --- |
| Développement (60 %) | 2789 | -0,020 % | 0,028 % | 0,048 % | 2,9 |
| Contrôle (40 %) | 1860 | -0,013 % | 0,061 % | 0,074 % | 3,5 |

Années où « hors séance » > « séance américaine » : 80 %.

**H1 confirmée** (critère : différence positive en développement et en contrôle avec t ≥ 2, et au moins 70 % des années).

## Limites

- Signal et exécution à la clôture du vendredi ; la sortie de sécurité est exécutée à la clôture, sans glissement de prix.
- Frais et financement estimés, identiques achat et vente ; pas d'écart de prix de courtier ; futures GC=F.
- Heures UTC fixes pour H1 : l'ouverture américaine se décale d'une heure selon l'heure d'été.
- Environ 250 essais ont été faits dans ce projet avant cette stratégie (voir Deflated Sharpe à 250). Cette stratégie, elle, vient de la littérature et n'a que 3 variantes.
- Aucune stratégie ne garantit un gain ; le suivi de tendance connaît de longues périodes sans gain.
