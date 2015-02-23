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

    def ime_vlasnika(self):
        return self._ime_vlasnika

    def set_ime_vlasnika(self, ime_vlasnika_in):
        self._ime_vlasnika = ime_vlasnika_in

class Vlasnik:
    def __init__(self, ime):
        self._ime = ime
        self._lista_cijena = []
        
    def ime(self):
        return self._ime
        
    def cijene(self):
        return self._lista_cijena

    def dodaj_cijenu(self, cijena, broj_postaja):
        self._lista_cijena.append((cijena, broj_postaja))

    def index(self):
        i = 0
        br = 0
        
        for (cijena, broj_postaja) in self._lista_cijena:
            i += cijena * broj_postaja
            br += broj_postaja
            
        return i / br

def gen_vlasnike_postaja(tree):
    """Generira dictionary koji mapira postaju sa njenim vlasnikom"""
    vlasnici_postaja = {}
    
    for vlasnik in tree:
        vlasnici_postaja[vlasnik["id_postaja"]] = vlasnik["obveznik"]

    return vlasnici_postaja

def gen_imena_vlasnika(tree):
    imena_vlasnika = {}

    for obveznik in tree:
        imena_vlasnika[obveznik["id_obveznik"]] = obveznik["naziv"]

    return imena_vlasnika

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
    
    vlasnici = map(lambda x: x.ime_vlasnika(), lista_postaja)

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
    
def gen_cijene_sa_vlasnicima(vrsta_goriva = 2, limit = 0):
    vrsta_goriva = str(vrsta_goriva)

    obveznik_json = load_obveznik()
    imena_vlasnika = gen_imena_vlasnika(obveznik_json)

    postaja_json = load_postaja()
    vlasnici_postaja = gen_vlasnike_postaja(postaja_json)

    cijene_json = load_cijene()
    lista_postaja = []
    for postaja in cijene_json:
        p = Postaja(postaja)
        p.set_ime_vlasnika(imena_vlasnika[vlasnici_postaja[int(p.id())]])
        lista_postaja.append(p)

    # print "Fetching done."
    
    cijene = dict_cijena_sa_postajama_za_vrstu(lista_postaja, vrsta_goriva)
    sortirane_cijene = sorted(cijene.items(), key = lambda x: x[0])

    cijene_sa_vlasnicima = []
    for (cijena, postaje) in sortirane_cijene:
        if not cijena:
            continue
        freq = frekvencija_vlasnika(postaje)
        filtered_freq = sorted(filter(lambda x: x[1] >= limit, freq), key = lambda x: -x[1])
        if filtered_freq:
            cijene_sa_vlasnicima.append((cijena, filtered_freq))

    return cijene_sa_vlasnicima

def gen_vlasnici_sa_cijenama(cijene_sa_vlasnicima):
    vlasnici_sa_cijenama = {}
    
    for cijena, vlasnici in cijene_sa_vlasnicima:
        for vlasnik in vlasnici:
            if not vlasnik[0] in vlasnici_sa_cijenama:
                vlasnici_sa_cijenama[vlasnik[0]] = Vlasnik(vlasnik[0])
            vlasnici_sa_cijenama[vlasnik[0]].dodaj_cijenu(cijena, vlasnik[1])

    vlasnici_sa_cijenama = sorted(vlasnici_sa_cijenama.values(), key=lambda x: x.ime())
    return vlasnici_sa_cijenama
            

if __name__ == "__main__":
    cijene_sa_vlasnicima = gen_cijene_sa_vlasnicima(limit = 4)
    vlasnici_sa_cijenama = gen_vlasnici_sa_cijenama(cijene_sa_vlasnicima)

    for c in cijene_sa_vlasnicima:
        print c

    print "--------------"
    
    for vlasnik in vlasnici_sa_cijenama:
        print vlasnik.ime(), vlasnik.cijene(), format("%.2f" % vlasnik.index())
