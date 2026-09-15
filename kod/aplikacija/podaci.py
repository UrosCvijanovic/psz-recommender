from obrada import db
from obrada.priprema.kategorije import ves_masine, frizideri, televizori

MODULI = {m.KATEGORIJA: m for m in [ves_masine, televizori, frizideri]}

PONUDE = None
SPECS = None
PRIPREMLJENO = {} # dataframe podataka kategorije

def ucitaj():
    global PONUDE, SPECS
    PONUDE = db.ucitaj_ponude()
    SPECS = db.ucitaj_specs()

    for kat, modul in MODULI.items():
        PRIPREMLJENO[kat] = modul.pripremi(PONUDE, SPECS).reset_index(drop=True)
        print(f"{kat}: {len(PRIPREMLJENO[kat])} proizvoda")

ucitaj()

def kategorije():
    return sorted(PRIPREMLJENO.keys())

def podaci(kat):
    return PRIPREMLJENO[kat]