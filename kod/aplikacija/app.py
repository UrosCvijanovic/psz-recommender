from flask import Flask, render_template, request

from aplikacija import predikcija, klasterovanje, preporuke, podaci

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html", kategorije=predikcija.kategorije())


@app.route('/regresija', methods=['GET', 'POST'])
def regresija():
    kat = request.values.get('kategorija')
    indeks = request.args.get('indeks', type=int)

    rezultat = None
    lista = None

    if request.method == 'POST' and kat:
        rezultat = predikcija.predvidi_rucno(kat, request.form)
    elif kat and indeks is not None:
        rezultat = predikcija.predvidi_za_id(kat, indeks)
    elif kat:
        lista = predikcija.test_proizvodi(kat)

    return render_template("stranice/regresija.html",
                           kategorije=podaci.kategorije(),
                           izabrana=kat,
                           lista=lista,
                           model=predikcija.MODELI.get(kat),
                           rezultat=rezultat)



@app.route('/klasterizacija', methods=['GET', 'POST'])
def klasterizacija():
    rezultat = None
    greska = None

    if request.method == 'POST':
        kat = request.form.get('kategorija')
        k = int(request.form.get('k', 3))

        tezine = {}
        for polje, vrednost in request.form.items():
            if polje.startswith('tez_') and vrednost.strip():
                t = float(vrednost)
                if t > 0:
                    tezine[polje[4:]] = t

        ukupno = sum(tezine.values())
        if not tezine:
            greska = "Izaberite bar jedan atribut (težina veća od 0)."
        elif ukupno > 100:
            greska = f"Zbir težina je {ukupno}%, dozvoljeno je najviše 100%."
        else:
            rezultat, greska = klasterovanje.pokreni(kat, tezine, k)
    else:
        kat = request.args.get('kategorija')

    return render_template("stranice/klasteri.html", kategorije=predikcija.kategorije(),
                           izabrana=kat,
                           atributi=klasterovanje.atributi(kat) if kat else None,
                           rezultat=rezultat,
                           greska=greska)


@app.route('/preporuke')
def preporuke_stranica():
    kat = request.args.get('kategorija')
    indeks = request.args.get('indeks', type=int)
    upit = request.args.get('upit', '')

    rezultat = None
    lista = None

    if kat and indeks is not None:
        slicni = preporuke.slicni_proizvodi(kat, indeks, n=5)
        rezultat = slicni
    elif kat:
        lista = preporuke.pretrazi(kat, upit=upit, n=12)

    return render_template("stranice/preporuke.html",
                           kategorije=podaci.kategorije(),
                           izabrana=kat,
                           lista=lista,
                           rezultat=rezultat)

if __name__ == '__main__':
    app.run(debug=True)