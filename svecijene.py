import json
import xml.etree.cElementTree as ET
from collections import defaultdict

def format_cijena(cijena):
    """Ako je cijena veća od 100, vrati cijenu djeljenu sa 100.

    Ako je cijena veća od 100, onda se vrlo vjerojatno radi o cijeni kojoj nedostaje decimalni zarez.
    """
    
    if float(cijena) > 100:
        return float(cijena) / 100
    return float(cijena)

def cijena_vrste_na_postaji(postaja, vrsta_goriva):
    """Prima json prikaz postaje i oznaku vrste goriva i vraća cijenu tog goriva na toj postaji."""
    
    for c in postaja["cijena"]:
        if c["vrsta_goriva"] == vrsta_goriva:
            return format_cijena(c["cijena"])

    return None
    
def ime_vrste_na_postaji(postaja, vrsta_goriva):
    """Prima json prikaz postaje i oznaku vrste goriva i vraća cijenu tog goriva na toj postaji."""
    
    for c in postaja["cijena"]:
        if c["vrsta_goriva"] == vrsta_goriva:
            return c["naziv"]

    return None

def postaja_po_id(json_data, postaja_id):
    for postaja in json_data:
        if postaja["id_postaja"] == postaja_id:
            return postaja

def dict_cijena_sa_postajama_za_vrstu(j, vrsta_goriva):
    cijene = {}
    for postaja in j:
        cijena = cijena_vrste_na_postaji(postaja, vrsta_goriva)[1]
        if cijena in cijene:
            cijene[cijena].append(postaja["id_postaja"])
        else:
            cijene[cijena] = [postaja["id_postaja"]]

    return cijene

def vlasnik_postaje_id(tree, postaja_id):
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
