# Stratégie intraday « Monte Carlo » v1 : résultats

Règles figées avant le test : `regles/montecarlo_intraday_v1.md`. Lancé une seule fois, sans retouche. Or XAUUSD, barres 5 min Dukascopy 2012-2026 ; frais de base 0,02 % l'aller-retour (stress 0,05 %), risque 0,5 % du capital par trade (1 R = 1 ATR horaire). Développement 2012-2019, validation 2020-2026.

## Verdict

**V1 ne passe pas tous les critères figés : elle n'est pas « solide » au sens que nous avions fixé.** Les chiffres ci-dessous sont publiés tels quels, sans retouche de la règle.

| Critère (figé avant le test) | Résultat | Détail |
|---|---|---|
| Gain net moyen > 0 avec t ≥ 2 en développement (2012-2019) | ✘ échoué | moyenne -0,052 R, t = -1,9 sur 1880 trades |
| Gain net moyen > 0 avec t ≥ 2 en validation (2020-2026) | ✘ échoué | moyenne -0,044 R, t = -1,5 sur 1611 trades |
| Au moins 100 trades et 60 % d'années positives | ✘ échoué | 3491 trades, 4 années positives sur 15 |
| Deflated Sharpe ≥ 0,95 (3 essais) | ✘ échoué | DSR = 0,00 (avec 350 essais : 0,00) |
| Rendement annuel après impôts > 0 | ✘ échoué | -5,9 % par an après impôts (-5,9 % avant impôts) |
| V1 fait mieux que V3 (sans Monte Carlo) en développement et en validation | ✔ réussi | V1 -0,052 / -0,044 R contre V3 -0,075 / -0,057 R (dév. / valid.) |

## Les quatre variantes

Moyennes par trade en R (1 R = risque pris). Brut = sans frais ; net = frais de base ; stress = frais 0,05 %. t = test de Newey-West sur le net.

| Variante | Trades | par semaine | gagnants | brut | net | t | net (stress) | années positives |
|---|---|---|---|---|---|---|---|---|
| V1 Monte Carlo + tendance + RSI | 3491 | 4,5 | 43 % | 0,039 | -0,048 | -2,4 | -0,179 | 4/15 |
| V2 Monte Carlo seul | 6048 | 7,9 | 42 % | 0,034 | -0,051 | -3,4 | -0,179 | 3/15 |
| V3 tendance + RSI (sans Monte Carlo) | 11222 | 14,6 | 42 % | 0,022 | -0,066 | -6,0 | -0,198 | 1/15 |
| Témoin hasard (aux heures de V3) | 11273 | 14,6 | 42 % | 0,013 | -0,075 | -6,8 | -0,207 | 1/15 |

| Variante | dév. : trades | dév. : net R | dév. : t | valid. : trades | valid. : net R | valid. : t | rend. annuel avant impôts | après impôts (31,4 %) | DSR (3 essais) | DSR (350 essais) |
|---|---|---|---|---|---|---|---|---|---|---|
| V1 | 1880 | -0,052 | -1,9 | 1611 | -0,044 | -1,5 | -5,9 % | -5,9 % | 0,00 | 0,00 |
| V2 | 3286 | -0,060 | -2,8 | 2762 | -0,041 | -1,9 | -10,6 % | -10,6 % | 0,00 | 0,00 |
| V3 | 6041 | -0,075 | -5,0 | 5181 | -0,057 | -3,5 | -23,2 % | -23,2 % | 0,00 | 0,00 |
| Hasard | 6047 | -0,067 | -4,4 | 5226 | -0,084 | -5,4 | -25,8 % | -25,8 % | 0,00 | 0,00 |

Sorties de V1 : stop 1854, cible 1282, heure 355.
Heures de décision évaluées : 34418 ; signaux d'achat/vente à l'heure : V1 7226, V2 12688, V3 27328.

## V1 année par année

| Année | Trades | net moyen (R) | total (R) |
|---|---|---|---|
| 2012 | 234 | -0,119 | -27,8 |
| 2013 | 219 | -0,167 | -36,7 |
| 2014 | 232 | -0,070 | -16,2 |
| 2015 | 260 | -0,022 | -5,8 |
| 2016 | 244 | 0,083 | 20,2 |
| 2017 | 255 | 0,005 | 1,2 |
| 2018 | 222 | -0,076 | -16,8 |
| 2019 | 214 | -0,075 | -16,1 |
| 2020 | 215 | -0,043 | -9,3 |
| 2021 | 241 | -0,193 | -46,5 |
| 2022 | 246 | -0,025 | -6,1 |
| 2023 | 256 | -0,109 | -27,9 |
| 2024 | 256 | -0,009 | -2,2 |
| 2025 | 221 | 0,045 | 9,9 |
| 2026 | 176 | 0,067 | 11,8 |

## Le témoin hasard

Le témoin tire le sens au hasard aux mêmes heures que V3 (graine 2026) : net moyen -0,075 R. Sur 100 autres tirages : médiane -0,088 R, 90 % des tirages entre -0,106 et -0,072 R ; 1 % des tirages font au moins aussi bien que V3 (-0,066 R).

## Le Monte Carlo prédit-il quelque chose ? (information)

Pour chaque heure de décision (achat et vente hypothétiques, sans limite de position) : probabilité annoncée par la simulation contre fréquence réelle « objectif touché avant le stop » (échéance 8 h ou 20:55 UTC ; pour les décisions de 13 h à 16 h l'échéance est plus courte que les 8 h simulées, ce qui biaise vers le bas).

| Probabilité annoncée | Cas | Annoncé en moyenne | Réalisé |
|---|---|---|---|
| < 20 % | 13744 | 13,4 % | 31,4 % |
| 20-30 % | 15004 | 25,1 % | 31,8 % |
| 30-40 % | 15352 | 34,8 % | 33,0 % |
| 40-50 % | 12048 | 44,7 % | 34,8 % |
| 50-60 % | 7718 | 54,4 % | 36,0 % |
| ≥ 60 % | 4970 | 66,9 % | 35,4 % |

Corrélation de rang entre probabilité annoncée et réussite réelle : 0,036 (décisions de 08 h à 12 h seulement, échéance complète de 8 h : 0,030).

## Monte Carlo des résultats de V1 (information)

10 000 rééchantillonnages au hasard (avec remise) des 3491 trades de V1 : probabilité que le total soit positif = 1 % ; total entre -283,2 et -51,7 R (5 % à 95 %) ; perte maximale médiane 193,5 R (95 % des cas sous 300,6 R). Cela mesure la part de chance dans l'ordre des trades, pas la validité de la règle dans le futur.

## À retenir

- Nombre d'essais cumulés dans ce dépôt : environ 350 + 3 variantes de cette stratégie.
- Le témoin hasard et V3 servent à savoir si le Monte Carlo **apporte** quelque chose en plus de la tendance : voir le critère 6.
- Les paramètres (seuils 0,50 / 0,15, stop 1,0 A, objectif 1,5 A, fenêtre de 96 variations) n'ont pas été ajustés après ce test.
- Frais supposés : 0,02 % l'aller-retour (à remplacer par le vrai spread de ton courtier). Impôt : 31,4 % (flat tax 2026), sans conseil fiscal.

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
