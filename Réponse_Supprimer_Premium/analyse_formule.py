from getpass import getpass
import pandas as pd
import psycopg2

mot_de_passe = getpass("Mot de passe PostgreSQL : ")

connexion = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="assurisk2",
    user="postgres",
    password=mot_de_passe,
)
connexion.autocommit = True
curseur = connexion.cursor()
print("connexion ouverte")

query = """
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
    s.sinistre_id,
    s.montant_estime,
    COALESCE(ips.montant_paye, 0) AS montant_indemnise
FROM clean_dim_contrat c
JOIN clean_fact_sinistre s
    ON c.contrat_id = s.contrat_id
LEFT JOIN indemnisation_par_sinistre ips
    ON s.sinistre_id = ips.sinistre_id
WHERE c.formule IN ('Premium', 'Essentielle');
"""

df = pd.read_sql_query(query, connexion)
curseur.close()
connexion.close()
print("connexion fermée")

total_estime_global = df["montant_estime"].sum()
total_indemnise_global = df["montant_indemnise"].sum()

synthese = []
for formule, grp in df.groupby("formule"):
    est = grp["montant_estime"]
    ind = grp["montant_indemnise"]

    synthese.append({
        "formule": formule,
        "nb_sinistres": len(grp),
        "moyenne_estime": round(est.mean(), 2),
        "charge_totale_estime": round(est.sum(), 2),
        "poids_estime_pct": round(est.sum() / total_estime_global * 100, 2),
        "moyenne_indemnise": round(ind.mean(), 2),
        "charge_totale_indemnise": round(ind.sum(), 2),
        "poids_indemnise_pct": round(ind.sum() / total_indemnise_global * 100, 2),
    })

df_synthese = pd.DataFrame(synthese)
print("\n" + df_synthese.to_string(index=False))

if {"Premium", "Essentielle"}.issubset(set(df_synthese["formule"])):
    prem = df_synthese[df_synthese["formule"] == "Premium"].iloc[0]
    ess = df_synthese[df_synthese["formule"] == "Essentielle"].iloc[0]
    print("\n--- Écart moyen Premium vs Essentielle ---")
    print(f"Écart moyen estimé / sinistre    : {prem['moyenne_estime'] - ess['moyenne_estime']:+.2f} €")
    print(f"Écart moyen indemnisé / sinistre : {prem['moyenne_indemnise'] - ess['moyenne_indemnise']:+.2f} €")