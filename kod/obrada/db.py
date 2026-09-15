import psycopg2
import pandas as pd
from konfiguracija import DB, CLEAN_SHEMA

# connect to the db
def connect():
    connection = psycopg2.connect(
        host=DB["host"],
        database=DB["database"],
        user=DB["user"],
        password=DB["password"],
        port=DB["port"],
    )
    return connection

def ucitaj_ponude(sema=CLEAN_SHEMA, tabela="ponuda"):

    conn = connect()
    try:
        return pd.read_sql(f"SELECT * FROM {sema}.{tabela}", conn)
    finally:
        conn.close()

def ucitaj_specs(sema=CLEAN_SHEMA):
    conn = connect()
    try:
        return pd.read_sql(f"SELECT * FROM {sema}.specifikacija", conn)
    finally:
        conn.close()