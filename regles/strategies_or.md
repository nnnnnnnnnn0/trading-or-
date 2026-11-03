# Règles figées : version 1 (3 novembre 2026)

Ces règles ne changent pas pendant les 6 premières semaines de test.
Toute idée nouvelle va dans `idees_en_attente.md` et repart avec un nouveau compteur d'ordres.
Un changement de règle se fait par un commit séparé qui explique pourquoi.

## Cadre
- Marché : or en dollars (XAU/USD), un seul instrument.
- Capital fictif 10 000 EUR, risque 1 % par ordre : quantité = (capital × 1 %) / |entrée − stop|.
- Horizon swing (2 à 10 jours). Données de clôture quotidienne, entrée à l'ouverture suivante.
- Maximum 2 ordres ouverts en même temps (tous corrélés). Aucun nouvel ordre après une perte de 2 % dans la journée.
- Perte de 5 % sur une semaine : pause et relecture du journal. Perte de 10 % depuis le plus haut : arrêt et revue complète.
- Jours d'annonce majeure : taille de position réduite de moitié.

## Niveau A (compte dans le classement) et niveau B (exploratoire, jamais compté)
Seul un signal produit par une règle ci-dessous est de niveau A. Le reste est de niveau B.

## Les quatre règles
1. **Repli dans la tendance** : moyenne 20 jours au-dessus de la 50 jours, première clôture sous la 20 jours : achat. Stop 2 × volatilité(14). Sortie : clôture sous la moyenne 50 jours, ou objectif 3R.
2. **Cassure de 20 jours** : clôture au-dessus du plus haut (ou sous le plus bas) des 20 clôtures précédentes. Stop : plus bas (ou plus haut) des 10 dernières clôtures, suiveur.
3. **Compression puis cassure** : largeur des bandes de Bollinger (20 jours, 2 écarts-types) au plus bas de 6 mois dans les 5 derniers jours, puis clôture hors des bandes. Stop : bande opposée. Objectif 2R, 10 jours maximum.
4. **Suite d'un événement macro** (manuelle) : après CPI, emploi ou Fed, si la clôture du jour est dans le quart haut ou bas de la séance, ordre dans ce sens le lendemain. Stop : extrême de la séance de l'annonce. Sortie après 3 jours.

## Témoin
Chaque règle est comparée à des entrées au hasard avec le même stop. Une règle qui ne bat pas le hasard après frais est abandonnée.

## Limite des données
Le script utilise des clôtures seulement : la volatilité est approchée (clôture à clôture) et la règle 4 ne peut pas être calculée automatiquement.
