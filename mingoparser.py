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
        self._lista_postaja = []
        self._cijene_sa_brojem_postaja = {}
        
    def id(self):
        return self._id
        
    def ime(self):
        return self._ime
        
    def dodaj_cijenu(self, vrsta_goriva, cijena, broj_postaja):
        if not vrsta_goriva in self._cijene_sa_brojem_postaja:
            self._cijene_sa_brojem_postaja[vrsta_goriva] = {}
        if not cijena in self._cijene_sa_brojem_postaja[vrsta_goriva]:
            self._cijene_sa_brojem_postaja[vrsta_goriva][cijena] = 0
        self._cijene_sa_brojem_postaja[vrsta_goriva][cijena] += broj_postaja

    def dodaj_postaju(self, postaja):
        self._lista_postaja.append(postaja)

    def broj_postaja(self, vrsta_goriva = None):
        if not vrsta_goriva:
            return len(self._lista_postaja)
            
        konacni_broj_postaja = 0
        if vrsta_goriva in self._cijene_sa_brojem_postaja:
            for broj_postaja in self._cijene_sa_brojem_postaja[vrsta_goriva].values():
                konacni_broj_postaja += broj_postaja
                
        return konacni_broj_postaja

    def gen_cijene_sa_brojem_postaja(self):
        self._cijene_sa_brojem_postaja = {}
        for postaja in self._lista_postaja:
            vgsc = postaja.vrste_goriva_sa_cijenom()
            for vrsta_goriva in vgsc:
                cijena = vgsc[vrsta_goriva]
                self.dodaj_cijenu(int(vrsta_goriva), cijena, 1)

    def cijene_sa_brojem_postaja(self, vrsta_goriva):
        if vrsta_goriva in self._cijene_sa_brojem_postaja:
            return self._cijene_sa_brojem_postaja[vrsta_goriva]
        else:
            return {}

    def vrste_goriva(self):
        return self._cijene_sa_brojem_postaja.keys()
        
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

            self._indeksi[vrsta_goriva] = i / br
                    
            
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

def vrste_goriva():
    vrste_json = load_vrste()
    vrste_goriva = gen_vrste_goriva(vrste_json)
    return vrste_goriva

def gen_cijene_sa_vlasnicima(vlasnici):
    cijene_sa_vlasnicima = {}
    
    for vlasnik in vlasnici.values():
        for vrsta_goriva in vlasnik.vrste_goriva():
            if vrsta_goriva not in cijene_sa_vlasnicima:
                cijene_sa_vlasnicima[vrsta_goriva] = {}
                
            cijene_sa_brojem_postaja = vlasnik.cijene_sa_brojem_postaja(vrsta_goriva)
            for cijena in cijene_sa_brojem_postaja:
                broj_postaja = cijene_sa_brojem_postaja[cijena]
                cv = cijene_sa_vlasnicima[vrsta_goriva]
                
                if not cijena in cv:
                    cv[cijena] = {}
                cv[cijena][vlasnik] = broj_postaja

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

    return vlasnici

def gen_hrvatska(vlasnici):
    hrvatska = Vlasnik(0, "Hrvatska")

    for vlasnik in vlasnici.values():
        for vrsta_goriva in vlasnik.vrste_goriva():
            cijena = vlasnik.indeks(vrsta_goriva)
            broj_postaja = vlasnik.broj_postaja(vrsta_goriva)
            hrvatska.dodaj_cijenu(vrsta_goriva, cijena, broj_postaja)

    hrvatska.gen_indeksi()

    return hrvatska
    
if __name__ == "__main__":
    limit = 4
    vrsta_goriva = 2
    vlasnici = gen_vlasnici_full()

    cijene_sa_vlasnicima = gen_cijene_sa_vlasnicima(vlasnici)

    for (cijena, lista_vlasnika) in cijene_sa_vlasnicima[vrsta_goriva].iteritems():
        if filter(lambda (vlasnik, broj_postaja): broj_postaja >= limit, lista_vlasnika.iteritems()):
            print cijena, filter(lambda (ime, broj_postaja): broj_postaja >= limit, map(lambda (vlasnik, broj_postaja): (vlasnik.ime(), broj_postaja), lista_vlasnika.iteritems()))

    print "--------------"

    sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())
    for vlasnik in sortirani_vlasnici:
        if vlasnik.broj_postaja() >= limit:
            if vlasnik.nudi_gorivo(vrsta_goriva):
                print vlasnik.ime(), vlasnik.cijene_sa_brojem_postaja(vrsta_goriva), vlasnik.broj_postaja(vrsta_goriva), format("%.2f" % vlasnik.indeks(vrsta_goriva))

    print "--------------"

    hrvatska = gen_hrvatska(vlasnici)

    print hrvatska.ime(), format("%.3f" % hrvatska.indeks(vrsta_goriva))
