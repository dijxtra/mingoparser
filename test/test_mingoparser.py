import unittest
from mingoparser import *


class MingoparserTest(unittest.TestCase):
    """Unit tests for records.py using mcintyre.ged."""

    def setUp(self):
        self.limit = 4
        self.vrsta_goriva = 2
        self.database_file = 'db.test.sqlite3'

    def test_main(self):
        init_sql('db.sqlite3')
        pisi_sve_u_sql('db.sqlite3')

        saver = Saver()
        vlasnici_sql = saver.citaj_vlasnike_sql('db.sqlite3')
        vlasnici_sql = saver.citaj_indekse_sql(vlasnici_sql, 'db.sqlite3')
        vlasnici_sql = saver.citaj_cijene_s_postajama_sql(vlasnici_sql, 'db.sqlite3')

        vlasnici = gen_vlasnici_full()

        saver = Saver()
        saver.pisi_indekse_json(vlasnici, 'vlasnici.json')
        saver.pisi_cijene_s_postajama_json(vlasnici, 'cijene_s_postajama.json')

        vlasnici_json = saver.citaj_indekse_json('vlasnici.json')
        vlasnici_json = saver.citaj_cijene_s_postajama_json(vlasnici_json, 'cijene_s_postajama.json')

        for vlasnik_json in vlasnici_json.values():
            self.assertTrue(vlasnik_json.id() in vlasnici_sql)

        for vlasnik_sql in vlasnici_sql.values():
            self.assertTrue(vlasnik_sql.id() in vlasnici_json)

        for vlasnik_sql in vlasnici_sql.values():
            vlasnik_json = vlasnici_json[vlasnik_sql.id()]
            self.assertEqual(vlasnik_sql.ime(), vlasnik_json.ime())
            

        
if __name__ == '__main__':
    unittest.main()


