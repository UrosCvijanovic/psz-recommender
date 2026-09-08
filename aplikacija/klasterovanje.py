from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
from modeli.k_means import KMeans
from obrada.priprema.kategorije import ves_masine, frizideri, televizori
from aplikacija import podaci


STATIC = Path(__file__).parent / "static"
STATIC.mkdir(exist_ok=True)

MODULI = {m.KATEGORIJA: m for m in [ves_masine, frizideri, televizori]}

def atributi(kat):
    return MODULI[kat].NUMERICKI + ["cena"]


def nacrtaj(d, kolone, km, centri, w, k):
    """Snima grafikon klastera u static/klasteri.png."""
    if len(kolone) == 1:
        jedan_atribut(d, kolone, km, centri, k)
    else:
        dve_ose(d, kolone, km, centri, w, k)
    plt.tight_layout()
    plt.savefig(STATIC / "klasteri.png", dpi=100)
    plt.close()


def jedan_atribut(d, kolone, km, centri, k):
    """Histogram raspodele po klasterima."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for i in range(k):
        idx = (km.labels == i).nonzero()[0]
        ax.hist(d.iloc[idx, 0], bins=25, alpha=0.6, label=f"klaster {i}")
    for c in centri[:, 0]:
        ax.axvline(c, color="red", linestyle="--")
    ax.set_xlabel(kolone[0])
    ax.set_ylabel("broj proizvoda")
    ax.set_title(f"Raspodela po klasterima ({kolone[0]})")
    ax.legend()


def dve_ose(d, kolone, km, centri, w, k):
    """Klasteri u originalnim jedinicama."""
    fig, ax = plt.subplots(figsize=(10, 7))

    for i in range(k):
        idx = (km.labels == i).nonzero()[0]
        ax.scatter(d.iloc[idx, 0], d.iloc[idx, 1], s=20, label=f"klaster {i}")

    ax.scatter(centri[:, 0], centri[:, 1], s=100, c="red", marker="X", edgecolors="black", label="centri")
    ax.set_xlabel(kolone[0])
    ax.set_ylabel(kolone[1])
    ax.set_title("Klasteri")
    ax.legend()

    if len(kolone) > 2:
        ax.set_title(f"Prikazane prve dve od {len(kolone)} dimenzija")


def pokreni(kat, tezine, k):
    df = podaci.podaci(kat)
    kolone = list(tezine.keys())
    d = df[kolone].dropna()

    # normalizuj tezine
    ukupno = sum(tezine.values())
    w = np.array([tezine[c] / ukupno for c in kolone])

    km = KMeans(k=k, seed=77, tezine=w).fit(d)

    # centri nazad u originalne jedinice
    centri = (km.centroids / w) * km.std + km.mean

    # spoji labele sa originalnim podacima
    rez = df.loc[d.index].copy()
    rez["klaster"] = km.labels

    klasteri = []
    for i in range(k):
        grupa = rez[rez.klaster == i]

        if len(grupa) == 0:
            continue

        klasteri.append({
            "broj": i,
            "n": len(grupa),
            "centar": {c: round(float(v), 1) for c, v in zip(kolone, centri[i])},
            "cena_medijana": round(grupa.cena.median()),
            "brendovi": grupa.brend.value_counts().head(3).to_dict(),
            "primeri": grupa.nlargest(3, "cena")[["naziv", "cena"]].to_dict("records"),
        })
    nacrtaj(d, kolone, km, centri, w, k)
    return {"klasteri": klasteri, "inercija": round(km.sum_squared_distance, 4)}