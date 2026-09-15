CREATE SCHEMA IF NOT EXISTS recommender_raw;

CREATE TABLE recommender_raw.ponuda_raw (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_id TEXT NOT NULL,
  ean TEXT NOT NULL,
  naziv TEXT NOT NULL,
  kategorija_path TEXT NOT NULL,
  cena NUMERIC(12,2) NOT NULL,
  cena_redovna NUMERIC(12,2),
  dostupan boolean NOT NULL,
  opis TEXT,
  karakteristike TEXT,
  brend TEXT NOT NULL,
  energetska_klasa TEXT,
  izvor TEXT NOT NULL,
  slika TEXT NOT NULL,
  url TEXT NOT NULL,
  datum_preuzimanja DATE NOT NULL,
  UNIQUE (product_id, izvor)
);

CREATE INDEX ean_idx ON recommender_raw.ponuda_raw (ean);
CREATE INDEX ponuda_kategorija_idx ON recommender_raw.ponuda_raw (kategorija_path);
CREATE INDEX ponuda_brend_idx ON recommender_raw.ponuda_raw (brend);


CREATE TABLE recommender_raw.specifikacija (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ponuda_id bigint NOT NULL REFERENCES recommender_raw.ponuda_raw(id) ON DELETE CASCADE,
  naziv TEXT NOT NULL,
  vrednost TEXT,
  UNIQUE (ponuda_id, naziv)
);