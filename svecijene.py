# -*- coding: utf-8 -*-
import json
import xml.etree.cElementTree as ET
from collections import defaultdict

class Postaja:
    def __init__(self, json_in):
        self.nazivi_po_vrsti = {}
        self.cijene_po_vrsti = {}
        
        for c in json_in["cijena"]:
            self.nazivi_po_vrsti[c["vrsta_goriva"]] = c["naziv"]

            cijena = float(c["cijena"])
            if cijena > 100: #Ako je cijena veća od 100, onda se vrlo vjerojatno radi o cijeni kojoj nedostaje decimalni zarez.
                cijena = cijena / 100
            self.cijene_po_vrsti[c["vrsta_goriva"]] = cijena

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


def dict_cijena_sa_postajama_za_vrstu(j, vrsta_goriva):
    """Generira dictionary popisa postaja po cijeni vrste goriva.

    Za svaku postaju određuje se cijena za ulaznu vrstu goriva i zatim se dodjeljuje u dictionary pod tom cijenom.
    """
    
    postaje_po_cijenama = {}
    for postaja in j:
        p = Postaja(postaja)
        cijena = p.cijena(vrsta_goriva)
        if cijena in postaje_po_cijenama:
            postaje_po_cijenama[cijena].append(postaja["id_postaja"])
        else:
            postaje_po_cijenama[cijena] = [postaja["id_postaja"]]

    return postaje_po_cijenama

def vlasnik_postaje_id(tree, postaja_id):
    """Za zadani ID postaje izvadi ID vlasnika postaje iz ulaznog ElementTree-a."""
    
    found_item = None
    for item in tree.iter(tag='item'):
        if found_item :
            break
        for child in item:
            if child.tag == "id_postaja":
                if child.text == postaja_id:
                    found_item = item
                    break

    obveznik_id = None
    for child in found_item:
        if child.tag == "obveznik":
            return child.text
    
def obveznik_naziv(tree, id_obveznik):
    """Za zadani ID postaje izvadi ID vlasnika postaje iz ulaznog ElementTree-a."""
    
    found_item = None
    for item in tree.iter(tag='item'):
        if found_item :
            break
        for child in item:
            if child.tag == "id_obveznik":
                if child.text == id_obveznik:
                    found_item = item
                    break

    for child in found_item:
        if child.tag == "naziv":
            return child.text
        
    
def frekvencija_vlasnika(lista_postaja):
    """Prima listu IDova postaja i vraća listu parova (ime vlasnika postaje, frekvencija)

    Prima listu IDova postaja u obliku ['1', '2', '3'] i vraća listu oblika [('Tri', 2), ('Dva', 1)], gdje je 'Tri' ime vlasnika postaja '1' i '2', a 'Dva' je ime vlasnika postaje '3'.
    """
    
    vlasnici = map(lambda x: vlasnik_postaje_id(postaja_tree, x), lista_postaja)

    d = defaultdict(int)
    for k in vlasnici:
        d[k] += 1

    return d.items()
    
if __name__ == "__main__":
    vrsta_goriva = "2"
    limit = 3

    with open ("vazeca-cijena.html", "r") as myfile:
        data=myfile.read()

    j = json.loads(data)

    obveznik_tree = ET.ElementTree(file='obveznik')
    postaja_tree = ET.ElementTree(file='postaja')
    
    cijene = dict_cijena_sa_postajama_za_vrstu(j, vrsta_goriva)
    sortirane_cijene = sorted(cijene.items(), key = lambda x: x[0])

    for (cijena, postaje) in sortirane_cijene:
        if not cijena:
            continue
        freq = frekvencija_vlasnika(postaje)
        filtered_freq = sorted(filter(lambda x: x[1] > limit, freq), key = lambda x: -x[1])
        if filtered_freq:
            print cijena, map(lambda x: (obveznik_naziv(obveznik_tree, x[0]), x[1]), filtered_freq)
