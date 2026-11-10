# Stratégie « Continuation Monte Carlo » v3 : résultats

Règles figées avant le test : `regles/continuation_monte_carlo_v3.md`. Lancé une seule fois, sans retouche. **L'idée vient de l'observation d'un tableau de la v2 sur les mêmes données : ce test n'est donc pas indépendant** et un bon résultat ne serait qu'une piste à confirmer en avant. Or XAUUSD, barres 5 min Dukascopy 2012-2026 ; une décision par jour à 08:00 UTC, dans le sens de la tendance ; frais 0,02 % l'aller-retour + 0,015 % par nuit (stress 0,05 % + 0,03 %) ; risque 0,5 % du capital par trade (1 R = distance du stop, 3 ATR horaires × √jours de détention). Développement 2012-2019, validation 2020-2026.

## Verdict

**Aucune des trois durées ne passe tous les critères figés : la continuation n'est pas « solide » au sens que nous avions fixé.** Les chiffres sont publiés tels quels, sans retouche de la règle.

| Critère (figé avant le test) | H0 : le jour même | H2 : 3 jours | H4 : 5 jours |
|---|---|---|---|
| Gain net moyen > 0 avec t ≥ 2 en développement (2012-2019) | ✘ -0,001 R, t = -0,0 (170 trades) | ✘ -0,080 R, t = -0,9 (117 trades) | ✘ 0,004 R, t = 0,0 (103 trades) |
| Gain net moyen > 0 avec t ≥ 2 en validation (2020-2026) | ✘ 0,110 R, t = 1,7 (180 trades) | ✘ 0,121 R, t = 1,4 (115 trades) | ✘ 0,145 R, t = 1,4 (97 trades) |
| Au moins 100 trades et 60 % d'années positives | ✔ 350 trades ; 9 années positives sur 15 | ✘ 232 trades ; 8 années positives sur 14 | ✘ 200 trades ; 6 années positives sur 12 |
| Deflated Sharpe ≥ 0,95 (9 essais) | ✘ DSR 0,36 (367 essais : 0,03) | ✘ DSR 0,13 (367 essais : 0,00) | ✘ DSR 0,37 (367 essais : 0,03) |
| Rendement annuel après impôts > 0 | ✔ 0,4 % par an (0,6 % avant impôts) | ✔ 0,1 % par an (0,2 % avant impôts) | ✔ 0,4 % par an (0,6 % avant impôts) |
| C fait mieux que Cz, Ct et le hasard en développement et en validation | ✘ C -0,001 / 0,110 R contre Cz 0,012 / 0,069 ; Ct 0,021 / 0,060 ; hasard 0,072 / 0,008 (dév. / valid.) | ✘ C -0,080 / 0,121 R contre Cz 0,026 / 0,082 ; Ct 0,002 / 0,071 ; hasard -0,022 / -0,053 (dév. / valid.) | ✘ C 0,004 / 0,145 R contre Cz 0,083 / 0,128 ; Ct -0,006 / 0,127 ; hasard -0,038 / -0,273 (dév. / valid.) |
| Gain net moyen > 0 avec les frais de stress | ✔ 0,022 R par trade | ✘ -0,027 R par trade | ✔ 0,020 R par trade |

Critères réussis (sur 7) : H0 3, H2 1, H4 2.

## Toutes les stratégies

Moyennes par trade en R. Brut = sans frais ; net = frais de base et financement ; stress = frais de stress ; t = Newey-West sur le net. 12 colonnes : trades, trades par an, gagnants, brut, net, t, net (stress), net en développement, net en validation, années positives, rendement annuel après impôts.

| Stratégie | Trades | par an | gagnants | brut | net | t | stress | dév. | valid. | années + | après impôts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 : C complète | 350 | 24 | 51 % | 0,079 | 0,056 | 1,2 | 0,022 | -0,001 | 0,110 | 9/15 | 0,4 % |
| H0 : Cz sans simulation | 421 | 29 | 51 % | 0,064 | 0,041 | 1,0 | 0,006 | 0,012 | 0,069 | 8/15 | 0,4 % |
| H0 : Ct tendance seule | 2490 | 169 | 49 % | 0,070 | 0,039 | 1,9 | -0,007 | 0,021 | 0,060 | 11/15 | 2,2 % |
| H0 : Hasard (jours de C) | 350 | 24 | 51 % | 0,062 | 0,039 | 0,9 | 0,005 | 0,072 | 0,008 | 8/15 | 0,2 % |
| H2 : C complète | 232 | 16 | 48 % | 0,059 | 0,020 | 0,3 | -0,027 | -0,080 | 0,121 | 8/14 | 0,1 % |
| H2 : Cz sans simulation | 274 | 19 | 48 % | 0,094 | 0,054 | 0,8 | 0,007 | 0,026 | 0,082 | 9/15 | 0,4 % |
| H2 : Ct tendance seule | 1071 | 73 | 45 % | 0,082 | 0,034 | 0,9 | -0,024 | 0,002 | 0,071 | 9/15 | 1,0 % |
| H2 : Hasard (jours de C) | 247 | 17 | 47 % | 0,000 | -0,038 | -0,7 | -0,083 | -0,022 | -0,053 | 6/15 | -0,2 % |
| H4 : C complète | 200 | 14 | 46 % | 0,120 | 0,072 | 1,0 | 0,020 | 0,004 | 0,145 | 6/12 | 0,4 % |
| H4 : Cz sans simulation | 231 | 16 | 48 % | 0,152 | 0,105 | 1,4 | 0,052 | 0,083 | 0,128 | 8/15 | 0,7 % |
| H4 : Ct tendance seule | 701 | 48 | 46 % | 0,114 | 0,055 | 1,2 | -0,012 | -0,006 | 0,127 | 9/15 | 1,0 % |
| H4 : Hasard (jours de C) | 208 | 14 | 41 % | -0,109 | -0,155 | -2,6 | -0,206 | -0,038 | -0,273 | 3/14 | -1,0 % |

Sorties de C : H0 : heure 263, stop 87 ; H2 : heure 156, stop 76 ; H4 : heure 138, stop 62.
Décisions à 08:00 évaluées : 3759 ; jours où C déclenche : 350, Cz : 421, Ct : 2490.

Information : **garder l'or** sur la même période rapporte 6,0 % par an avant impôts et 4,5 % par an après impôts (vente à la fin, 31,4 %).

## Années, durée par durée (C : nombre de trades / total en R)

| Année | H0 | H2 | H4 |
|---|---|---|---|
| 2012 | 14 / 2,0 | 11 / -1,3 | 9 / 1,3 |
| 2013 | 23 / 2,1 | 14 / -4,5 | 13 / -3,1 |
| 2014 | 22 / -3,1 | 15 / -3,8 | 14 / -2,0 |
| 2015 | 28 / -2,4 | 18 / -0,1 | 16 / 3,1 |
| 2016 | 22 / 0,8 | 15 / -2,3 | 14 / -2,4 |
| 2017 | 17 / -0,5 | 15 / 3,8 | 12 / 5,1 |
| 2018 | 19 / -1,8 | 14 / -1,5 | 14 / -3,5 |
| 2019 | 25 / 2,8 | 15 / 0,2 | 11 / 2,1 |
| 2020 | 31 / 0,3 | 15 / 5,3 | 13 / 0,0 |
| 2021 | 25 / 4,6 | 17 / -1,4 | 14 / 1,8 |
| 2022 | 29 / 4,8 | 18 / 0,2 | 13 / 4,6 |
| 2023 | 23 / 4,7 | 14 / 1,6 | 11 / 4,1 |
| 2024 | 26 / -0,2 | 16 / 2,4 | 15 / -1,0 |
| 2025 | 23 / 6,9 | 18 / 4,4 | 17 / 6,0 |
| 2026 | 23 / -1,3 | 17 / 1,5 | 14 / -1,5 |

## Le hasard (information)

Même jours que C, sens tiré au sort (graine 2026) puis 100 autres tirages par durée, mêmes stop et frais.

| Durée | net du tirage principal | médiane des 100 tirages | 90 % des tirages entre | tirages au moins aussi bons que C |
|---|---|---|---|---|
| H0 | 0,039 R | -0,031 R | -0,111 et 0,041 R | 3 % |
| H2 | -0,038 R | -0,053 R | -0,155 et 0,068 R | 17 % |
| H4 | -0,155 R | -0,067 R | -0,166 et 0,055 R | 1 % |

## Monte Carlo des résultats de C (information)

10 000 rééchantillonnages des trades (avec remise) : probabilité que le total soit positif, fourchette 5-95 % du total en R, perte maximale médiane.

| Durée | Trades | P(total > 0) | total 5 % - 95 % (R) | perte max médiane (R) |
|---|---|---|---|---|
| H0 | 350 | 89 % | -7,6 à 47,8 | 12,4 |
| H2 | 232 | 61 % | -21,1 à 29,9 | 14,8 |
| H4 | 200 | 84 % | -9,7 à 38,7 | 11,1 |

## À retenir

- Essais cumulés dans ce dépôt : environ 367 (dont les 9 stratégies de ce test).
- L'hypothèse vient des mêmes données : seule une confirmation en avant (paper trading, règles inchangées) aurait une vraie valeur.
- Aucun paramètre n'a été ajusté après ce test (08:00, q' > 0,25, stop 3 A √jours, durées 0/2/4 jours).
- Frais supposés à remplacer par ceux de ton courtier ; impôt 31,4 % (flat tax 2026), sans conseil fiscal.

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
