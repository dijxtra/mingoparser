# -*- coding: utf-8 -*-
import json
import xml.etree.cElementTree as ET
from collections import defaultdict

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
    
    for item in tree.iter(tag='item'):
        id = None
        obveznik = None
        for child in item:
            if child.tag == "id_postaja":
                id = child.text
            if child.tag == "obveznik":
                obveznik = child.text
        if id:
            vlasnici_postaja[id] = obveznik

    return vlasnici_postaja

def gen_imena_vlasnika(tree):
    imena_vlasnika = {}
    
    for item in tree.iter(tag='item'):
        postaja_id = None
        obveznik = None
        for child in item:
            if child.tag == "id_obveznik":
                obveznik_id = child.text
            if child.tag == "naziv":
                naziv = child.text

        if obveznik_id:
            imena_vlasnika[obveznik_id] = naziv

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

    obveznik_tree = ET.ElementTree(file='obveznik')
    imena_vlasnika = gen_imena_vlasnika(obveznik_tree)

    postaja_tree = ET.ElementTree(file='postaja')
    vlasnici_postaja = gen_vlasnike_postaja(postaja_tree)

    with open ("vazeca-cijena.html", "r") as myfile:
        data=myfile.read()

    j = json.loads(data)
    lista_postaja = []
    for postaja in j:
        p = Postaja(postaja)
        p.set_ime_vlasnika(imena_vlasnika[vlasnici_postaja[p.id()]])
        lista_postaja.append(p)
    
    cijene = dict_cijena_sa_postajama_za_vrstu(lista_postaja, vrsta_goriva)
    sortirane_cijene = sorted(cijene.items(), key = lambda x: x[0])

    for (cijena, postaje) in sortirane_cijene:
        if not cijena:
            continue
        freq = frekvencija_vlasnika(postaje)
        filtered_freq = sorted(filter(lambda x: x[1] > limit, freq), key = lambda x: -x[1])
        if filtered_freq:
            print cijena, filtered_freq
