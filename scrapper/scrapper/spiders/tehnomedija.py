import json
from scrapy.spiders import SitemapSpider

class TehnomedijaSpider(SitemapSpider):
    name = "tehnomedija"
    allowed_domains = ["www.tehnomedia.rs"]
    sitemap_urls = ["https://www.tehnomedia.rs/sitemap.xml"]
    sitemap_rules = [(r"/proizvod/", "parse_product")]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "AUTOTHROTTLE_ENABLED": True,
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_IGNORE_MISSING": True,
        "HTTPCACHE_EXPIRATION_SECS": 0,
        "USER_AGENT": "psz-recommender studentski projekat",
        #"CLOSESPIDER_TIMEOUT": 60,
    }

    DOZVOLJENE = {
        "Bela tehnika",
        "Mali kuhinjski aparati",
        "Mali kućni aparati",
        "Mali kućni i kuhinjski aparati",
        "Grejanje i hlađenje",
        "Klimatizacija i grejanje",
    }

    def json_ld_product (self, response):
        for b in response.css('script[type="application/ld+json"]::text').getall():
            obj = json.loads(b)
            if obj.get('@type') == "Product":
                return obj
            for node in obj.get("@graph", []):
                if node.get('@type') == "Product":
                    return node
        return None

    def u_kategoriji(self, kategorija):
        if not kategorija:
            return False

        segmenti = [s.strip() for s in kategorija.split(">")]

        prvi = segmenti[0]
        if prvi in self.DOZVOLJENE:
            return True

        if prvi.startswith("TV") and len(segmenti) > 1 and segmenti[1] == "Televizori":
            return True
        return False

    def parse_product(self, response):
        p = self.json_ld_product(response)
        if p is None:
            self.logger.warning("Nema Product JSON-LD: %s", response.url)
            return

        kategorija = p.get("category", "")
        if not self.u_kategoriji(kategorija):
            return

        specs = {}
        karakteristike = []
        tekuci = None

        for tr in response.css("table.product-full-desc-table tr"):
            # naslov stranice ili samostalna karakteristika
            if tr.css("td.feature-title"):
                t = " ".join(x.strip() for x in tr.css("td.feature-title ::text").getall() if x.strip())
                if t:
                    karakteristike.append(t)
                tekuci = None
                continue
            # nastavak prethodnog kljuca
            if tr.css("td.feature-item"):
                t = " ".join(x.strip() for x in tr.css("td.feature-item ::text").getall() if x.strip())
                if not t:
                    continue
                if tekuci:
                    specs[tekuci] = ((specs[tekuci] or "") + "\n" + t).strip()
                else:
                    karakteristike.append(t)
                continue

            # obican kljuc-vrednost
            kljuc = " ".join(x.strip() for x in tr.css("td.feature ::text").getall() if x.strip())
            if kljuc:
                vrednost = " ".join(x.strip() for x in tr.xpath("td[2]//text()").getall() if x.strip())
                specs[kljuc] = vrednost or None
                tekuci = kljuc

        offers = p.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}

        img = p.get("image")
        if isinstance(img, list):
            img = img[0] if img else None

        dostupan = p.get("dostupan")
        if not isinstance(dostupan, bool):
            dostupan = False

        cena_mp = response.css("del::text").get() # cena maloprodaja

        yield {
            "url": response.url,
            "izvor": "tehnomedija.rs",
            "product_id": p.get("productID"),
            "ean": p.get("gtin") or p.get("sku"),
            "naziv": p.get("name"),
            "opis": p.get("description"),
            "brend": (p.get("brand") or {}).get("name"),
            "kategorija_path": p.get("category"),
            "cena": offers.get("price"),
            "cena_mp_raw": cena_mp,
            "valuta": offers.get("priceCurrency"),
            "slika": img,
            "dostupan": "InStock" in offers.get("availability") or "",
            "energetska_klasa": specs.get("Energetska klasa") or specs.get("Energetske klasa"),
            "specifikacije": specs,
            "karakteristike": karakteristike,
        }