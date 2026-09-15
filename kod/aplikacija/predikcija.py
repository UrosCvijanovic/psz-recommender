import json
import numpy as np
import pandas as pd
from pathlib import Path
from aplikacija import podaci


#MODELI = json.loads(Path("../modeli/obuceni.json").read_text(encoding="utf-8"))
KOREN = Path(__file__).resolve().parent.parent
MODELI = json.loads((KOREN / "modeli" / "obuceni.json").read_text(encoding="utf-8"))

def kategorije():
    return sorted(MODELI.keys())

def test_proizvodi(kat):
    """
        Proizvodi iz test skupa
    """
    m = MODELI[kat]
    df = podaci.podaci(kat)
    d = df[df.id.isin(m["test_sample"])]

    rez = []
    for _, r in d.iterrows():
        atributi = {}
        for k in m["numericki"] + list(m["opcije"]):
            if pd.notna(r[k]):
                atributi[k] = r[k]
        rez.append({
            "id": int(r["id"]),
            "naziv": r["naziv"],
            "slika": r["slika"],
            "cena": float(r["cena"]),
            "atributi": atributi,
        })
    return rez

def predvidi_za_id(kat, pid):
    m = MODELI[kat]
    r = podaci.podaci(kat).query("id == @pid").iloc[0]
    unos = {k: r[k] for k in m["numericki"] + list(m["opcije"]) if pd.notna(r[k])}
    pred = predvidi(kat, unos)
    print(f"Predvidjena: {pred}\n")
    print(f"Stvarna: {float(r.cena)}")
    print(f"Razlika: {float(r.cena) - pred}")
    return {"stvarna": float(r.cena), "predvidjena": round(pred)}

def sklopi_red(kat, unos):
    m = MODELI[kat]
    red = {k: 0.0 for k in m["kolone"]}
    red.update(m["medijane"])

    for kljuc, vrednost in unos.items():
        if kljuc in red and not any(kljuc == k.split("_")[0] for k in m["opcije"]):
            red[kljuc] = float(vrednost)
        else:
            kolona = f"{kljuc}_{vrednost}"
            if kolona in red:
                red[kolona] = 1.0
    for kljuc in unos:
        if f"ima_{kljuc}" in red:
            red[f"ima_{kljuc}"] = 1.0
    for k in m["opcije"]:
        if k not in unos and f"{k}_nan" in red:
            red[f"{k}_nan"] = 1.0

    return np.array([red[k] for k in m["kolone"]])


def predvidi(kat, unos):
    m = MODELI[kat]
    x = sklopi_red(kat, unos)
    x = (x - np.array(m["mean"])) / np.array(m["std"])
    log_cena = float(np.dot(x, m["weights"]) + m["bias"])
    return np.exp(log_cena)

if __name__ == "__main__":
    print("kategorije:", kategorije())

    kat = "ves-masine"
    m = MODELI[kat]
    print(f"\n{kat}: {len(m['kolone'])} kolona")
    print("numericki (medijane):", m["medijane"])
    print("opcije:", {k: v[:5] for k, v in m["opcije"].items()})

    unos = {"kapacitet": 8, "centrifuga": 1400, "brend_model": "BEKO", "tip": "pranje"}
    print("\npredikcija:", round(predvidi(kat, unos)))

    print(sklopi_red("ves-masine", {"kapacitet": 8}))