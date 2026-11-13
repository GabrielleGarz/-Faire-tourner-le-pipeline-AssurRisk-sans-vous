JOUR 1 — LUNDI 9 : Remise en main Python, Rappel & JSON
1. Rappel des bases Python (rappel_22_octobre.py)
Ce qu’elle fait : Réactive les notions fondamentales de Python sans dépendance externe (manipulation de listes, de dictionnaires via .items(), de boucles for, et gestion d'erreurs d'indentation ou d'indices).

Ce qu’elle produit : Des affichages console validant l'ajout d'éléments (append), la structure des paires clés-valeurs, et l'analyse de messages d'erreur (IndexError, ValueError, IndentationError).

Ce qu’elle contrôle : La maîtrise de la syntaxe de base indispensable pour parcourir et structurer les futurs fichiers de configuration du pipeline.

Ce qui se passe si elle échoue : Le script lève une exception bloquante qui permet d'apprendre à lire une trace d'erreur (numéro de ligne et type d'anomalie) pour corriger le code.

2. L’inventaire, chronomètre en main (Première approche de la purge et des données)
Ce qu’elle fait : Exécute manuellement la reconstruction de la base dans DBeaver en appliquant notamment la commande TRUNCATE fact_sinistre CASCADE; pour purger instantanément la table des sinistres et ses dépendances (fact_indemnisation), puis réalise les imports séquentiels.

Ce qu’elle produit : Une base vidée proprement et un relevé métrique quantitatif (temps total au chronomètre, nombre de fichiers ouverts).

Ce qu’elle contrôle : La conscience empirique de la complexité humaine et la nécessité d'utiliser TRUNCATE ... CASCADE pour réinitialiser l'environnement sans laisser de résidus.

Ce qui se passe si elle échoue : L'oubli d'une purge ou d'un ordre d'import fausse l'état de la base et génère des erreurs de contraintes d'intégrité (clés étrangères).

3. Vous le refaites (pipeline.py minimal et TRUNCATE)
Ce qu’elle fait : Crée et exécute un premier script Python minimaliste se connectant à PostgreSQL avec autocommit=True pour automatiser la réinitialisation de la base (intégrant le TRUNCATE initial).

Ce qu’elle produit : Une base de données remise à zéro (vérifiée à 12 490 lignes dans DBeaver) et un temps d'exécution mesuré (0,006 s).

Ce qu’elle contrôle : La bonne communication entre le script Python, le pilote psycopg2 et la bonne exécution des requêtes de purge SQL.

Ce qui se passe si elle échoue : Le script s'arrête net (erreur de connexion ou d'authentification) et la base n'est pas nettoyée.

4. Du JSON au tableau
Ce qu’elle fait : Charge le fichier JSON brut (meteo_30_villes.json), extrait les dictionnaires internes via une boucle, transforme chaque bloc journalier en DataFrame pandas, et les assemble via pd.concat.

Ce qu’elle produit : Un tableau tabulaire global de données météorologiques dont les dimensions sont vérifiées par la propriété .shape.

Ce qu’elle contrôle : La structure des clés du JSON (latitude, longitude, daily) et la cohérence volumétrique globale du jeu de données (30 villes multipliées par le nombre de jours).

Ce qui se passe si elle échoue : Une erreur de type FileNotFoundError ou une rupture dans la liste accumulée (morceaux) bloque la transformation, empêchant de constituer le tableau prêt pour l'injection.

5. Reprise
Ce qu’elle fait : Consolide les acquis de la journée, finalise les scripts restants en suspens et permet l'entraide collaborative au sein du binôme.

Ce qu’elle produit : Un état de l'art stabilisé et fonctionnel de tous les exercices du lundi avant d'attaquer l'enchaînement automatisé du mardi.

Ce qu’elle contrôle : L'absence de lacunes individuelles sur les prérequis fondamentaux en Python et en manipulation de structures de données.

Ce qui se passe si elle échoue : Le retard s'accumule sur les notions de base, compromettant la compréhension des briques d'automatisation et d'architecture des jours suivants.

JOUR 2 — MARDI 10 : La chaîne s'enchaîne toute seule

1. Ranger, numéroter et ordonner les scripts SQL (01_init.sql à 06_controles.sql)
Ce qu’elle fait : Classe et renomme les scripts SQL de manière séquentielle pour respecter les dépendances de l'architecture de données.

Ce qu’elle produit : Une suite logique de fichiers prêts à l'exécution automatisée sans rupture relationnelle.

Ce qu’elle contrôle : Le respect de l'ordre technique (par exemple, prouvant que 04_rattachement.sql ne peut tourner avant que la météo ne soit chargée, ou que lancer 02_clean.sql avant 01_init.sql lève une erreur de table inexistante).

Ce qui se passe si elle échoue : Une erreur de dépendance s'affiche en base de données (UndefinedTable), bloquant instantanément le flux.

2. Purge et réinitialisation de la base (TRUNCATE fact_sinistre CASCADE;)
Ce qu’elle fait : Exécute la commande ultra-rapide TRUNCATE fact_sinistre CASCADE; pour vider instantanément la table des sinistres et répercuter le nettoyage sur toutes les tables dépendantes (comme fact_indemnisation).

Ce qu’elle produit : Une remise à zéro de la volumétrie (passant par exemple de 12 490 lignes à 0), confirmée par les messages d'information de PostgreSQL (NOTICE).

Ce qu’elle contrôle : L'état initial sain de la base de données et l'absence totale de résidus ou de doublons provenant d'exécutions antérieures.

Ce qui se passe si elle échoue : Sans ce nettoyage en cascade, les exécutions successives génèrent des violations de contraintes d'intégrité et accumulent des doublons en base.

3. Automatisation par liste et boucle Python (pipeline.py)
Ce qu’elle fait : Transforme la séquence des fichiers SQL en une structure de données Python (liste de tuples) et parcourt cette liste via une boucle for pour ouvrir, lire (open().read()) et exécuter chaque requête séquentiellement via le curseur.

Ce qu’elle produit : L'enchaînement automatisé et sans intervention manuelle des scripts de staging et de nettoyage.

Ce qu’elle contrôle : La syntaxe du parcours de tuples, l'encodage des fichiers (utf-8) et la transmission correcte des requêtes au SGBD.

Ce qui se passe si elle échoue : Le script lève une exception (comme un FileNotFoundError si un nom de fichier est erroné) et interrompt net l'exécution.

4. Journalisation et chronométrage des performances (journal_pipeline.csv)
Ce qu’elle fait : Mesure le temps d'exécution de chaque script SQL à l'aide du module time (time.time() - debut), affiche l'avancement en console, et consolide les résultats dans un fichier CSV de suivi (sorties/journal_pipeline.csv).

Ce qu’elle produit : Le fichier d'historisation détaillé consignant le nom du fichier, le libellé de l'étape, l'outil (SQL) et la durée en secondes (mettant en évidence que 01_init.sql est l'étape la plus lourde, autour de 63 à 89 secondes).

Ce qu’elle contrôle : La traçabilité globale des performances et l'identification des goulets d'étranglement SGBD ou système.

Ce qui se passe si elle échoue : En cas de plantage d'une étape, le journal s'interrompt à l'instant exact de l'erreur, fournissant un indicateur précis du point de rupture.

5. Contrôles intermédiaires de volumétrie
Ce qu’elle fait : Insère des requêtes de comptage ciblées en Python via pd.read_sql (par exemple après 02_clean.sql) pour valider les volumes intermédiaires à la volée.

Ce qu’elle produit : Des affichages de contrôle en console validant la conformité du nombre de lignes traitées par rapport aux attentes (ex. vérification des 12 490 lignes propres).

Ce qu’elle contrôle : Le bon comportement des filtres appliqués dans les scripts de nettoyage et l'absence de pertes de données inattendues.

Ce qui se passe si elle échoue : Un contrôle placé uniquement à la fin indique qu'il y a un problème global, mais ne dit pas où l'anomalie s'est produite. Les contrôles intermédiaires permettent d'isoler immédiatement l'étape défectueuse (ex. soupçonner en premier 02_clean.sql si le volume est faux).

6. Validation de rejouabilité
Ce qu’elle fait : Relance l'intégralité du pipeline deux fois d'affilée pour comparer les journaux et vérifier la stabilité des sorties.

Ce qu’elle produit : Deux séries de résultats aux comptages de lignes strictement identiques, malgré des variations de temps d'exécution liées à la charge du SGBD.

Ce qu’elle contrôle : grâce au TRUNCATE initial, le pipeline peut être relancé n'importe quel nombre de fois sans risque de dupliquer les données, de corrompre l'historique ou de laisser des résidus.

Ce qui se passe si elle échoue : Si le script n'était pas idempotent (absence de nettoyage préalable), chaque nouveau lancement accumulerait des données et fausserait l'ensemble des indicateurs de l'entreprise.

JOUR 3 — JEUDI 12 : La météo entre dans la chaîne
1. Injection performante des DataFrames en base (COPY STDIN avec io.StringIO)
Ce qu’elle fait : Sérialise les DataFrames pandas (météo et coordonnées des villes) dans un tampon mémoire (io.StringIO()) et pousse massivement les données vers PostgreSQL via la méthode ultra-rapide curseur.copy_expert("COPY ... FROM STDIN WITH (FORMAT csv)", tampon).

Ce qu’elle produit : L'alimentation complète des tables cibles en base (par exemple 21 930 lignes injectées dans meteo_assurrisk).

Ce qu’elle contrôle : Le format des flux de données et la stricte correspondance entre l'ordre des colonnes du DataFrame et celui de la table SQL (l'en-tête étant ignoré grâce à header=False et index=False).

Ce qui se passe si elle échoue : Une erreur de type DataError ou d'incompatibilité de structure bloque le transfert des données en mémoire vers le serveur SGBD.

2. La garde intelligente anti-API (os.path.exists)
Ce qu’elle fait : Vérifie par programmation si le fichier meteo_30_villes.json est déjà présent localement sur le disque avant de décider d'interroger ou non l'API Open-Meteo.

Ce qu’elle produit : Un aiguillage conditionnel (Cas 1 : chargement direct local / Cas 2 : appel réseau distant si absent) accompagné d'un message d'information explicite dans les logs.

Ce qu’elle contrôle : L'utilisation rationnelle des ressources réseau et la protection contre le dépassement des quotas distants (rate limiting) en cas de lancements multiples, notamment en salle de cours.

Ce ki se passe si elle échoue : En l'absence de garde, chaque exécution de script déclenche des requêtes simultanées redondantes vers l'API, risquant de saturer le serveur distant et de bloquer les utilisateurs.

3. Structuration hybride de l'orchestration en deux boucles
Ce qu’elle fait : Découpe le script d'orchestration global en deux blocs distincts (la première partie SQL amont -> l'étape intermédiaire Python d'appel et d'injection météo -> la seconde partie SQL aval).

Ce qu’elle produit : Un pipeline unifié, séquentiel et cohérent alternant les outils selon les besoins du traitement.

Ce qu’elle contrôle : Le respect absolu des dépendances techniques : s'assurer que les tables mères et les structures de staging sont créées (SQL), que les données externes sont transformées et injectées (Python), avant de lancer les jointures et calculs finaux (SQL).

Ce qui se passe si elle échoue : Une mauvaise imbrication ou une fusion en une seule boucle provoque des erreurs de dépendance en base, car les scripts SQL aval tentent d'exploiter des tables ou des données qui n'existent pas encore.

4. Rattachement et croisement de la chaîne (04_rattachement.sql et 05_croisement.sql)
Ce qu’elle fait : Intègre les scripts de rattachement géographique et de croisement des sinistres avec la météo dans la seconde liste d'exécution du pipeline, en mesurant leur durée unitaire.

Ce qu’elle produit : L'exécution des jointures complexes et la création de la table finale consolidée (fact_sinistre_meteo).

Ce qu’elle contrôle : La cohérence des données croisées et la bonne application des règles de gestion entre les sinistres propres et les relevés climatiques.

Ce qui se passe si elle échoue : Le pipeline s'interrompt ou la table finale n'est pas alimentée correctement, empêchant d'atteindre les indicateurs cibles.

5. Test global et validation des indicateurs de référence (fact_sinistre_meteo)
Ce qu’elle fait : Efface l'environnement et relance l'intégralité du pipeline de bout en bout pour confronter le résultat réel aux attendus métiers stricts.

Ce qu’elle produit : La table finale fact_sinistre_meteo auditable et prête pour l'analyse.

Ce qu’elle contrôle : Les métriques absolues de qualité et de volumétrie : exactement 12 098 lignes finales, 0 valeur nulle sur les codes météo (weather_code IS NULL), et 0 doublon sur le couple (ville, date).

Ce qui se passe si elle échoue : Toute divergence par rapport à ces seuils impose de remonter le fil des contrôles étape par étape pour identifier l'anomalie d'origine sans corriger au hasard.

6. Génération des contrôles Python et audit complet de qualité des données (controles_python.csv et requêtes d'audit SQL)
Ce qu’elle fait : Exécute une batterie de vérifications automatisées à la fois côté Python (via un tableau comparant les valeurs observées et attendues : garde du fichier local, nombre de villes, volumétrie des DataFrames) et côté SQL (via un dictionnaire de requêtes d'audit ciblées pour détecter d'éventuels doublons sur les tables de dimension et de faits, ainsi que les sinistres orphelins de météo weather_code IS NULL), puis consigne les résultats dans un fichier CSV de traçabilité (../sorties/controles_python.csv) et affiche un rapport synthétique en console.

Ce qu’elle produit : Le fichier de suivi controles_python.csv structuré avec les colonnes controle, objet, valeur_observee et attendu, ainsi qu'un affichage console listant chaque indicateur d'audit et son nombre de lignes de résultat (garantissant par exemple 0 ligne pour les doublons ou les valeurs manquantes).

Ce qu’elle contrôle : L'intégrité globale du pipeline, la conformité des données chargées en mémoire avant injection, l'unicité des identifiants (sinistre_id, contrat_id, garantie_id, etc.) pour éviter toute duplication, et la robustesse des jointures entre les données assurancielles et météorologiques.

Ce qui se passe si elle échoue : Le script lève une erreur d'exécution SQL (en cas de syntaxe incorrecte dans les requêtes d'audit) ou met en évidence des anomalies quantitatives (lignes de résultat supérieures à 0 sur les contrôles de doublons ou de valeurs nulles), signalant immédiatement une non-conformité dans la qualité des données du pipeline.

JOUR 4 — VENDREDI 13 : Livrer et montrer
1. Gestion sécurisée des répertoires de sortie (os.makedirs("sorties", exist_ok=True))
Ce qu’elle fait : Initialise et crée par programmation le dossier de stockage (sorties/) dès le lancement du script Python pour y centraliser les livrables (journal_pipeline.csv, controles.csv, etc.).

Ce qu’elle produit : Le répertoire physique prêt à recevoir les fichiers de suivi, garantissant que les écritures ultérieures par pandas s'exécuteront sans encombre.

Ce qu’elle contrôle : L'existence préalable du chemin cible et la propriété d'idempotence des répertoires, permettant de relancer le script à l'infini sans intervention manuelle.

Ce qui se passe si elle échoue : Sans l'argument exist_ok=True, la seconde exécution consécutive du pipeline se solde immédiatement par une erreur bloquante de type FileExistsError (code d'erreur Windows 183), interrompant net le traitement avant même qu'il ne commence.