## Partie 1 — Le montant d’un sinistre
Observation : Le montant estimé le plus faible de la table s'élève à 80,0 € (contre une moyenne et une médiane globales nettement plus élevées : [Moyenne : 6795.8 € / Médiane : 4576.0 €]).
Mon hypothèse : Ce plancher de 80,0 € correspond à de petits sinistres courants ou à un seuil minimal d'indemnisation, tandis que les événements graves tirent la moyenne vers le haut.
Ce que j'avais décidé de vérifier AVANT : Comparer la moyenne et la médiane de `montant_estime` (et de `franchise`) par `type_sinistre` pour distinguer un barème fixe d'une dispersion réelle.
Ce que j'ai trouvé : La franchise suit un barème fixe par type de sinistre, alors que `montant_estime` varie réellement selon la gravité, avec un minimum à 80,0 € sur les petits dossiers.
Ma conclusion : Confirmée — le minimum de 80,0 € reflète les sinistres de faible ampleur, et l'écart moyenne/médiane s'explique par les sinistres les plus coûteux (confiance : élevée).

## Partie 2 — Le type de sinistre le plus fréquent
Observation : Dégâts des eaux en tête à Toulouse (147 sinistres) et dans chacune des 30 villes étudiées.
Mon hypothèse : Les dégâts des eaux constituent le sinistre le plus fréquent et récurrent dans l'habitat urbain, devant les aléas climatiques saisonniers.
Ce que j'avais décidé de vérifier AVANT : Vérifier si les dégâts des eaux arrivent systématiquement en 1re position dans les 30 villes ou si des sinistres climatiques dominent selon la géographie.
Ce que j'ai trouvé : Les 30 villes placent bien les dégâts des eaux au 1er rang (ex. Toulouse : 147), sans dominance climatique locale.
Ma conclusion : Confirmée — niveau de confiance élevé, la cohérence est observée sur l'ensemble des 30 villes.

## Partie 3 — Octobre 2025
Observation : 1 940 sinistres en octobre 2025 contre une médiane mensuelle d'environ 432 sinistres (2e mois le plus élevé à 1 027).
Mon hypothèse : Une catastrophe climatique majeure (tempête, inondation ou grêle) a provoqué cet afflux soudain de déclarations en octobre 2025.
Ce que j'avais décidé de vérifier AVANT : Contrôler l'explosion des sinistres climatiques, la concentration sur quelques villes et l'existence d'un pic journalier brutal.
Ce que j'ai trouvé : Dégâts des eaux à 44,8 % (tempêtes 12,9 %, grêle 4,0 %), volumes par ville homogènes (70 à 87) et pics journaliers étalés (90–99 cas/jour).
Ma conclusion : Infirmée — niveau de confiance élevé, les trois axes de vérification (nature, géographie, temporalité) convergent.

## Partie 4 — Ce que la météo n’explique pas
Corrélation 1 : `montant_estime` vs précipitations (`precipitation_sum`) : r = +0,022 (et `franchise` : r = -0,002), soit une absence de lien linéaire.
Corrélation 2 : `montant_estime` vs rafales de vent (`wind_gusts_10m_max`) : r = -0,015 (et `franchise` : r = -0,035), soit une corrélation quasi nulle.
Corrélation 3 : `montant_estime` vs températures (`temperature_2m_max` : r = +0,031 ; `temperature_2m_min` : r = +0,025), sans effet linéaire marqué sur le montant.
Limite de l'explication météo : Même si précipitations et rafales corrèlent modérément entre elles (r = +0,322) et les températures max/min fortement (r = +0,885), la météo n'explique ni le montant des sinistres ni le pic d'octobre 2025.
Synthèse : D'autres facteurs (usure des réseaux/bâtiments, types de contrats/franchises ou dynamique de déclaration) doivent être analysés au-delà des variables météo.

