# trading-or : une seule stratégie sur l'or, testée sur le maximum de données

**Paper trading uniquement, aucun argent réel. Ce dépôt n'est ni un conseil en investissement ni une prévision.** Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.

Le dépôt ne contient que ce qu'il faut pour récupérer les données et tester la stratégie « Régime or v1 » (règles figées avant tout test dans `regles/strategie_regime_v1.md`, aucun paramètre ajusté après coup).

## Organisation
| Chemin | Contenu |
| --- | --- |
| `regles/strategie_regime_v1.md` | les règles figées, les sources, le plan de test et les critères de réussite |
| `scripts/donnees/fetch_jour.py` | or (GC=F) et dollar (DXY) via Yahoo, taux réels américains 10 ans via US Treasury → `data/or_jour.csv`, `data/dollar_dxy.csv`, `data/taux_reels_10ans.csv` |
| `scripts/donnees/fetch_histo.py` | or au comptant XAUUSD, minutes Dukascopy agrégées en 5 min, par lots → `data/histo/xauusd_5m_AAAA.csv.gz` (reprend là où il s'est arrêté ; état dans `data/histo/statut.txt`, jours restants dans `reste.txt`) |
| `scripts/backtests/backtest_regime.py` | le backtest (module A : régime journalier ; module B : hypothèse H1 sur le 5 min) et le signal du jour |
| `tests/` | tests sur données inventées, sans réseau |
| `resultats/regime_v1.md` | rapport du backtest (créé au premier lancement) |
| `.github/workflows/donnees.yml` | téléchargement automatique des données |

## Utilisation
```
python -m unittest discover -s tests          # tests
python scripts/backtests/backtest_regime.py   # rapport complet -> resultats/regime_v1.md
python scripts/backtests/backtest_regime.py --signal   # position conseillée à la dernière clôture (fictive)
```
Il faut `pandas` et `numpy`. Le backtest utilise les données déjà présentes dans `data/` : le réseau n'est pas nécessaire.

## Téléchargement automatique (GitHub Actions, workflow « Données »)
- Chaque jour ouvré à 6 h 30 UTC et à chaque modification de `scripts/donnees/` : données quotidiennes (travail `jour`) et historique 5 min (travail `histo`).
- Le travail `histo` télécharge par lots de 20 minutes et **se relance tout seul** tant qu'il reste des jours (`data/histo/reste.txt`). Un jour qui échoue 15 fois est abandonné et noté dans `data/histo/echecs.json`.
- Lancement manuel : onglet Actions, « Données », « Run workflow » (mode `tout`, `jour` ou `histo`).
- **Minutes gratuites : 2 000 par mois pour un dépôt privé, illimitées pour un dépôt public.** Privé et minutes épuisées : tous les lancements échouent en 2 secondes.
- Dépôt public : le contenu (code, données, résultats) est lisible par tous. Aucune clé ni mot de passe n'est nécessaire ni ne doit être écrit dans ce dépôt. Les données viennent de sources gratuites (Yahoo, Dukascopy, US Treasury) dont les conditions d'usage peuvent limiter leur redistribution.

## Ce que les études précédentes ont montré (supprimées du dépôt, récupérables dans l'historique git, par exemple le commit `0c9719b`)
Aucun avantage durable n'a été trouvé : 4 règles figées, stratégie multi-échelles, modèle multi-facteurs (AUC ≈ 0,51), récurrences journalières (112 essais), 17 indicateurs (34 essais), combinaisons Ichimoku (32 essais), 15 stratégies intraday (39 essais). Environ 250 essais au total, d'où la prudence sur les résultats « trop beaux » (Deflated Sharpe). Garder l'or battait presque tout sur 2021-2026.

## Limites
- Futures GC=F (jour) et or au comptant XAUUSD (5 min) diffèrent légèrement.
- Frais et financement estimés, pas d'écart de prix réel de courtier.
- Sources gratuites non officielles : elles peuvent changer ou tomber en panne.
