# -*- coding: utf-8 -*-
import json
import urllib2
import os, io
import datetime
import sqlite3 as lite

def path():
    dirname = os.path.dirname(__file__)
    
    if dirname == '':
        return ''
    else:
        return dirname + '/'

class CitacVrijednosti:
    def load_vrste(self):
        url = 'http://min-go.hr/api/web_api/web/vrste-goriva'
        return json.loads(urllib2.urlopen(url).read())

    def load_obveznik(self):
        url = 'http://min-go.hr/api/web_api/web/obveznik'
        return json.loads(urllib2.urlopen(url).read())

    def load_postaja(self):
        url = 'http://min-go.hr/api/web_api/web/postaja'
        return json.loads(urllib2.urlopen(url).read())

    def load_cijene(self):
        url = 'http://min-go.hr/api/web_api/web/vazeca-cijena'
        return urllib2.urlopen(url).read()

    def vrste_goriva(self):
        vrste_json = load_vrste()
        vrste_goriva = gen_vrste_goriva(vrste_json)
        return vrste_goriva

    def gen_vlasnici_postaja_dict(self, tree):
        """Generira dictionary koji mapira postaju sa njenim vlasnikom"""
        vlasnici_postaja = {}

        for vlasnik in tree:
            vlasnici_postaja[vlasnik["id_postaja"]] = vlasnik["obveznik"]

        return vlasnici_postaja

    def gen_vlasnici(self, tree):
        vlasnici = {}

        for obveznik in tree:
            vlasnici[obveznik["id_obveznik"]] = Vlasnik(obveznik["id_obveznik"], obveznik["naziv"].encode('utf-8'))

        return vlasnici

    def gen_vrste_goriva(self, json):
        vrste_goriva = []

        for gorivo in json:
            vrste_goriva.append([gorivo["id_vrstagoriva"], gorivo["vrsta_goriva"]])

        return vrste_goriva

    def gen_vlasnici_full(self):
        obveznik_json = self.load_obveznik()
        vlasnici = self.gen_vlasnici(obveznik_json)

        postaja_json = self.load_postaja()
        vlasnici_postaja = self.gen_vlasnici_postaja_dict(postaja_json)

        cijene_json = self.load_cijene()
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

class CitacVrijednostiOffline(CitacVrijednosti):
    def __init__(self, dir):
        self.dir = path() + dir
        
    def load_vrste(self):
        file_name = self.dir  + 'vrste-goriva'
        with open(file_name) as f:
            return json.loads(f.read())

    def load_obveznik(self):
        file_name = self.dir + 'obveznik'
        with open(file_name) as f:
            return json.loads(f.read())

    def load_postaja(self):
        file_name = self.dir + 'postaja'
        with open(file_name) as f:
            return json.loads(f.read())

    def load_cijene(self):
        file_name = self.dir + 'vazeca-cijena'
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
        self._zadnja_promjena = {}
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

    def dodaj_indeks(self, vrsta_goriva, broj_postaja, indeks, datetime):
        self._indeksi[vrsta_goriva] = indeks
        self._zadnja_promjena[vrsta_goriva] = datetime

    def vrijeme_zadnjeg_upisa(self, vrsta_goriva):
        return self._zadnja_promjena[vrsta_goriva]

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

def gen_hrvatska(vlasnici):
    hrvatska = Vlasnik(0, "Hrvatska")

    for vlasnik in vlasnici.values():
        for vrsta_goriva in vlasnik.vrste_goriva():
            cijena = vlasnik.indeks(vrsta_goriva)
            broj_postaja = vlasnik.broj_postaja(vrsta_goriva)
            hrvatska.dodaj_cijenu(vrsta_goriva, cijena, broj_postaja)

    hrvatska.gen_indeksi()

    return hrvatska

class DatabaseConnection:
    def __init__(self, baza):
        self.baza = path() + baza
        self.con = lite.connect(self.baza)

    def kreiraj_tablice(self):
        self.kreiraj_tablicu_vlasnika()
        self.kreiraj_tablicu_indeksa()
        self.kreiraj_tablicu_cijena()
        self.kreiraj_vieweve()

    def popuni_osnovne_tablice(self, vlasnici, datum = None):
        self.pisi_vlasnike(vlasnici, datum)

    def popuni_tablice(self, vlasnici, datum = None):
        self.pisi_indekse(vlasnici, datum)
        self.pisi_cijene_s_postajama(vlasnici, datum)

    def kreiraj_tablicu_vlasnika(self):
        with self.con:
            cur = self.con.cursor()    

            cur.execute("DROP TABLE IF EXISTS vlasnici")
            cur.execute("""CREATE TABLE vlasnici(
vlasnik_id INT,
vlasnik_ime TEXT,
datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
            self.con.commit()
        
    def kreiraj_tablicu_indeksa(self):
        with self.con:
            cur = self.con.cursor()    

            cur.execute("DROP TABLE IF EXISTS indeksi")
            cur.execute("""CREATE TABLE indeksi(
vlasnik_id INT,
vrsta_goriva INT,
broj_postaja INT,
indeks FLOAT,
start_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
end_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
            self.con.commit()
        
    def kreiraj_tablicu_cijena(self):
        with self.con:
            cur = self.con.cursor()    

            cur.execute("DROP TABLE IF EXISTS cijene")
            cur.execute("""CREATE TABLE cijene(
vlasnik_id INT,
vrsta_goriva INT,
broj_postaja INT,
cijena FLOAT,
datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
            self.con.commit()

    def kreiraj_vieweve(self):
        with self.con:
            cur = self.con.cursor()    

            cur.execute("DROP VIEW IF EXISTS najnoviji_indeksi")
            cur.execute("""
create view najnoviji_indeksi as
select
indeksi.rowid, indeksi.*
from indeksi
join (
    select rowid, vlasnik_id, vrsta_goriva, max(end_datetime)
    from indeksi
    group by vlasnik_id, vrsta_goriva
) filter
  on indeksi.rowid = filter.rowid
""")
            
            cur.execute("DROP VIEW IF EXISTS indeksi_osim_najnovijih")
            cur.execute("""
create view indeksi_osim_najnovijih as
select indeksi.rowid, indeksi.*
from indeksi
left outer join najnoviji_indeksi
  on indeksi.vlasnik_id = najnoviji_indeksi.vlasnik_id
  and indeksi.vrsta_goriva = najnoviji_indeksi.vrsta_goriva
  and indeksi.indeks = najnoviji_indeksi.indeks
where najnoviji_indeksi.rowid is null
""")

            cur.execute("DROP VIEW IF EXISTS prednajnoviji_indeksi")
            cur.execute("""
create view prednajnoviji_indeksi as
select
indeksi_osim_najnovijih.*
from indeksi_osim_najnovijih
join (
  select rowid, vlasnik_id, vrsta_goriva, max(end_datetime) maxdatetime
  from indeksi_osim_najnovijih
  group by vlasnik_id, vrsta_goriva
) filter
  on indeksi_osim_najnovijih.rowid = filter.rowid
""")
            self.con.commit()

    def pisi_vlasnike(self, vlasnici, datum = None):
        sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())

        with self.con:

            self.con.row_factory = lite.Row
            cur = self.con.cursor()

            vlasnici_za_upis = []
            for vlasnik in sortirani_vlasnici:
                if datum:
                    vlasnici_za_upis.append((
                        vlasnik.id(),
                        vlasnik.ime().decode('utf-8'),
                        datum
                    ))
                else:
                    vlasnici_za_upis.append((
                        vlasnik.id(),
                        vlasnik.ime().decode('utf-8'),
                    ))

            if datum:
                cur.executemany("INSERT INTO vlasnici (vlasnik_id, vlasnik_ime, datetime) VALUES(?, ?, ?)", vlasnici_za_upis)
            else:
                cur.executemany("INSERT INTO vlasnici (vlasnik_id, vlasnik_ime) VALUES(?, ?)", vlasnici_za_upis)
            self.con.commit()

    def pisi_indekse(self, vlasnici, datum = None):
        sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())

        with self.con:

            self.con.row_factory = lite.Row
            cur = self.con.cursor()

            indeksi_za_upis = []
            for vlasnik in sortirani_vlasnici:
                for vrsta_goriva in vlasnik.vrste_goriva():
                    if vlasnik.nudi_gorivo(vrsta_goriva):
                        if datum:
                            indeksi_za_upis.append((
                                vlasnik.id(),
                                vrsta_goriva,
                                vlasnik.broj_postaja(vrsta_goriva),
                                vlasnik.indeks(vrsta_goriva),
                                datum
                            ))
                        else:
                            indeksi_za_upis.append((
                                vlasnik.id(),
                                vrsta_goriva,
                                vlasnik.broj_postaja(vrsta_goriva),
                                vlasnik.indeks(vrsta_goriva),
                            ))

            if datum:
                cur.executemany("INSERT INTO indeksi (vlasnik_id, vrsta_goriva, broj_postaja, indeks, end_datetime) VALUES(?, ?, ?, ?, ?)", indeksi_za_upis)
            else:
                cur.executemany("INSERT INTO indeksi (vlasnik_id, vrsta_goriva, broj_postaja, indeks) VALUES(?, ?, ?, ?)", indeksi_za_upis)

            self.con.commit()
        
    def pisi_cijene_s_postajama(self, vlasnici, datum = None):
        sortirani_vlasnici = sorted(vlasnici.values(), key=lambda v: v.ime())

        with self.con:

            self.con.row_factory = lite.Row
            cur = self.con.cursor()    

            redovi_za_upis = []
            for vlasnik in sortirani_vlasnici:
                for vrsta_goriva in vlasnik.vrste_goriva():
                    if vlasnik.nudi_gorivo(vrsta_goriva):
                        cbp = vlasnik.cijene_sa_brojem_postaja(vrsta_goriva)
                        for cijena in cbp:
                            broj_postaja = cbp[cijena]
                            if datum:
                                redovi_za_upis.append((
                                    vlasnik.id(),
                                    vrsta_goriva,
                                    broj_postaja,
                                    cijena,
                                    datum
                                ))
                            else:
                                redovi_za_upis.append((
                                    vlasnik.id(),
                                    vrsta_goriva,
                                    broj_postaja,
                                    cijena
                                ))

            if datum:
                cur.executemany("INSERT INTO cijene (vlasnik_id, vrsta_goriva, broj_postaja, cijena, datetime) VALUES(?, ?, ?, ?, ?)", redovi_za_upis)
            else:
                cur.executemany("INSERT INTO cijene (vlasnik_id, vrsta_goriva, broj_postaja, cijena) VALUES(?, ?, ?, ?)", redovi_za_upis)

            self.con.commit()

    def citaj_vlasnike(self):
        vlasnici = {}
        
        with self.con:

            self.con.row_factory = lite.Row
            cur = self.con.cursor()

            for (vlasnik_id, vlasnik_ime) in self.con.execute("""
            select
            vlasnik_id, vlasnik_ime
            from
            vlasnici
            """):
                vlasnik_ime = vlasnik_ime.encode('utf-8')
                if not vlasnik_id in vlasnici:
                    vlasnici[vlasnik_id] = Vlasnik(vlasnik_id, vlasnik_ime)
                else:
                    stari_vlasnik = vlasnici[vlasnik_id]
                    if stari_vlasnik.ime() != vlasnik_ime:
                        error = "Vlasnik " + stari_vlasnik.ime() + " promijenio ime u " + vlasnik_ime + "!"
                        print error
                        #raise Exception(error)

        return vlasnici

    def citaj_indekse(self, vlasnici):
        with self.con:

            self.con.row_factory = lite.Row
            cur = self.con.cursor()

            for (vlasnik_id, vlasnik_ime, vrsta_goriva, broj_postaja, indeks, datetime) in self.con.execute("""
            select
            vlasnici.vlasnik_id, vlasnik_ime, vrsta_goriva, broj_postaja, indeks, najnoviji_indeksi.end_datetime
            from najnoviji_indeksi
            join vlasnici
            on najnoviji_indeksi.vlasnik_id = vlasnici.vlasnik_id
            """):
                vlasnik = vlasnici[vlasnik_id]

                vlasnik.dodaj_indeks(
                    vrsta_goriva,
                    broj_postaja,
                    indeks,
                    datetime,
                )

        return vlasnici

    def citaj_cijene_s_postajama(self, vlasnici):
        with self.con:

            self.con.row_factory = lite.Row
            cur = self.con.cursor()

            for (vlasnik_id, vrsta_goriva, broj_postaja, cijena, datetime) in self.con.execute("""
            select cijene.vlasnik_id, cijene.vrsta_goriva, cijene.broj_postaja, cijene.cijena, cijene.datetime
            from cijene
            join (select rowid, vlasnik_id, vrsta_goriva, cijena, max(datetime) maxdatetime from cijene group by vlasnik_id, vrsta_goriva, cijena) filter
            on cijene.rowid = filter.rowid
            """):
                vlasnik = vlasnici[vlasnik_id]
                vlasnik.dodaj_cijenu(vrsta_goriva, cijena, broj_postaja)
            
        return vlasnici

    def vrijeme_zadnjeg_upisa(self, vrsta_goriva = None):
        with self.con:

            self.con.row_factory = lite.Row
            cur = self.con.cursor()

            if vrsta_goriva:
                cur.execute("select max(end_datetime) maxdatetime from indeksi where vrsta_goriva = ?", (str(vrsta_goriva)))
                datetime = cur.fetchone()[0]
            else:
                cur.execute("select max(end_datetime) maxdatetime from indeksi")
                datetime = cur.fetchone()[0]

        return datetime
