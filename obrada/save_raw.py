import json
import re
import psycopg2
from datetime import datetime
from decimal import Decimal
from psycopg2.extras import execute_values

from obrada import db

DATUMI = {
    "gigatron.rs":    datetime(2026, 7, 23),
    "tehnomedija.rs": datetime(2026, 7, 26),
}

IZVORI = [
    ("../podaci/gigatron.jsonl", "gigatron.rs", DATUMI["gigatron.rs"]),
    ("../podaci/tehnomedija.jsonl", "tehnomedija.rs", DATUMI["tehnomedija.rs"]),
]

IZBACI_SPEC = {
    "NAV Category ID Description",
    "NAV Name",
    "NAV Model",
    "NAV Podsticaj",
    "Prava potrošača",
    "Vendor",
}

def ubaci_specifikacije(cursor, ponuda_id, specs):
    if not specs:
        return 0

    redovi = [(ponuda_id, naziv, vrednost) for naziv, vrednost in specs.items()]
    execute_values(
        cursor,
        "INSERT INTO recommender_raw.specifikacija (ponuda_id, naziv, vrednost) VALUES %s",
        redovi,
    )
    return len(redovi)

def ubaci_ponudu(cursor, x, cena_redovna, dostupan, karakteristike, izvor, datum):
    cursor.execute(
        """
        INSERT INTO recommender_raw.ponuda_raw (
            product_id, ean, naziv, kategorija_path, cena, cena_redovna, 
            dostupan, opis, karakteristike, brend, energetska_klasa, izvor, 
            slika, url, datum_preuzimanja
        )
       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
       RETURNING id
       """,
        (
            x["product_id"], x["ean"], x["naziv"], x["kategorija_path"],
            x["cena"], cena_redovna, dostupan, x.get("opis"),
            karakteristike, x["brend"], x.get("energetska_klasa"),
            izvor, x["slika"], x["url"], datum,
        ),
    )
    return cursor.fetchone()[0]


def parsiraj_mp_cenu(mp_raw):
    if not mp_raw:
        return None
    m = re.search(r"[\d.,]+", mp_raw)
    if not m:
        return None
    mp_clean = Decimal(m.group().replace(".", "").replace(",", "."))
    return mp_clean

def main():
    conn = None
    try:
        # open the connection
        conn = db.connect()

        # cursor
        cursor = conn.cursor()
        for putanja, izvor, datum in IZVORI:
            print(putanja, izvor, datum)
            with open(putanja, encoding="utf-8") as f:
                for linija in f:
                    x = json.loads(linija)
                    if izvor == "gigatron.rs":
                        cena_redovna = x.get("cena_redovna")
                    else:
                        cena_redovna = parsiraj_mp_cenu(x.get("cena_mp_raw"))

                    dostupan = x.get("dostupan")
                    if not isinstance(dostupan, bool):
                        dostupan = False
                    karakteristike = "\n".join(x.get("karakteristike") or []) or None
                    specs = {k: v for k, v in (x.get("specifikacije") or {}).items() if k not in IZBACI_SPEC}
                    new_row_id = ubaci_ponudu(cursor, x, cena_redovna, dostupan, karakteristike, izvor, datum)
                    ubaci_specifikacije(cursor, new_row_id, specs)
                conn.commit()
        # close the cursor
        cursor.close()
    except psycopg2.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
