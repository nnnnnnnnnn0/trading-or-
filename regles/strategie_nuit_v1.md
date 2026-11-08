# Stratégie « Nuit or » v1 : règles figées avant le test (7-8 nov 2026)

Origine : l'hypothèse H1 du backtest Régime or v1 (l'or monte surtout hors séance américaine, 13 h à 21 h UTC), confirmée sur 2012-2026 **sans frais**. Question posée ici : reste-t-il un gain **après frais** ?

## Règles (aucun paramètre ajusté après le test)
1. Chaque jour de bourse : **achat à l'ouverture de la barre 5 min de 21 h 00 UTC**, **vente à l'ouverture de la barre de 13 h 00 UTC du jour de bourse suivant** (le vendredi, la position est tenue jusqu'au lundi). Exposition 1 fois le capital, pas de levier, pas de vente à découvert, aucun stop, aucun filtre.
2. Données : or au comptant XAUUSD, 5 min (Dukascopy), 2012 à 2026. Un jour sans prix aux deux heures est ignoré.
3. Frais : variante **A** = 0,05 % par aller-retour + 0,015 % par nuit calendaire tenue (mêmes hypothèses que le module quotidien). Variante **B** (sensibilité, frais réduits de moitié) = 0,025 % par aller-retour + 0,0075 % par nuit.
4. Deux variantes seulement. Le Deflated Sharpe est calculé avec 2 essais, et aussi avec 250 par honnêteté.

## Critères de réussite (tous exigés, sur la variante A)
- Rendement net moyen par trade > 0 **et** t de Newey-West ≥ 2 en développement (60 % premiers jours) **et** en contrôle (40 % derniers).
- Positif dans au moins 3 des 4 blocs égaux, et dans au moins 70 % des années.
- Deflated Sharpe ≥ 0,95 avec 2 essais.
- Si la stratégie échoue, on le publie tel quel. La variante B sert à savoir quel niveau de frais serait nécessaire, pas à remplacer A.
