# Règles « achat seulement » sur l'or après impôts : résultats

Règles : `regles/apres_impots_v1.md`, figées avant le test, lancées une seule fois. Or journalier (GC=F) du 2012-01-03 au 2026-11-06 (3734 séances, 14,8 ans). **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

Hypothèses : frais 0,05 %% l'aller-retour + 0,15 %% par an de détention ; impôt 31,4 %% des plus-values nettes de l'année (taux 2026 du prélèvement forfaitaire en France, moins-values reportées, position ouverte vendue à la fin) ; décision aux clôtures, exécution à la clôture suivante. Pas un conseil fiscal.

| Règle | Jours investis | Entrées par an | Rendement annuel avant impôts | Après impôts 31,4 % | Après impôts 45 % | Valeur finale après impôts (1 = capital) | Perte max (avant impôts) | Après impôts par bloc (4 blocs) | Hasard | Deflated Sharpe (4 / 340 essais) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R  Garder l'or | 100 % | 0 | 6,3 % | 4,9 % | 4,1 % | 2,02 | -42 % | -9 % / 3 % / 6 % / 18 % | — | — |
| A  Tendance 200 jours | 57 % | 2,2 | 4,1 % | 3,0 % | 2,5 % | 1,55 | -32 % | -7 % / -1 % / 3 % / 17 % | 33 % | 0,64 / 0,07 |
| B  Momentum 12 mois | 56 % | 0,6 | 5,3 % | 3,9 % | 3,2 % | 1,76 | -27 % | -2 % / -2 % / 4 % / 15 % | 16 % | 0,75 / 0,12 |
| C  Tendance + macro | 44 % | 2,7 | 1,6 % | 0,7 % | 0,4 % | 1,12 | -31 % | -7 % / -1 % / 3 % / 6 % | 66 % | 0,38 / 0,02 |
| D  Tendance 200 j + sortie de sécurité | 57 % | 2,4 | 4,2 % | 3,1 % | 2,6 % | 1,58 | -32 % | -7 % / -1 % / 3 % / 17 % | 28 % | 0,66 / 0,07 |

Blocs égaux de 3,7 ans environ ; « hasard » = part de 1 000 décalages aléatoires des mêmes expositions qui rapportent au moins autant.

### Verdict

**Aucune règle ne remplit tous les critères.**
- A  Tendance 200 jours : critères non remplis : rendement après impôts positif sur la période et dans 3 blocs sur 4 ; au moins 70 % du rendement de garder l'or avec une perte max réduite à 60 % ; pas meilleure que le hasard ; Deflated Sharpe.
- B  Momentum 12 mois : critères non remplis : rendement après impôts positif sur la période et dans 3 blocs sur 4 ; au moins 70 % du rendement de garder l'or avec une perte max réduite à 60 % ; pas meilleure que le hasard ; Deflated Sharpe.
- C  Tendance + macro : critères non remplis : rendement après impôts positif sur la période et dans 3 blocs sur 4 ; au moins 70 % du rendement de garder l'or avec une perte max réduite à 60 % ; pas meilleure que le hasard ; Deflated Sharpe.
- D  Tendance 200 j + sortie de sécurité : critères non remplis : rendement après impôts positif sur la période et dans 3 blocs sur 4 ; au moins 70 % du rendement de garder l'or avec une perte max réduite à 60 % ; pas meilleure que le hasard ; Deflated Sharpe.

## Limites

- La période 2012-2026 contient une forte hausse de l'or (surtout 2019-2026) : « garder l'or » en profite pleinement, et toute règle qui le quitte la subit. Ce n'est pas une prévision.
- Futures GC=F, séance du jour ; exécution aux clôtures sans glissement ; frais et impôts estimés (moins-values reportées sans limite de durée, ce qui est une simplification).
- Environ 340 essais ont été faits dans ce projet ; le Deflated Sharpe à 340 essais est donné par honnêteté.
