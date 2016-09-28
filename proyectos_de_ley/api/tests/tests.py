import json

from django.test import Client
from django.test import TestCase

from pdl.models import Proyecto
from pdl.models import Seguimientos
from pdl.models import Slug


class TestAPI(TestCase):
    def setUp(self):
        self.maxDiff = None
        dummy = {
            "codigo": "03774",
            'legislatura': 2016,
            "congresistas": "Dammert Ego Aguirre, Manuel Enrique Ernesto; Lescano Ancieta, Yonhy; Merino De Lama, Manuel; Guevara Amasifuen, Mesias Antonio; Mavila Leon, Rosa Delsa; Mendoza Frisch, Veronika Fanny",
            "expediente": "http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/03774?opendocument",
            "fecha_presentacion": "2014-09-05",
            "id": 3763,
            "numero_proyecto": "03774/2014-CR",
            "pdf_url": "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/Contdoc02_2011_2.nsf/d99575da99ebfbe305256f2e006d1cf0/dbc9030966aac60905257d4a007b75d9/$FILE/PL03774050914.pdf",
            "seguimiento_page": "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso/9609130B9871582F05257D4A00752301?opendocument",
            "short_url": "4aw8ym",
            "nombre_comision": "economia",
            "time_created": "2014-09-05 03:00:00",
            "time_edited": "2014-09-05 03:00:00",
            "titulo": "Propone establecer los lineamientos para la promoción de la eficiencia y competitividad en la actividad empresarial del Estado, garantizando su aporte estratégico para el desarrollo descentralizado y la soberanía nacional."
        }
        self.p = Proyecto(**dummy)
        self.p.save()

        dummy_slug = {
            "nombre": "Dammert Ego Aguirre, Manuel Enrique Ernesto",
            "ascii": "Dammert Ego Aguirre, Manuel Enrique Ernesto",
            "slug": "dammert_ego_aguirre/",
        }
        Slug(**dummy_slug).save()

        self.c = Client()

    def test_getting_proyecto(self):
        response = self.c.get('/api/proyecto.json/03774-2016/')
        result = json.loads(response.content.decode('utf-8'))
        expected = "03774"
        self.assertEqual(expected, result['codigo'])

    def test_getting_proyecto_csv(self):
        response = self.c.get('/api/proyecto.csv/03774-2016/')
        result = response.content.decode('utf-8')
        expected = "03774"
        self.assertTrue(expected in result)

    def test_getting_proyecto_missing(self):
        response = self.c.get('/api/proyecto.json/037740-2016/')
        result = response.content.decode('utf-8')
        expected = '{"error": "proyecto no existe"}'
        self.assertEqual(expected, result)

    def test_getting_proyecto_missing_csv(self):
        response = self.c.get('/api/proyecto.csv/037740-2016/')
        result = response.content.decode('utf-8')
        expected = 'error,proyecto no existe'
        self.assertEqual(expected, result)

    def test_getting_projects_of_person(self):
        response = self.c.get('/api/congresista.json/Dammert Ego/')
        result = json.loads(response.content.decode('utf-8'))
        expected = 'Dammert Ego Aguirre, Manuel Enrique Ernesto'
        self.assertEqual(expected, result['resultado'][0]['nombre'])

    def test_getting_projects_of_person_csv(self):
        response = self.c.get('/api/congresista.csv/Dammert Ego/')
        result = response.content.decode('utf-8')
        expected = 'Dammert Ego Aguirre, Manuel Enrique Ernesto'
        self.assertTrue(expected in result)

    def test_getting_projects_of_person_and_comission(self):
        response = self.c.get('/api/congresista_y_comision.json/Dammert Ego/economia/')
        result = json.loads(response.content.decode('utf-8'))
        expected = ['03774-2016']
        self.assertEqual(expected, result['resultado'][0]['proyectos'])

    def test_getting_projects_of_person_and_comission_csv(self):
        response = self.c.get('/api/congresista_y_comision.csv/Dammert Ego/economia/')
        result = response.content.decode('utf-8')
        expected = '03774-2016'
        self.assertTrue(expected in result)

    def test_getting_projects_of_person_and_comission_csv_missing(self):
        response = self.c.get('/api/congresista_y_comision.csv/Dammert Egolalala/economia/')
        result = response.content.decode('utf-8')
        expected = 'error,no se pudo encontrar congresista'
        self.assertEqual(expected, result)

    def test_not_enough_names_to_search_for_person(self):
        response = self.c.get('/api/congresista.json/Dammert/')
        result = json.loads(response.content.decode('utf-8'))
        expected = 'ingrese un nombre y un apellido'
        self.assertEqual(expected, result['error'])

    def test_not_enough_names_to_search_for_person_in_comision(self):
        response = self.c.get('/api/congresista_y_comision.json/Dammert/economia/')
        result = json.loads(response.content.decode('utf-8'))
        expected = 'ingrese un nombre y un apellido'
        self.assertEqual(expected, result['error'])

    def test_person_cannot_be_found(self):
        response = self.c.get('/api/congresista.json/Aus Bus/')
        result = json.loads(response.content.decode('utf-8'))
        expected = 'no se pudo encontrar congresista'
        self.assertEqual(expected, result['error'])

    def test_person_name_incomplete(self):
        response = self.c.get('/api/congresista.json/Bus/')
        result = json.loads(response.content.decode('utf-8'))
        expected = 'ingrese un nombre y un apellido'
        self.assertEqual(expected, result['error'])

    def test_person_name_incomplete_csv(self):
        response = self.c.get('/api/congresista.csv/Bus/')
        result = response.content.decode('utf-8')
        expected = 'error,ingrese un nombre y un apellido'
        self.assertEqual(expected, result)

    def test_exonerados_dictamen_empty(self):
        response = self.c.get('/api/exonerados_dictamen.json/')
        result = json.loads(response.content.decode('utf-8'))
        expected = {'error': 'no se encontraron resultados'}
        self.assertEqual(expected, result)

    def test_exonerados_dictamen(self):
        Seguimientos(proyecto=self.p,
                     evento='exoneración de dictamen',
                     fecha='2010-10-10').save()
        response = self.c.get('/api/exonerados_dictamen.json/')
        result = json.loads(response.content.decode('utf-8'))
        expected = {'resultado': ['03774-2016']}
        self.assertEqual(expected, result)

    def test_exonerados_dictamen_csv(self):
        Seguimientos(proyecto=self.p,
                     evento='exoneración de dictamen',
                     fecha='2010-10-10').save()
        response = self.c.get('/api/exonerados_dictamen.csv/')
        result = response.content.decode('utf-8')
        expected = '03774-2016'
        self.assertTrue(expected in result)

    def test_exonerados_dictamen_csv_empty(self):
        response = self.c.get('/api/exonerados_dictamen.csv/')
        result = response.content.decode('utf-8')
        expected = 'error,no se encontraron resultados'
        self.assertEqual(expected, result)

    def test_exonerados_2da_votacion_empty(self):
        response = self.c.get('/api/exonerados_2da_votacion.json/')
        result = json.loads(response.content.decode('utf-8'))
        expected = {'error': 'no se encontraron resultados'}
        self.assertEqual(expected, result)

    def test_exonerados_2da_votacion_empty_csv(self):
        response = self.c.get('/api/exonerados_2da_votacion.csv/')
        result = response.content.decode('utf-8')
        expected = 'error,no se encontraron resultados'
        self.assertEqual(expected, result)

    def test_exonerados_2da_votacion(self):
        Seguimientos(proyecto=self.p,
                     evento='dispensado 2da',
                     fecha='2010-10-10').save()
        response = self.c.get('/api/exonerados_2da_votacion.json/')
        result = json.loads(response.content.decode('utf-8'))
        expected = {'resultado': ['03774-2016']}
        self.assertEqual(expected, result)

    def test_exonerados_2da_votacion_csv(self):
        Seguimientos(proyecto=self.p,
                     evento='dispensado 2da',
                     fecha='2010-10-10').save()
        response = self.c.get('/api/exonerados_2da_votacion.csv/')
        result = response.content.decode('utf-8')
        expected = '03774-2016'
        self.assertTrue(expected in result)
