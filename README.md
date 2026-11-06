# trading-or : paper trading sur l'or

Projet de test de stratégies sur l'or, **en ordres fictifs, sans argent réel**. Ce n'est ni un conseil en investissement ni une prévision : un résultat fictif surestime presque toujours le réel (pas de peur, pas de glissement de prix). Un bon backtest ne prouve rien sur l'avenir.

## Organisation
| Dossier | Contenu |
| --- | --- |
| `regles/` | règles figées (`strategies_or.md`), idées en attente, idée de portefeuille (`portefeuille.md`) |
| `scripts/donnees/` | téléchargements : `fetch_or.py` (Alpha Vantage), `fetch_ohlc.py` (GC=F jour / 1 h / 5 min), `fetch_facteurs.py` (dollar, taux, argent, VIX, S&P, pétrole, calendrier), `fetch_histo.py` (historique 5 min de l'or au comptant, Dukascopy) |
| `scripts/quotidien/` | ce qui tourne chaque jour : `signaux_or.py` (signaux, rapport), `modele_facteurs.py` (probabilité du lendemain, journal de prédictions) |
| `scripts/backtests/` | recherches et backtests : règles figées, multi-échelles, indicateurs, Ichimoku, intraday, récurrences |
| `data/` | données téléchargées (CSV) ; `data/histo/` = historique 5 min compressé par année |
| `resultats/` | rapports des backtests (un fichier par étude) |
| `rapports/` | rapport quotidien des signaux |
| `journal/` | ordres fictifs (`journal_or.csv`), leçons (`lecons.csv`), prédictions du modèle (`predictions_modele.csv`) |
| `tests/` | tests sur des données inventées |
| `.github/workflows/bilan_or.yml` | automatisation (voir ci-dessous) |

## Automatisation (GitHub Actions, workflow « Bilan or »)
- **Chaque jour ouvré à 6 h 30 UTC** et à chaque modification du code : tests, téléchargement des données, signaux du jour, prédiction du modèle, enregistrement.
- **Historique 5 min** : un second travail télécharge Dukascopy par lots de 50 minutes et **se relance tout seul** tant qu'il reste des jours à télécharger (`data/histo/reste.txt`). Une journée qui échoue 8 fois est abandonnée. État lisible dans `data/histo/statut.txt`.
- Lancement manuel : onglet Actions, « Bilan or », « Run workflow » (mode `histo` pour le seul téléchargement).

## Mise en route
1. Dépôt **privé**. Clé Alpha Vantage : `Settings > Secrets and variables > Actions`, nom `ALPHAVANTAGE_API_KEY`. Ne l'écris jamais dans un fichier.
2. Onglet Actions : active les workflows si GitHub le demande.

## Limites connues
- Données gratuites non officielles (Yahoo, Dukascopy, flux de calendrier) : elles peuvent changer ou tomber en panne.
- Futures GC=F et or au comptant (XAUUSD) diffèrent légèrement.
- Le calendrier des annonces n'existe que depuis novembre 2026.
