# Autres marchés pour prévoir l'or : résultats

Règles : `regles/marches_croises_v1.md`, figées avant le test, lancées **une seule fois**. Or GC=F du 2006-06-01 au 2026-11-06 ; développement jusqu'à fin 2015, validation depuis 2016. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

Signal avec les clôtures de la séance t ; ordre sur l'or à l'ouverture de t+1, sortie à sa clôture. Frais 0,02 % l'aller-retour (stress 0,05 %), 1 fois le capital. « Après impôts » = 31,4 % des plus-values nettes annuelles, moins-values reportées.

Référence **garder l'or** (20,4 ans) : 9,6 % par an avant impôts, 7,9 % par an après impôts (vente à la fin).

| N° | Règle | Ordres | Par semaine | Gagnants | Brut moyen | Net moyen | Net stress | t | Dév. jusqu'à 2015 (net / t) | Valid. depuis 2016 (net / t) | Années positives | Deflated Sharpe (12 / 340 essais) | Rdt annuel avant / après impôts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | Mineurs d'or devant l'or | 5135 | 4,8 | 46 % | 0,044 % | 0,024 % | -0,006 % | 1,7 | 0,053 % / 2,5 | -0,003 % / -0,1 | 57 % | 0,50 / 0,10 | 4,8 % / 2,9 % |
| 6 | Rapport or/argent 5 jours | 5132 | 4,8 | 46 % | 0,025 % | 0,005 % | -0,025 % | 0,3 | 0,004 % / 0,2 | 0,005 % / 0,3 | 52 % | 0,09 / 0,00 | -0,2 % / -0,7 % |
| 10 | Obligations TLT | 5113 | 4,8 | 44 % | 0,011 % | -0,009 % | -0,039 % | -0,6 | 0,014 % / 0,7 | -0,030 % / -1,5 | 43 % | 0,01 / 0,00 | -3,5 % / -3,9 % |
| 4 | Taux réels (variation du jour) | 4631 | 4,3 | 45 % | 0,009 % | -0,011 % | -0,041 % | -0,7 | 0,005 % / 0,2 | -0,025 % / -1,2 | 43 % | 0,01 / 0,00 | -3,6 % / -4,0 % |
| 0 | Témoin hasard | 5141 | 4,8 | 44 % | 0,008 % | -0,012 % | -0,042 % | -0,9 | -0,034 % / -1,6 | 0,007 % / 0,4 | 29 % | 0,01 / 0,00 | -4,3 % / -4,5 % |
| 3 | Rendement 10 ans | 5055 | 4,7 | 44 % | 0,004 % | -0,016 % | -0,046 % | -1,1 | 0,012 % / 0,6 | -0,041 % / -2,1 | 33 % | 0,00 / 0,00 | -5,1 % / -5,5 % |
| 2 | Dollar 5 jours | 5111 | 4,8 | 44 % | 0,002 % | -0,018 % | -0,048 % | -1,2 | -0,002 % / -0,1 | -0,033 % / -1,7 | 33 % | 0,00 / 0,00 | -5,7 % / -6,0 % |
| 1 | Dollar du jour | 5081 | 4,8 | 44 % | -0,009 % | -0,029 % | -0,059 % | -2,0 | -0,005 % / -0,2 | -0,050 % / -2,8 | 48 % | 0,00 / 0,00 | -8,1 % / -8,8 % |
| 8 | Actions (valeur refuge) | 5134 | 4,8 | 44 % | -0,009 % | -0,029 % | -0,059 % | -2,0 | -0,031 % / -1,5 | -0,027 % / -1,3 | 38 % | 0,00 / 0,00 | -8,3 % / -8,3 % |
| 11 | Cuivre et pétrole | 5138 | 4,8 | 44 % | -0,019 % | -0,039 % | -0,069 % | -2,7 | -0,042 % / -1,9 | -0,036 % / -1,9 | 29 % | 0,00 / 0,00 | -10,5 % / -10,8 % |
| 5 | Argent | 5129 | 4,8 | 43 % | -0,026 % | -0,046 % | -0,076 % | -3,2 | -0,042 % / -2,1 | -0,049 % / -2,5 | 24 % | 0,00 / 0,00 | -12,0 % / -12,3 % |
| 12 | Score composé (≥ 3 sur 4) | 1656 | 1,6 | 42 % | -0,032 % | -0,052 % | -0,082 % | -2,1 | -0,001 % / -0,0 | -0,087 % / -2,8 | 33 % | 0,00 / 0,00 | -4,5 % / -4,8 % |
| 9 | VIX (±5 %) | 2053 | 1,9 | 43 % | -0,040 % | -0,060 % | -0,090 % | -2,6 | -0,081 % / -2,2 | -0,042 % / -1,4 | 33 % | 0,00 / 0,00 | -6,4 % / -6,4 % |

### Verdict

**Aucune des 12 règles ne remplit tous les critères.**

- Gain net moyen positif : 2 règles sur 12 ; avec t ≥ 2 sur toute la période : 0 ; positives avec t ≥ 2 à la fois en développement et en validation : 0. Gain brut (avant frais) positif : 6.
- Avec 12 essais, environ 0,5 règle atteint t ≥ 2 par pur hasard.

Critères non remplis (les 6 meilleures par gain net moyen) :

- Mineurs d'or devant l'or : validation, années positives, Deflated Sharpe.
- Rapport or/argent 5 jours : développement, validation, années positives, Deflated Sharpe, après impôts.
- Obligations TLT : développement, validation, années positives, Deflated Sharpe, après impôts.
- Taux réels (variation du jour) : développement, validation, années positives, Deflated Sharpe, après impôts.
- Rendement 10 ans : développement, validation, années positives, Deflated Sharpe, après impôts.
- Dollar 5 jours : développement, validation, années positives, Deflated Sharpe, après impôts.

## Limites

- Données Yahoo gratuites (clôtures et ouvertures de futures à heures non parfaitement alignées : l'ouverture de t+1 est supposée après les clôtures de t). Frais et impôts estimés ; pas de glissement.
- Impôts : hypothèse du prélèvement forfaitaire unique français de 31,4 % ; pas un conseil fiscal.
- Environ 340 essais dans ce projet ; le Deflated Sharpe à 340 essais est donné par honnêteté.
