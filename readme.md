# 🚀 Pipeline ETL Assurisk2 — Automatisation Sinistres & Météo

## 📋 Contexte et Objectif du Projet

Auparavant, la reconstruction de la table analytique finale (`fact_sinistre_meteo`) nécessitait une succession d'opérations manuelles dispersées entre DBeaver, des scripts SQL lancés individuellement, des imports CSV manuels et des fichiers JSON bruts. Ce processus était long, source d'erreurs humaines et difficilement reproductible.

**L'objectif de ce projet** est de unifier et d'automatiser l'intégralité de cette chaîne de traitement en **une seule commande**, en combinant le meilleur de deux technologies :
* **PostgreSQL (SQL)** : Création des schémas, purge des tables, nettoyage de la couche propre, rattachements géographiques et croisements analytiques.
* **Python** : Orchestration séquentielle, lecture et transformation des flux JSON, injection haute performance en mémoire, journalisation des temps d'exécution et audits automatisés de qualité des données.

---

## 🏗️ Architecture et Structure du Projet

```text
## 🏗️ Architecture et Structure du Projet

```text
Brief 12/
└── Compte rendu Brief 12/
    ├── sorties/                             # Dossier généré automatiquement au lancement
    │   ├── controles_python.csv             # Rapport d'audit technique Python
    │   ├── controles.csv                    # Résultats des audits SQL et contrôles qualité
    │   └── journal_pipeline.csv             # Historique et chronométrage de chaque étape
    └── sql/
        ├── 01_init.sql                      # Réinitialisation et purge (TRUNCATE CASCADE)
        ├── 02_clean.sql                     # Couche propre (clean_*) et traitement NULL / chaînes vides
        ├── 03_tables_meteo.sql              # Création des structures d'accueil météo
        ├── 04_rattachement.sql              # Rattachement géographique sinistres <-> villes (avec contrôle vides/NULL)
        ├── 05_croisement.sql                # Croisement final -> fact_sinistre_meteo
        ├── 06_controles.sql                 # Requêtes SQL de contrôle qualité (villes, météo, montants, dates)
        ├── meteo_30_villes.json             # Cache local des données météo (30 villes)
        ├── pipeline.py                      # Script principal d'orchestration hybride
        ├── pipeline_sauvegarde.py           # Copie de sauvegarde du script d'orchestration
        └── villes_coordonnees_meteo.csv     # Référentiel géographique des villes
---

## ⚙️ Fonctionnement de la Chaîne Hybride (`pipeline.py`)

Le pipeline s'exécute de manière strictement séquentielle en trois phases :

1. **Initialisation & Préparation SQL (`01` à `03`)**
   * Création sécurisée du répertoire de sortie (`os.makedirs("sorties", exist_ok=True)`).
   * Purge instantanée de la base via `TRUNCATE fact_sinistre CASCADE;` pour garantir un environnement vierge.
   * Nettoyage des données sources et création des tables d'attente météorologiques.
2. **Collecte, Transformation & Injection Python**
   * **Garde intelligente anti-API** : Vérification via `os.path.exists()` de la présence locale de `meteo_30_villes.json`. L'API Open-Meteo n'est interrogée que si le fichier local est absent, protégeant ainsi le service contre la surcharge et le blocage de quotas (*rate limiting*).
   * Transformation du JSON en DataFrame `pandas` et injection massive en base via un tampon mémoire (`io.StringIO`) et la commande `COPY ... FROM STDIN`.
3. **Rattachement, Croisement & Audits Finaux (`04` à `06`)**
   * Exécution des jointures géographiques et temporelles pour alimenter `fact_sinistre_meteo`.
   * Lancement automatique de la batterie de tests d'intégrité (Python + SQL) et export des journaux CSV.

---

## 🛠️ Prérequis et Installation

### Technologies requises
* **Python 3.10+**
* **PostgreSQL 14+**

### Dépendances Python
Installez les bibliothèques nécessaires via `pip` :
```bash
pip install pandas psycopg2-binary requests
```

---

## 🚀 Exécution

1. Vérifiez que votre serveur **PostgreSQL** est démarré et que les identifiants de connexion dans `pipeline.py` correspondent à votre base locale.
2. Placez-vous dans le répertoire du projet et lancez la commande unique :
```bash
python pipeline.py
```

---

## 🛡️ Garanties Qualité et Métriques Cibles

### 1. Idempotence
Le pipeline est **100 % idempotent** : grâce à la purge initiale en cascade (`TRUNCATE ... CASCADE`) et à la gestion sécurisée des dossiers (`exist_ok=True`), il peut être relancé un nombre illimité de fois d'affilée sans jamais créer de doublons ni corrompre l'historique.

### 2. Indicateurs de Validation (`fact_sinistre_meteo`)
À l'issue de chaque exécution, les audits automatisés valident les seuils critiques suivants :
* **Volumétrie finale exacte** : `12 098` lignes consolidées.
* **Complétude météorologique** : `0` sinistre sans code météo (`weather_code IS NULL`).
* **Unicité stricte** : `0` doublon sur les identifiants de sinistres ou sur le couple `(ville, date)`.

### 3. Traçabilité et Diagnostic
En cas d'anomalie ou d'interruption (fichier manquant, erreur SQL), le script s'arrête immédiatement sur l'étape fautive sans corrompre la base, et le fichier `sorties/journal_pipeline.csv` permet d'identifier instantanément l'étape incriminée ainsi que les temps de traitement de chaque brique.