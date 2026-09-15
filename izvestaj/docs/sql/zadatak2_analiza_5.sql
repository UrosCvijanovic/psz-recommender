SELECT naziv, brend, cena, ek_ocena, ek_skala, izvor
FROM recommender_clean.ponuda
WHERE kategorija = 'televizori'
ORDER BY cena DESC
LIMIT 30;