import pandas as pd
import psycopg2
import warnings
from getpass import getpass

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

mot_de_passe = getpass("Mot de passe PostgreSQL : ")
connexion = psycopg2.connect(host="localhost", port=5432, dbname="assurisk2",
user="postgres", password=mot_de_passe)

df = pd.read_sql("SELECT * FROM fact_sinistre_meteo", connexion)
df["montant_estime"]   = df["montant_estime"].astype(float)
df["franchise"]        = df["franchise"].astype(float)
df["date_survenance"]  = pd.to_datetime(df["date_survenance"])
df["date_declaration"] = pd.to_datetime(df["date_declaration"])

# Affichage des 10 premières lignes du DataFrame
print(df.head(10))
# Affichage des dimensions du DataFrame
print(df.shape)

#1. Combien de lignes et combien de colonnes compte la table ?
print("Affichage des dimensions de la table :")
print(f"Nombre de lignes : {df.shape[0]}")
print(f"Nombre de colonnes : {df.shape[1]}")

#2. Y a-t-il des valeurs manquantes ? Si oui, dans quelles colonnes ?
print("Valeurs manquantes par colonne :")
print(df.isnull().sum())

#3. Quel est le montant le plus faible de la table, et le plus élevé ?
print(f"Montant le plus faible : {df['montant_estime'].min()}")
print(f"Montant le plus élevé : {df['montant_estime'].max()}")

#4. Combien de types de sinistre différents y a-t-il ?
print(f"Nombre de types de sinistre différents : {df['type_sinistre'].nunique()}")

#5. Quelle est la moyenne et la médiane de la colonne 'montant_estime' ?
print(f"Moyenne : {df['montant_estime'].mean()}")
print(f"Médiane : {df['montant_estime'].median()}")

#6. Quelle est la moyenne et la médiane de la colonne 'franchise' ?
#Appliquez à la colonnefranchise le réflexe du cours de ce matin :
#Quand la moyenne et la médiane s’écartent, il y a quelque chose à
#comprendre. Et la réponse est presque toujours dans un groupby
#Faites donc ce groupby sur la franchise , groupée par type de sinistre, et
#affichez la moyenne et la médiane de chaque type.
df.groupby("type_sinistre")["franchise"].agg(["mean", "median"])
print("Moyenne et médiane de la franchise par type de sinistre :")
print(df.groupby("type_sinistre")["franchise"].agg(["mean", "median"]))

#7.Faites le même groupby sur la colonne montant_estime au lieu de franchise.
#Comparez les deux tableaux. Lequel des deux ressemble à un barème fixe, 
#et lequel ressemble à de vrais montants qui varient.
df.groupby("type_sinistre")["montant_estime"].agg(["mean", "median"])
print("Moyenne et médiane du montant estimé par type de sinistre :")
print(df.groupby("type_sinistre")["montant_estime"].agg(["mean", "median"]))

#8.Un outil dont vous aurez besoin pour la case 4

df["type_sinistre"].value_counts(normalize=True)

#normalize=True rend des parts (entre 0 et 1) au lieu de comptes. 
#Multipliez par 100 pour avoir des pourcentages.
print("Pourcentages des types de sinistre :")
print(df["type_sinistre"].value_counts(normalize=True)* 100)

#9.Calcule le pourcentage de chaque sinistre à l'intérieur de chaque ville
pourcentages_ville = (
    df.groupby("ville_sinistre")["type_sinistre"]
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
    .unstack()
)

print(pourcentages_ville[["Dégât des eaux"]])


#10.Calcule le nombre de chaque sinistre à l'intérieur de chaque ville
frequence_ville = (
    df.groupby("ville_sinistre")["type_sinistre"]
    .value_counts()
    .unstack()
)
print(frequence_ville[["Dégât des eaux"]])

#11.Affiche le nombre de sinistres de type "Dégât des eaux" pour chaque ville
#On choisit 5 villes : Lille, Aix-en-Provence, Marseille, Lyon et Toulouse

lille = df[df["ville_sinistre"] == "Lille"]
print("frequence des types de sinistre à Lille :")
print(lille["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

print("frequence des types de sinistre à Aix-en-Provence :")
aix= df[df["ville_sinistre"] == "Aix-en-Provence"]
print(aix["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

print("frequence des types de sinistre à Marseille :")
marseille = df[df["ville_sinistre"] == "Marseille"]
print(marseille["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

print("frequence des types de sinistre à Lyon :")
lyon = df[df["ville_sinistre"] == "Lyon"]
print(lyon["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

print("frequence des types de sinistre à Toulouse :")
toulouse = df[df["ville_sinistre"] == "Toulouse"]
print(toulouse["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

#12.Faites-le proprement sur les trente villes d’un coup, et affichez le minimum et le 
#maximum de la part du dégât des eaux.

print("Pourcentage de sinistres de type 'Dégât des eaux' pour les 30 villes :")
part = (df.groupby("ville_sinistre")["type_sinistre"]
.apply(lambda s: s.value_counts(normalize=True).mul(100).round(1)))
print(part.xs("Dégât des eaux", level=1).describe())

#13.Pour obtenir ces chiffres et mettre en évidence ce pic exceptionnel en octobre 2025, 
#le code Python s'articule autour de la conversion des dates,
#du regroupement par mois et du calcul des effectifs.

#13.1.S'assurer que la colonne de date est bien au format datetime
df['date_sinistre'] = pd.to_datetime(df['date_survenance'])

#13.2. Extraire l'année et le mois (format 'YYYY-MM') et compter les sinistres par mois
sinistres_par_mois = df['date_sinistre'].dt.to_period('M').value_counts().sort_values(ascending=False)

#13.3.Afficher les mois les plus chargés (pour voir octobre 2025 en 1ère position et le 2e)
print("Top des mois les plus chargés :")
print(sinistres_par_mois.head(5))

#13.4.Calculer un indicateur de 'mois ordinaire' (la médiane hors pics)
print("\nMédiane des sinistres par mois (mois ordinaire) :")
print(sinistres_par_mois.median())

#14.Comment isoler le mois d’octobre 2025

octobre_2025 = df[(df["date_survenance"] >= "2025-10-01") & (df["date_survenance"] <= "2025-10-31")]
reste = df[~df.index.isin(octobre_2025.index)]
print("Nombre de sinistres en octobre 2025 :", len(octobre_2025))
print("Nombre de sinistres hors octobre 2025 :", len(reste))

#15.Le code Python pour les 3 hypothèses question 3 de l'enquête

# ==========================================
# HYPOTHÈSE 1 : La nature des sinistres
# ==========================================
print("--- 1. Part des types de sinistres en octobre 2025 (%) ---")
repartition_types = octobre_2025['type_sinistre'].value_counts(normalize=True).mul(100).round(1)
print(repartition_types)


# ==========================================
# HYPOTHÈSE 2 : La concentration géographique
# ==========================================
print("\n--- 2. Top 10 des villes les plus touchées en octobre 2025 ---")
# Croiser les villes et les types de sinistres pour octobre 2025
detail_villes_octobre = (
    octobre_2025.groupby(['ville_sinistre', 'type_sinistre'])
    .size()
    .unstack(fill_value=0)
)

# Ajouter une colonne Total pour trier par les villes les plus touchées
detail_villes_octobre['Total'] = detail_villes_octobre.sum(axis=1)
detail_villes_octobre = detail_villes_octobre.sort_values(by='Total', ascending=False)

print(detail_villes_octobre.head(10))


# ==========================================
# HYPOTHÈSE 3 : Le pic journalier (étalé ou brutal)
# ==========================================
print("\n--- 3. Les 5 jours les plus chargés d'octobre 2025 ---")
pic_journalier = octobre_2025.groupby(octobre_2025['date_survenance']).size().sort_values(ascending=False)
print(pic_journalier.head(5))

#Rappel des notions du cours de ce matin : .shape, .head(), .isna().sum(), .describe(), .value_counts(), groupby()  

#.shape : Renvoie la taille du tableau sous forme de couple (nombre_de_lignes, 
# nombre_de_colonnes). C'est un attribut (sans parenthèses). 
# Exemple : (12098, 8) signifie 12 098 lignes et 8 colonnes.

#.head() : Affiche les 5 premières lignes par défaut (ou n lignes si vous précisez .head(10)). 
#Utile pour vérifier l'aspect des données et les noms de colonnes.

#.isna().sum() : Compte le nombre de valeurs manquantes (NaN ou None) dans chaque colonne. 
# Permet de repérer immédiatement les colonnes incomplètes avant de nettoyer ou calculer.

#.describe() : Calcule des statistiques descriptives rapides sur les colonnes numériques : 
# effectif (count), moyenne (mean), écart-type (std), minimum (min), 
# quartiles (25%, 50% médiane, 75%) et maximum (max).

#.value_counts() : Compte la fréquence d'apparition de chaque valeur unique dans une colonne 
# (souvent du texte ou des catégories). Par défaut, trie du plus fréquent au moins fréquent ; 
# avec normalize=True, donne les proportions (ex. : parts en pourcentage).

#groupby() : Regroupe les lignes selon une ou plusieurs colonnes 
# (ex. par région ou par type de sinistre) pour appliquer ensuite un calcul sur chaque groupe 
# (somme .sum(), moyenne .mean(), comptage .count(), etc.).

#16.Choix de la colonnne region_sinistre et application des six commandes du cours
#.shape, .head(), .isna().sum(), .describe(), .value_counts(), groupby()
print("Application des six commandes sur la colonne 'region_sinistre' :")
# Application de .shape
df['region_sinistre'].shape
print("Application de .shape :")
print(df['region_sinistre'].shape)

# Application de .head()
df['region_sinistre'].head()
print("\nApplication de .head() :")
print(df['region_sinistre'].head())

# Application de .isna().sum()
df['region_sinistre'].isna().sum()
print("\nApplication de .isna().sum() :")
print(df['region_sinistre'].isna().sum())

# Application de .describe()
df['region_sinistre'].describe()
print("\nApplication de .describe() :")
print(df['region_sinistre'].describe())

# Application de .value_counts()
df['region_sinistre'].value_counts()
print("\nApplication de .value_counts() :")
print(df['region_sinistre'].value_counts())

# Application de .groupby('region_sinistre').size()
df.groupby('region_sinistre').size()
print("\nApplication de .groupby('region_sinistre').size() :")
print(df.groupby('region_sinistre').size())

#17.Prenez une deuxième colonne et refaites l’étape 3 : j'ai choisi la colonne weather_code
#.shape, .head(), .isna().sum(), .describe(), .value_counts(), groupby()
print("\nApplication des six commandes sur la colonne 'weather_code' :")
# Application de .shape
df['weather_code'].shape
print("Application de .shape :")
print(df['weather_code'].shape)

# Application de .head()
df['weather_code'].head()
print("\nApplication de .head() :")
print(df['weather_code'].head())

# Application de .isna().sum()
df['weather_code'].isna().sum()
print("\nApplication de .isna().sum() :")
print(df['weather_code'].isna().sum())

# Application de .describe()
df['weather_code'].describe()
print("\nApplication de .describe() :")
print(df['weather_code'].describe())

# Application de .value_counts()
df['weather_code'].value_counts()
print("\nApplication de .value_counts() :")
print(df['weather_code'].value_counts())

# Application de .groupby('weather_code').size()
df.groupby('weather_code').size()
print("\nApplication de .groupby('weather_code').size() :")
print(df.groupby('weather_code').size())

print("\nExploration terminée. Vous pouvez maintenant analyser les résultats)")