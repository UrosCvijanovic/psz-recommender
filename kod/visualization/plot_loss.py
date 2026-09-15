import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ULAZ = Path(__file__).resolve().parent

def grafikon_kategorije(istorije):
    fig, ax = plt.subplots(figsize=(9, 5))
    for kat, h in istorije.items():
        ax.plot(list(h.keys()), list(h.values()), label=kat)
    ax.set_xlim(0, 800)
    ax.set_yscale("log")
    ax.set_xlabel("iteracija")
    ax.set_ylabel("MSE (log skala)")
    ax.set_title("Konvergencija gradijentnog spusta")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ULAZ / "plots" / "05_konvergencija.png", dpi=150)
    plt.close()


def ucitaj_istorije():
    istorije = {}
    for f in sorted(ULAZ.glob("*_loss_data.json")):
        kat = f.stem.replace("_loss_data", "")
        d = json.loads(f.read_text())
        istorije[kat] = { int(k) : v for k, v in d.items() }
    return istorije



def main():
    print("Hello world")
    istorije = ucitaj_istorije()
    grafikon_kategorije(istorije)

if __name__ == "__main__":
    main()