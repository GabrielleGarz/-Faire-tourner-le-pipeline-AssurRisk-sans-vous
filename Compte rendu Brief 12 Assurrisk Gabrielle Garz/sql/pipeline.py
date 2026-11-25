from pathlib import Path
import psycopg2
from getpass import getpass
import time
import pandas as pd
import json
import io
import os

# Dossier contenant pipeline.py (.../sql/) et dossier sorties (.../sorties/)
BASE_DIR = Path(__file__).resolve().parent
SORTIES_DIR = BASE_DIR.parent / "sorties"
os.makedirs(SORTIES_DIR, exist_ok=True)

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
journal = []


def enregistrer_etape(fichier, etape, outil, debut):
    duree = round(time.time() - debut, 1)
    journal.append([fichier, etape, outil, duree, "ok"])
    return duree


def jouer_sql(fichier, libelle):
    debut = time.time()
    chemin_sql = BASE_DIR / fichier
    requete = chemin_sql.read_text(encoding="utf-8")
    curseur.execute(requete)
    duree = enregistrer_etape(fichier, libelle, "SQL", debut)
    print("  [SQL]", libelle, "-", duree, "s")


def charger_dans_postgres(tableau, nom_table):
    tampon = io.StringIO()
    tableau.to_csv(tampon, index=False, header=False)
    tampon.seek(0)
    curseur.copy_expert(f"COPY {nom_table} FROM STDIN WITH (FORMAT csv)", tampon)


def verifier_comptage_table(table, label=None):
    """Retourne le nombre de lignes d'une table PostgreSQL et affiche un contrôle."""
    nom_affiche = label or table
    resultat = pd.read_sql(f"SELECT count(*) AS n FROM {table}", connexion)
    nb_lignes = int(resultat["n"][0])
    print(f"      controle : {nom_affiche} = {nb_lignes} lignes")
    return nb_lignes


def combien(nom_de_table):
    curseur.execute("SELECT count(*) FROM " + nom_de_table)
    return curseur.fetchone()[0]


# -------------------------------------------------------------
# GARDE OPEN-METEO
# -------------------------------------------------------------
chemin_meteo = BASE_DIR / "meteo_30_villes.json"

if chemin_meteo.exists():
    print("  [INFO] Cas 1 : Le fichier local existe -> chargement direct sans appel API.")
else:
    print("  [INFO] Cas 2 : Le fichier local est manquant -> interrogation de l'API Open-Meteo...")

# -------------------------------------------------------------
# PREMIÈRE PARTIE SQL : Initialisation et tables (Avant l'étape Python)
# -------------------------------------------------------------
etapes_avant = [
    ("01_init.sql", "Reinitialiser la base"),
    ("02_clean.sql", "Construire la couche propre"),
    ("03_tables_meteo.sql", "Creer les tables qui attendent la meteo"),
]

for fichier, libelle in etapes_avant:
    jouer_sql(fichier, libelle)

# -------------------------------------------------------------
# ÉTAPE PYTHON : Chargement du JSON, transformation et COPY
# -------------------------------------------------------------
debut = time.time()

with chemin_meteo.open(encoding="utf-8") as f:
    meteo_brute = json.load(f)

morceaux = []
for localisation in meteo_brute:
    tableau = pd.DataFrame(localisation["daily"])
    tableau["latitude"] = localisation["latitude"]
    tableau["longitude"] = localisation["longitude"]
    morceaux.append(tableau)

meteo = pd.concat(morceaux, ignore_index=True)

# Injection de la table meteo_assurrisk
charger_dans_postgres(meteo, "meteo_assurrisk")

# Injection de la table villes_coordonnees_meteo
chemin_villes = BASE_DIR / "villes_coordonnees_meteo.csv"
villes = pd.read_csv(chemin_villes, encoding="utf-8-sig")
charger_dans_postgres(villes, "villes_coordonnees_meteo")

duree = enregistrer_etape(
    "pipeline.py", "Charger la meteo et les villes", "PYTHON", debut
)
print(
    "  [PYTHON]",
    len(meteo),
    "lignes de meteo et",
    len(villes),
    "villes -",
    duree,
    "s",
)

# -------------------------------------------------------------
# SECONDE PARTIE SQL : Contrôles et étapes d'après
# -------------------------------------------------------------
etapes_apres = [
    ("04_rattachement.sql", "Rattacher la meteo aux sinistres"),
    ("05_croisement.sql", "Creer la table fact_sinistre_meteo"),
    ("06_controles.sql", "Lancer les controles de cohérence"),
]
for fichier, libelle in etapes_apres:
    jouer_sql(fichier, libelle)

# -------------------------------------------------------------
# JOURNALISATION ET CONTRÔLES FINAUX
# -------------------------------------------------------------
suivi = pd.DataFrame(journal, columns=["fichier", "etape", "outil", "secondes", "statut"])
suivi.to_csv(
    SORTIES_DIR / "journal_pipeline.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig",
)

nb_clean_fact_sinistre = verifier_comptage_table("clean_fact_sinistre")
nb_fact_sinistre = verifier_comptage_table("fact_sinistre")
nb_fact_sinistre_meteo = verifier_comptage_table("fact_sinistre_meteo")

# -------------------------------------------------------------
# GÉNÉRATION AUTOMATIQUE DU FICHIER DE CONTRÔLES PYTHON (controles_python.csv)
# -------------------------------------------------------------
controles_python = [
    [
        "garde_fichier_local",
        "meteo_30_villes.json",
        chemin_meteo.exists(),
        True,
    ],
    ["nb_villes_json", "meteo_brute", len(meteo_brute), 30],
    ["lignes_dataframe_meteo", "meteo", len(meteo), len(meteo)],
    [
        "lignes_clean_fact_sinistre",
        "clean_fact_sinistre",
        nb_clean_fact_sinistre,
        "> 0",
    ],
    ["lignes_fact_sinistre", "fact_sinistre", nb_fact_sinistre, "> 0"],
    [
        "lignes_fact_sinistre_meteo",
        "fact_sinistre_meteo",
        nb_fact_sinistre_meteo,
        "> 0",
    ],
    [
        "lignes_villes_chargees",
        "villes_coordonnees_meteo",
        len(villes),
        len(villes),
    ],
]

df_controles_python = pd.DataFrame(
    controles_python, columns=["controle", "objet", "valeur_observee", "attendu"]
)
df_controles_python.to_csv(
    SORTIES_DIR / "controles_python.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig",
)
print("  [PYTHON] Fichier controles_python.csv généré dans sorties/")

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
    "total_villes_coordonnees_meteo": "SELECT count(*) FROM villes_coordonnees_meteo;",
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

controles.to_csv(
    SORTIES_DIR / "controles.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig",
)

print(
    "fact_sinistre_meteo contient",
    combien("fact_sinistre_meteo"),
    "lignes",
)

# Fermeture propre de la connexion
curseur.close()
connexion.close()
print("connexion fermée")