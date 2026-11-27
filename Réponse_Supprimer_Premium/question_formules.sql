--1.Le coût moyen par dossier Premium est-il effectivement supérieur à la formule Essentielle ?

WITH indemnisation_par_sinistre AS (
    SELECT
        sinistre_id,
        SUM(montant_indemnise) AS montant_paye
    FROM clean_fact_indemnisation
    WHERE statut_paiement = 'payé'
    GROUP BY sinistre_id
)
SELECT
    c.formule,
    COUNT(s.sinistre_id) AS nb_sinistres,
    ROUND(AVG(s.montant_estime), 2) AS cout_moyen_estime,
    ROUND(AVG(COALESCE(ips.montant_paye, 0)), 2) AS cout_moyen_indemnise
FROM clean_dim_contrat c
JOIN clean_fact_sinistre s
    ON c.contrat_id = s.contrat_id
LEFT JOIN indemnisation_par_sinistre ips
    ON s.sinistre_id = ips.sinistre_id
GROUP BY c.formule
ORDER BY c.formule;

--résultat :
--Confort			4684	6691.06	3454.35
--Essentielle		5005	6787.93	3414.32
--Premium			2409	7016.15	3586.59

--Quel poids représente Premium dans la charge totale de sinistres ?

WITH indemnisation_par_sinistre AS (
    SELECT
        sinistre_id,
        SUM(montant_indemnise) AS montant_paye
    FROM clean_fact_indemnisation
    WHERE statut_paiement = 'payé'
    GROUP BY sinistre_id
),
charge_par_formule AS (
    SELECT
        c.formule,
        COUNT(s.sinistre_id) AS nb_sinistres,
        COALESCE(SUM(s.montant_estime), 0) AS charge_estimee,
        COALESCE(SUM(ips.montant_paye), 0) AS charge_indemnisee
    FROM clean_dim_contrat c
    JOIN clean_fact_sinistre s
        ON c.contrat_id = s.contrat_id
    LEFT JOIN indemnisation_par_sinistre ips
        ON s.sinistre_id = ips.sinistre_id
    GROUP BY c.formule
)
SELECT
    formule,
    nb_sinistres,
    ROUND(charge_estimee, 2) AS charge_estimee,
    ROUND(
        (charge_estimee / NULLIF(SUM(charge_estimee) OVER (), 0)) * 100,
        2
    ) AS poids_charge_estimee_pct,
    ROUND(charge_indemnisee, 2) AS charge_indemnisee,
    ROUND(
        (charge_indemnisee / NULLIF(SUM(charge_indemnisee) OVER (), 0)) * 100,
        2
    ) AS poids_charge_indemnisee_pct
FROM charge_par_formule
ORDER BY charge_indemnisee DESC;

--résultat :
--Essentielle		5005	33973573.00	41.32	17088678.69	40.78
--Confort			4684	31340940.00	38.12	16180196.56	38.61
--Premium			2409	16901896.00	20.56	8640102.17	20.62

--2.Est-ce que la formule Premium génère-t-elle plus ou moins de sinistres par contrat / assuré que Essentielle ?

WITH sinistres_par_contrat AS (
    SELECT
        contrat_id,
        COUNT(sinistre_id) AS nb_sinistres
    FROM clean_fact_sinistre
    GROUP BY contrat_id
)
SELECT
    c.formule,
    COUNT(DISTINCT c.contrat_id) AS nb_contrats,
    COUNT(DISTINCT c.assure_id) AS nb_assures,
    COALESCE(SUM(spc.nb_sinistres), 0) AS nb_sinistres,

    -- Fréquence par contrat
    ROUND(
        COALESCE(SUM(spc.nb_sinistres), 0)::numeric / NULLIF(COUNT(DISTINCT c.contrat_id), 0)*100,
        4
    ) AS sinistres_par_contrat,

    -- Fréquence par assuré
    ROUND(
        COALESCE(SUM(spc.nb_sinistres), 0)::numeric / NULLIF(COUNT(DISTINCT c.assure_id), 0)*100,
        4
    ) AS sinistres_par_assure,

    -- Contrats moyens par assuré (utile si un assuré cumule plusieurs contrats)
    ROUND(
        COUNT(DISTINCT c.contrat_id)::numeric / NULLIF(COUNT(DISTINCT c.assure_id), 0),
        2
    ) AS contrats_par_assure
FROM clean_dim_contrat c
LEFT JOIN sinistres_par_contrat spc
    ON c.contrat_id = spc.contrat_id
GROUP BY c.formule
ORDER BY c.formule;


--résultat :
--Confort			11752	9407	4684	39.8570	49.7927	1.25
--Essentielle		11975	9557	5005	41.7954	52.3700	1.25
--Premium			5841	4680	2409	41.2429	51.4744	1.25

--3.Le surcoût des sinistres Premium est-il absorbé (ou amplifié) par le niveau de franchise appliqué, 
--et quel est l'écart entre le montant estimé, 
--la franchise à la charge de l'assuré et le montant effectivement indemnisé par AssurRisk ?

WITH indemnisation_par_sinistre AS (
    SELECT
        sinistre_id,
        SUM(montant_indemnise) AS montant_paye
    FROM clean_fact_indemnisation
    WHERE statut_paiement = 'payé'
    GROUP BY sinistre_id
),
sinistres_enrichis AS (
    SELECT
        c.formule,
        s.sinistre_id,
        s.montant_estime,
        s.franchise,
        COALESCE(ips.montant_paye, 0) AS montant_indemnise,
        -- Écart comptable : estimé moins franchise et moins payé
        (s.montant_estime - s.franchise - COALESCE(ips.montant_paye, 0)) AS ecart_estime_vs_franchise_et_paye,
        -- Part absorbée par la franchise rapportée au montant estimé (%)
        CASE
            WHEN s.montant_estime > 0 THEN (s.franchise / s.montant_estime) * 100
            ELSE NULL
        END AS part_franchise_estime_pct
    FROM clean_dim_contrat c
    JOIN clean_fact_sinistre s
        ON c.contrat_id = s.contrat_id
    LEFT JOIN indemnisation_par_sinistre ips
        ON s.sinistre_id = ips.sinistre_id
)
SELECT
    formule,
    COUNT(sinistre_id) AS nb_sinistres,

    -- Totaux par formule
    ROUND(SUM(montant_estime), 2) AS total_estime,
    ROUND(SUM(franchise), 2) AS total_franchise,
    ROUND(SUM(montant_indemnise), 2) AS total_indemnise,
    ROUND(SUM(ecart_estime_vs_franchise_et_paye), 2) AS total_ecart_estime_moins_franchise_paye,

    -- Moyennes par dossier sinistre
    ROUND(AVG(montant_estime), 2) AS moy_estime_par_sinistre,
    ROUND(AVG(franchise), 2) AS moy_franchise_par_sinistre,
    ROUND(AVG(montant_indemnise), 2) AS moy_indemnise_par_sinistre,
    ROUND(AVG(ecart_estime_vs_franchise_et_paye), 2) AS moy_ecart_par_sinistre,

    -- Poids relatif moyen de la franchise dans l'estimation (%)
    ROUND(AVG(part_franchise_estime_pct), 2) AS part_moyenne_franchise_dans_estime_pct
	FROM sinistres_enrichis
	GROUP BY formule
	ORDER BY formule;

--résultat :
--Confort			4684	31340940.00	1063980.00	16180196.56	14096763.44	6691.06	227.15	3454.35	3009.56	8.27
--Essentielle		5005	33973573.00	1147850.00	17088678.69	15737044.31	6787.93	229.34	3414.32	3144.26	8.20
--Premium			2409	16901896.00	555020.00	8640102.17	7706773.83	7016.15	230.39	3586.59	3199.16	8.06
    
    
