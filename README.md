# trading-or : stratégies sur l'or, testées sur le maximum de données et en paper trading quotidien

**Paper trading uniquement, aucun argent réel. Ce dépôt n'est ni un conseil en investissement ni une prévision.** Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.

Le dépôt contient ce qu'il faut pour récupérer les données, tester des stratégies aux règles figées avant tout test (jamais ajustées après coup) et suivre un **paper trading quotidien sur graphique 5 min** (28 stratégies + un témoin hasard).

## Organisation
| Chemin | Contenu |
| --- | --- |
| `regles/` | règles figées : `strategie_regime_v1.md`, `strategie_nuit_v1.md`, `strategie_compression_v1.md`, `sessions_5m_v1.md` (24 stratégies par session), `apres_impots_v1.md` (achat seulement après impôts), `marches_croises_v1.md` (12 règles sur d'autres marchés) et `papier_5m_v1.md` (les 28 stratégies du paper trading) |
| `scripts/donnees/fetch_jour.py` | or (GC=F), dollar (DXY), argent, mineurs d'or (GDX), S&P 500, VIX, taux 10 ans, TLT, cuivre et pétrole via Yahoo, taux réels américains 10 ans via US Treasury → `data/*.csv` |
| `scripts/donnees/fetch_histo.py` | or au comptant XAUUSD, minutes Dukascopy agrégées en 5 min, par lots → `data/histo/xauusd_5m_AAAA.csv.gz` (reprend là où il s'est arrêté ; état dans `data/histo/statut.txt`, jours restants dans `reste.txt`) |
| `scripts/backtests/` | backtests : `backtest_regime.py` (régime journalier, hypothèse H1), `backtest_nuit.py`, `backtest_compression.py`, `backtest_sessions.py`, `backtest_apres_impots.py`, `backtest_marches.py`, `analyse_gagnants.py` (recherche de conditions avec contrôle et test de permutation) |
| `scripts/papier/` | paper trading 5 min : `indicateurs.py`, `strategies.py` (28 stratégies + témoin), `moteur.py` (ordres, journal, classement) |
| `journal/` | **le paper trading** : `ordres.csv` (tous les ordres), `jours/AAAA-MM-JJ.md` (ordres du jour en heure de Paris, gagné / perdu), `classement.md` (cumul par stratégie) |
| `tests/` | tests sur données inventées, sans réseau |
| `resultats/` | rapports : `regime_v1.md`, `nuit_v1.md`, `compression_v1.md`, `sessions_v1.md`, `apres_impots_v1.md`, `marches_croises_v1.md`, `analyse_gagnants.md`, `papier_histo.md` (les 28 stratégies rejouées une fois sur 14 ans) |
| `.github/workflows/` | `donnees.yml` (téléchargement des données) et `papier.yml` (paper trading, se lance après chaque téléchargement) |

## Utilisation
```
python -m unittest discover -s tests          # tests
python scripts/backtests/backtest_regime.py   # rapport complet -> resultats/regime_v1.md
python scripts/backtests/backtest_regime.py --signal   # position conseillée à la dernière clôture (fictive)
python scripts/papier/moteur.py               # paper trading : recalcule journal/ (départ le 9 nov 2026)
```
Il faut `pandas` et `numpy`. Le backtest utilise les données déjà présentes dans `data/` : le réseau n'est pas nécessaire.

## Téléchargement automatique (GitHub Actions, workflow « Données »)
- Du lundi au samedi à 6 h 30 UTC et à chaque modification de `scripts/donnees/` : données quotidiennes (travail `jour`) et historique 5 min (travail `histo`). Le workflow « Paper trading 5 min » se lance ensuite et met `journal/` à jour avec les ordres de la veille (le paper trading est donc **différé d'un jour**).
- Le travail `histo` télécharge par lots de 20 minutes et **se relance tout seul** tant qu'il reste des jours (`data/histo/reste.txt`). Un jour qui échoue 15 fois est abandonné et noté dans `data/histo/echecs.json`.
- Lancement manuel : onglet Actions, « Données », « Run workflow » (mode `tout`, `jour` ou `histo`).
- **Minutes gratuites : 2 000 par mois pour un dépôt privé, illimitées pour un dépôt public.** Privé et minutes épuisées : tous les lancements échouent en 2 secondes.
- Dépôt public : le contenu (code, données, résultats) est lisible par tous. Aucune clé ni mot de passe n'est nécessaire ni ne doit être écrit dans ce dépôt. Les données viennent de sources gratuites (Yahoo, Dukascopy, US Treasury) dont les conditions d'usage peuvent limiter leur redistribution.

## Ce que les études précédentes ont montré (supprimées du dépôt, récupérables dans l'historique git, par exemple le commit `0c9719b`)
Aucun avantage durable n'a été trouvé : 4 règles figées, stratégie multi-échelles, modèle multi-facteurs (AUC ≈ 0,51), récurrences journalières (112 essais), 17 indicateurs (34 essais), combinaisons Ichimoku (32 essais), 15 stratégies intraday (39 essais). Environ 340 essais au total (dont 28 stratégies 5 min, 24 stratégies de sessions, 4 règles après impôts et 12 règles sur d'autres marchés, toutes sans avantage), d'où la prudence sur les résultats « trop beaux » (Deflated Sharpe). Garder l'or battait presque tout sur 2021-2026.

## Limites
- Futures GC=F (jour) et or au comptant XAUUSD (5 min) diffèrent légèrement.
- Frais et financement estimés, pas d'écart de prix réel de courtier.
- Sources gratuites non officielles : elles peuvent changer ou tomber en panne.
