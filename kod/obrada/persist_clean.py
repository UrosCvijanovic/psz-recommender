import psycopg2
from obrada import db
from psycopg2.extras import execute_values
from obrada.preprocessing import preprocess_engine


def napuni_ponude(cursor, ponude):
    """
        Upisuje ponude, vraca mapu raw_id -> novi id.
    """
    # pandas NaN vrednosti u SQL NULL
    ponude = ponude.astype(object).where(ponude.notna(), None)
    mapa = {}
    for _, x in ponude.iterrows():
        cursor.execute("""
            INSERT INTO recommender_clean.ponuda (
               raw_id, product_id, ean, naziv, kategorija, cena, cena_redovna, 
               dostupan, opis, karakteristike, brend, ek_ocena, ek_skala, 
               izvor, slika, url, datum_preuzimanja
            )  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            x["id"], x["product_id"], x["ean"], x["naziv"], x["kategorija"],
            x["cena"], x["cena_redovna"], x["dostupan"], x["opis"],
            x["karakteristike"], x["brend"], x["ek_ocena"], x["ek_skala"],
            x["izvor"], x["slika"], x["url"], x["datum_preuzimanja"]
        ))
        mapa[x["id"]] = cursor.fetchone()[0]
    return mapa

def napuni_specifikacije(cursor, specs, mapa):
    redovi = []
    for _, s in specs.iterrows():
        novi_id = mapa.get(s["ponuda_id"])
        if novi_id is None:
            continue
        redovi.append((novi_id, s["naziv"], s["vrednost"]))
    execute_values(cursor, "INSERT INTO recommender_clean.specifikacija (ponuda_id, naziv, vrednost) VALUES %s", redovi)
    return len(redovi)

def main():
    conn = None
    try:
        # open the connection
        conn = db.connect()
        ponuda, specs = preprocess_engine()
        # cursor
        cursor = conn.cursor()

        idx_map = napuni_ponude(cursor, ponuda)
        n = napuni_specifikacije(cursor, specs, idx_map)

        print(f"ponude: {len(idx_map)} | specifikacije: {n}")

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