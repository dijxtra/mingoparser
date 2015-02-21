# -*- coding: utf-8 -*-
import json
from collections import defaultdict
import urllib2

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
    
if __name__ == "__main__":
    vrsta_goriva = "2"
    limit = 3
    obveznik_url = 'http://min-go.hr/api/web_api/web/obveznik'
    postaja_url = 'http://min-go.hr/api/web_api/web/postaja'
    cijene_url = 'http://min-go.hr/api/web_api/web/vazeca-cijena'

    print "Fetching obveznik..."
    obveznik_json = json.loads(urllib2.urlopen(obveznik_url).read())
    imena_vlasnika = gen_imena_vlasnika(obveznik_json)

    print "Fetching postaja..."
    postaja_json = json.loads(urllib2.urlopen(postaja_url).read())
    vlasnici_postaja = gen_vlasnike_postaja(postaja_json)

    print "Fetching cijene..."
    cijene_json = urllib2.urlopen(cijene_url).read()
    j = json.loads(cijene_json)
    lista_postaja = []
    for postaja in j:
        p = Postaja(postaja)
        p.set_ime_vlasnika(imena_vlasnika[vlasnici_postaja[int(p.id())]])
        lista_postaja.append(p)

    print "Fetching done."
    
    cijene = dict_cijena_sa_postajama_za_vrstu(lista_postaja, vrsta_goriva)
    sortirane_cijene = sorted(cijene.items(), key = lambda x: x[0])

    for (cijena, postaje) in sortirane_cijene:
        if not cijena:
            continue
        freq = frekvencija_vlasnika(postaje)
        filtered_freq = sorted(filter(lambda x: x[1] > limit, freq), key = lambda x: -x[1])
        if filtered_freq:
            print cijena, filtered_freq
