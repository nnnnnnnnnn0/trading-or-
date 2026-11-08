# Stratégie « Compression Or » v1 : règles figées avant le test (8 nov 2026)

Idée (Crabel, années 1990, jamais testée ici) : après une journée où l'or bouge très peu, la journée suivante bouge souvent plus fort. Objectif demandé : au moins 2 à 3 ordres par semaine.

## Données et jours
Or au comptant XAUUSD, barres 5 min (Dukascopy), 2012 à 2026. **Jour de séance** = de 22 h 00 UTC la veille à 22 h 00 UTC (la séance du dimanche soir compte pour le lundi). Les week-ends et jours fériés sont fournis en barres plates (volume nul) : un jour est valide seulement s'il a au moins 200 barres 5 min **et** au moins 100 barres avec un volume non nul ; sinon il est ignoré (précision de nettoyage des données, écrite avant tout calcul de résultat). Plus haut H, plus bas B, clôture C = dernière barre. Amplitude R = H − B. Vraie amplitude TR = max(H − B, |H − C précédente|, |B − C précédente|). ATR = moyenne des TR sur 14 jours.

## Règles
1. **Jour comprimé (jour J−1)** : au moins un de ces trois critères :
   - R(J−1) ≤ le minimum des R des 3 jours précédents ;
   - jour « à l'intérieur » : H(J−1) < H(J−2) et B(J−1) > B(J−2) ;
   - R(J−1) < 0,7 × ATR calculée jusqu'à J−2.
2. **Ordres pour la séance J** : achat stop à H(J−1) et vente stop à B(J−1). Le premier touché s'exécute (au niveau, ou à l'ouverture de la barre si elle s'ouvre au-delà) et annule l'autre. Si les deux niveaux sont touchés dans la même barre 5 min, le trade est ignoré. Ordres valables pendant la séance J seulement.
3. **Sortie** : stop à 1 × ATR(J−1) contre la position, objectif à 2 × ATR(J−1), sinon sortie à la clôture de la 3e séance (J, J+1, J+2). Si stop et objectif sont dans la même barre, le stop est compté. Stop gappé exécuté au pire prix (ouverture de la barre).
4. **Une seule position à la fois** : si une position est encore ouverte au début de la séance J, le signal est ignoré.
5. **Taille** : risque de 0,5 % du capital par trade (1 × ATR = 1 R = 0,5 % du capital). Pas de levier particulier.
6. **Frais** : 0,05 % l'aller-retour + 0,015 % par nuit calendaire tenue, convertis en R.

## Variantes (2 seulement)
- **A** : ordres d'achat et de vente.
- **B** : seulement dans le sens de la tendance à 3 mois : achat si C(J−1) > C 63 jours plus tôt, sinon vente.

## Critères de réussite (tous exigés, pour une variante)
- Gain net moyen par trade > 0 et t de Newey-West ≥ 2, en développement (60 % premiers trades) et en contrôle (40 % derniers).
- Positif dans au moins 3 des 4 blocs égaux de trades, et dans au moins 60 % des années (années avec au moins 5 trades).
- Deflated Sharpe ≥ 0,95 avec 2 essais (aussi calculé avec 250 essais par honnêteté).
- Au moins 100 trades au total.

## À titre d'information (hors critères)
Même mécanique appliquée aux jours **non** comprimés (contrôle : la compression apporte-t-elle quelque chose ?) ; sensibilité aux frais ; répartition des sorties ; nombre de trades par semaine.

Si la stratégie échoue, on le publie tel quel, sans la retoucher.
