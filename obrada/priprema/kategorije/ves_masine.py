from obrada.priprema.atributi import dodaj_atribut, ek_rang
from obrada.priprema.parsiranje import parsiraj_broj, parsiraj_max, parsiraj_duzinu_cm

KATEGORIJA = "ves-masine"
NUMERICKI = ["kapacitet", "centrifuga", "nivo_buke", "dubina", "ek_rang"]
#KATEGORICKI = ["brend_model", "tip"]
KATEGORICKI = ["tip"]
CENTRIFUGA = ["Brzina centrifuge", "Broj obrtaja centrifuge"]
INDIKATORI = ["ek_rang", "centrifuga"]

def tip_ves_masine(pid, ima_pranje, ima_susenje):
    pranje = pid in ima_pranje
    susenje = pid in ima_susenje
    if pranje and susenje:
        return "pranje_susenje"
    if susenje:
        return "susenje"
    if pranje:
        return "pranje"
    return None

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

    # =============== Razdvajanje Kapaciteta pranja i susenja (ves masine, susilice, ves masine + susilice) ===============
    ima_pranje = set(vm[vm.naziv.isin(["Kapacitet", "Kapacitet pranja"])].ponuda_id)
    ima_susenje = set(vm[vm.naziv == "Kapacitet sušenja"].ponuda_id)
    print("Ima pranje: ", len(ima_pranje))
    print("Ima susenje: ", len(ima_susenje))
    print("Ima oba: ", len(list(set(ima_pranje) & set(ima_susenje))))

    p_vm["tip"] = p_vm["id"].apply(tip_ves_masine, ima_pranje=ima_pranje, ima_susenje=ima_susenje)
    print(p_vm.tip.value_counts(dropna=False))


    # =============== Kapacitet pranja i susenja u kg ===============
    prioritet = {"Kapacitet": 1, "Kapacitet pranja": 1, "Kapacitet sušenja": 2}

    kapacitet = vm[vm.naziv.isin(prioritet.keys())].copy()
    kapacitet["kg"] = kapacitet.vrednost.apply(parsiraj_broj)

    # za kombinovan mod uzmimamo kapacitet pranja, ne susenja
    p_vm = dodaj_atribut(p_vm, vm, prioritet.keys(), "kapacitet", parsiraj_broj, prioritet=prioritet, opseg=(3, 20))
    p_vm = dodaj_atribut(p_vm, vm, CENTRIFUGA, "centrifuga", parsiraj_max, opseg=(400, 2000))
    p_vm = dodaj_atribut(p_vm, vm, ["Nivo buke"], "nivo_buke", parsiraj_max, opseg=(40, 90))
    p_vm = dodaj_atribut(p_vm, vm, ["Dubina"], "dubina", parsiraj_duzinu_cm, opseg=(30, 80))

    # energetska klasa kao rang
    p_vm["ek_rang"] = p_vm.apply(ek_rang, axis=1)

    return p_vm