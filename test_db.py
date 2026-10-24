import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")

with psycopg.connect(url) as conn:
    rows = conn.execute("SELECT id, full_name FROM customers").fetchall()
    for row in rows:
        print(row)