import re

REPLACE_COMMA = re.compile(r"(?<=\d),(?=\d)")

def parsiraj_broj(v): # "8 kg" => 8.0
    if not isinstance(v, str):
        return None
    # zarez u tacku izmedju cifara
    v = re.sub(REPLACE_COMMA, ".", v)
    m = re.search(r"\d+(?:\.\d+)?", v)
    return float(m.group()) if m else None

def parsiraj_max(v): # "1400/1200 o/min" => 1400.0
    if not isinstance(v, str):
        return None
    v = re.sub(REPLACE_COMMA, ".", v)
    brojevi = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", v)]
    return max(brojevi) if brojevi else None

def parsiraj_duzinu_cm(v): # "585 mm" => 58.5
    if not isinstance(v, str):
        return None

    v = re.sub(REPLACE_COMMA, ".", v)
    m = re.search(r"(\d+(?:\.\d+)?)\s(mm|cm)?", v, re.IGNORECASE)
    if not m:
        return None

    broj = float(m.group(1))
    if (m.group(2) or "").lower() == "mm":
        broj /= 10
    return broj

def normalizuj_tekst(v):
    if not isinstance(v, str):
        return None
    return v.strip().capitalize()