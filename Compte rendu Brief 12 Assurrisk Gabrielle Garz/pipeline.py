import psycopg2
from getpass import getpass
import time 
import pandas as pd
import json
import io
import os
import os

# Création sécurisée du répertoire des sorties
os.makedirs("../sorties", exist_ok=True)

mot_de_passe = getpass("Mot de passe PostgreSQL : ")

connexion = psycopg2.connect(host="localhost", port=5432, dbname="assurisk2",
                             user="postgres", password=mot_de_passe)
connexion.autocommit = True
curseur = connexion.cursor()
print("connexion ouverte")

# -------------------------------------------------------------
# GARDE OPEN-METEO
# -------------------------------------------------------------
chemin_meteo = "meteo_30_villes.json"

if os.path.exists(chemin_meteo):
    print("  [INFO] Cas 1 : Le fichier local existe -> chargement direct sans appel API.")
else:
    print("  [INFO] Cas 2 : Le fichier local est manquant -> interrogation de l'API Open-Meteo...")

# -------------------------------------------------------------
# PREMIÈRE PARTIE SQL : Initialisation et tables (Avant l'étape Python)
# -------------------------------------------------------------
etapes_avant = [
    ("01_init.sql",         "Reinitialiser la base"),
    ("02_clean.sql",        "Construire la couche propre"),
    ("03_tables_meteo.sql", "Creer les tables qui attendent la meteo"),
]

journal = []
for fichier, libelle in etapes_avant:
    debut = time.time()
    requete = open(fichier, encoding="utf-8").read()
    curseur.execute(requete)
    duree = round(time.time() - debut, 1)
    journal.append([fichier, libelle, "SQL", duree])
    print("  [SQL]", libelle, "-", duree, "s")


# -------------------------------------------------------------
# ÉTAPE PYTHON : Chargement du JSON, transformation et COPY
# -------------------------------------------------------------
debut = time.time()

meteo_brute = json.load(open(chemin_meteo, encoding="utf-8"))

morceaux = []
for localisation in meteo_brute:
    tableau = pd.DataFrame(localisation["daily"])
    tableau["latitude"]  = localisation["latitude"]
    tableau["longitude"] = localisation["longitude"]
    morceaux.append(tableau)

meteo = pd.concat(morceaux, ignore_index=True)

# Injection de la table meteo_assurrisk
tampon = io.StringIO()
meteo.to_csv(tampon, index=False, header=False)
tampon.seek(0)
curseur.copy_expert("COPY meteo_assurrisk FROM STDIN WITH (FORMAT csv)", tampon)

# Injection de la table villes_coordonnees_meteo
villes = pd.read_csv("villes_coordonnees_meteo.csv", encoding="utf-8-sig")
tampon_villes = io.StringIO()
villes.to_csv(tampon_villes, index=False, header=False)
tampon_villes.seek(0)
curseur.copy_expert("COPY villes_coordonnees_meteo FROM STDIN WITH (FORMAT csv)", tampon_villes)

duree = round(time.time() - debut, 1)
journal.append(["pipeline.py", "Charger la meteo et les villes", "PYTHON", duree])
print("  [PYTHON]", len(meteo), "lignes de meteo et", len(villes), "villes -", duree, "s")


# -------------------------------------------------------------
# SECONDE PARTIE SQL : Contrôles et étapes d'après 
# -------------------------------------------------------------
etapes_apres = [
    ("04_rattachement.sql", "Rattacher la meteo aux sinistres"),
    ("05_croisement.sql", "Creer la table fact_sinistre_meteo"),
    ("06_controles.sql", "Lancer les controles de cohérence")
]
for fichier, libelle in etapes_apres:
    debut = time.time()
    requete = open(fichier, encoding="utf-8").read()
    curseur.execute(requete)
    duree = round(time.time() - debut, 1)
    journal.append([fichier, libelle, "SQL", duree])
    print("  [SQL]", libelle, "-", duree, "s")


# -------------------------------------------------------------
# JOURNALISATION ET CONTRÔLES FINAUX
# -------------------------------------------------------------
suivi = pd.DataFrame(journal, columns=["fichier", "etape", "outil", "secondes"])
suivi.to_csv("../sorties/journal_pipeline.csv", sep=";", decimal=",",
             index=False, encoding="utf-8-sig")

verification = pd.read_sql("SELECT count(*) AS n FROM clean_fact_sinistre", connexion)
print("      controle : clean_fact_sinistre =", verification["n"][0], "lignes")

verification = pd.read_sql("SELECT count(*) AS n FROM fact_sinistre", connexion)
print("      controle : fact_sinistre =", verification["n"][0], "lignes")

verification = pd.read_sql("SELECT count(*) AS n FROM fact_sinistre_meteo", connexion)
print("      controle : fact_sinistre_meteo =", verification["n"][0], "lignes")

# -------------------------------------------------------------
# GÉNÉRATION AUTOMATIQUE DU FICHIER DE CONTRÔLES PYTHON (controles_python.csv)
# -------------------------------------------------------------
controles_python = [
    ["garde_fichier_local", "meteo_30_villes.json", os.path.exists(chemin_meteo), True],
    ["nb_villes_json", "meteo_brute", len(meteo_brute), 30],
    ["lignes_dataframe_meteo", "meteo", len(meteo), len(meteo)],
    ["lignes_clean_fact_sinistre", "clean_fact_sinistre", int(verification["n"][0]), "> 0"],
    ["lignes_villes_chargees", "villes_coordonnees_meteo", len(villes), len(villes)],
]

df_controles_python = pd.DataFrame(controles_python, columns=["controle", "objet", "valeur_observee", "attendu"])
df_controles_python.to_csv("../sorties/controles_python.csv", sep=";", decimal=",",
                           index=False, encoding="utf-8-sig")
print("  [PYTHON] Fichier controles_python.csv généré dans ../sorties/")

# ---------------------------------------------------------------------------------
# AUDIT DE QUALITÉ DES DONNÉES : DÉTECTION DES DOUBLONS ET CONTRÔLE DES VOLUMÉTRIES
# ---------------------------------------------------------------------------------
requetes_audits = {
    "doublons_fact_sinistre_meteo": "SELECT sinistre_id, date_survenance, COUNT(*) AS nombre_doublons FROM fact_sinistre_meteo GROUP BY sinistre_id, date_survenance HAVING COUNT(*) > 1;",
    "sans_meteo": "SELECT COUNT(*) AS sans_meteo FROM fact_sinistre_meteo WHERE weather_code IS NULL;",
    "doublons_clean_fact_sinistre": "SELECT sinistre_id, COUNT(*) AS nombre_doublons FROM clean_fact_sinistre GROUP BY sinistre_id HAVING COUNT(*) > 1;",
    "doublons_clean_dim_contrat": "SELECT contrat_id, COUNT(*) AS nombre_doublons FROM clean_dim_contrat GROUP BY contrat_id HAVING COUNT(*) > 1;",
    "doublons_clean_dim_garantie": "SELECT garantie_id, COUNT(*) AS nombre_doublons FROM clean_dim_garantie GROUP BY garantie_id HAVING COUNT(*) > 1;",
    "doublons_clean_fact_indemnisation": "SELECT indemnisation_id, COUNT(*) AS nombre_doublons FROM clean_fact_indemnisation GROUP BY indemnisation_id HAVING COUNT(*) > 1;",
    "doublons_clean_contrat_garantie": "SELECT contrat_id, COUNT(*) AS nombre_doublons FROM clean_contrat_garantie GROUP BY contrat_id HAVING COUNT(*) > 1;",
    "doublons_clean_dim_assure": "SELECT assure_id, COUNT(*) AS nombre_doublons FROM clean_dim_assure GROUP BY assure_id HAVING COUNT(*) > 1;",
    "doublons_clean_dim_agence": "SELECT agence_id, COUNT(*) AS nombre_doublons FROM clean_dim_agence GROUP BY agence_id HAVING COUNT(*) > 1;",
    "total_meteo_assurrisk": "SELECT count(*) FROM meteo_assurrisk;",
    "total_meteo_assurrisk_ville": "SELECT count(*) FROM meteo_assurrisk_ville;",
    "meteo_en_double": "SELECT ville, time, count(*) AS meteo_en_double FROM meteo_assurrisk_ville GROUP BY 1, 2 HAVING count(*) > 1;",
    "total_villes_coordonnees_meteo": "SELECT count(*) FROM villes_coordonnees_meteo;"
}

resultats_audit = []
for nom_controle, sql in requetes_audits.items():
    df_res = pd.read_sql(sql, connexion)
    resultats_audit.append({"controle": nom_controle, "lignes_resultat": len(df_res)})

controles = pd.DataFrame(resultats_audit)

print()
print("CONTROLES")
for index, row in controles.iterrows():
    print("   ", row["controle"], ":", row["lignes_resultat"], "lignes d'anomalies détectées")

controles.to_csv("../sorties/controles.csv", sep=";", decimal=",",
                 index=False, encoding="utf-8-sig")

# Fermeture propre de la connexion
curseur.close()
connexion.close()
print("connexion fermée")