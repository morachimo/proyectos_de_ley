import json
import os

from django.test import TestCase, Client
from django.core.management import call_command

from pdl.models import Proyecto
from pdl.models import Seguimientos
from pdl.models import Slug


class TestSearchAdvancedViews(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.c = Client()

        this_folder = os.path.abspath(os.path.dirname(__file__))
        dummy_db_json = os.path.join(this_folder, '..', '..', 'pdl', 'tests', 'dummy_db.json')
        dummy_items = json.loads(open(dummy_db_json, 'r').read())

        for i in dummy_items:
            b = Proyecto(**i)
            b.save()
            s = Seguimientos(proyecto=b, fecha='2014-06-23',
                             evento='Decreado a... Ciencia, Innovación y Tecnología')
            s.save()
            s1 = Seguimientos(proyecto=b, fecha='2015-06-23',
                              evento='En comisión de Ciencia, Innovación y Tecnología')
            s1.save()

        Slug(nombre='Chihuan Ramos, Leyla Felicita', ascii='Chihuan Ramos, Leyla Felicita',
             slug='chihuan-ramos-leyla-felicita').save()

    def test_index(self):
        response = self.c.get('/search-advanced/')
        self.assertEqual(200, response.status_code)

    def test_index_form_invalid(self):
        response = self.c.get('/search-advanced/?date_from=hola&date_to=12%2F19%2F2014')
        self.assertEqual(200, response.status_code)

    def test_index_search_date(self):
        response = self.c.get('/search-advanced/?date_from=03%2F03%2F2015&date_to=07%2F02%2F2015')
        self.assertEqual(200, response.status_code)

    def test_index_search_comission(self):
        call_command('create_stats')
        response = self.c.get('/search-advanced/?comision=Ciencia&grupo_parlamentario=--Escoger bancada--')
        self.assertTrue('arco y flecha' in str(response.content))

    def test_search_palabra_clave(self):
        response = self.c.get('/search-advanced/?query=arco y flecha')
        self.assertTrue('arco y flecha' in str(response.content))

    def test_search_congresista(self):
        response = self.c.get('/search-advanced/?congresista=1&grupo_parlamentario=--Escoger bancada--')
        self.assertTrue('arco y flecha' in str(response.content))

    def test_numero_total_de_leyes(self):
        response = self.c.get('/search-advanced/?dictamen=NÚMERO TOTAL DE LEYES')
        self.assertEqual(200, response.status_code)

    def test_exonerados_dictamen(self):
        response = self.c.get('/search-advanced/?dictamen=Exonerados de dictamen')
        self.assertEqual(200, response.status_code)

    def test_numero_total_aprobados(self):
        response = self.c.get('/search-advanced/?dispensados_2da_votacion=TOTAL aprobados')
        self.assertEqual(200, response.status_code)

    def test_numero_total_dispensados(self):
        response = self.c.get('/search-advanced/?dispensados_2da_votacion=TOTAL dispensados')
        self.assertEqual(200, response.status_code)

    def test_dispensados_acuerdo_pleno(self):
        response = self.c.get('/search-advanced/?dispensados_2da_votacion=Dispensados por acuerdo del pleno')
        self.assertEqual(200, response.status_code)

    def test_dispensados_junta_portavoces(self):
        response = self.c.get('/search-advanced/?dispensados_2da_votacion=Dispensados por junta portavoces')
        self.assertEqual(200, response.status_code)

    def test_dispensados_otros(self):
        response = self.c.get('/search-advanced/?dispensados_2da_votacion=Otros proyectos dispensados')
        self.assertEqual(200, response.status_code)
