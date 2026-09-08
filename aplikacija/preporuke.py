import pandas as pd

from aplikacija import podaci
from modeli.recommender import Recommender


PREPORUKE = {} # kategorija -> {"rec": Recommender, "df": DataFrame}

def pripremi():
    for kat in podaci.kategorije():
        modul = podaci.MODULI[kat]
        df = podaci.podaci(kat)

        # brend se izostavlja iz vektora, inace sve proporuke su istog brenda
        kategoricki = [k for k in modul.KATEGORICKI if k != "brend_model"]

        X = pd.get_dummies(df[modul.NUMERICKI + kategoricki], columns=kategoricki, drop_first=True)

        for kol in modul.INDIKATORI:
            X[f"ima_{kol}"] = df[kol].notna().astype(int)
        X = X.fillna(X.median())

        PREPORUKE[kat] = {
            "rec": Recommender(metrika="kosinus").fit(X),
            "df": df,
        }

pripremi()

def pretrazi(kat, upit="", n=30):
    p = PREPORUKE[kat]
    df = p["df"]
    if upit:
        m = df.naziv.str.contains(upit, case=False, na=False, regex=False)
        d = df[m]
    else:
        d = df
    return [{"indeks": i, "naziv": r.naziv, "brend": r.brend, "cena": r.cena, "slika": r.slika} for i, r in d.head(n).iterrows()]

def slicni_proizvodi(kat, indeks, n=5):
    p = PREPORUKE[kat]
    df, rec = p["df"], p["rec"]

    idx, ocene = rec.slicni(indeks, n=50)

    polazni = df.iloc[indeks]
    vidjeni = { polazni.ean }
    rezultat = []

    for i, o in zip(idx, ocene):
        red = df.iloc[i]
        if red.ean in vidjeni:
            continue

        vidjeni.add(red.ean)
        rezultat.append({
            "naziv": red.naziv,
            "brend": red.brend,
            "cena": red.cena,
            "slika": red.slika,
            "url": red.url,
            "izvor": red.izvor,
            "rastojanje": round(float(o), 3),
        })
        if len(rezultat) == n:
            break
    return {"polazni": polazni.to_dict(), "preporuke": rezultat }