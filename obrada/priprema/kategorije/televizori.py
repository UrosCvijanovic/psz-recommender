import re

import numpy as np

from obrada.priprema.atributi import dodaj_atribut, ek_rang
from obrada.priprema.parsiranje import parsiraj_broj, parsiraj_max, parsiraj_duzinu_cm

CENA_OPSEG = (0, 500000)

KATEGORIJA = "televizori"
NUMERICKI = ["log_dijagonala", "osvezavanje", "ek_rang"]
#KATEGORICKI = ["brend_model", "rez", "teh"]
KATEGORICKI = ["rez", "teh"]
INDIKATORI = ["ek_rang"]

"""
    (\d{3,5}) -> grupa cifara (\d) ponovljena 3 do 5 puta. Broj od 3 do 5 cifara. U zagradi pa pristupamo sa m.group(1)
    \s* -> nula ili vise belina, 3840 x 2160 i 3840x2160
    [x×] -> latinicno x ili simbol mnozenja
    \s* -> isto sa druge strane znaka
    
"""
REZ_REG = re.compile(r"(\d{3,5})\s*[x×]\s*(\d{3,5})")


def rezolucija_kategorija(v):
    if not isinstance(v, str):
        return None
    m = REZ_REG.search(v)
    if not m:
        return None

    sirina = int(m.group(1))

    if sirina >= 7000:
        return "8K"
    if sirina >= 3000:
        return "4K"
    if sirina >= 1900:
        return "FullHD"
    return "HD"


def tehnologija_grupa(v):
    if not isinstance(v, str):
        return None

    t = v.upper().replace("-", " ").replace("MINILED", "MINI LED")

    if "OLED" in t and "QLED" not in t:
        return "OLED"
    if "MINI LED" in t or "NEO QLED" in t or "NEOQLED" in t or "MICRO RGB" in t:
        return "MiniLED"
    if "QLED" in t or "QNED" in t or "NANOCELL" in t or "ULED" in t:
        return "QLED"
    if "LED" in t:
        return "LED"
    return "LCD"


def pripremi(ponude, specs):
    """Vraca DataFrame spreman za model."""

    # merge EAV
    kategorije = ponude[["id", "izvor", "kategorija", "brend"]].rename(columns={"id": "ponuda_id"})
    s = specs.merge(kategorije, on="ponuda_id", how="inner")

    # filter po kategoriji
    vm = s[s.kategorija == KATEGORIJA]
    # print(vm.shape)
    p_vm = ponude[ponude.kategorija == KATEGORIJA].copy()

    brend_freq = ponude.brend.value_counts()

    p_vm["brend_model"] = p_vm.brend.where(p_vm.brend.isin(brend_freq[brend_freq >= 30].index), "OSTALO")
    print(p_vm.brend_model.nunique(), "brendova posle sazimanja")

    p_vm = dodaj_atribut(p_vm, vm, ["Dijagonala ekrana"], "dijagonala", parsiraj_broj, opseg=(20, 250))
    p_vm = dodaj_atribut(p_vm, vm, ["Rezolucija", "Rezolucija ekrana"],"rez", rezolucija_kategorija)
    p_vm = dodaj_atribut(p_vm, vm, ["Tehnologija ekrana"], "teh", tehnologija_grupa)
    p_vm = dodaj_atribut(p_vm, vm, ["Osvežavanje"], "osvezavanje", parsiraj_max, opseg=(24, 240))

    p_vm["log_dijagonala"] = np.log(p_vm["dijagonala"])

    # energetska klasa kao rang
    p_vm["ek_rang"] = p_vm.apply(ek_rang, axis=1)

    lo, hi = CENA_OPSEG
    pre = len(p_vm)
    p_vm = p_vm[p_vm.cena.between(lo, hi)].copy()
    print(f"Cena van opsega [{lo},{hi}]: odbaceno {pre - len(p_vm)}")
    return p_vm