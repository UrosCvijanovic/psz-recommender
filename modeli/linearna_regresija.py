import json
import numpy as np
import pandas as pd
from obrada import db
from pathlib import Path
from sklearn.model_selection import train_test_split
from modeli.linear_regression import LinearRegression
from obrada.priprema.kategorije import ves_masine, frizideri, televizori

IZLAZ = Path("modeli/obuceni.json")
MODULI = [ves_masine, televizori, frizideri]

def napravi_matricu(df, numericki, kategoricki, indikatori=()):
    X = pd.get_dummies(df[numericki + kategoricki], columns=kategoricki, drop_first=True)
    for kol in indikatori:
        X[f"ima_{kol}"] = df[kol].notna().astype(int)
    X = X.fillna(X.median())
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
        # Fitting the Multiple Linear Regression model
        mlr = LinearRegression(0.1, 8000)
        mlr.fit(x_train, y_train)
        modeli[modul.KATEGORIJA] = {
            "weights": mlr.weights.tolist(),
            "bias": float(mlr.bias),
            "mean": mlr.mean.tolist(),
            "std": mlr.std.tolist(),
            "kolone": list(X.columns),
            "medijane": X[modul.NUMERICKI].median().to_dict(),
            "numericki": modul.NUMERICKI,
            "opcije": {k: sorted(df[k].dropna().unique().tolist()) for k in modul.KATEGORICKI},
        }
    sacuvaj_modele(modeli)


if __name__ == "__main__":
    main()