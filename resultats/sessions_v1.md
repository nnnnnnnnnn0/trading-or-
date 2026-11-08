# 24 stratégies « sessions » sur 14 ans : résultats

Règles : `regles/sessions_5m_v1.md`, figées avant le test, lancées **une seule fois**. Or au comptant 5 min du 2012-01-02 au 2026-11-06 ; développement 2012-2019, validation 2020-2026. **Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**

Un trade par jour au plus par stratégie. Frais de base 0,02 % l'aller-retour (stress 0,05 %). Rendements par trade en %, pour 1 fois le capital. « Après impôts » = 31,4 % des plus-values nettes annuelles, moins-values reportées.

Référence **garder l'or** (07:00 UTC, de 2012-01-02 à 2026-11-06) : 6,6 % par an avant impôts, 5,1 % par an après impôts (vente à la fin).

| N° | Stratégie | Ordres | Par semaine | Gagnants | Brut moyen | Net moyen | Net stress | t | Dév. 2012-2019 (net / t) | Valid. 2020-2026 (net / t) | Années positives | Deflated Sharpe (24 / 330 essais) | Rdt annuel avant / après impôts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9 | Tendance 5 j suivie | 3817 | 4,9 | 51 % | 0,024 % | 0,004 % | -0,026 % | 0,3 | 0,012 % / 0,7 | -0,005 % / -0,3 | 47 % | 0,05 / 0,00 | 0,2 % / -0,6 % |
| 19 | Clôture veille haut/bas suivie | 1501 | 1,9 | 48 % | 0,024 % | 0,004 % | -0,026 % | 0,2 | 0,011 % / 0,4 | -0,004 % / -0,1 | 53 % | 0,03 / 0,00 | 0,0 % / -0,5 % |
| 24 | Asie suivie si tendance 20 j d'accord | 1912 | 2,5 | 48 % | 0,017 % | -0,003 % | -0,033 % | -0,3 | -0,008 % / -0,5 | 0,002 % / 0,1 | 47 % | 0,01 / 0,00 | -0,6 % / -0,7 % |
| 11 | Tendance 20 j suivie | 3814 | 4,9 | 51 % | 0,016 % | -0,004 % | -0,034 % | -0,3 | 0,015 % / 0,9 | -0,026 % / -1,4 | 40 % | 0,01 / 0,00 | -1,8 % / -2,6 % |
| 7 | Veille suivie | 3818 | 4,9 | 48 % | 0,016 % | -0,004 % | -0,034 % | -0,3 | -0,019 % / -1,2 | 0,013 % / 0,7 | 53 % | 0,01 / 0,00 | -1,9 % / -1,9 % |
| 17 | Asie + Londres alignées | 1837 | 2,4 | 48 % | 0,015 % | -0,005 % | -0,035 % | -0,3 | -0,019 % / -1,2 | 0,011 % / 0,5 | 53 % | 0,01 / 0,00 | -0,8 % / -0,8 % |
| 15 | 1re heure New York suivie | 3814 | 4,9 | 46 % | 0,014 % | -0,006 % | -0,036 % | -0,7 | -0,000 % / -0,0 | -0,012 % / -1,0 | 47 % | 0,00 / 0,00 | -1,7 % / -1,8 % |
| 3 | Londres suivie | 3816 | 4,9 | 48 % | 0,012 % | -0,008 % | -0,038 % | -0,8 | -0,012 % / -1,0 | -0,004 % / -0,2 | 33 % | 0,00 / 0,00 | -2,5 % / -2,5 % |
| 5 | New York matin suivi | 3817 | 4,9 | 45 % | 0,012 % | -0,008 % | -0,038 % | -1,2 | -0,004 % / -0,4 | -0,013 % / -1,3 | 33 % | 0,00 / 0,00 | -2,3 % / -2,4 % |
| 18 | Londres renverse l'Asie | 1978 | 2,6 | 48 % | 0,009 % | -0,011 % | -0,041 % | -0,8 | -0,005 % / -0,3 | -0,019 % / -0,8 | 53 % | 0,00 / 0,00 | -1,7 % / -1,8 % |
| 13 | 1re heure Londres suivie | 3811 | 4,9 | 47 % | 0,005 % | -0,015 % | -0,045 % | -1,9 | -0,009 % / -0,9 | -0,022 % / -1,8 | 20 % | 0,00 / 0,00 | -4,1 % / -4,3 % |
| 1 | Asie suivie | 3817 | 4,9 | 46 % | 0,002 % | -0,018 % | -0,048 % | -2,2 | -0,034 % / -3,3 | 0,002 % / 0,1 | 33 % | 0,00 / 0,00 | -4,8 % / -4,8 % |
| 2 | Asie inversée | 3817 | 4,9 | 49 % | 0,002 % | -0,018 % | -0,048 % | -2,2 | -0,002 % / -0,2 | -0,037 % / -3,0 | 33 % | 0,00 / 0,00 | -4,9 % / -4,9 % |
| 21 | Fin de New York suivie | 3733 | 4,8 | 42 % | -0,000 % | -0,020 % | -0,050 % | -4,6 | -0,025 % / -4,6 | -0,015 % / -2,1 | 7 % | 0,00 / 0,00 | -5,0 % / -5,0 % |
| 22 | Fin de New York inversée | 3733 | 4,8 | 46 % | -0,000 % | -0,020 % | -0,050 % | -4,7 | -0,016 % / -2,9 | -0,025 % / -3,6 | 0 % | 0,00 / 0,00 | -5,0 % / -5,0 % |
| 23 | Londres suivie si tendance 20 j d'accord | 1945 | 2,5 | 49 % | -0,001 % | -0,021 % | -0,051 % | -1,6 | -0,012 % / -0,7 | -0,031 % / -1,5 | 33 % | 0,00 / 0,00 | -2,9 % / -2,9 % |
| 8 | Veille inversée | 3818 | 4,9 | 49 % | -0,001 % | -0,021 % | -0,051 % | -1,7 | -0,008 % / -0,5 | -0,036 % / -2,0 | 33 % | 0,00 / 0,00 | -6,1 % / -6,5 % |
| 12 | Tendance 20 j inversée | 3814 | 4,9 | 47 % | -0,001 % | -0,021 % | -0,051 % | -1,7 | -0,043 % / -2,7 | 0,003 % / 0,1 | 27 % | 0,00 / 0,00 | -6,2 % / -6,2 % |
| 14 | 1re heure Londres inversée | 3811 | 4,9 | 48 % | -0,004 % | -0,024 % | -0,054 % | -3,1 | -0,030 % / -3,0 | -0,018 % / -1,4 | 20 % | 0,00 / 0,00 | -6,3 % / -6,3 % |
| 20 | Clôture veille haut/bas inversée | 1501 | 1,9 | 49 % | -0,005 % | -0,025 % | -0,055 % | -1,2 | -0,022 % / -0,9 | -0,027 % / -0,8 | 33 % | 0,00 / 0,00 | -2,8 % / -2,9 % |
| 4 | Londres inversée | 3816 | 4,9 | 48 % | -0,006 % | -0,026 % | -0,056 % | -2,8 | -0,022 % / -1,9 | -0,031 % / -2,1 | 13 % | 0,00 / 0,00 | -6,9 % / -7,0 % |
| 10 | Tendance 5 j inversée | 3817 | 4,9 | 46 % | -0,009 % | -0,029 % | -0,059 % | -2,3 | -0,039 % / -2,4 | -0,018 % / -0,9 | 27 % | 0,00 / 0,00 | -8,0 % / -8,1 % |
| 6 | New York matin inversé | 3817 | 4,9 | 47 % | -0,011 % | -0,031 % | -0,061 % | -4,5 | -0,033 % / -3,8 | -0,028 % / -2,6 | 0 % | 0,00 / 0,00 | -7,8 % / -7,8 % |
| 16 | 1re heure New York inversée | 3814 | 4,9 | 48 % | -0,011 % | -0,031 % | -0,061 % | -3,9 | -0,036 % / -3,9 | -0,026 % / -1,9 | 7 % | 0,00 / 0,00 | -8,0 % / -8,0 % |
| 0 | Témoin hasard (Londres → New York) | 3817 | 4,9 | 47 % | -0,017 % | -0,037 % | -0,067 % | -3,9 | -0,020 % / -1,7 | -0,056 % / -3,7 | 20 % | 0,00 / 0,00 | -9,4 % / -9,4 % |

### Verdict

**Aucune des 24 stratégies ne remplit tous les critères.**

- Gain net moyen positif : 2 stratégies sur 24 ; avec t ≥ 2 sur toute la période : 0 ; positives avec t ≥ 2 à la fois en développement et en validation : 0.
- Avec 24 essais, environ 1 stratégie atteint t ≥ 2 par pur hasard ; le témoin hasard donne un gain net moyen de -0,037 %.

Critères non remplis, stratégie par stratégie (les 8 meilleures par gain net moyen) :

- Tendance 5 j suivie : développement, validation, années positives, Deflated Sharpe, après impôts.
- Clôture veille haut/bas suivie : développement, validation, années positives, fréquence, Deflated Sharpe, après impôts.
- Asie suivie si tendance 20 j d'accord : développement, validation, années positives, Deflated Sharpe, après impôts.
- Tendance 20 j suivie : développement, validation, années positives, Deflated Sharpe, après impôts.
- Veille suivie : développement, validation, années positives, Deflated Sharpe, après impôts.
- Asie + Londres alignées : développement, validation, années positives, Deflated Sharpe, après impôts.
- 1re heure New York suivie : développement, validation, années positives, Deflated Sharpe, après impôts.
- Londres suivie : développement, validation, années positives, Deflated Sharpe, après impôts.

## Limites

- Heures UTC fixes : l'heure d'été décale les ouvertures de Londres et de New York d'une heure, ce qui brouille les fenêtres. Ouvertures de barres 5 min, pas de glissement ; frais estimés.
- Impôts : hypothèse du prélèvement forfaitaire unique français de 31,4 % sur les plus-values de titres ; l'or physique, les CFD sur certains régimes ou un autre pays donnent d'autres résultats. Ce n'est pas un conseil fiscal.
- Environ 330 essais ont été faits dans ce projet ; le Deflated Sharpe à 330 essais est donné par honnêteté.
