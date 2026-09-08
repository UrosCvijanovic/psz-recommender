from flask import Flask, render_template, request

from aplikacija import predikcija, klasterovanje, preporuke, podaci

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html", kategorije=predikcija.kategorije())


@app.route('/regresija', methods=['GET', 'POST'])
def regresija():
    if request.method == 'POST':
        kat = request.form['kategorija']
        unos = { k: v for k, v in request.form.items() if k != "kategorija" and v.strip() }
        rezultat = round(predikcija.predvidi(kat, unos))
    else:
        kat = request.args.get('kategorija')
        rezultat = None
    return render_template("stranice/regresija.html",
                           kategorije=predikcija.kategorije(),
                           izabrana=kat,
                           model=predikcija.MODELI.get(kat),
                           rezultat=rezultat)

@app.route('/klasterizacija', methods=['GET', 'POST'])
def klasterizacija(rezultat=None):
    rezultat = None
    greska = None

    if request.method == 'POST':
        kat = request.form['kategorija']
        k = int(request.form['k'])

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
            greska = f"Zbor tezina je {ukupno}%, dozvoljeno je najvise 100%"
        else:
            rezultat = klasterovanje.pokreni(kat, tezine, k)
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

    rezultat = None
    lista = None

    if kat and indeks is not None:
        slicni = preporuke.slicni_proizvodi(kat, indeks, n=5)
        rezultat = slicni
    elif kat:
        lista = preporuke.pretrazi(kat, n=12)

    return render_template("stranice/preporuke.html",
                           kategorije=podaci.kategorije(),
                           izabrana=kat,
                           lista=lista,
                           rezultat=rezultat)

if __name__ == '__main__':
    app.run(debug=True)