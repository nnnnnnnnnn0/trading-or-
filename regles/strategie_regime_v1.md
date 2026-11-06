# Stratégie « Régime or » v1 : proposition (pas encore testée)

Rédigée à partir de la littérature, **avant tout backtest**. Les paramètres ci-dessous sont figés : aucun ne sera ajusté après avoir vu un résultat.

## Sources
- Suivi de tendance : Hurst, Ooi, Pedersen, *A Century of Evidence on Trend-Following Investing* (signal = moyenne des signes des rendements sur 1, 3 et 12 mois ; volatilité cible 10 % ; Sharpe net 0,77 sur 1880-2013, mais plus mitigé depuis 2008).
- Moteurs de l'or : taux réels et dollar (revue JSR « A Review of Gold Pricing: Real Interest Rate and U.S. Dollar Index ») ; Erb & Harvey, *The Golden Dilemma* (l'or est une couverture d'inflation peu fiable à court terme ; le prix réel de l'or revient vers sa moyenne sur le très long terme).
- Ciblage de volatilité : Harvey et al. (Man Institute), *The Impact of Volatility Targeting* (réduit les pertes extrêmes ; gain de Sharpe négligeable pour les matières premières : on l'utilise comme contrôle du risque, pas comme source de gain).
- Effet nuit / jour : *Overnight versus day returns in gold and gold related assets* (Journal of Economics and Finance, 2018) : rendements de nuit positifs, rendements de jour négatifs.
- Méthode : Bailey & López de Prado (Deflated Sharpe Ratio) ; CXO Advisory (compter toutes les variantes, plusieurs sous-périodes).

## Module A : régime (cœur, quotidien, rééquilibrage chaque vendredi à la clôture)
1. **Tendance T** = moyenne des signes des rendements sur 21, 63 et 252 jours de bourse. T vaut −1, −1/3, +1/3 ou +1.
2. **Macro M** = moyenne de (− signe de la variation du taux réel américain 10 ans sur 63 jours) et (− signe de la variation du dollar DXY sur 63 jours). Taux réels et dollar qui baissent = favorable à l'or. M vaut −1, 0 ou +1.
3. **Score S = 0,7 × T + 0,3 × M** (la tendance domine, comme dans la littérature ; la macro confirme).
4. **Direction** : achat si S ≥ +0,5, vente si S ≤ −0,5, sinon à plat.
5. **Taille** : volatilité cible 10 % par an ; exposition = 10 % / volatilité réalisée sur 20 jours, plafonnée à 1,5 fois le capital.
6. **Sécurité** : sortie si la clôture dépasse 3 × ATR(14 jours) contre la position depuis l'entrée ; retour possible au rééquilibrage suivant.
7. Frais comptés : 0,05 % l'aller-retour + 0,015 % par nuit.

## Module B : moment de la journée (à tester séparément, hypothèse H1)
« Les rendements de l'or se concentrent en dehors des heures américaines (13 h à 21 h UTC). » Test sur l'historique 5 min de 14 ans (quand il sera complet) : rendement moyen par tranche horaire, développement contre contrôle. S'il tient, le module A pourrait entrer et sortir à ces moments pour réduire les frais et améliorer l'entrée. **Pas dans le cœur tant que non confirmé.**

## Plan de test (fixé d'avance)
- **3 variantes seulement** : V1 principale ; V2 tendance seule (position = signe de T, sans macro, sans seuil) ; V3 comme V1 avec pondération 0,5 / 0,5.
- Données : 2006-2026 journalières (GC=F), taux réels FRED, dollar. Rapport par bloc (4 blocs égaux), par décennie, achats et ventes séparés, comparé à garder l'or.
- **Critères de réussite, tous exigés** : Sharpe net ≥ Sharpe de « garder l'or » moins 0,1 ; perte maximale ≤ 60 % de celle de « garder l'or » ; positif dans au moins 3 blocs sur 4 ; au plus 5 % de hasard (décalages aléatoires) ; Deflated Sharpe ≥ 0,95 avec 3 essais. Deflated Sharpe aussi calculé avec tous les essais du projet (environ 250) par honnêteté.
- Si la stratégie échoue : on le publie tel quel, sans la retoucher pour la faire passer.
- Si elle réussit : paper trading en conditions réelles (journal quotidien) avant tout argent réel.

## Attentes réalistes
Le suivi de tendance est lent, avec des séries de pertes et des périodes sans signal ; il n'offre pas « un trade fiable par jour ». Il vise un profil de gain/risque plus régulier que garder l'or, pas une promesse de gain.
