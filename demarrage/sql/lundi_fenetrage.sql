
--================================================================
--Question 1 : Les trois sinistres les plus chers de chaque région
--================================================================

WITH classement_sinistres AS (
    SELECT 
        region_sinistre,
        sinistre_id,        
        type_sinistre,
        montant_estime,
        ROW_NUMBER() OVER (
            PARTITION BY region_sinistre 
            ORDER BY montant_estime DESC
        ) AS rang
    FROM fact_sinistre_meteo
)
SELECT 
    region_sinistre,
    sinistre_id,
    type_sinistre,
    montant_estime,
    rang
FROM classement_sinistres
WHERE rang <= 3
ORDER BY region_sinistre ASC, rang ASC;

--Bis : modification de la requête pour les 5 sinistres les plus chers par région

WITH classement_sinistres AS (
    SELECT 
        region_sinistre,
        sinistre_id,        
        type_sinistre,
        montant_estime,
        ROW_NUMBER() OVER (
            PARTITION BY region_sinistre 
            ORDER BY montant_estime DESC
        ) AS rang
    FROM fact_sinistre_meteo
)
SELECT 
    region_sinistre,
    sinistre_id,
    type_sinistre,
    montant_estime,
    rang
FROM classement_sinistres
WHERE rang <= 5
ORDER BY region_sinistre ASC, rang ASC;

--résultat : 60 lignes (12*5)

--=================================================================================
--Question 2 : L’écart entre un sinistre et la moyenne de son type
--=================================================================================

SELECT 
    sinistre_id,
    type_sinistre,
    ROUND(AVG(montant_estime) OVER (PARTITION BY type_sinistre), 2) AS moyenne_du_type,
    ROUND(montant_estime - AVG(montant_estime) OVER (PARTITION BY type_sinistre), 2) AS ecart
FROM fact_sinistre_meteo
ORDER BY sinistre_id ASC;

--résultat :
--1	Dégât des eaux	2070.00	4478	-2408

--Ajoutez une sixième colonne qui affiche le mot au-dessus quand le montant
--dépasse la moyenne de son type, et en-dessous sinon.
--Indice : CASE WHEN ... THEN 'au-dessus' ELSE 'en-dessous' END

SELECT 
    sinistre_id,
    type_sinistre,
    ROUND(AVG(montant_estime) OVER (PARTITION BY type_sinistre), 2) AS moyenne_du_type,
    ROUND(montant_estime - AVG(montant_estime) OVER (PARTITION BY type_sinistre), 2) AS ecart,
CASE 
        WHEN montant_estime >  ROUND(AVG(montant_estime) OVER (PARTITION BY type_sinistre), 2) THEN 'au_dessus'
        WHEN montant_estime <  ROUND(AVG(montant_estime) OVER (PARTITION BY type_sinistre), 2) THEN 'au_dessous'
        ELSE 'égal'
END AS position_moyenne
FROM fact_sinistre_meteo
ORDER BY sinistre_id ASC;


--=============================================================
--Question 3 : La part de chaque région dans le total
--=============================================================

--region_sinistre | nb | pct

WITH part_région AS (
    SELECT 
        region_sinistre,
        COUNT(*) AS nb
    FROM fact_sinistre_meteo
    GROUP BY region_sinistre
)
SELECT 
    region_sinistre,
    nb,
    ROUND((nb::numeric / SUM(nb) OVER ()) * 100, 1) AS pct
FROM part_région
ORDER BY nb DESC;

--==================================================================
--Question 4 : Le type de sinistre le plus fréquent de chaque ville
--==================================================================

--ville_sinistre | type_sinistre | nb

WITH occurrence_sinistres AS (
    -- Étape 1 : Compter le nombre de fois qu'un type de sinistre apparaît par ville
    SELECT 
        ville_sinistre,
        type_sinistre,
        COUNT(*) AS nb_frequence
    FROM fact_sinistre_meteo
    GROUP BY ville_sinistre, type_sinistre
),
classement_villes AS (
    -- Étape 2 : Classer les types de sinistres pour chaque ville du plus fréquent au moins fréquent
    SELECT 
        ville_sinistre,
        type_sinistre,
        nb_frequence,
        ROW_NUMBER() OVER (
            PARTITION BY ville_sinistre 
            ORDER BY nb_frequence DESC
        ) AS rang
    FROM occurrence_sinistres
)
-- Étape 3 : Ne garder que le premier de chaque ville (le plus fréquent) et trier par nombre décroissant
SELECT 
    ville_sinistre,
    type_sinistre,
    nb_frequence
FROM classement_villes
WHERE rang = 1
ORDER BY nb_frequence DESC;

--Affichez le nombre de sinistres par mois, du premier au dernier mois de la table.
--Deux colonnes : le mois au format 2025-10 , et le nombre. Trié du plus grand nombre au plus petit.
--Indice : pour transformer une date en 2025-10 , PostgreSQL a
--to_char(date_survenance, 'YYYY-MM').


SELECT 
    TO_CHAR(date_survenance, 'YYYY-MM') AS mois,
    COUNT(*) AS nombre
FROM fact_sinistre_meteo
GROUP BY TO_CHAR(date_survenance, 'YYYY-MM')
ORDER BY nombre DESC;
