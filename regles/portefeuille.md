# Gestion de portefeuille inspirée de Markowitz (proposition, pas encore active)

Idée de la fiche reçue (Markowitz) : ne pas juger un placement seul, mais selon la façon dont il se comporte avec les autres. Combiner des éléments qui ne bougent pas ensemble réduit le risque sans réduire forcément le rendement.

## Ce que les données confirment (2006 à 2026, rendements journaliers)
- Or / S&P 500 : +0,04 (quasi nulle, mais instable : de −0,33 à +0,43 selon les années).
- Or / dollar : −0,38 (stable). Or / taux 10 ans : −0,17.
- Or / argent : +0,79 (presque le même pari).
- L'or est donc un bon diversifiant d'un portefeuille d'actions, mais **notre projet ne trade que l'or** : la diversification entre actifs ne s'applique pas ici.

## Où l'idée s'applique à notre projet (à tester, règles actuelles inchangées)
1. **Entre les règles.** Quand au moins 2 règles auront un avantage démontré, mesurer la corrélation de leurs résultats quotidiens. Deux règles très corrélées = un seul pari (elles partagent un seul budget de risque).
2. **Pondération par le risque** (et non par le rendement espéré) : donner à chaque règle une taille inversement proportionnelle à sa volatilité de résultats. On évite la méthode de Markowitz classique, qui exige des rendements espérés et se montre très instable quand ils sont mal estimés.
3. **Limite de risque commune.** Deux ordres dans le même sens = un seul gros pari (déjà dans les règles : 2 ordres ouverts maximum, 1 % de risque chacun). Ajouter : risque total ouvert ≤ 2 % du capital.
4. **Facteurs.** Le dollar et les taux (corrélations stables avec l'or) restent des variables du modèle multi-facteurs ; l'argent ne l'est pas (redondant).

## Avertissements
- Cette théorie suppose que les rendements espérés et les corrélations restent stables : ce n'est pas le cas (voir l'instabilité Or / S&P).
- Aucune règle n'a encore d'avantage démontré : il n'y a rien à pondérer pour l'instant.
- Contenu pédagogique, pas un conseil financier.
