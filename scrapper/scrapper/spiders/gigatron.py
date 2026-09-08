import json
import re

from scrapy.spiders import SitemapSpider

class GigatronSpider(SitemapSpider):
    name = "gigatron"
    allowed_domains = ["gigatron.rs"]
    sitemap_urls = ["https://gigatron.rs/sitemap/proizvodi.xml"]
    sitemap_rules = [(r"/proizvod/", "parse_product")]

    """
        ([0-9a-f]+): --> oznaka linije
        \["\$" --> fiksni pocetak RSC elementa
        "\$L([0-9a-f]+)", --> # oznaka komponente, npr. $L6a
        "(\d+)", # iza sledi objekat (ne trosi znak)
        (?=\{) # iza sledi objekat (ne trosi znak)
        
    """
    RSC = re.compile(r'([0-9a-f]+):\["\$","\$L([0-9a-f]+)","(\d+)",(?=\{)')

    DOZVOLJENE = (
        "bela-tehnika",
        "tv-audio-video/televizori",
        "mali-kucni-aparati",
        "mali-kuhinjski-aparati",
    )

    ZABRANJENE = (
        "bela-tehnika/oprema-za-belu-tehniku",
        "bela-tehnika/grejna-tela/dodatna-oprema-za-grejna-tela",
        "bela-tehnika/klima-uređaji-i-oprema/oprema-za-klima-uređaje",
        "bela-tehnika/sporeti/dodatna-oprema-za-sporete",
        "mali-kucni-aparati/pegle/oprema-za-peglanje",
        "mali-kucni-aparati/usisivaci/oprema-za-usisivace",
        "mali-kuhinjski-aparati/nastavci-i-dodaci",
        "mali-kuhinjski-aparati/espresso-i-kafe-aparati/dodaci-za-pripremu-kafe",
        "mali-kuhinjski-aparati/espresso-i-kafe-aparati/oprema-za-espresso-aparate",
        "mali-kuhinjski-aparati/preciscivaci-vode/zamenski-filteri-i-dodatna-oprema",
        "mali-kuhinjski-aparati/preciscivaci-vode/ugradni-filteri",
        "mali-kuhinjski-aparati/espresso-i-kafe-aparati/kafe",
        "mali-kuhinjski-aparati/preciscivaci-vode/flasice"
    )

    PRIBOR_RECI = ("oprema", "dodaci", "dodatna", "pribor", "zamenski", "filteri", "nastavci")

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 3,
        "USER_AGENT": "psz-recommender studentski projekat",
        "AUTOTHROTTLE_ENABLED": True
        #"CLOSESPIDER_TIMEOUT": 120,
    }

    @staticmethod
    def ocisti(v):
        if not isinstance(v, str):
            return v
        v = v.strip()
        if not v:
            return None
        if v.startswith("$"): # '$undefined', '$65', '$32:props:...'
            return None
        return v

    @staticmethod
    def rsc_strings(html):
        """
            Vrati listu string-argumenata iz svih self.__next_f.push([1,"..."]).
        """
        out = []
        marker = 'self.__next_f.push([1,'
        idx = 0
        while True:
            i = html.find(marker, idx)

            if i == -1:
                break
            start = i + len(marker)
            # argument je JSON string koji pocinje sa " ---> nadji ga json dekoderom
            try:
                s, end = json.JSONDecoder().raw_decode(html, start) # dekoder pravilno postuje escape "\" znake, zato koristimo raw decoder umesto
                if isinstance(s, str):
                    out.append(s)
                idx = end
            except ValueError:
                idx = start + 1
        return out

    def je_pribor(self, path):
        zadnji = path.split("/")[-1]
        return any(r in zadnji for r in self.PRIBOR_RECI)

    def u_kategoriji(self, path):
        if not path:
            return False
        if any(path == p or path.startswith(p + "/") for p in self.ZABRANJENE):
            return False
        if self.je_pribor(path):
            return False
        return any(path == p or path.startswith(p + "/") for p in self.DOZVOLJENE)

    def view_item(self, payload):
        """Vrati product objekat iz view_item bloka, ili None."""
        i = payload.find('"event":"view_item"')
        if i == -1:
            return None
        j = payload.find('"product":', i)
        if j == -1:
            return None
        k = payload.find("{", j)
        if k == -1:
            return None
        try:
            obj, _ = json.JSONDecoder().raw_decode(payload, k)
        except ValueError:
            return None
        return obj if isinstance(obj, dict) else None

    def extract_pdp(self, payload, slug):
        for match in self.RSC.finditer(payload):
            try:
                obj, _ = json.JSONDecoder().raw_decode(payload, match.end())
            except ValueError:
                continue
            if not isinstance(obj, dict):
                continue
            if obj.get("urlKey") != slug:
                continue
            if obj.get("productId") != match.group(3):
                self.logger.warning("Product Id se ne poklapa (%s vs %s)", match.group(3), obj.get("productId"))
            return obj
        return None

    def parse_product(self, response):
        payload = "".join(self.rsc_strings(response.text))
        # sidro: objekat koji prosledjuje PdpClientReviewsShell komponenta

        # slug iz URL-a: poslednji segment, otporan na trailing slash i query
        slug = response.url.split("?")[0].rstrip("/").split("/")[-1]

        obj = self.extract_pdp(payload, slug)
        if obj is None:
            self.logger.warning("Nema PDP objekta: %s", response.url)
            return

        path = (obj.get("lastCategory") or {}).get("url_path")
        if not self.u_kategoriji(path):
            return

        prod = self.view_item(payload)
        brand = None
        if prod is None:
            self.logger.warning("Nema view_item bloka: %s", response.url)
        elif prod.get("productId") != obj.get("productId"): # dva bloka pricaju o razlicitim proizvodima
            self.logger.warning("productId se ne poklapa izmedju blokova (%s vs %s): %s",prod.get("productId"), obj.get("productId"), response.url,)
        else:
            brand = prod.get("brand")
            
        yield self.build_item(obj, brand, path, response.url)

    def build_item(self, obj, brand, path, url):
        specs = {}
        for s in obj.get("specifications", []):
            ime, vrednost = s.get("name"), s.get("value")
            if ime:
                specs[ime] = self.ocisti(vrednost)

        return {
            "url": url,
            "izvor": "gigatron.rs",
            "product_id": obj.get("productId"),
            "sku": obj.get("sku"),
            "ean": obj.get("ean"),
            "naziv": obj.get("name"),
            "brend": brand,
            "kategorija_path": path,
            "cena": obj.get("specialPrice"),
            "cena_redovna": obj.get("priceRegular"),
            "dostupan": obj.get("available"),
            "energetska_klasa": self.ocisti(obj.get("energyLabel")),
            "slika": obj.get("imageUrl"),
            "ocena": (obj.get("initialRating") or {}).get("average"),
            "broj_ocena": (obj.get("initialRating") or {}).get("total"),
            "specifikacije": specs,
        }