# trading-or : paper trading sur l'or

Projet de test de stratégies sur l'or, **en ordres fictifs, sans argent réel**. Ce n'est ni un conseil en investissement ni une prévision : un résultat fictif surestime presque toujours le réel (pas de peur, pas de glissement de prix).

## Contenu
- `regles/` : les règles figées et la liste d'idées en attente.
- `scripts/fetch_or.py` : télécharge l'historique quotidien de l'or (Alpha Vantage).
- `scripts/signaux_or.py` : calcule les signaux de niveau A et écrit un rapport dans `rapports/`.
- `tests/` : tests du code sur des données inventées (pas de vraies données).
- `journal/` : journal des ordres et leçons (fichiers CSV à remplir).
- `data/annonces.csv` : journal des annonces macro.
- `.github/workflows/bilan_or.yml` : lance tout cela chaque jour ouvré (et à la demande).

## Mise en route
1. Crée un dépôt **privé** sur GitHub et envoie-y ces fichiers.
2. Ajoute ta clé Alpha Vantage comme secret : `Settings > Secrets and variables > Actions > New repository secret`, nom `ALPHAVANTAGE_API_KEY`. Ne l'écris jamais dans un fichier.
3. Onglet `Actions` : active les workflows si GitHub le demande, puis lance « Bilan or » avec `Run workflow`.
4. Le rapport apparaît dans `rapports/AAAA-MM-JJ.md`. Donne-le à Claude pour l'interprétation (actualité, calendrier macro, scénario).

## Points non vérifiés
- Le workflow et la récupération des données n'ont pas pu être testés de bout en bout avant livraison : les tests unitaires portent sur le calcul, pas sur le réseau. Le premier lancement manuel dira si tout passe.
- Le format de réponse d'Alpha Vantage est celui observé via le connecteur ; l'appel direct est présumé identique.
- Les week-ends sont retirés de l'historique par hypothèse.
- Les limites du plan gratuit de GitHub Actions et de la clé gratuite Alpha Vantage (25 requêtes par jour) sont à vérifier.
