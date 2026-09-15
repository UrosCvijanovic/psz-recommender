import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

class LinearRegression:
    def __init__(self, lr: int = 0.01, n_iters: int = 1000, modul: str = None) -> None:
        self.lr = lr # learning rate (alpha)
        self.modul_name = modul
        self.n_iters = n_iters
        self.weights = None # koeficijenti (jedan po koloni)
        self.bias = 0.0
        self.history = {}

        # standardizacija
        self.mean = 0.0
        self.std = 0.0


    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0)
        self.std[self.std==0] = 1


        X = self.standardize(X)
        num_samples, num_features = X.shape # X shape [N, f]
        self.weights = np.zeros(num_features) # W shape [f, 1]

        for i in range(self.n_iters):
            # y_pred shape should be N, 1
            dj_dw, dj_db = self.gradijent(X, y)
            self.weights -= self.lr * dj_dw
            self.bias -= self.lr * dj_db
            cost = self.loss(X, y)

            self.history[i] = cost
            if i % 100 == 0:
                print(f"Iteracija {i} Trosak: {cost}")

        if self.modul_name is not None:
            with open(f'{self.modul_name}_loss_data.json', 'w') as fp:
                json.dump(self.history, fp)

    def predict_standardized(self, X_standardized):
        m, n = X_standardized.shape
        y_hat = np.zeros(m)

        for i in range(m):
            suma = self.bias
            for j in range(n):
                suma += self.weights[j] * X_standardized[i][j]
            y_hat[i] = suma
        return y_hat

    def predict(self, X):
        """
            Predikcija za nove uzorke.
        """
        X = np.asarray(X, dtype=float)
        x_std = self.standardize(X)
        return self.predict_standardized(x_std)


    def loss(self, X, y):
        """
            MSE: J = 1/2n * sum(predikcija - y)^2
        """
        m = X.shape[0]
        y_hat = self.predict_standardized(X)
        SE_sum = np.sum((y_hat - y)**2)
        MSE = SE_sum / (2.0 * m)
        return MSE

    def gradijent(self, X, y):
        """
            Parcijalni izvodi funkcije troska po w i b.
            ∂J/∂wⱼ = (1/m)·Σᵢ (h(x⁽ⁱ⁾) − y⁽ⁱ⁾)·xⱼ⁽ⁱ⁾
            Vraca (grad_w, grad_b).
        """
        m, n = X.shape

        dj_dw = np.zeros(n) # vektor tezina
        dj_db = 0

        h_x = self.predict_standardized(X) # predikcija / hipoteza

        for i in range(m): # po redovima
            err = h_x[i] - y[i] # (h(x⁽ⁱ⁾) − y⁽ⁱ⁾)
            for j in range(n):
                dj_dw[j] += err * X[i][j] # po featurima / za svaki feature tezina
            dj_db += err

        return dj_dw / m, dj_db / m

    def standardize(self, X):
        return (X - self.mean) / self.std

    def plot_loss(self):
        iterations = list(self.history.keys())
        loss = list(self.history.values())

        plt.plot(iterations, loss, label=self.modul_name)
        plt.yscale("log")
        plt.xlabel("iteracija")
        plt.ylabel("trošak (log skala)")
        plt.savefig(f"{self.modul_name}_loss.png")