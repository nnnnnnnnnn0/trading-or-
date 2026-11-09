# Autres marchés pour prévoir l'or : 12 règles quotidiennes, règles figées (9 nov 2026)

Question : les mouvements d'autres marchés (dollar, taux, argent, mineurs d'or, actions, obligations, cuivre et pétrole) **à la clôture américaine** prévoient-ils le rendement de l'or le lendemain ? 12 règles, fixées avant le test, lancées **une seule fois**, chacune dans le **sens économique prévu** (sans tester le sens contraire, pour ne pas doubler les essais). Un trade par jour au plus, 2 à 5 ordres par semaine.

## Données
Yahoo, journalier : or GC=F (ouverture et clôture), argent SI=F, mineurs d'or GDX, S&P 500 ^GSPC, VIX ^VIX, rendement du Trésor 10 ans ^TNX, obligations longues TLT, cuivre HG=F, pétrole CL=F, dollar DX-Y.NYB (déjà dans le dépôt), taux réels 10 ans US Treasury (déjà dans le dépôt). Période : début des données communes (2006) à la dernière séance ; **développement : jusqu'au 31 déc. 2015 ; validation : à partir du 1er janv. 2016**.

## Exécution (commune)
Signal calculé avec les clôtures de la séance t (toutes avant 23:00 UTC). **Achat ou vente de l'or à l'ouverture de la séance suivante t+1, sortie à sa clôture.** Frais de base 0,02 % l'aller-retour (stress 0,05 %). Sans levier, 1 fois le capital. Un jour sans signal : pas d'ordre.

## Les 12 règles (sens économique)
1. **Dollar du jour** : DXY en hausse → vente de l'or ; en baisse → achat.
2. **Dollar 5 jours** : même règle avec la variation sur 5 séances.
3. **Rendement 10 ans** : ^TNX en hausse → vente ; en baisse → achat.
4. **Taux réels** : variation du jour du taux réel 10 ans en hausse → vente ; en baisse → achat.
5. **Argent** : SI=F en hausse → achat ; en baisse → vente.
6. **Rapport or / argent sur 5 jours** : en baisse (l'argent fait mieux) → achat ; en hausse → vente.
7. **Mineurs d'or devant l'or** : (rendement GDX − rendement or) du jour > 0 → achat ; < 0 → vente.
8. **Actions** : S&P 500 en baisse → achat ; en hausse → vente (valeur refuge).
9. **VIX** : hausse de plus de 5 % → achat ; baisse de plus de 5 % → vente ; sinon rien.
10. **Obligations** : TLT en hausse → achat ; en baisse → vente.
11. **Cuivre et pétrole** : moyenne des rendements HG=F et CL=F > 0 → achat ; < 0 → vente.
12. **Score composé** : somme des signes (−DXY, −^TNX, +TLT, +SI=F) ≥ 3 → achat ; ≤ −3 → vente ; sinon rien.

## Critères pour dire « profitable » (tous exigés, pour une règle)
1. Gain net moyen par trade > 0 avec t (Newey-West) ≥ 2 en développement **et** en validation.
2. Au moins 60 % d'années positives ; au moins 2 ordres par semaine.
3. Deflated Sharpe ≥ 0,95 avec 12 essais (aussi donné avec 340 essais).
4. Rendement annuel après impôts (31,4 % des plus-values nettes annuelles, moins-values reportées) > 0.

Si aucune ne passe, on le publie tel quel. Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
