
RANG_NOVA = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
RANG_STARA = {"A+++": 1, "A++": 2, "A+": 3, "A": 4, "B": 5, "C": 6, "D": 7, "E": 8, "F": 9, "G": 10}

def ek_rang(red):
    if red["ek_skala"] == "nova":
        return RANG_NOVA.get(red["ek_ocena"])
    if red["ek_skala"] == "stara":
        return RANG_STARA.get(red["ek_ocena"])
    return None


def pokrivenost(vm, nazivi, oznaka):
    ids = set(vm[vm.naziv.isin(nazivi)].ponuda_id)
    n = vm.ponuda_id.nunique()
    print(f"{oznaka:25} {len(ids):4} / {n}  ({100*len(ids)/n:.1f}%)")
    return ids

def dodaj_atribut(p_vm, vm, nazivi, kolona, parser, prioritet = None, opseg=None):
    """
        Parsira jedan numericki atribut iz EAV tabele i lepi ga na p_vm.
    """
    d = vm[vm.naziv.isin(nazivi)].copy()
    d[kolona] = d.vrednost.apply(parser)
    if prioritet:
        d["prio"] = d.naziv.map(prioritet)
        d = d.sort_values(by="prio").drop_duplicates("ponuda_id", keep="first")
    p_vm[kolona] = p_vm["id"].map(d.set_index("ponuda_id")[kolona])

    if opseg:
        lo, hi = opseg
        #van = p_vm.loc[~((p_vm[kolona] < lo) | (p_vm[kolona] > hi))]
        van = (~p_vm[kolona].between(lo, hi) & p_vm[kolona].notna()).sum()
        if van:
            print(f"  {kolona}: {van} vrednosti van opsega [{lo},{hi}] -> None")
        p_vm.loc[~p_vm[kolona].between(lo, hi), kolona] = None
    return p_vm