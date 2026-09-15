SELECT kategorija, COUNT(*) as broj_po_kategoriji
FROM recommender_clean.ponuda
GROUP BY kategorija
ORDER BY broj_po_kategoriji DESC;