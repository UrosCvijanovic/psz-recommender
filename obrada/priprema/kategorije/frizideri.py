from obrada.priprema.atributi import dodaj_atribut, ek_rang
from obrada.priprema.parsiranje import parsiraj_broj, parsiraj_max, normalizuj_tekst

CENA_OPSEG = (10000, 500000)

KATEGORIJA = "frizideri"
NUMERICKI = ["potrosnja", "zapremina_frizidera", "zapremina_zamrzivaca", "nivo_buke", "sirina", "visina", "dubina", "ek_rang"]
#KATEGORICKI = ["brend_model", "polozaj_zamrzivaca", "no_frost"]
KATEGORICKI = ["polozaj_zamrzivaca", "no_frost"]
INDIKATORI = ["ek_rang", "zapremina_zamrzivaca"]

def pripremi(ponude, specs):
    """Vraca DataFrame spreman za model."""

    # merge EAV
    kategorije = ponude[["id", "izvor", "kategorija", "brend"]].rename(columns={"id": "ponuda_id"})
    s = specs.merge(kategorije, on="ponuda_id", how="inner")

    # filter po kategoriji
    vm = s[s.kategorija == KATEGORIJA]
    print(vm.shape)
    p_vm = ponude[ponude.kategorija == KATEGORIJA].copy()

    brend_freq = ponude.brend.value_counts()

    p_vm["brend_model"] = p_vm.brend.where(p_vm.brend.isin(brend_freq[brend_freq >= 30].index), "OSTALO")
    print(p_vm.brend_model.nunique(), "brendova posle sazimanja")

    p_vm = dodaj_atribut(p_vm, vm, ["Položaj zamrzivača"], "polozaj_zamrzivaca", normalizuj_tekst)
    p_vm = dodaj_atribut(p_vm, vm, ["No Frost"], "no_frost", normalizuj_tekst)

    p_vm = dodaj_atribut(p_vm, vm, ["Potrošnja el. energije", "Potrošnja energije"], "potrosnja", parsiraj_broj, opseg=(50, 400))
    p_vm = dodaj_atribut(p_vm, vm, ["Zapremina frižidera"], "zapremina_frizidera", parsiraj_broj)
    p_vm = dodaj_atribut(p_vm, vm, ["Zapremina zamrzivača"], "zapremina_zamrzivaca", parsiraj_broj)

    p_vm = dodaj_atribut(p_vm, vm, ["Širina"], "sirina", parsiraj_broj)
    p_vm = dodaj_atribut(p_vm, vm, ["Visina"], "visina", parsiraj_broj)
    p_vm = dodaj_atribut(p_vm, vm, ["Dubina"], "dubina", parsiraj_broj)

    p_vm = dodaj_atribut(p_vm, vm, ["Nivo buke"], "nivo_buke", parsiraj_max, opseg=(20, 90))

    # energetska klasa kao rang
    p_vm["ek_rang"] = p_vm.apply(ek_rang, axis=1)

    lo, hi = CENA_OPSEG
    pre = len(p_vm)
    p_vm = p_vm[p_vm.cena.between(lo, hi)].copy()
    print(f"Cena van opsega [{lo},{hi}]: odbaceno {pre - len(p_vm)}")

    return p_vm