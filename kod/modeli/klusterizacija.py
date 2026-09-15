#import matplotlib
#matplotlib.use("Agg")
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from modeli.training.k_means import KMeans
from obrada import db
from obrada.priprema.kategorije import ves_masine, frizideri, televizori

MODULI = [frizideri]

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

    for modul in MODULI:
        df = modul.pripremi(ponude, specs)
        print(df.columns)
        d = df[["zapremina_frizidera", "cena"]].dropna()

        """
        skorovi = []
        for k in range(2, 15):
            print(f"K= {k}")
            rez = []
            for s in [1, 7, 42, 77, 123]:
                km = KMeans(k=k, seed=s).fit(d)
                sc = km.silhouette_score
                rez.append(sc)
            najbolja = max(rez)
            print(f" Najbolja silueta: {najbolja:.4f}")
            skorovi.append(najbolja)

        opsezi = list(range(2, 15))
        najbolji_k = opsezi[int(np.argmax(skorovi))]
        plt.figure(figsize=(8, 5))
        plt.plot(opsezi, skorovi, marker="o")
        plt.axvline(najbolji_k, color="red", linestyle="--", label=f"maksimum: k={najbolji_k}")
        plt.xlabel("broj klustera (k)")
        plt.ylabel("siluetni koeficijent")
        plt.ylim(0, 0.5)
        plt.title("Siluetni koeficijent (zapremina_frizidera, cena)")
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(Path(__file__).resolve().parent / "silueta_frizideri.png", dpi=150)
        plt.close()

        json.dump(dict(zip(map(str, opsezi), skorovi)),
                  open(Path(__file__).resolve().parent / "silueta_frizideri.json", "w"),
                  indent=2)
        
        """
        km = KMeans(k=3, seed=77).fit(d)

        # centri nazad u originalne jedinice
        centri = km.centroids * km.std + km.mean

        # spoji labele sa punim podacima (d je nastao dropna, pa ide preko indeksa)
        rez = df.loc[d.index].copy()
        rez["klaster"] = km.labels

        for i in range(km.k):
            g = rez[rez.klaster == i]
            print(f"klaster {i} ({len(g)} proizvoda)")
            for kol, v in zip(d.columns, centri[i]):
                print(f"{kol:12} {v:10.1f}")
            print(f"medijana cene: {g.cena.median():.0f}")
            print(f"brendovi: {g.brend.value_counts().head(3).to_dict()}")
            print()

        X_OSA, Y_OSA = "zapremina_frizidera", "cena"
        ix, iy = list(d.columns).index(X_OSA), list(d.columns).index(Y_OSA)

        for i in range(km.k):
            idx = (km.labels == i).nonzero()[0]
            sc = plt.scatter(d.iloc[idx][X_OSA], d.iloc[idx][Y_OSA], s=20, label=f"klaster {i}")
            plt.scatter(centri[i, ix], centri[i, iy], s=250, color=sc.get_facecolor()[0], marker="X", edgecolors="black", linewidths=1.5)
        plt.xlabel(X_OSA)
        plt.ylabel(Y_OSA)
        plt.title(f"Klasteri (k={3}) prikaz po zapremini i ceni")
        plt.legend()
        plt.tight_layout()
        plt.savefig(Path(__file__).resolve().parent / "klusteri_frizider.png", dpi=150)
        plt.close()

if __name__ == "__main__":
    main()