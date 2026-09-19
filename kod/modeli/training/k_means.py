import matplotlib.pyplot as plt
import numpy as np

SEEDOVI = (77, 1, 7, 42, 123)

class KMeans:
    def __init__(self, k=3, n_iters: int = 1000, tezine = None, tol=1e-4, seed=714, debug = False) -> None:
        self.debug = debug
        self.k = k # hiperparametar k
        self.n_iters = n_iters
        self.tolerance = tol # prag pomeranja centara za zaustavljanje
        self.seed = seed
        self.tezine = tezine

        self.centroids = None # (k, n_atrubuta)
        self.labels = None
        self.sum_squared_distance = None
        self.silhouette_score = None

        # standardizacija
        self.mean = 0.0
        self.std = 0.0


    def fit(self, X):
        X = np.asarray(X, dtype=float)

        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0)
        self.std[self.std == 0] = 1

        X = self.standardize(X)

        if self.tezine is not None:
            X = X * self.tezine
        n_uzoraka, n_atributa = X.shape # X shape [N, f]

        # 1. initialize - randomly select clusters
        self.initialize(X, n_uzoraka)

        for step in range(self.n_iters):
            # 2. clusterization
            klase = self.clusterize(X)

            # 3. reposition centroids
            stari = self.centroids.copy()
            self.reposition_centers(X, klase)
            pomeraj = np.sqrt(((self.centroids - stari) ** 2).sum())
            if pomeraj < self.tolerance:
                break

        self.labels = self.clusterize(X)
        self.sum_squared_distance = self.loss(X, self.labels)
        self.silhouette_score = self.silhouette(X, self.labels)
        return self

    def initialize(self, X, n_uzoraka):
        # biramo k uzoraka iz podataka da budu centroidi na pocetku
        rng = np.random.default_rng(self.seed)
        indeksi = rng.choice(n_uzoraka, self.k, replace=False)
        self.centroids = X[indeksi]


    def clusterize(self, X):
        kolone = []
        for i in range(self.k):
            dist = np.sqrt(((X - self.centroids[i]) ** 2).sum(axis=1))
            kolone.append(dist)
        rastojanja = np.stack(kolone, axis=1)  # (n, k)
        return np.argmin(rastojanja, axis=1)

    def reposition_centers(self, X, klase):
        for klasa in set(klase):
            self.centroids[klasa, :] = np.mean(X[klase == klasa, :], axis=0)


    def loss(self, X, klase):
        """
             J = (1/m)·Σᵢ ‖xᵢ − μ_c(i)‖²
        """
        total= 0.0
        for i in range(self.k):
            tacke = X[klase == i]
            if len(tacke) == 0:
                continue
            total += ((tacke - self.centroids[i])**2).sum()
        return total / len(X)

    def standardize(self, X):
        return (X - self.mean) / self.std

    def silhouette(self, X, klase):
        """
            Prosecan siluentni koeficijent, blize 1 = bolje razdvojeni koeficijenti
            a za i - cohesion -> mean svih distanca u klasteru kome a pripada od samog a[i]
            b za i - separation -> minimum od svih mean distanca sa tacaka u ostalim klasterima
            (mean distanca tacaka iz najblizeg klastera)
            silhouette koeficijent = (b - a) / max(a, b)
        """
        n = len(X)
        ocene = np.zeros(n)

        for i in range(n):
            svoj = klase[i]
            a = np.inf
            b = np.inf

            for c in range(self.k):
                tacke = X[klase == c]

                if len(tacke) == 0:
                    continue

                d = np.sqrt(((tacke - X[i]) ** 2).sum(axis=1))
                if c == svoj:
                    if len(tacke) > 1:
                        a = d.sum() / (len(tacke) - 1)
                    else:
                        a = 0.0
                else:
                    b = min(b, d.mean())
            if a == 0:
                ocene[i] = 0.0
            else:
                ocene[i] = (b - a) / max(a, b)
        return ocene.mean() # mean svih silhouette koeficijenata

def najbolji_od(X, k, tezine=None, seedovi=SEEDOVI):
    najbolji = None
    for s in seedovi:
        km = KMeans(k=k, seed=s, tezine=tezine).fit(X)
        if najbolji is None or km.sum_squared_distance < najbolji.sum_squared_distance:
            najbolji = km
    return najbolji