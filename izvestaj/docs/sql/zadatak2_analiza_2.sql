SELECT brend, COUNT(*) as top10_brend
FROM recommender_clean.ponuda
GROUP BY brend
ORDER BY top10_brend DESC
LIMIT 10;