import numpy as np

class Recommender:
    def __init__(self, metrika="kosinus"):
        self.metrika = metrika
        self.X = None # (n_prozvoda, n_atributa), standardizovano

        # standardizacija
        self.mean = 0.0
        self.std = 0.0


    def fit(self, X):
        """
            Pamti matricu proizvoda i parametre skaliranja
        """
        X = np.asarray(X, dtype=float)
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0)
        self.std[self.std == 0] = 1.0
        self.X = self.standardize(X)

        return self

    def slicni(self, indeks, n=5):
        """
            Vraca (indeksi, ocene) n najslicnijih proizvada proizvodu na poziciji indeks, bez njega samog
        """
        ocene = self.ocene_prema(self.X[indeks])

        ocene[indeks] = np.inf
        red = np.argsort(ocene)

        najbolji = red[:n]
        return najbolji, ocene[najbolji]

    def slicni_unosu(self, vektor, n=5):
        """Isto, ali za proizvod koji korisnik sam unese (sirove vrednosti)."""
        v = self.standardize(np.asarray(vektor, dtype=float))
        ocene = self.ocene_prema(v)
        red = np.argsort(ocene)
        return red[:n], ocene[red[:n]]

    # ---------- interno ----------

    def ocene_prema(self, v):
        """Slicnost (ili rastojanje) vektora v prema svim proizvodima."""
        if self.metrika == "kosinus":
            return self.kosinus(v)
        return self.euklid(v)

    def kosinus(self, v):
        """
            cos(a,b) = (a·b) / (|a|·|b|).  Manji ugao izmedju vektora daje veci kosinus, pa za ovu metriku veci kosinus znaci slicnije.
            Da uskladimo dve metrike, vracamo 1-cos, pa pomearmo opseg na [0-2], gde manja vrednost znaci (blizi) slicniji vektori
        """
        brojilac = self.X @ v # (n, m) @ (m, ) = (n, )
        # np.linalg.norm(self.X, axis=1) posto je shape (n, m)
        imenilac = np.linalg.norm(self.X, axis=1) * np.linalg.norm(v)
        imenilac[imenilac == 0] = 1e-12
        return 1 - (brojilac / imenilac) # 1-cos

    def euklid(self, v):
        """Euklidsko rastojanje. Manje = slicnije."""
        return np.linalg.norm(self.X - v, axis=1)

    def standardize(self, X):
        return (X - self.mean) / self.std