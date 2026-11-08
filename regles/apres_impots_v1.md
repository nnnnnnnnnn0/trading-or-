# Stratégies sur l'or testées APRÈS IMPÔTS, 2012-2026 : règles figées (8 nov 2026)

Question posée : existe-t-il une règle simple qui soit gagnante **après impôts** sur les 14 ans de backtest ? Pour éviter de chercher jusqu'à trouver un mirage, les 4 règles ci-dessous (plus la référence « garder l'or ») sont fixées **avant** le test, et lancées une seule fois. Toutes sont « achat seulement / liquidités » (pas de vente à découvert, pas de levier), sur données journalières de l'or (futures GC=F, séance du jour).

## Règles
- **Référence R : garder l'or** de la première à la dernière séance.
- **A : Tendance 200 jours** : achat si la clôture est au-dessus de sa moyenne sur 200 séances, sinon liquidités. Décision chaque vendredi (clôture), appliquée à la clôture suivante.
- **B : Momentum 12 mois** : achat si le rendement sur 252 séances est positif, sinon liquidités. Décision à la dernière séance de chaque mois.
- **C : Tendance + macro** : achat si (A) est à l'achat **et** si les taux réels américains 10 ans OU le dollar (DXY) ont baissé sur 63 séances (valeurs de la veille), sinon liquidités. Décision chaque vendredi.
- **D : Tendance 200 jours avec sortie de sécurité** : comme A, mais sortie immédiate si la clôture tombe de plus de 12 % sous son plus haut depuis l'entrée, puis retour seulement après un nouveau vendredi au-dessus de la moyenne 200 jours.

## Frais et impôts (hypothèses, pas des conseils fiscaux)
- Frais : 0,05 % l'aller-retour à chaque entrée-sortie, et 0,15 % par an de frais de détention (type ETC) sur les jours investis. Pas de financement (pas de levier).
- **Impôt : 31,4 % des plus-values nettes de l'année** (taux du prélèvement forfaitaire unique 2026 en France : 12,8 % + 18,6 % de prélèvements sociaux ; pas de l'or physique, qui a un autre régime). Gains réalisés = à chaque sortie. Moins-values reportées sur les gains suivants (sans limite de durée, simplification). Impôt prélevé à la fin de chaque année. Position encore ouverte à la fin du test : vendue (donc imposée) pour comparer toutes les règles de la même façon. Sensibilité : 0 % et 45 %.
- Période : du 2 janvier 2012 à la dernière séance disponible.

## Critères pour dire « gagnante après impôts » (tous exigés, pour une règle)
1. Rendement annuel après impôts > 0 sur la période complète **et** dans au moins 3 des 4 blocs égaux (chaque bloc recalculé à neuf).
2. Rendement après impôts final ≥ 70 % de celui de « garder l'or » **et** perte maximale ≤ 60 % de celle de « garder l'or ».
3. Test du hasard (1 000 décalages circulaires des expositions) : au plus 5 % font aussi bien.
4. Deflated Sharpe ≥ 0,95 avec 4 essais (aussi donné avec 260 pour honnêteté).

Si aucune règle ne passe, on le publie tel quel. Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
