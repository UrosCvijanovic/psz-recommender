import os
import matplotlib
import pandas as pd
matplotlib.use("Agg") # bez GUI-ja
import matplotlib.pyplot as plt
from pathlib import Path
from obrada import db

IZLAZ = Path(__file__).resolve().parent / "plots"
IZLAZ.mkdir(parents=True, exist_ok=True)

def grafikon_kategorije(df):
    ukupno = len(df)
    top_10 = df['kategorija'].value_counts().head(10)
    procenti = (top_10 / ukupno) * 100
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(top_10.index, top_10.values, align="center")
    # broj i pocenat iznad svakog bar-a
    for bar, n, p in zip(bars, top_10.values, procenti.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{n}\n{p:.1f}%", ha="center", va="bottom")

    ax.set_title(f"10 najzastupljenijih kategorija (Ukupno {ukupno} ponuda)")
    ax.set_ylabel("Broj proizvoda")
    ax.set_ylim(0, top_10.max() * 1.20) # 20% eksta prosora na y-osi za tekst
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"{IZLAZ}/01_kategorije.png", dpi=150)
    plt.close()

def grafikon_brendovi(df):
    ukupno = len(df)
    top_k = 10
    top_n = df['brend'].value_counts().head(top_k)
    procenti = (top_n / ukupno) * 100
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(top_n.index, top_n.values, align="center")
    # broj i pocenat iznad svakog bar-a
    for bar, n, p in zip(bars, top_n.values, procenti.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{n}\n{p:.1f}%", ha="center", va="bottom")

    ax.set_title(f"5 najzastupljenijih brendova (ukupno {ukupno} ponuda)")
    ax.set_ylabel("Broj proizvoda")
    ax.set_ylim(0, top_n.max() * 1.20)  # 20% eksta prosora na y-osi za tekst
    plt.xticks(rotation=45, ha="right")
    plt.savefig(f"{IZLAZ}/02_brendovi.png", dpi=150)
    plt.close()

def grafikon_cenovni_opsezi(df):
    bins = [0, 30000, 100000, 300000, float("inf")]
    oznake = ["≤ 30.000", "30.001 - 100.000", "100.001 - 300.000", "≥ 300.000"]
    ranges = pd.cut(df["cena"], bins=bins, labels=oznake, include_lowest=True)
    brojevi = ranges.value_counts().reindex(oznake)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(brojevi, labels=oznake,  autopct='%1.1f%%', shadow=True, startangle=90)
    plt.savefig(f"{IZLAZ}/03_granice_cena.png", dpi=150)
    plt.close()

def grafikon_energetska_klasa(df):
    ukupno = len(df)
    poznata = df[df['ek_skala'].notna()]

    redosled = {
        "nova": ["A", "B", "C", "D", "E", "F", "G"],
        "stara": ["A+++", "A++", "A+", "A", "B", "C", "D", "E"],
    }

    fig, osе = plt.subplots(1, 2, figsize=(14, 6))
    for ax, skala in zip(osе, ["stara", "nova"]):
        podaci = poznata[poznata.ek_skala == skala]
        brojevi = podaci.ek_ocena.value_counts().reindex(redosled[skala]).dropna()
        procenti = (brojevi / ukupno) * 100
        bars = ax.bar(brojevi.index, brojevi.values, align="center")

        for bar, n, p in zip(bars, brojevi.values, procenti.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{n}\n{p:.1f}%", ha="center", va="bottom")

        ax.set_title(f"{skala.capitalize()} skala ({len(podaci)} proizvoda)")
        ax.set_ylabel("Broj proizvoda")
        ax.set_ylim(0, brojevi.max() * 1.20)
    fig.suptitle(f"Raspodela po energetskoj klasi (poznata za {len(poznata)} of ukupno {ukupno} proizvoda)")
    plt.tight_layout()
    plt.savefig(f"{IZLAZ}/04_energetska_klasa.png", dpi=150)
    plt.close()

def main():
    df = db.ucitaj_ponude()
    os.makedirs(IZLAZ, exist_ok=True)
    grafikon_kategorije(df)
    grafikon_brendovi(df)
    grafikon_cenovni_opsezi(df)
    grafikon_energetska_klasa(df)

if __name__ == "__main__":
    main()