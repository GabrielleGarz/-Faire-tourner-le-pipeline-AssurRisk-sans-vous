Rapport d’audit — Anomalies et preuves SQL



1\. Villes manquantes ou vides (ville\_sinistre NULL ou chaîne vide)

Nature de l’anomalie : Présence de lignes où ville\_sinistre est NULL ou réduite à des espaces / une chaîne vide (BTRIM(ville\_sinistre) = ''), empêchant un rattachement fiable aux 30 villes du référentiel ou faussement comptabilisées hors classement.



Chiffrage constaté : \[nb\_lignes\_ville\_vide] lignes sur \[total\_lignes] (\[pct\_ville\_vide] % du total).



Requête SQL de preuve :

SELECT

&#x20;   COUNT(\*) AS total\_lignes,

&#x20;   COUNT(\*) FILTER (WHERE ville\_sinistre IS NULL OR BTRIM(ville\_sinistre) = '') AS nb\_villes\_vides,

&#x20;   ROUND(

&#x20;       100.0 \* COUNT(\*) FILTER (WHERE ville\_sinistre IS NULL OR BTRIM(ville\_sinistre) = '')

&#x20;       / NULLIF(COUNT(\*), 0),

&#x20;       2

&#x20;   ) AS pct\_villes\_vides

FROM fact\_sinistre\_meteo;



\--Résultat :

12098	0	0.00



2\. Données météorologiques manquantes ou incomplètes (weather\_code, températures, précipitations, vent)

Nature de l’anomalie : Absence de code météo (weather\_code IS NULL) ou valeurs NULL sur les mesures journalières (temperature\_2m\_max, temperature\_2m\_min, precipitation\_sum, wind\_gusts\_10m\_max), créant des lignes sans couverture météo exploitable.



Chiffrage constaté : \[nb\_weather\_code\_null] lignes sans weather\_code ; \[nb\_meteo\_partielle] lignes avec au moins une variable météo NULL ; \[nb\_meteo\_complete] lignes complètes.



Requête SQL de preuve :

SELECT

&#x20;   COUNT(\*) AS total\_lignes,

&#x20;   COUNT(\*) FILTER (WHERE weather\_code IS NULL) AS nb\_weather\_code\_null,

&#x20;   COUNT(\*) FILTER (WHERE temperature\_2m\_max IS NULL OR temperature\_2m\_min IS NULL) AS nb\_temp\_null,

&#x20;   COUNT(\*) FILTER (WHERE precipitation\_sum IS NULL) AS nb\_precip\_null,

&#x20;   COUNT(\*) FILTER (WHERE wind\_gusts\_10m\_max IS NULL) AS nb\_vent\_null,

&#x20;   COUNT(\*) FILTER (

&#x20;       WHERE weather\_code IS NULL

&#x20;          OR temperature\_2m\_max IS NULL

&#x20;          OR temperature\_2m\_min IS NULL

&#x20;          OR precipitation\_sum IS NULL

&#x20;          OR wind\_gusts\_10m\_max IS NULL

&#x20;   ) AS nb\_lignes\_meteo\_incomplete

FROM fact\_sinistre\_meteo;



\--Résultat :

12098	0	0	0	0	0





3\. Décalage ou incohérence de jointure géographique / temporelle (lignes orphelines ou sans correspondance météo)

Nature de l’anomalie : Sinistres présents dans la couche nettoyée qui ne trouvent pas de correspondance exacte sur le couple (ville, date) ou dont la date de déclaration est antérieure à la date de survenance (date\_declaration < date\_survenance).



Chiffrage constaté : \[nb\_dates\_inversees] dossiers avec date\_declaration < date\_survenance ; \[nb\_sans\_jointure] lignes non rattachées au référentiel ville/météo.



Requête SQL de preuve :

SELECT

&#x20;   COUNT(\*) FILTER (WHERE date\_survenance IS NULL OR date\_declaration IS NULL) AS nb\_dates\_null,

&#x20;   COUNT(\*) FILTER (WHERE date\_declaration < date\_survenance) AS nb\_declaration\_avant\_survenance,

&#x20;   COUNT(\*) FILTER (

&#x20;       WHERE ville\_sinistre IS NULL

&#x20;          OR BTRIM(ville\_sinistre) = ''

&#x20;          OR weather\_code IS NULL

&#x20;   ) AS nb\_lignes\_rattachement\_incomplet

FROM fact\_sinistre\_meteo;



\--Résultat :

0	0	0



4\. Valeurs extrêmes ou atypiques sur montant\_estime et franchise

Nature de l’anomalie : Montants estimés ou franchises NULL, négatifs (< 0) ou présentant un fort écart entre moyenne et médiane (avec un plancher observé à 80,0 € sur montant\_estime et une corrélation linéaire d’environ 0,58 entre montant\_estime et franchise).



Chiffrage constaté : \[nb\_montant\_negatif\_ou\_null] montants NULL ou < 0 ; \[nb\_franchise\_negatif\_ou\_null] franchises NULL ou < 0 ; minimum observé à 80,0 €.



Requête SQL de preuve :

SELECT

&#x20;   COUNT(\*) FILTER (WHERE montant\_estime IS NULL OR montant\_estime < 0) AS nb\_montant\_anormal,

&#x20;   COUNT(\*) FILTER (WHERE franchise IS NULL OR franchise < 0) AS nb\_franchise\_anormale,

&#x20;   MIN(montant\_estime) AS montant\_min,

&#x20;   MAX(montant\_estime) AS montant\_max,

&#x20;   ROUND(AVG(montant\_estime)::numeric, 2) AS montant\_moyen,

&#x20;   ROUND(PERCENTILE\_CONT(0.5) WITHIN GROUP (ORDER BY montant\_estime)::numeric, 2) AS montant\_median

FROM fact\_sinistre\_meteo;



\--Résultat :

**0	0	80.00	49912.00	6795.87	4576.00**



5.Ce qu’on peut conclure malgré tout



Malgré les zones d’ombre liées aux valeurs vides ou manquantes sur certaines villes ou variables météo, plusieurs résultats restent solides et exploitables :



Le dégât des eaux reste le premier sinistre : Il arrive en tête à Toulouse (147 sinistres), représente 29,1 % de l’ensemble des dossiers (contre 17,5 % pour le deuxième type) et se maintient en première position dans les 30 villes (de 23,1 % à 34,8 %). Tant que les lignes à ville vide ou NULL ne représentent qu’une minorité marginale, ce classement structurel ne s’effondre pas.



Le pic d’octobre 2025 (1 940 sinistres contre une médiane mensuelle d’environ 432) ne s’explique pas par un événement météo ponctuel : Les dégâts des eaux pèsent 44,8 % du mois contre 12,9 % pour les tempêtes et 4,0 % pour la grêle, les volumes par ville restent homogènes (70 à 87 sinistres) et les pics journaliers restent modérés et étalés (90 à 99 cas/jour).



La météo journalière n’est pas le moteur principal du montant estimé : Les corrélations linéaires entre montant\_estime et les variables météo restent proches de zéro (-0,015 à +0,031), tandis que montant\_estime et franchise partagent un lien plus net (r ≈ 0,58).





