import pandas as pd

# 1. Chargement des fichiers sources
df_sinistre = pd.read_csv("clean_fact_sinistre.csv")
df_meteo = pd.read_csv("meteo_assurisk_ville.csv")

# 2. Harmonisation des formats de date pour la jointure
df_sinistre['date_survenance'] = pd.to_datetime(df_sinistre['date_survenance']).dt.date
df_meteo['meteo_date'] = pd.to_datetime(df_meteo['time']).dt.date

# 3. Réalisation du LEFT JOIN (équivalent du LEFT JOIN SQL)
df_fact = pd.merge(
    df_sinistre,
    df_meteo,
    how='left',
    left_on=['ville_sinistre', 'date_survenance'],
    right_on=['ville', 'meteo_date']
)

# 4. Sélection des colonnes pour correspondre exactement au SELECT
colonnes_selectionnees = [
    'sinistre_id', 'contrat_id', 'agence_id', 'garantie_id',
    'date_survenance', 'date_declaration', 'type_sinistre',
    'cause_sinistre', 'statut_sinistre', 'montant_estime',
    'franchise', 'ville_sinistre', 'departement_sinistre',
    'region_sinistre', 'meteo_date', 'weather_code',
    'temperature_2m_max', 'temperature_2m_min',
    'precipitation_sum', 'wind_gusts_10m_max'
]

# Filtrage des colonnes présentes dans le DataFrame fusionné
df_fact_sinistre_meteo = df_fact[[col for col in colonnes_selectionnees if col in df_fact.columns]]

# 5. Export de la nouvelle table (équivalent du CREATE TABLE AS)
df_fact_sinistre_meteo.to_csv("fact_sinistre_meteo.csv", index=False)

#Affciher les 10 premières lignes de fact_sinistre_meteo

print(df_fact_sinistre_meteo.head(10))