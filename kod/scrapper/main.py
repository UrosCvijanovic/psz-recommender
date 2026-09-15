import json, collections

g = [json.loads(l) for l in open("../podaci/gigatron.jsonl", encoding="utf-8")]
t = [json.loads(l) for l in open("../podaci/tehnomedija.jsonl", encoding="utf-8")]

p = [x for x in g if isinstance(x["cena"], float) and x["cena"] != int(x["cena"])]
print(p)
print(collections.Counter(x["dostupan"] for x in t))
print(collections.Counter(x["dostupan"] for x in g))

sve = [k for x in t for k in (x.get("karakteristike") or [])]
print("sa novim redom:", sum(1 for k in sve if "\n" in k))
print("sa zarezom:", sum(1 for k in sve if "," in k))

print(collections.Counter(type(x.get("dostupan")).__name__ for x in t))
lose = [x for x in t if not isinstance(x.get("dostupan"), bool)]
print(len(lose))
for x in lose[:3]:
    print(repr(x.get("dostupan")), "|", x["url"])


sumnjivi = [x for x in t if x.get("cena") == 233799]
for x in sumnjivi:
    print(repr(x.get("dostupan")), "|", repr(x.get("opis"))[:60], "|", x["url"])

"""
d = [json.loads(l) for l in open("test.jsonl", encoding="utf-8")]
print(len(d))
print("bez slike:      ", sum(1 for x in d if not x["slika"]))
print("prazne specs:   ", sum(1 for x in d if not x["specifikacije"]))
print("prazne karakt.: ", sum(1 for x in d if not x["karakteristike"]))
print("sa cena_mp:     ", sum(1 for x in d if x["cena_mp_raw"]))
znakovi = sorted(sum(len(v) for v in x["specifikacije"].values() if v) for x in d)
print("medijana znakova u specs:", znakovi[len(znakovi)//2], "(pre popravke bilo 107)")

print("min:", znakovi[0], "| 25%:", znakovi[len(znakovi)//4], "| medijana:", znakovi[len(znakovi)//2],
      "| 75%:", znakovi[3*len(znakovi)//4], "| max:", znakovi[-1])

b = next((x for x in d if "BM3WFSU37413WPBB1" in x["naziv"]), None)
if b:
    print("Beko:", sum(len(v) for v in b["specifikacije"].values() if v), "znakova,",
          len(b["specifikacije"]), "kljuceva")

import collections
po_kat = collections.defaultdict(list)
for x in d:
    kat = x["kategorija_path"].split(">")[0].strip()
    po_kat[kat].append(sum(len(v) for v in x["specifikacije"].values() if v))
for k, v in sorted(po_kat.items(), key=lambda i: -len(i[1])):
    v.sort()
    print(f"{k:28} n={len(v):4} medijana={v[len(v)//2]:5}")

for x in d:
    if not x["specifikacije"]:
        print(x["url"], "| karakteristike:", len(x["karakteristike"]))
"""

"""
g = [json.loads(l) for l in open("products_full.jsonl", encoding="utf-8")]
t = [json.loads(l) for l in open("tehnomedija_full.jsonl", encoding="utf-8")]

# samo pouzdani EAN-ovi (13, 12, 8 cifara)
def ean_set(data):
    return {str(d["ean"]) for d in data if d.get("ean") and len(str(d["ean"])) in (8, 12, 13)}

eg, et = ean_set(g), ean_set(t)
print("Gigatron:", len(eg), "| Tehnomedia:", len(et))
print("presek:", len(eg & et))
print("unija:", len(eg | et))
"""

"""
print(len(data))
print(collections.Counter(d["kategorija_path"].split("/")[0] for d in data))
print("televizori:", sum(1 for d in data if d["kategorija_path"].startswith("tv-audio-video")))
print("bez brenda:", sum(1 for d in data if not d["brend"]))
print("bez cene:", sum(1 for d in data if not d["cena"]))
print("sa energ. klasom:", sum(1 for d in data if d["energetska_klasa"]))
print("duplikati po product_id:", len(data) - len({d["product_id"] for d in data}))
"""

""" 
data = [json.loads(l) for l in open("tehnomedija.jsonl", encoding="utf-8")]
print(collections.Counter(d["cat"].split(" > ")[0] for d in data).most_common())

print(collections.Counter(
    " > ".join(d["cat"].split(" > ")[:2])
    for d in data if d["cat"].startswith("TV")
).most_common())


for c in sorted(set(d["cat"].split(" > ")[0] for d in data)):
    print(repr(c))

razlika = sum(1 for d in data if d.get("gtin") and d.get("sku") and d["gtin"] != d["sku"])
prazni = sum(1 for d in data if not d.get("gtin"))
print("gtin != sku:", razlika, "| bez gtin:", prazni)
"""