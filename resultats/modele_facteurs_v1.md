# Modèle multi-facteurs v1 : l'or le lendemain

Données : 5041 jours de bourse (2006-10-20 à 2026-11-04), 16 facteurs (or, dollar, taux, argent, VIX, S&P 500, pétrole). Test strictement chronologique : réentraînement tous les 63 jours, toujours évalué sur des jours que le modèle n'a jamais vus. Environ 3728 jours testés.

**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

## Résumé (derniers 30 % de la période testée)

| Modèle | AUC (0,5 = hasard) | Rendement moyen par ordre | Verdict |
| --- | --- | --- | --- |
| Régression logistique | 0,537 | 0,175 % | Absent ou instable |
| Petits arbres | 0,544 | 0,131 % | Absent ou instable |

## Détail

### Régression logistique

| Période | Jours | Précision | AUC | Brier (modèle / constante) | Ordres | Réussite | Rendement moyen par ordre (± IC 95 %) | Frais ×2 | Part des tirages au hasard aussi bons |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 3728 | 51,7 % | 0,513 | 0,2512 / 0,2502 | 1367 | 50 % | 0,039 % ± 0,062 | -0,011 % | 0 % |
| Premiers 70 % (information) | 2609 | 50,9 % | 0,506 | 0,2526 / 0,2507 | 1060 | 48 % | -0,001 % ± 0,068 | -0,051 % | 6 % |
| Derniers 30 % (contrôle) | 1119 | 53,7 % | 0,537 | 0,2479 / 0,2489 | 307 | 57 % | 0,175 % ± 0,144 | 0,125 % | 0 % |

**Verdict : Absent ou instable.**

Rendement moyen par ordre, année par année : 2012 : 0,04 % · 2013 : -0,18 % · 2014 : -0,09 % · 2015 : -0,10 % · 2016 : 0,17 % · 2017 : 0,12 % · 2018 : -0,05 % · 2019 : 0,01 % · 2020 : 0,13 % · 2021 : 0,09 % · 2022 : 0,22 % · 2023 : -0,01 % · 2024 : 0,20 % · 2025 : 0,31 % · 2026 : 0,22 %

### Petits arbres

| Période | Jours | Précision | AUC | Brier (modèle / constante) | Ordres | Réussite | Rendement moyen par ordre (± IC 95 %) | Frais ×2 | Part des tirages au hasard aussi bons |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tout | 3728 | 51,4 % | 0,510 | 0,2539 / 0,2502 | 1900 | 50 % | 0,005 % ± 0,050 | -0,045 % | 4 % |
| Premiers 70 % (information) | 2609 | 50,8 % | 0,498 | 0,2566 / 0,2507 | 1388 | 48 % | -0,041 % ± 0,053 | -0,091 % | 43 % |
| Derniers 30 % (contrôle) | 1119 | 53,0 % | 0,544 | 0,2477 / 0,2489 | 512 | 55 % | 0,131 % ± 0,115 | 0,081 % | 0 % |

**Verdict : Absent ou instable.**

Rendement moyen par ordre, année par année : 2012 : -0,01 % · 2013 : -0,00 % · 2014 : -0,11 % · 2015 : -0,13 % · 2016 : 0,07 % · 2017 : -0,13 % · 2018 : -0,02 % · 2019 : 0,01 % · 2020 : -0,03 % · 2021 : -0,05 % · 2022 : -0,06 % · 2023 : -0,03 % · 2024 : 0,08 % · 2025 : 0,48 % · 2026 : 0,12 %

## Probabilité pour la prochaine séance (information, pas un conseil)

- Régression logistique : 50 % de chances que l'or monte après la clôture du 2026-11-04.
- Petits arbres : 52 % de chances que l'or monte après la clôture du 2026-11-04.

Facteurs les plus pesants dans la régression (valeurs standardisées) : vix_1j (-0,126), or_1j (-0,106), dist_ma50 (0,095), or_20j (-0,066), vol_20j (-0,055), pente_5j (0,055).

## Hypothèses et limites

- Futures GC=F, clôture à clôture. Les heures de clôture des facteurs diffèrent légèrement (VIX, taux, actions) : léger décalage possible.
- Frais comptés à chaque ordre (0,05 % aller-retour, sans économie quand la position se poursuit dans le même sens) : estimation prudente. Pas de financement de nuit ni d'écart de prix réel de courtier.
- Règles figées : 16 facteurs, 2 modèles, seuil 55 % / 45 %, entrée à la clôture, sortie à la clôture suivante. Aucun réglage après coup. Deux modèles testés : seuil de 2,5 % au lieu de 5 % pour parler d'avantage probable.
- Un signal quotidien n'est pas un trade « fiable » : même un bon modèle se trompe souvent. L'AUC proche de 0,5 signifie qu'il ne fait pas mieux que le hasard.
- Mauvaise nouvelle fréquente : la précision d'un modèle journalier sur l'or dépasse rarement 52 %. Elle ne couvre alors pas les frais.
