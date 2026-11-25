import sys
import io

# Forcer l'encodage UTF-8 pour la sortie standard et les chemins
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import psycopg2

conn = psycopg2.connect(
    dbname="assurrisk2",
    user="utilisateur",
    password="gaby1967",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

with open("script.sql", "r", encoding="utf-8-sig") as f:
    cur.execute(f.read())

conn.commit()
cur.close()
conn.close()