"""
Profilisanje sirovih JSONL podataka pred projektovanje baze.
Pokretanje:  python profil.py podaci/gigatron.jsonl podaci/tehnomedija.jsonl
"""
import json, sys, collections, re

HTML = re.compile(r"<[^>]+>")

def ucitaj(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f]

def linija(n=78):
    print("-" * n)

def kolone(skupovi):
    print("=" * 78)
    print("1. KOLONE PO IZVORU")
    print("=" * 78)
    sve = set()
    for _, d in skupovi:
        sve |= set(d[0].keys()) if d else set()
    for _, d in skupovi:
        sve |= {k for x in d for k in x}
    imena = [ime for ime, _ in skupovi]
    print(f"{'kolona':22} " + " ".join(f"{i[:14]:>16}" for i in imena))
    for k in sorted(sve):
        red = f"{k:22} "
        for _, d in skupovi:
            ima = sum(1 for x in d if x.get(k) not in (None, "", [], {}))
            red += f"{ima:>10} ({100*ima//max(len(d),1):>3}%)"
        print(red)

def vrednosti(ime, d):
    print("=" * 78)
    print(f"2. VREDNOSTI — {ime}  ({len(d)} zapisa)")
    print("=" * 78)

    # cena
    cene = [x["cena"] for x in d if isinstance(x.get("cena"), (int, float))]
    if cene:
        cene.sort()
        print(f"cena:  min={cene[0]:>10}  medijana={cene[len(cene)//2]:>10}  max={cene[-1]:>12}")
        print(f"       nula ili manje: {sum(1 for c in cene if c <= 0)}")
        print(f"       decimalne:      {sum(1 for c in cene if c != int(c))}")

    # brend
    br = collections.Counter(x.get("brend") for x in d)
    print(f"brend: {len(br)} razlicitih | top5: {[b for b,_ in br.most_common(5)]}")
    varijante = collections.defaultdict(set)
    for b in br:
        if b:
            varijante[b.strip().upper()].add(b)
    kolizije = {k: v for k, v in varijante.items() if len(v) > 1}
    print(f"       razlicito pisano isto ime: {len(kolizije)} {list(kolizije.items())[:3]}")

    # kategorija
    kat = collections.Counter(x.get("kategorija_path") for x in d)
    print(f"kategorija: {len(kat)} razlicitih punih putanja")
    sep = ">" if any(">" in (k or "") for k in kat) else "/"
    nivoi = collections.Counter(len([s for s in (k or "").split(sep) if s.strip()]) for k in kat)
    print(f"            broj nivoa: {dict(sorted(nivoi.items()))}  (separator '{sep}')")

    # ean
    ean = [str(x.get("ean") or "") for x in d]
    duz = collections.Counter(len(e) for e in ean)
    print(f"ean:   duzine {dict(sorted(duz.items()))}")
    print(f"       prazni: {duz.get(0,0)} | duplikati unutar izvora: {len(ean)-len(set(ean))}")

    # product_id
    pid = [str(x.get("product_id") or "") for x in d]
    print(f"product_id: duplikati unutar izvora: {len(pid)-len(set(pid))}")

def specifikacije(ime, d):
    print("=" * 78)
    print(f"3. SPECIFIKACIJE — {ime}")
    print("=" * 78)
    kljucevi = collections.Counter()
    ukupno_parova = 0
    sa_html = 0
    prazne = 0
    for x in d:
        s = x.get("specifikacije") or {}
        if not s:
            prazne += 1
        for k, v in s.items():
            kljucevi[k] += 1
            ukupno_parova += 1
            if isinstance(v, str) and HTML.search(v):
                sa_html += 1
    print(f"proizvoda bez specifikacija: {prazne}")
    print(f"razlicitih naziva specifikacija: {len(kljucevi)}")
    print(f"UKUPNO PAROVA (=redova u EAV tabeli): {ukupno_parova}")
    print(f"vrednosti sa HTML tagovima: {sa_html} ({100*sa_html//max(ukupno_parova,1)}%)")
    print(f"\nnajcesci nazivi (kandidati za kolone):")
    for k, n in kljucevi.most_common(25):
        print(f"   {n:6} ({100*n//len(d):>3}%)  {k}")
    retki = sum(1 for _, n in kljucevi.items() if n < len(d) * 0.01)
    print(f"\nnaziva koji se javljaju kod <1% proizvoda: {retki}")

def preklapanje(a, b, ime_a, ime_b):
    print("=" * 78)
    print("4. PREKLAPANJE IZVORA")
    print("=" * 78)
    def ok(x):
        e = str(x.get("ean") or "")
        return e if len(e) in (8, 12, 13) else None
    ea = {ok(x) for x in a} - {None}
    eb = {ok(x) for x in b} - {None}
    print(f"{ime_a}: {len(ea)} pouzdanih EAN | {ime_b}: {len(eb)}")
    print(f"presek: {len(ea & eb)} | unija: {len(ea | eb)}")
    print(f"ukupno redova ako je red = PONUDA: {len(a) + len(b)}")
    print(f"ukupno redova ako je red = PROIZVOD: ~{len(ea | eb)}")

if __name__ == "__main__":
    import json, collections

    d = [json.loads(l) for l in open("podaci/tehnomedija.jsonl", encoding="utf-8")]

    ukupno = prazne = 0
    kljucevi_praznih = collections.Counter()
    kljucevi_punih = collections.Counter()

    print(set(x["valuta"] for x in d))

    for x in d:
        for k, v in (x.get("specifikacije") or {}).items():
            ukupno += 1
            if not v:
                prazne += 1
                kljucevi_praznih[k] += 1
            else:
                kljucevi_punih[k] += 1

    print(f"parova ukupno: {ukupno} | sa praznom vrednoscu: {prazne} ({100 * prazne // ukupno}%)")
    print(f"razlicitih kljuceva: praznih={len(kljucevi_praznih)} punih={len(kljucevi_punih)}")
    print(f"kljuceva koji SU I prazni I puni: {len(set(kljucevi_praznih) & set(kljucevi_punih))}")
    print("\nprimeri praznih kljuceva:")
    for k, n in kljucevi_praznih.most_common(15):
        print(f"  {n:5}  {k[:70]}")

    retki = [k for k, n in kljucevi_punih.items() if n <= 3]
    import random;

    random.seed(1)
    for x in d:
        for k, v in (x.get("specifikacije") or {}).items():
            if k in retki and v and len(v) > 60:
                print(f"[{k}]\n  {v[:200]}\n")
                break
        if random.random() > 0.98: break

    brojac = collections.Counter()
    for x in d:
        for k in (x.get("specifikacije") or {}):
            brojac[k] += 1
    prag = len(d) * 0.01

    bez = sa = 0
    for x in d:
        s = x.get("specifikacije") or {}
        cest = sum(len(v) for k, v in s.items() if v and brojac[k] >= prag)
        redak = sum(len(v) for k, v in s.items() if v and brojac[k] < prag)
        karak = sum(len(k) for k in (x.get("karakteristike") or []))
        bez += cest + karak
        sa += cest + karak + redak

    print(f"znakova teksta bez retkih: {bez // len(d)} po proizvodu")
    print(f"znakova teksta sa retkim:  {sa // len(d)} po proizvodu")
    print(f"retki donose: +{100 * (sa - bez) // max(bez, 1)}%")

    """
    putanje = sys.argv[1:]
    skupovi = [(p.split("/")[-1], ucitaj(p)) for p in putanje]
    kolone(skupovi)
    for ime, d in skupovi:
        vrednosti(ime, d)
        specifikacije(ime, d)
    if len(skupovi) == 2:
        preklapanje(skupovi[0][1], skupovi[1][1], skupovi[0][0], skupovi[1][0])
    """