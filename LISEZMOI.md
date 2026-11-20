# Pipeline AssurRisk

Ce projet exécute l'initialisation SQL, charge les données météo (`meteo_30_villes.json` et `villes_coordonnees_meteo.csv`), lance le croisement et les contrôles qualité dans PostgreSQL (`assurisk2`), puis génère les fichiers de suivi et d'audit dans `sorties/`.

## Ordre d'exécution
1. `01_init.sql` : réinitialise la base.
2. `02_clean.sql` : construit la couche propre.
3. `03_tables_meteo.sql` : crée les tables prévues pour la météo.
4. `pipeline.py` (étape Python) : charge le JSON météo et le CSV des villes, les injecte dans PostgreSQL, puis enchaîne `04_rattachement.sql` (rattachement météo/sinistres), `05_croisement.sql` (`fact_sinistre_meteo`) et `06_controles.sql` (contrôles de cohérence).

## Lancement
Placez-vous dans le dossier contenant `pipeline.py` et les fichiers `.sql`, puis lancez :
`python pipeline.py`