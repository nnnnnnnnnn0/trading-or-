# Stratégie Compression Or v1 : résultats

Règles : `regles/strategie_compression_v1.md`, figées avant le test. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

Or au comptant 5 min, 3833 jours de séance valides du 2012-01-03 au 2026-11-06. Un R = le risque d'un trade (1 × ATR) = 0,5 % du capital. Frais de base : 0,05 % l'aller-retour + 0,015 % par nuit.

| Variante | Trades | Par semaine | Gain brut moyen | Gain net moyen | t | Gagnants | Rendement annuel (capital) | Développement (moy. R / t) | Contrôle (moy. R / t) | Blocs (moy. R) | Années positives | Deflated Sharpe (2 / 250 essais) | Objectif / stop / temps | Achats / ventes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A (achat et vente) | 855 | 1,1 | 0,028 R | -0,037 R | -1,1 | 43 % | -1,1 % | -0,057 / -1,3 | -0,007 / -0,2 | -0,03 ; -0,12 ; 0,04 ; -0,04 | 40 % | 0,06 / 0,00 | 9 % / 34 % / 57 % | 456 / 399 |
| B (sens de la tendance) | 632 | 0,8 | 0,092 R | 0,026 R | 0,7 | 48 % | 0,6 % | 0,005 / 0,1 | 0,058 / 0,9 | 0,04 ; -0,10 ; 0,06 ; 0,10 | 53 % | 0,55 / 0,01 | 9 % / 32 % / 58 % | 358 / 274 |

### Verdict

- Variante A : critères non remplis : gain net positif avec t ≥ 2 en développement et en contrôle ; positif dans moins de 3 blocs sur 4 ; moins de 60 % d'années positives ; Deflated Sharpe < 0,95.
- Variante B : critères non remplis : gain net positif avec t ≥ 2 en développement et en contrôle ; moins de 60 % d'années positives ; Deflated Sharpe < 0,95.

**La stratégie n'est pas retenue ; elle n'est pas retouchée pour la faire passer.**

Trades ignorés : A : 510 / B : 340 (position déjà ouverte) et A : 0 / B : 0 (deux niveaux touchés dans la même barre).

### Contrôle : même mécanique les jours NON comprimés (information)

| Variante | Trades | Gain brut moyen | Gain net moyen | t |
| --- | --- | --- | --- | --- |
| A | 1818 | 0,054 R | -0,014 R | -0,6 |
| B | 1043 | 0,064 R | -0,004 R | -0,1 |

Si le contrôle fait aussi bien que les règles, la compression n'apporte rien : on ne ferait que profiter (ou souffrir) d'une cassure générale.

### Gain net moyen par année (R, variante A)

| Année | Gain net moyen (R) |
| --- | --- |
| 2012 | -0,149 |
| 2013 | 0,061 |
| 2014 | -0,108 |
| 2015 | -0,009 |
| 2016 | -0,058 |
| 2017 | -0,272 |
| 2018 | -0,046 |
| 2019 | 0,042 |
| 2020 | 0,061 |
| 2021 | -0,009 |
| 2022 | 0,041 |
| 2023 | 0,001 |
| 2024 | 0,026 |
| 2025 | -0,049 |
| 2026 | -0,100 |

## Limites

- Exécution des ordres stop supposée au niveau (ou à l'ouverture en cas de gap), sans glissement ; or au comptant ; frais estimés.
- Dans la barre d'entrée, seul le stop est vérifié ; stop et objectif dans une même barre 5 min : stop compté (hypothèse prudente).
- Environ 255 essais ont été faits dans ce projet avant cette stratégie ; le Deflated Sharpe à 250 essais est donné par honnêteté.
- Heures UTC fixes pour le jour de séance ; la séance de New York se décale d'une heure selon l'heure d'été.
