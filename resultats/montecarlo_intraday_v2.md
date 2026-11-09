# Stratégie « Confluence Monte Carlo » v2 : résultats

Règles figées avant le test : `regles/montecarlo_intraday_v2.md` (recherche et description complète). Lancé une seule fois, sans retouche. Or XAUUSD, barres 5 min Dukascopy 2012-2026 ; frais de base 0,02 % l'aller-retour (stress 0,05 %), risque 0,5 % du capital par trade (1 R = distance du stop, 1,5 ATR horaire). Développement 2012-2019, validation 2020-2026.

## Verdict

**F ne passe pas tous les critères figés (1 ligne réussie sur 8 ; le critère 1 compte pour deux lignes, développement et validation) : elle n'est pas « solide » au sens que nous avions fixé.** Les chiffres sont publiés tels quels, sans retouche de la règle.

| Critère (figé avant le test) | Résultat | Détail |
|---|---|---|
| Gain net moyen > 0 avec t ≥ 2 en développement (2012-2019) | ✘ échoué | moyenne -0,076 R, t = -1,5 sur 344 trades |
| Gain net moyen > 0 avec t ≥ 2 en validation (2020-2026) | ✘ échoué | moyenne -0,003 R, t = -0,1 sur 311 trades |
| Au moins 100 trades et 60 % d'années positives | ✘ échoué | 655 trades, 6 années positives sur 15 (années de 20 trades ou plus) |
| Deflated Sharpe ≥ 0,95 (5 essais) | ✘ échoué | DSR = 0,01 (avec 358 essais : 0,00) |
| Rendement annuel après impôts > 0 | ✘ échoué | -1,0 % par an après impôts (-1,0 % avant impôts) |
| F fait mieux que Fz (sans simulation) en développement et en validation | ✔ réussi | F -0,076 / -0,003 R contre Fz -0,078 / -0,023 R (dév. / valid.) |
| F fait mieux que le témoin hasard en développement et en validation | ✘ échoué | F -0,076 / -0,003 R contre hasard 0,042 / -0,057 R (dév. / valid.) |
| Gain net moyen > 0 avec les frais de stress (0,05 %) | ✘ échoué | -0,114 R par trade avec frais de stress |

## Les variantes

Moyennes par trade en R (1 R = distance du stop). Brut = sans frais ; net = frais de base ; stress = frais 0,05 %. t = test de Newey-West sur le net.

| Variante | Trades | par semaine | gagnants | brut | net | t | net (stress) | années positives |
|---|---|---|---|---|---|---|---|---|
| F complète (Monte Carlo + tendances + filtres) | 655 | 0,9 | 51 % | 0,007 | -0,041 | -1,2 | -0,114 | 6/15 |
| Fz sans simulation (écart normalisé) | 607 | 0,8 | 50 % | -0,005 | -0,053 | -1,5 | -0,126 | 6/15 |
| Fnt sans tendances | 1092 | 1,4 | 51 % | 0,016 | -0,032 | -1,2 | -0,104 | 4/15 |
| Fnv sans filtres volatilité/volume | 1724 | 2,2 | 52 % | 0,028 | -0,030 | -1,3 | -0,118 | 8/15 |
| Témoin hasard (aux heures de F) | 657 | 0,9 | 50 % | 0,043 | -0,005 | -0,1 | -0,077 | 9/15 |

| Variante | dév. : trades | dév. : net R | dév. : t | valid. : trades | valid. : net R | valid. : t | rend. annuel avant impôts | après impôts (31,4 %) | DSR (5 essais) | DSR (358 essais) |
|---|---|---|---|---|---|---|---|---|---|---|
| F | 344 | -0,076 | -1,5 | 311 | -0,003 | -0,1 | -1,0 % | -1,0 % | 0,01 | 0,00 |
| Fz | 330 | -0,078 | -1,6 | 277 | -0,023 | -0,5 | -1,1 % | -1,1 % | 0,00 | 0,00 |
| Fnt | 574 | -0,046 | -1,2 | 518 | -0,016 | -0,5 | -1,2 % | -1,3 % | 0,01 | 0,00 |
| Fnv | 904 | -0,045 | -1,4 | 820 | -0,013 | -0,4 | -1,9 % | -1,9 % | 0,01 | 0,00 |
| Hasard | 344 | 0,042 | 0,8 | 313 | -0,057 | -1,1 | -0,2 % | -0,5 % | 0,09 | 0,00 |

Sorties de F : stop 237, cible 213, heure 205.
Heures de décision évaluées : 67650 ; déclenchements (sens ≠ 0, distance à l'objectif valide) : F 1743, Fz 1502, Fnt 2852, Fnv 6298.

## F année par année

| Année | Trades | net moyen (R) | total (R) |
|---|---|---|---|
| 2012 | 34 | -0,138 | -4,7 |
| 2013 | 43 | 0,127 | 5,5 |
| 2014 | 48 | -0,083 | -4,0 |
| 2015 | 45 | 0,085 | 3,8 |
| 2016 | 48 | 0,088 | 4,2 |
| 2017 | 41 | -0,322 | -13,2 |
| 2018 | 51 | -0,210 | -10,7 |
| 2019 | 34 | -0,210 | -7,1 |
| 2020 | 31 | -0,020 | -0,6 |
| 2021 | 47 | -0,173 | -8,1 |
| 2022 | 58 | 0,047 | 2,7 |
| 2023 | 46 | -0,043 | -2,0 |
| 2024 | 58 | -0,054 | -3,1 |
| 2025 | 41 | 0,116 | 4,8 |
| 2026 | 30 | 0,181 | 5,4 |

## Le témoin hasard

Le témoin tire le sens au hasard aux mêmes heures que F, avec les mêmes stop et objectif (graine 2026) : net moyen -0,005 R. Sur 100 autres tirages : médiane -0,043 R, 90 % des tirages entre -0,097 et 0,011 R ; 43 % des tirages font au moins aussi bien que F (-0,041 R).

## Le repli dans le cône prédit-il quelque chose ? (information)

Pour tous les moments où la tendance journalière et la tendance horaire vont dans le même sens : rendement des 4 heures suivantes, compté dans le sens de la tendance, selon la position du prix dans le cône Monte Carlo (en bas = repli profond contre la tendance). Les observations se chevauchent (une toutes les 30 min) : à lire comme une tendance générale, pas comme un test.

| Position dans le cône | Cas | rendement moyen 4 h (points de base) | en ATR | part positive |
|---|---|---|---|---|
| 0-5 % (repli extrême) | 2708 | -1,96 | -0,010 | 54 % |
| 5-25 % (repli profond : zone d'achat de F) | 8554 | 0,13 | 0,038 | 54 % |
| 25-50 % | 11857 | 1,13 | 0,072 | 53 % |
| 50-75 % | 11286 | 1,47 | 0,084 | 52 % |
| 75-95 % | 7584 | 1,42 | 0,070 | 50 % |
| 95-100 % (déjà très étendu) | 2598 | 1,24 | 0,014 | 50 % |

## Monte Carlo des résultats de F (information)

10 000 rééchantillonnages au hasard (avec remise) des 655 trades de F : probabilité que le total soit positif = 12 % ; total entre -64,1 et 9,7 R (5 % à 95 %) ; perte maximale médiane 40,2 R (95 % des cas sous 71,7 R). Cela mesure la part de chance dans l'ordre des trades, pas la validité de la règle dans le futur.

## À retenir

- Essais cumulés dans ce dépôt : environ 358 (dont les 5 variantes de ce test).
- Fz et le témoin hasard servent à savoir si la **simulation** apporte quelque chose en plus d'un simple écart normalisé et d'un tirage au sort (critères 5 et 6).
- Aucun paramètre n'a été ajusté après ce test (fenêtre de 480 variations, 2 000 trajectoires, bornes 0,05 / 0,25, stop 1,5 A, objectif = médiane du cône entre 1 et 3 A).
- Frais supposés : 0,02 % l'aller-retour (à remplacer par le vrai spread de ton courtier). Impôt : 31,4 % (flat tax 2026), sans conseil fiscal.

Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
