# Règles « achat seulement » sur l'or, testées APRÈS IMPÔTS : règles figées (9 nov 2026)

Question : une règle simple (achat ou liquidités, sans levier ni vente à découvert) est-elle gagnante après impôts sur les 14 ans de 2012 à 2026 ? Les 4 règles ci-dessous (et la référence « garder l'or ») sont fixées **avant** le test et lancées **une seule fois**. Données : or journalier (futures GC=F), du 2 janvier 2012 à la dernière séance.

## Règles
- **Référence R : garder l'or** de la première à la dernière séance.
- **A : Tendance 200 jours** : achat si la clôture est au-dessus de sa moyenne sur 200 séances, sinon liquidités. Décision chaque vendredi (ou dernière séance de la semaine), exécutée à la clôture de la séance suivante.
- **B : Momentum 12 mois** : achat si le rendement sur 252 séances est positif, sinon liquidités. Décision à la dernière séance de chaque mois, exécutée à la clôture suivante.
- **C : Tendance + macro** : achat si A est à l'achat **et** si les taux réels américains 10 ans OU le dollar (DXY) ont baissé sur 63 séances (valeurs de la veille), sinon liquidités. Décision hebdomadaire comme A.
- **D : Tendance 200 jours avec sortie de sécurité** : comme A, mais sortie (à la clôture suivante) si la clôture tombe à plus de 12 % sous son plus haut depuis l'entrée ; retour seulement à une décision du vendredi où A est à l'achat.

## Frais et impôts (hypothèses, pas des conseils fiscaux)
- Frais : 0,05 % l'aller-retour à chaque entrée-sortie ; 0,15 % par an de frais de détention (type ETC) sur les jours investis ; pas de financement (pas de levier).
- **Impôt : 31,4 %** des plus-values nettes de l'année (taux 2026 du prélèvement forfaitaire unique en France : 12,8 % + 18,6 % de prélèvements sociaux ; l'or physique relève d'un autre régime). Plus-value réalisée à chaque sortie. Moins-values reportées sans limite de durée (simplification). Impôt prélevé en fin d'année. Position ouverte à la fin du test : vendue et imposée, pour comparer toutes les règles de la même façon.

## Critères pour dire « gagnante après impôts » (tous exigés, pour une règle)
1. Rendement annuel après impôts > 0 sur la période complète **et** dans au moins 3 des 4 blocs égaux (chaque bloc recalculé à neuf).
2. Rendement final après impôts ≥ 70 % de celui de « garder l'or » **et** perte maximale (avant impôts) ≤ 60 % de celle de « garder l'or ».
3. Test du hasard (1 000 décalages circulaires des expositions) : au plus 5 % font aussi bien en rendement moyen quotidien.
4. Deflated Sharpe ≥ 0,95 avec 4 essais (aussi donné avec 340 essais).

Si aucune ne passe, on le publie tel quel. Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.
