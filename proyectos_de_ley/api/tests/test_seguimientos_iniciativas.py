import json

from django.test import Client
from django.test import TestCase

from pdl.models import Proyecto


class TestAPI(TestCase):
    def setUp(self):
        self.maxDiff = None
        dummy = {
            "codigo": "03774",
            'legislatura': 2011,
            "congresistas": "Dammert Ego Aguirre, Manuel Enrique Ernesto; Lescano Ancieta, Yonhy; Merino De Lama, Manuel; Guevara Amasifuen, Mesias Antonio; Mavila Leon, Rosa Delsa; Mendoza Frisch, Veronika Fanny",
            "expediente": "http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/03774?opendocument",
            "fecha_presentacion": "2014-09-05",
            "id": 3763,
            "numero_proyecto": "03774/2014-CR",
            "pdf_url": "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/Contdoc02_2011_2.nsf/d99575da99ebfbe305256f2e006d1cf0/dbc9030966aac60905257d4a007b75d9/$FILE/PL03774050914.pdf",
            "seguimiento_page": "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso/9609130B9871582F05257D4A00752301?opendocument",
            "short_url": "4aw8ym",
            "time_created": "2014-09-05 03:00:00",
            "time_edited": "2014-09-05 03:00:00",
            "titulo": "Propone establecer los lineamientos para la promoción de la eficiencia y competitividad en la actividad empresarial del Estado, garantizando su aporte estratégico para el desarrollo descentralizado y la soberanía nacional."
        }
        dummy1 = {
            "codigo": "03775",
            'legislatura': 2011,
            "congresistas": "Dammert Ego Aguirre, Manuel Enrique Ernesto; Lescano Ancieta, Yonhy; Merino De Lama, Manuel; Guevara Amasifuen, Mesias Antonio; Mavila Leon, Rosa Delsa; Mendoza Frisch, Veronika Fanny",
            "expediente": "http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/03774?opendocument",
            "fecha_presentacion": "2014-09-05",
            "id": 3764,
            "numero_proyecto": "03775/2014-CR",
            "pdf_url": "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/Contdoc02_2011_2.nsf/d99575da99ebfbe305256f2e006d1cf0/dbc9030966aac60905257d4a007b75d9/$FILE/PL03774050914.pdf",
            "seguimiento_page": "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/Sicr/TraDocEstProc/CLProLey2011.nsf/PAporNumeroInverso/9609130B9871582F05257D4A00752301?opendocument",
            "short_url": "4aw8ym",
            "iniciativas_agrupadas": "{03774}",
            "time_created": "2014-09-05 03:00:00",
            "time_edited": "2014-09-05 03:00:00",
            "titulo": "Propone establecer los lineamientos para la promoción de la eficiencia y competitividad en la actividad empresarial del Estado, garantizando su aporte estratégico para el desarrollo descentralizado y la soberanía nacional."
        }
        p = Proyecto(**dummy)
        p.save()

        p1 = Proyecto(**dummy1)
        p1.save()
        self.c = Client()

    def test_api_seguimientos(self):
        response = self.c.get('/api/seguimientos.json/03774-2011/')
        as_string = response.content.decode("utf-8")
        result = json.loads(as_string)
        expected = "Proyecto No: 03774_2014-CR"
        self.assertEqual(expected, result['timeline']['text'])

    def test_api_seguimientos_csv(self):
        response = self.c.get('/api/seguimientos.csv/03774-2011/')
        result = response.content.decode("utf-8")
        expected = "Proyecto No: 03774_2014-CR"
        self.assertTrue(expected in result)

    def test_api_seguimientos_csv_missing(self):
        response = self.c.get('/api/seguimientos.csv/0377400-2011/')
        result = response.content.decode("utf-8")
        expected = "error,proyecto no existe"
        self.assertEqual(expected, result)

    def test_api_seguimientos_missing(self):
        response = self.c.get('/api/seguimientos.json/0377400-2011/')
        as_string = response.content.decode("utf-8")
        result = json.loads(as_string)
        expected = "proyecto no existe"
        self.assertEqual(expected, result['error'])

    def test_api_iniciativas(self):
        response = self.c.get('/api/iniciativas.json/03775-2011/')
        as_string = response.content.decode("utf-8")
        result = json.loads(as_string)
        expected = '03774'
        self.assertEqual(expected, result['iniciativas'][0]['codigo'])

    def test_api_iniciativas_csv(self):
        response = self.c.get('/api/iniciativas.csv/03775-2011/')
        result = response.content.decode("utf-8")
        expected = '03774'
        self.assertTrue(expected in result)

    def test_api_iniciativas_csv_project_missing(self):
        response = self.c.get('/api/iniciativas.csv/037759976987897-2011/')
        result = response.content.decode("utf-8")
        expected = 'error,proyecto no existe'
        self.assertEqual(expected, result)

    def test_api_iniciativas_csv_missing(self):
        response = self.c.get('/api/iniciativas.csv/03774-2011/')
        result = response.content.decode("utf-8")
        expected = 'error,sin iniciativas agrupadas'
        self.assertEqual(expected, result)

    def test_api_iniciativas_missing(self):
        response = self.c.get('/api/iniciativas.json/03774-2011/')
        as_string = response.content.decode("utf-8")
        result = json.loads(as_string)
        expected = 'sin iniciativas agrupadas'
        self.assertEqual(expected, result['error'])

    def test_api_iniciativas_missing_proyecto(self):
        response = self.c.get('/api/iniciativas.json/000003770000-2011/')
        as_string = response.content.decode("utf-8")
        result = json.loads(as_string)
        expected = 'proyecto no existe'
        self.assertEqual(expected, result['error'])
