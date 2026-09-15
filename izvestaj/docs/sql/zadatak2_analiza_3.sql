SELECT COUNT(*) as klasa_iznad_c
FROM recommender_clean.ponuda
WHERE (ek_skala = 'nova' and ek_ocena in ('A', 'B', 'C'))
    OR (ek_skala = 'stara' and ek_ocena in ('A+', 'A++', 'A+++'));