import numpy as np
from modeli.recommender import Recommender
from obrada import db
from obrada.priprema.kategorije import ves_masine, frizideri, televizori
import pandas as pd

MODULI = [ves_masine, televizori, frizideri]

def skaliraj_kolone(X, prefiks, faktor):
    """
        Umanjivanje uticaja nekog tipa atributa
    """
    X = X.copy()
    kolone = [c for c in X.columns if c.startswith(prefiks)]
    X[kolone] = X[kolone] * faktor
    return X

def napravi_matricu(df, numericki, kategoricki, indikatori=()):
    X = pd.get_dummies(df[numericki + kategoricki], columns=kategoricki, drop_first=True)
    for kol in indikatori:
        X[f"ima_{kol}"] = df[kol].notna().astype(int)
    X = X.fillna(X.median())
    X["log_cena"] = np.log(df["cena"].values)
    return X

def main():
    ponude = db.ucitaj_ponude()
    specs = db.ucitaj_specs()
    preporuke = {}
    for modul in MODULI:
        df = modul.pripremi(ponude, specs)
        X = napravi_matricu(df, modul.NUMERICKI, modul.KATEGORICKI, modul.INDIKATORI)
        X = skaliraj_kolone(X, "brend_model_", 0.1)

        rec = Recommender(metrika="euklid").fit(X)

        preporuke[modul.KATEGORIJA] = {
            "rec": rec,
            "df": df.reset_index(drop=True),  # pozicija u df = pozicija u X
        }

        idx, ocene = rec.slicni(0, n=5)
        d = preporuke[modul.KATEGORIJA]["df"]
        print(f"\n=== {modul.KATEGORIJA} ===")
        print("polazni:", d.iloc[0].naziv, "|", d.iloc[0].cena)
        for i, o in zip(idx, ocene):
            print(f"  {o:.3f}  {d.iloc[i].naziv[:55]:57} {d.iloc[i].cena}")


if __name__ == "__main__":
    main()