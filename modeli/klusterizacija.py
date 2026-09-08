from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from modeli.k_means import KMeans
from obrada import db
from obrada.priprema.kategorije import ves_masine, frizideri, televizori
import pandas as pd


IZLAZ = Path("modeli/obuceni.json")
MODULI = [ves_masine]

def napravi_matricu(df, numericki, kategoricki, indikatori=()):
    X = pd.get_dummies(df[numericki + kategoricki], columns=kategoricki, drop_first=True)
    for kol in indikatori:
        X[f"ima_{kol}"] = df[kol].notna().astype(int)
    X = X.fillna(X.median())
    y = np.log(df["cena"])
    return X, y


def main():
    ponude = db.ucitaj_ponude()
    specs = db.ucitaj_specs()

    modeli = {}
    for modul in MODULI:
        df = modul.pripremi(ponude, specs)
        print(df.columns)
        d = df[["kapacitet", "nivo_buke", "cena"]].dropna()

        #X, y = napravi_matricu(df, modul.NUMERICKI, modul.KATEGORICKI, modul.INDIKATORI)

        inercije = []
        opsezi = range(2, 15)
        for k in range(2, 15):
            print(f"K= {k}")
            najbolja = min(
                KMeans(k=k, seed=s).fit(d).sum_squared_distance
                for s in [1, 7, 42, 77, 123]
            )
            print(f" Najbolja inercija {najbolja}")
            inercije.append(najbolja)


        plt.plot(opsezi, inercije, marker="o")
        plt.xlabel("broj klastera (k)")
        plt.ylabel("inercija")
        plt.title("Lakat metoda")
        plt.grid(True)
        plt.show()

        km = KMeans(k=4, seed=7, debug=True)
        km.fit(d)

if __name__ == "__main__":
    main()