import matplotlib.pyplot as plt
import numpy as np

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
        self.X_std = None
        self.history = {}

        # standardizacija
        self.mean = 0.0
        self.std = 0.0


    def fit(self, X):
        X = np.asarray(X, dtype=float)

        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0)
        self.std[self.std == 0] = 1

        X = self.standardize(X)
        self.X_std = X

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
            pomeraj = np.linalg.norm(self.centroids - stari)
            if pomeraj < self.tolerance:
                self.labels = self.clusterize(X)
                self.sum_squared_distance = self.loss(X, self.labels)
                break
            #print(self.centroids)

            self.sum_squared_distance = self.loss(X, klase)

            self.labels = klase
            self.silhouette_score = self.silhouette(X, self.labels)

        if self.debug:
            print(self.centroids)
            # Kreiraj 3D scatter plot sa bojama po klasterima
            #self.plot_3d_interactive(X)
            for i in range(self.k):
                sc = plt.scatter(X[klase == i, 0], X[klase == i, 1], s=20, label=f"klaster {i}")
                boja = sc.get_facecolor()[0]
                plt.scatter(self.centroids[i, 0], self.centroids[i, 1], s=250, c=boja, marker="X", edgecolor="black", linewidths=1.5)
            plt.legend()
            plt.show()
            plt.close()
        return self

    def predict(self, X):
        """
            Predikcija za nove uzorke.
        """
        X = np.asarray(X, dtype=float)
        Xs = self.standardize(X)
        if self.tezine is not None:
            Xs = Xs * self.tezine
        return self.clusterize(Xs)


    def initialize(self, X, n_uzoraka):
        # biramo k uzoraka iz podataka da budu centroidi na pocetku
        rng = np.random.default_rng(self.seed)
        indeksi = rng.choice(n_uzoraka, self.k, replace=False)
        self.centroids = X[indeksi]


    def clusterize(self, X):
        kolone = []
        for i in range(self.k):
            dist = np.linalg.norm(X - self.centroids[i], axis=1)  # (n, )
            kolone.append(dist)
        rastojanja = np.stack(kolone, axis=1)  # (n, k)
        return np.argmin(rastojanja, axis=1)

    def reposition_centers(self, X, klase):
        for klasa in set(klase):
            self.centroids[klasa, :] = np.mean(X[klase == klasa, :], axis=0)


    def loss(self, X, klase):
        """
            𝐽𝑐(1),…,𝑐(𝑚),𝜇(1),…,𝜇𝐾=1𝑚෍𝑖 = 1/𝑚 ||𝑥(𝑖)−𝜇𝑐(𝑖)||2
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

                d = np.linalg.norm(tacke - X[i], axis=1)
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
