CREATE SCHEMA IF NOT EXISTS recommender_clean;

CREATE TABLE recommender_clean.ponuda (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_id TEXT NOT NULL,
  raw_id BIGINT NOT NULL UNIQUE,
  ean TEXT NOT NULL,
  naziv TEXT NOT NULL,
  kategorija TEXT NOT NULL,
  cena NUMERIC(12,2) NOT NULL,
  cena_redovna NUMERIC(12,2),
  dostupan boolean NOT NULL,
  opis TEXT,
  karakteristike TEXT,
  brend TEXT NOT NULL,
  ek_ocena TEXT,
  ek_skala TEXT,
  izvor TEXT NOT NULL,
  slika TEXT NOT NULL,
  url TEXT NOT NULL,
  datum_preuzimanja DATE NOT NULL,
  UNIQUE (product_id, izvor)
);

CREATE INDEX clean_ean_idx ON recommender_clean.ponuda (ean);
CREATE INDEX clean_ponuda_kategorija_idx ON recommender_clean.ponuda (kategorija);
CREATE INDEX clean_ponuda_brend_idx ON recommender_clean.ponuda (brend);
CREATE INDEX clean_ponuda_cena_idx ON recommender_clean.ponuda (cena);


CREATE TABLE recommender_clean.specifikacija (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ponuda_id bigint NOT NULL REFERENCES recommender_clean.ponuda(id) ON DELETE CASCADE,
  naziv TEXT NOT NULL,
  vrednost TEXT,
  UNIQUE (ponuda_id, naziv)
);