import re
from urllib.parse import unquote
import psycopg2
import pandas as pd
import unicodedata
import html as html_lib
from konfiguracija import RAW_SHEMA
from obrada import db

IZBACI_NIVO2 = {
    # nije bela tehnika
    "sudopere-i-slavine",
    # pribor i oprema
    "oprema-za-belu-tehniku",
    "oprema-i-sredstva-za-kafe-aparate",
    "oprema-i-sredstva-za-grejanje-i-hladjenje",
    # van opsega
    "preciscivaci-vode",
    "specijalizovani-kucni-aparati",
    "specijalizovani-kuhinjski-aparati",
    "grejne-fioke",
    "kucni-aparati",
    "aparati-za-pripremu-i-cuvanje-hrane",
    "pomocni-kuhinjski-aparati",
    "aparati-za-obradu-i-cuvanje-hrane",
    "aparati-za-vodu-i-filtraciju",
    "aparati-za-poslastice-i-razonodu",
    "aparati-za-desert-i-zabavno-kuvanje",
    "elektricni-rostilji",
    "rostilji-i-grilovi",
    "grejna-tela"
}

# pribor se prepoznaje po obrascu, na bilo kom nivou
PRIBOR_RECI = ("oprema", "sredstva", "dodaci", "dodatna", "pribor", "zamenski", "nastavci", "prikljucci")
PRIBOR_IZUZECI = {"klima-uredjaji-i-oprema"}

RAZLOZI_NA_NIVO3 = {
    "ugradna-tehnika",
    "aparati-za-vodu-sokove-i-napitke",
    "espresso-i-kafe-aparati",
    "tosteri-i-aparati-za-sendvice",
    "sporeti",
}

VARIJANTE = {
    "airfryeri": "airfryer",
    "multipraktici": "multipraktik",
    "mikseri": "mikseri-i-seckalice",
    "seckalice": "mikseri-i-seckalice",
    # treba proveriti koliko je opreme unutar klima-uredjaji-i-oprema
    "klima-uredjaji-i-oprema": "klima-uredjaji",
    "aparati-za-espresso-kafu": "espresso-aparati",
    "ugradni-aspiratori": "aspiratori",
    "ugradni-frizideri": "frizideri",
    # gigatron sporeti
    "elektricni-sporeti": "sporeti",
    "kombinovani-sporeti": "sporeti",
    "mini-sporeti": "sporeti",
    # tehnomedija sporeti
    "staklokeramicki-sporeti": "sporeti",
    "sporeti-sa-ringlama": "sporeti",
    "indukcioni-sporeti": "sporeti",
}


DOZVOLJENE_KATEGORIJE = {
    "frizideri",
    "usisivaci",
    "ves-masine",
    "televizori",
    "sporeti",
    "pegle",
    "masine-za-pranje-sudova",
    "ugradne-rerne",
    "espresso-aparati",
    "ugradne-ploce",
    "aparati-za-kuvanje-i-pecenje",
    "aparati-za-tretiranje-vazduha",
    # potencijalno izbaci kuvala za vodu
    "kuvala-za-vodu",
    "klima-uredjaji",
    "blenderi",
    "bojleri",
    "airfryer",
    "mikrotalasne-rerne",
    "tosteri",
    "aspiratori",
    "ventilatori",
    "sokovnici",
    "multipraktik",
    "parocistaci",
    "mikseri-i-seckalice",
    "aparati-za-kafu",
    "zamrzivaci",
}

BREND_ISPRAVKE = {
    "BLACK & DECKER": "BLACK AND DECKER",
    "ALFA": "ALFA PLAM",
}

ANOMALIJE_SET = {'/', 'AAA', 'A - 20%', 'F (A++)'}

NOVA_SKALA_KATEGORIJE = { "frizideri", "zamrzivaci", "ves-masine", "masine-za-pranje-sudova", "televizori", "bojleri",}
BEZ_SKALE = {"sporeti"}

def razlozi(red):
    if red["izvor"] == "gigatron.rs":
        delovi = unquote(red["kategorija_path"]).split("/")
    else:
        delovi = red["kategorija_path"].split(">")
    return [d.strip() for d in delovi if d.strip()]

def u_slug(s):
    if not isinstance(s, str):
        return None
    s = s.replace("đ", "dj").replace("Đ", "Dj")
    # razdvaja dijakriticke znakove od slova, ovo povecava duzinu stringa za broj dijartickih znakova
    # mora da se znakovi izbaci naknadno
    s = unicodedata.normalize("NFD", s)
    # join ako nije dijarticki znak
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def uzmi_nivo(lista, i):
    if len(lista) > i:
        return u_slug(lista[i])
    return None

def je_pribor(s):
    if not isinstance(s, str):
        return False
    if s in PRIBOR_IZUZECI:
        return False
    for rec in PRIBOR_RECI:
        if rec in s:
            return True
    return False

def kanonska_kategorija(red):
    n1, n2, n3 = red["nivo1"], red["nivo2"], red["nivo3"]

    # Filtriranje po tipu kategorije
    if n2 in IZBACI_NIVO2:
        return None
    if je_pribor(n2) or je_pribor(n3):
        return None

    # grupisane kategorije -> uzmi nivo 3
    if n2 in RAZLOZI_NA_NIVO3:
        if not isinstance(n3, str):
            return None
        kategorija = n3
    else:
        kategorija = n2

    kategorija = VARIJANTE.get(kategorija, kategorija)

    # ako je nivo2 u dozvoljenom skupu
    if kategorija in DOZVOLJENE_KATEGORIJE:
        return kategorija

    return None

def brend_kljuc(s):
    if not isinstance(s, str):
        return None
    k = s.strip().upper()
    return BREND_ISPRAVKE.get(k, k)

def ocitsti_ocenu(ocena):
    m = re.match(r"^([A-GА])(\+*)", ocena)
    if m is None:
        return None

    slovo, plusevi = m.group(1), m.group(2)
    return slovo.replace("А", "A") + plusevi


def energetska_klasa_kljuc(energetksa_klasa, kategorija):
    if not isinstance(energetksa_klasa, str):
        return None, None

    v = energetksa_klasa.strip()

    # Dvostruke vrednosti (klime) i anomalije -> odbacivanje
    if '/' in v or any(anomaly == v for anomaly in ANOMALIJE_SET):
        return None, None

    # Skala iz same vrednosti
    skala = None
    if '+' in v:
        skala = "stara"
    elif 'Novo' in v:
        skala = "nova"

    # Izvuci slovo
    ocena = ocitsti_ocenu(v)
    if ocena is None:
        return None, None

    if skala is None:
        if kategorija in BEZ_SKALE:
            return None, None
        skala = "nova" if kategorija in NOVA_SKALA_KATEGORIJE else "stara"

    return ocena, skala

def energetska_red(red):
    return energetska_klasa_kljuc(red["energetska_klasa"], red["kategorija"])

def dodaj_nivoe(ponude):
    df = ponude.copy()
    df["nivoi"] = df[["izvor", "kategorija_path"]].apply(razlozi, axis=1)
    df["nivo1"] = df["nivoi"].apply(uzmi_nivo, i=0)
    df["nivo2"] = df["nivoi"].apply(uzmi_nivo, i=1)
    df["nivo3"] = df["nivoi"].apply(uzmi_nivo, i=2)
    return df


def normalizuj_kategorije(ponude):
    """
        Vadi jednu kategoriju iz kategorija_path i odbacuje zapise van opsega.
    """
    df = ponude.copy()
    df["kategorija"] = df.apply(kanonska_kategorija, axis=1)
    return df


def normalizuj_brend(ponude):
    df = ponude.copy()
    df["brend"] = df["brend"].apply(brend_kljuc)
    return df


def normalizuj_energetsku(ponude):
    df = ponude.copy()
    df[["ek_ocena", "ek_skala"]] = df.apply(energetska_red, axis=1, result_type="expand")
    return df


def filtriraj_po_broju_specs(ponude, specs, prag):
    """
        Odbacuje zapise sa premalo atributa
        vraca (ponude, specs) uskladjene.
    """
    broj = specs.groupby("ponuda_id").size()
    ponude = ponude.copy()
    ponude["n_specs"] = ponude["id"].map(broj).fillna(0).astype(int)
    ponude = ponude[ponude.n_specs >= prag].copy()
    specs = specs[specs.ponuda_id.isin(ponude.id)].copy()
    return ponude, specs

BR = re.compile(r"\s*(?:<br\s*/?>|</p>\s*<p>)\s*", re.IGNORECASE)
TAG = re.compile(r"<[^>]+>")

def ocisti_vrednost(vrednost):
    if not isinstance(vrednost, str):
        return None
    v = BR.sub("\n", vrednost)
    v = TAG.sub("", v)
    v = html_lib.unescape(v)
    # izbaci visestruke razmake
    v = re.sub(r"[ \t]+", " ", v)
    return v.strip() or None

def ocisti_specifikacije(specs):
    df = specs.copy()
    df["vrednost"] = df["vrednost"].apply(ocisti_vrednost)
    return df[df.vrednost.notna()].copy()

def preprocess_engine():
    ponude = db.ucitaj_ponude(sema=RAW_SHEMA)
    specs = db.ucitaj_specs(sema=RAW_SHEMA)

    specs = ocisti_specifikacije(specs)
    ponude = dodaj_nivoe(ponude)
    ponude = normalizuj_kategorije(ponude)
    ponude = ponude[ponude.kategorija.notna()].copy()
    ponude = normalizuj_brend(ponude)
    ponude = normalizuj_energetsku(ponude)

    ponude, specs = filtriraj_po_broju_specs(ponude, specs, prag=3)
    print(f"ponude: {len(ponude)} | specifikacije: {len(specs)}")

    print(ponude.columns)
    kat = ponude[["id", "kategorija"]].rename(columns={"id": "ponuda_id"})
    s = specs.merge(kat, on="ponuda_id", how="inner")

    vm = s[s.kategorija == "ves-masine"]
    ima_sirinu = set(vm[vm.naziv == "Širina"].ponuda_id)
    ima_dim = set(vm[vm.naziv.str.startswith("Dimenzije", na=False)].ponuda_id)
    print("ima Širinu:", len(ima_sirinu))
    print("ima Dimenzije ali NE Širinu:", len(ima_dim - ima_sirinu))

    ima_visinu = set(vm[vm.naziv == "Visina"].ponuda_id)
    print("ima Visinu:", len(ima_visinu))
    print("ima Dimenzije ali NE Visinu:", len(ima_dim - ima_visinu))
    return ponude, specs

if __name__ == "__main__":
    preprocess_engine()