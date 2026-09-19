import json
import numpy as np
import pandas as pd
from obrada import db
from pathlib import Path
from sklearn.model_selection import train_test_split
from modeli.training.linear_regression import LinearRegression
from obrada.priprema.kategorije import ves_masine, frizideri, televizori

IZLAZ = Path(__file__).resolve().parent / "obuceni_short.json"
MODULI = [ves_masine, televizori, frizideri]

def calculate_rmse(y_true, y_pred):
    n = len(y_true)

    if n != len(y_pred):
        return None

    squared_error = np.sum((y_true - y_pred) ** 2)

    mse = squared_error / n

    rmse = np.sqrt(mse)

    return rmse

def calculate_r2(y_true, y_pred):
    # 1. calculate mean of actual test set
    y_mean = np.mean(y_true)

    # 2. calculate sum of squared residuals
    ssr = np.sum((y_true - y_pred) ** 2)

    # 3. calculate total sum of squares
    sst = np.sum((y_true - y_mean) ** 2)

    # calculate R2
    if sst == 0:
        return 0.0

    r2 = 1 - (ssr / sst)

    return r2


def napravi_matricu(df, numericki, kategoricki, indikatori=()):
    X = pd.get_dummies(df[numericki + kategoricki], columns=kategoricki, drop_first=True, dummy_na=True)
    for kol in indikatori:
        X[f"ima_{kol}"] = df[kol].notna().astype(int)
    y = np.log(df["cena"])
    return X, y


def sacuvaj_modele(modeli):
    IZLAZ.parent.mkdir(parents=True, exist_ok=True)
    with open(IZLAZ, "w", encoding="utf-8") as f:
        json.dump(modeli, f, ensure_ascii=False, indent=2)

def main():
    ponude = db.ucitaj_ponude()
    specs = db.ucitaj_specs()
    modeli = {}
    for modul in MODULI:
        df = modul.pripremi(ponude, specs)
        X, y = napravi_matricu(df, modul.NUMERICKI, modul.KATEGORICKI, modul.INDIKATORI)
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=77)

        med = x_train[modul.NUMERICKI].median()
        x_train = x_train.fillna(med)
        x_test = x_test.fillna(med)

        # Fitting the Multiple Linear Regression model
        mlr = LinearRegression(0.1, 8000, modul=modul.IME_KATEGORIJE)
        mlr.fit(x_train, y_train)

        y_pred = mlr.predict(x_test)

        rmse_value = calculate_rmse(y_test, y_pred)
        rmse_rsd = calculate_rmse(np.exp(y_test), np.exp(y_pred))
        r2_score = calculate_r2(y_test, y_pred)
        #mlr.plot_loss()

        modeli[modul.KATEGORIJA] = {
            "ukupno_proizvoda": len(df),
            "trening_proizvoda": len(x_train),
            "test_proizvoda": len(x_test),
            "weights": mlr.weights.tolist(),
            "bias": float(mlr.bias),
            "mean": mlr.mean.tolist(),
            "std": mlr.std.tolist(),
            "kolone": list(X.columns),
            "broj_kolona": len(list(X.columns)),
            "r2": r2_score,
            "rmse": rmse_value,
            "rmse_rsd": rmse_rsd,
            "medijane": med.to_dict(),
            "numericki": modul.NUMERICKI,
            "opcije": {k: sorted(df[k].dropna().unique().tolist()) for k in modul.KATEGORICKI},
            "test_sample": df.loc[x_test.index[:10], "id"].tolist(),
        }
    sacuvaj_modele(modeli)


if __name__ == "__main__":
    main()