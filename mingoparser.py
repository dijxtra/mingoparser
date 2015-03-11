# -*- coding: utf-8 -*-
import json
import urllib2
import os, io
import sqlite3 as lite

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

    def prazna(self):
        if not self.cijene_po_vrsti:
            return True
        return False
            
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
        self._indeksi = {}
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

    def broj_postaja(self, vrsta_goriva = None, cijena = None):
        if not vrsta_goriva:
            konacni_broj_postaja = 0
            for vrsta_goriva in self._cijene_sa_brojem_postaja:
                broj_postaja = self.broj_postaja(vrsta_goriva)
                if konacni_broj_postaja < broj_postaja:
                    konacni_broj_postaja = broj_postaja
            return konacni_broj_postaja
            
        konacni_broj_postaja = 0
        if vrsta_goriva in self._cijene_sa_brojem_postaja:
            for c in self._cijene_sa_brojem_postaja[vrsta_goriva]:
                broj_postaja = self._cijene_sa_brojem_postaja[vrsta_goriva][c]
                if cijena:
                    if cijena != c:
                        continue
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

    def dodaj_indeks(self, vrsta_goriva, broj_postaja, indeks):
        self._indeksi[vrsta_goriva] = indeks

def gen_vlasnici_postaja_dict(tree):
    """Generira dictionary koji mapira postaju sa njenim vlasnikom"""
    vlasnici_postaja = {}
    
    for vlasnik in tree:
        vlasnici_postaja[vlasnik["id_postaja"]] = vlasnik["obveznik"]

    return vlasnici_postaja

def gen_vlasnici(tree):
    vlasnici = {}

    for obveznik in tree:
        vlasnici[obveznik["id_obveznik"]] = Vlasnik(obveznik["id_obveznik"], obveznik["naziv"].encode('utf-8'))

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

    vlasnici_mozda_prazni = vlasnici
    vlasnici = {}
    
    for kljuc in vlasnici_mozda_prazni:
        vlasnik = vlasnici_mozda_prazni[kljuc]
        if vlasnik.broj_postaja() > 0:
            vlasnici[vlasnik.id()] = vlasnik

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

class Saver:
    def pisi_indekse_json(self, vlasnici, file_name):
        file_name = path() + file_name
        sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())

        json_za_upis = []
        for vlasnik in sortirani_vlasnici:
            for vrsta_goriva in vlasnik.vrste_goriva():
                if vlasnik.nudi_gorivo(vrsta_goriva):
                    json_za_upis.append({
                        'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'vlasnik_id': vlasnik.id(),
                        'vlasnik_ime': vlasnik.ime(),
                        'vrsta_goriva': vrsta_goriva,
                        'broj_postaja': vlasnik.broj_postaja(vrsta_goriva),
                        'indeks': vlasnik.indeks(vrsta_goriva),
                    })

        with io.open(file_name, 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(json_za_upis)))
        
    def kreiraj_tablicu_vlasnika(self, file_name):
        file_name = path() + file_name

        con = lite.connect(file_name)
        with con:
            cur = con.cursor()    

            cur.execute("DROP TABLE IF EXISTS vlasnici")
            cur.execute("""CREATE TABLE vlasnici(
vlasnik_id INT,
vlasnik_ime TEXT,
datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
            con.commit()
        
    def kreiraj_tablicu_indeksa(self, file_name):
        file_name = path() + file_name

        con = lite.connect(file_name)
        with con:
            cur = con.cursor()    

            cur.execute("DROP TABLE IF EXISTS indeksi")
            cur.execute("""CREATE TABLE indeksi(
vlasnik_id INT,
vrsta_goriva INT,
broj_postaja INT,
indeks FLOAT,
datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
            con.commit()
        
    def kreiraj_tablicu_cijena(self, file_name):
        file_name = path() + file_name

        con = lite.connect(file_name)
        with con:
            cur = con.cursor()    

            cur.execute("DROP TABLE IF EXISTS cijene")
            cur.execute("""CREATE TABLE cijene(
vlasnik_id INT,
vrsta_goriva INT,
broj_postaja INT,
cijena FLOAT,
datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
            con.commit()

    def pisi_indekse_sql(self, vlasnici, file_name):
        file_name = path() + file_name
        sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())

        con = lite.connect(file_name)
        with con:

            con.row_factory = lite.Row
            cur = con.cursor()

            vlasnici_za_upis = []
            indeksi_za_upis = []
            for vlasnik in sortirani_vlasnici:
                vlasnici_za_upis.append((
                            vlasnik.id(),
                            vlasnik.ime().decode('utf-8'),
                        ))

                for vrsta_goriva in vlasnik.vrste_goriva():
                    if vlasnik.nudi_gorivo(vrsta_goriva):
                        indeksi_za_upis.append((
                            vlasnik.id(),
                            vrsta_goriva,
                            vlasnik.broj_postaja(vrsta_goriva),
                            vlasnik.indeks(vrsta_goriva),
                        ))

            cur.executemany("INSERT INTO vlasnici (vlasnik_id, vlasnik_ime) VALUES(?, ?)", vlasnici_za_upis)
            con.commit()
            cur.executemany("INSERT INTO indeksi (vlasnik_id, vrsta_goriva, broj_postaja, indeks) VALUES(?, ?, ?, ?)", indeksi_za_upis)
            con.commit()
        
    def pisi_cijene_s_postajama_json(self, vlasnici, file_name):
        file_name = path() + file_name
        sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())

        json_za_upis = []
        for vlasnik in sortirani_vlasnici:
            for vrsta_goriva in vlasnik.vrste_goriva():
                if vlasnik.nudi_gorivo(vrsta_goriva):
                    json_za_upis.append({
                        'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'vlasnik_id': vlasnik.id(),
                        'vrsta_goriva': vrsta_goriva,
                        'cijene_sa_brojem_postaja': vlasnik.cijene_sa_brojem_postaja(vrsta_goriva),
                    })

        with io.open(file_name, 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(json_za_upis)))

    def pisi_cijene_s_postajama_sql(self, vlasnici, file_name):
        file_name = path() + file_name
        sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())

        con = lite.connect(file_name)
        with con:

            con.row_factory = lite.Row
            cur = con.cursor()    

            redovi_za_upis = []
            for vlasnik in sortirani_vlasnici:
                for vrsta_goriva in vlasnik.vrste_goriva():
                    if vlasnik.nudi_gorivo(vrsta_goriva):
                        cbp = vlasnik.cijene_sa_brojem_postaja(vrsta_goriva)
                        for cijena in cbp:
                            broj_postaja = cbp[cijena]
                        redovi_za_upis.append((
                            vlasnik.id(),
                            vrsta_goriva,
                            broj_postaja,
                            cijena
                        ))

            cur.executemany("INSERT INTO cijene (vlasnik_id, vrsta_goriva, broj_postaja, cijena) VALUES(?, ?, ?, ?)", redovi_za_upis)
            con.commit()

    def citaj_indekse_json(self, file_name):
        file_name = path() + file_name
        
        json_za_citanje = []
        with open(file_name) as f:
            json_za_citanje = json.loads(f.read())

        vlasnici = {}
        for vlasnik_json in json_za_citanje:
            if vlasnik_json['vlasnik_id'] in vlasnici:
                vlasnik = vlasnici[vlasnik_json['vlasnik_id']]
            else:
                vlasnik = Vlasnik(vlasnik_json['vlasnik_id'], vlasnik_json['vlasnik_ime'].encode('utf-8'))
                vlasnici[vlasnik.id()] = vlasnik

            vlasnik.dodaj_indeks(
                vlasnik_json['vrsta_goriva'],
                vlasnik_json['broj_postaja'],
                vlasnik_json['indeks'],
            )
            
        return vlasnici

    def citaj_indekse_sql(self, file_name):
        file_name = path() + file_name
        vlasnici = {}
        
        con = lite.connect(file_name)
        with con:

            con.row_factory = lite.Row
            cur = con.cursor()

            for (vlasnik_id, vlasnik_ime, vrsta_goriva, broj_postaja, indeks, datetime) in con.execute("""
            select
            indeksi.vlasnik_id, vlasnici.vlasnik_ime, indeksi.vrsta_goriva, indeksi.broj_postaja, indeksi.indeks, indeksi.datetime
            from indeksi
            join vlasnici
            on indeksi.vlasnik_id = vlasnici.vlasnik_id
            """):
                if vlasnik_id in vlasnici:
                    vlasnik = vlasnici[vlasnik_id]
                else:
                    vlasnik = Vlasnik(vlasnik_id, vlasnik_ime.encode('utf-8'))
                    vlasnici[vlasnik.id()] = vlasnik

                vlasnik.dodaj_indeks(
                    vrsta_goriva,
                    broj_postaja,
                    indeks,
                )

        return vlasnici

    def citaj_cijene_s_postajama_json(self, vlasnici, file_name):
        file_name = path() + file_name
        
        json_za_citanje = []
        with open(file_name) as f:
            json_za_citanje = json.loads(f.read())

        for vlasnik_json in json_za_citanje:
            vlasnik = vlasnici[vlasnik_json['vlasnik_id']]

            for cijena in vlasnik_json['cijene_sa_brojem_postaja']:
                broj_postaja = vlasnik_json['cijene_sa_brojem_postaja'][cijena]
                vlasnik.dodaj_cijenu(vlasnik_json['vrsta_goriva'], float(cijena), broj_postaja)
            
        return vlasnici

    def citaj_cijene_s_postajama_sql(self, vlasnici, file_name):
        file_name = path() + file_name

        con = lite.connect(file_name)
        with con:

            con.row_factory = lite.Row
            cur = con.cursor()

            for (vlasnik_id, vrsta_goriva, broj_postaja, cijena, datetime) in con.execute("select * from cijene"):
                vlasnik = vlasnici[vlasnik_id]
                vlasnik.dodaj_cijenu(vrsta_goriva, cijena, broj_postaja)
            
        return vlasnici

def debug_usporedi_vlasnike(vlasnici, vlasnici2):
    for key in vlasnici:
        v1 = vlasnici[key]
        v2 = vlasnici2[key]
        if v1._ime != v2._ime or v1._id != v2._id or v1._indeksi != v2._indeksi or v1._cijene_sa_brojem_postaja != v2._cijene_sa_brojem_postaja:
            print key
            print vlasnici[key]._cijene_sa_brojem_postaja#__dict__
            print vlasnici2[key]._cijene_sa_brojem_postaja#__dict__
            exit()
    for key in vlasnici2:
        v1 = vlasnici[key]
        v2 = vlasnici2[key]
        if v1._ime != v2._ime or v1._id != v2._id or v1._indeksi != v2._indeksi or v1._cijene_sa_brojem_postaja != v2._cijene_sa_brojem_postaja:
            print key
            print vlasnici[key]._cijene_sa_brojem_postaja#__dict__
            print vlasnici2[key]._cijene_sa_brojem_postaja#__dict__
            exit()
    print "Nema razlika"

def pisi_sve_u_sql(ime_baze):
    saver = Saver()
    saver.kreiraj_tablicu_vlasnika(ime_baze)
    saver.kreiraj_tablicu_indeksa(ime_baze)
    saver.kreiraj_tablicu_cijena(ime_baze)
    
    vlasnici = gen_vlasnici_full()

    saver.pisi_indekse_sql(vlasnici, ime_baze)
    saver.pisi_cijene_s_postajama_sql(vlasnici, ime_baze)

    
if __name__ == "__main__":
    limit = 4
    vrsta_goriva = 2

    pisi_sve_u_sql('db.sqlite3')

    saver = Saver()
    vlasnici = saver.citaj_indekse_sql('db.sqlite3')
    vlasnici = saver.citaj_cijene_s_postajama_sql(vlasnici, 'db.sqlite3')

    cijene_sa_vlasnicima = gen_cijene_sa_vlasnicima(vlasnici)

    for (cijena, lista_vlasnika) in cijene_sa_vlasnicima[vrsta_goriva].iteritems():
        if filter(lambda (vlasnik, broj_postaja): broj_postaja >= limit, lista_vlasnika.iteritems()):
            print cijena, filter(lambda (ime, broj_postaja): broj_postaja >= limit, map(lambda (vlasnik, broj_postaja): (vlasnik.ime(), broj_postaja), lista_vlasnika.iteritems()))

    print "--------------"

    sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())
    for vlasnik in sortirani_vlasnici:
        if vlasnik.nudi_gorivo(vrsta_goriva):
            if vlasnik.broj_postaja(vrsta_goriva) >= limit:
                print vlasnik.ime(), vlasnik.cijene_sa_brojem_postaja(vrsta_goriva), vlasnik.broj_postaja(vrsta_goriva), format("%.2f" % vlasnik.indeks(vrsta_goriva))

    print "--------------"

    hrvatska = gen_hrvatska(vlasnici)

    print hrvatska.ime(), format("%.3f" % hrvatska.indeks(vrsta_goriva))
