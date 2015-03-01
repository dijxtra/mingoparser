# -*- coding: utf-8 -*-
import json
from collections import defaultdict
import urllib2
import os

ONLINE = False

def path():
    dirname = os.path.dirname(__file__)
    
    if dirname == '':
        return ''
    else:
        return dirname + '/'

def load_vrste():
    if (ONLINE):
        url = 'http://min-go.hr/api/web_api/web/vrste-goriva'
        return json.loads(urllib2.urlopen(url).read())
    else:
        file_name = path() + 'inputs/vrste-goriva'
        with open(file_name) as f:
            return json.loads(f.read())

def load_obveznik():
    if (ONLINE):
        url = 'http://min-go.hr/api/web_api/web/obveznik'
        return json.loads(urllib2.urlopen(url).read())
    else:
        file_name = path() + 'inputs/obveznik'
        with open(file_name) as f:
            return json.loads(f.read())

def load_postaja():
    if (ONLINE):
        url = 'http://min-go.hr/api/web_api/web/postaja'
        return json.loads(urllib2.urlopen(url).read())
    else:
        file_name = path() + 'inputs/postaja'
        with open(file_name) as f:
            return json.loads(f.read())

def load_cijene():
    if (ONLINE):
        url = 'http://min-go.hr/api/web_api/web/vazeca-cijena'
        return urllib2.urlopen(url).read()
    else:
        file_name = path() + 'inputs/vazeca-cijena'
        with open(file_name) as f:
            return json.loads(f.read())


class Postaja:
    def __init__(self, json_in):
        self._id = json_in["id_postaja"]
        self.nazivi_po_vrsti = {}
        self.cijene_po_vrsti = {}
        
        for c in json_in["cijena"]:
            self.nazivi_po_vrsti[c["vrsta_goriva"]] = c["naziv"]

            cijena = float(c["cijena"])
            if cijena > 100: #Ako je cijena veća od 100, onda se vrlo vjerojatno radi o cijeni kojoj nedostaje decimalni zarez.
                cijena = cijena / 100
            self.cijene_po_vrsti[c["vrsta_goriva"]] = cijena


    def id(self):
        """Vraća ID postaje"""
        return self._id
        
    def cijena(self, vrsta_goriva):
        """Vraća cijenu vrste goriva na postaji."""
        
        if vrsta_goriva in self.cijene_po_vrsti:
            return self.cijene_po_vrsti[vrsta_goriva]
        else:
            return None
    
    def ime_goriva(vrsta_goriva):
        """Vraća ime vrste goriva na postaji."""
        
        if vrsta_goriva in self.nazivi_po_vrsti:
            return self.nazivi_po_vrsti[vrsta_goriva]
        else:
            return None

    def vrste_goriva_sa_cijenom(self):
        return self.cijene_po_vrsti
        
    def vlasnik(self):
        return self._vlasnik

    def set_vlasnik(self, vlasnik_in):
        self._vlasnik = vlasnik_in

class Vlasnik:
    def __init__(self, id, ime):
        self._id = id
        self._ime = ime
        self._lista_cijena = []
        self._lista_postaja = []
        self._cijene_sa_brojem_postaja = {}
        
    def id(self):
        return self._id
        
    def ime(self):
        return self._ime
        
    def cijene(self):
        return self._lista_cijena

    def dodaj_cijenu(self, cijena, broj_postaja):
        self._lista_cijena.append((cijena, broj_postaja))

    def dodaj_postaju(self, postaja):
        self._lista_postaja.append(postaja)

    def broj_postaja(self):
        return len(self._lista_postaja)

    def gen_cijene_sa_brojem_postaja(self):
        self._cijene_sa_brojem_postaja = {}
        for postaja in self._lista_postaja:
            vgsc = postaja.vrste_goriva_sa_cijenom()
            for vrsta_goriva in vgsc:
                cijena = vgsc[vrsta_goriva]
                if not int(vrsta_goriva) in self._cijene_sa_brojem_postaja:
                    self._cijene_sa_brojem_postaja[int(vrsta_goriva)] = {}
                if not cijena in self._cijene_sa_brojem_postaja[int(vrsta_goriva)]:
                    self._cijene_sa_brojem_postaja[int(vrsta_goriva)][cijena] = 0
                self._cijene_sa_brojem_postaja[int(vrsta_goriva)][cijena] += 1

    def cijene_sa_brojem_postaja(self, vrsta_goriva):
        if vrsta_goriva in self._cijene_sa_brojem_postaja:
            return self._cijene_sa_brojem_postaja[vrsta_goriva]
        else:
            return {}

    def nudi_gorivo(self, vrsta_goriva):
        if vrsta_goriva in self._cijene_sa_brojem_postaja:
            return True
        else:
            return False
        
    def gen_indeksi(self):
        self._indeksi = {}
        for vrsta_goriva in self._cijene_sa_brojem_postaja:
            i = 0
            br = 0
            for cijena in self._cijene_sa_brojem_postaja[vrsta_goriva]:
                broj_postaja = self._cijene_sa_brojem_postaja[vrsta_goriva][cijena]
                i += cijena * broj_postaja
                br += broj_postaja
                print br

            self._indeksi[vrsta_goriva] = i / br
                    
            
    def index(self):
        i = 0
        br = 0
        
        for (cijena, broj_postaja) in self._lista_cijena:
            i += cijena * broj_postaja
            br += broj_postaja
            
        return i / br

    def indeks(self, vrsta_goriva):
        if vrsta_goriva in self._indeksi:
            return self._indeksi[vrsta_goriva]
        else:
            return None

def gen_vlasnici_postaja_dict(tree):
    """Generira dictionary koji mapira postaju sa njenim vlasnikom"""
    vlasnici_postaja = {}
    
    for vlasnik in tree:
        vlasnici_postaja[vlasnik["id_postaja"]] = vlasnik["obveznik"]

    return vlasnici_postaja

def gen_vlasnici(tree):
    vlasnici = {}

    for obveznik in tree:
        vlasnici[obveznik["id_obveznik"]] = Vlasnik(obveznik["id_obveznik"], obveznik["naziv"])

    return vlasnici

def gen_vrste_goriva(json):
    vrste_goriva = []

    for gorivo in json:
        vrste_goriva.append([gorivo["id_vrstagoriva"], gorivo["vrsta_goriva"]])

    return vrste_goriva

def dict_cijena_sa_postajama_za_vrstu(lista_postaja, vrsta_goriva):
    """Generira dictionary popisa postaja po cijeni vrste goriva.

    Za svaku postaju određuje se cijena za ulaznu vrstu goriva i zatim se dodjeljuje u dictionary pod tom cijenom.
    """
    
    postaje_po_cijenama = {}
    for postaja in lista_postaja:
        cijena = postaja.cijena(vrsta_goriva)
        if cijena in postaje_po_cijenama:
            postaje_po_cijenama[cijena].append(postaja)
        else:
            postaje_po_cijenama[cijena] = [postaja]

    return postaje_po_cijenama
    
def frekvencija_vlasnika(lista_postaja):
    """Prima listu postaja i vraća listu parova (ime vlasnika postaje, frekvencija)"""
    
    vlasnici = map(lambda x: x.vlasnik(), lista_postaja)

    d = defaultdict(int)
    for k in vlasnici:
        d[k] += 1

    return d.items()
    
def vrste_goriva():
    vrste_json = load_vrste()
    vrste_goriva = gen_vrste_goriva(vrste_json)
    return vrste_goriva

def main(vrsta_goriva = 2, limit = 0):
    return gen_cijene_sa_vlasnicima(vrsta_goriva, limit)
    
def gen_cijene_po_postajama():
    obveznik_json = load_obveznik()
    vlasnici = gen_vlasnici(obveznik_json)

    postaja_json = load_postaja()
    vlasnici_postaja = gen_vlasnici_postaja_dict(postaja_json)

    cijene_json = load_cijene()
    lista_postaja = []
    for postaja in cijene_json:
        p = Postaja(postaja)
        p.set_vlasnik(vlasnici[vlasnici_postaja[int(p.id())]])
        lista_postaja.append(p)

    # print "Fetching done."
    return lista_postaja
    
def gen_cijene_sa_vlasnicima(vrsta_goriva = 2, limit = 0):
    vrsta_goriva = str(vrsta_goriva)

    lista_postaja = gen_cijene_po_postajama()
    cijene = dict_cijena_sa_postajama_za_vrstu(lista_postaja, vrsta_goriva)

    cijene_sa_vlasnicima = []
    for (cijena, postaje) in cijene.items():
        if not cijena:
            continue
        freq = frekvencija_vlasnika(postaje)
        filtered_freq = sorted(filter(lambda x: x[1] >= limit, freq), key = lambda x: -x[1])
        if filtered_freq:
            cijene_sa_vlasnicima.append((cijena, filtered_freq))

    return cijene_sa_vlasnicima

def gen_vlasnici_full():
    obveznik_json = load_obveznik()
    vlasnici = gen_vlasnici(obveznik_json)

    postaja_json = load_postaja()
    vlasnici_postaja = gen_vlasnici_postaja_dict(postaja_json)

    cijene_json = load_cijene()
    lista_postaja = []
    for postaja in cijene_json:
        p = Postaja(postaja)
        vlasnik = vlasnici[vlasnici_postaja[int(p.id())]]
        
        vlasnik.dodaj_postaju(p)
        p.set_vlasnik(vlasnik)
        
        lista_postaja.append(p)

    for vlasnik in vlasnici.values():
        vlasnik.gen_cijene_sa_brojem_postaja()
        vlasnik.gen_indeksi()

    
    for vlasnik in vlasnici.values():
        print vlasnik.ime(), vlasnik._cijene_sa_brojem_postaja

    return vlasnici

def gen_hrvatska(cijene_sa_vlasnicima):
    hrvatska = Vlasnik(0, "Hrvatska")

    for (cijena, lista_vlasnika) in cijene_sa_vlasnicima:
        ukupno_postaja = 0
        for (vlasnik, broj_postaja) in lista_vlasnika:
            ukupno_postaja += broj_postaja
        hrvatska.dodaj_cijenu(cijena, ukupno_postaja)

    return hrvatska
    
if __name__ == "__main__":
    limit = 4
    vlasnici = gen_vlasnici_full()

    cijene_sa_vlasnicima = gen_cijene_sa_vlasnicima(limit = limit)

    for (cijena, lista_vlasnika) in cijene_sa_vlasnicima:
        print cijena, map(lambda x: (x[0].ime(), x[1]), lista_vlasnika)

    print "--------------"

    sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())
    for vlasnik in sortirani_vlasnici:
        if vlasnik.broj_postaja() >= limit:
            if vlasnik.nudi_gorivo(2):
                print vlasnik.ime(), vlasnik.cijene_sa_brojem_postaja(2), format("%.2f" % vlasnik.indeks(2))

    print "--------------"

    hrvatska = gen_hrvatska(cijene_sa_vlasnicima)

    print hrvatska.ime(), format("%.3f" % hrvatska.index())
