import datetime

from django.test import TestCase

from pdl.models import Proyecto, Seguimientos, Expedientes
from seguimientos import utils


class Object(object):
    """Dummy class for testing."""
    pass


class TestSeguimientos(TestCase):
    def setUp(self):
        proyecto = Proyecto(**{
            "numero_proyecto": "02764/2013-CR",
            "codigo": "02764",
            "legislatura": 2011,
            "short_url": "4zhube",
            "titulo": "Propone Ley Universitaria",
            "iniciativas_agrupadas": ['01790', '01800'],
            "fecha_presentacion": "2010-10-10",
            "id": 1,
        })
        proyecto.save()

        seguimiento1 = {
            'fecha': '2013-10-14',
            'evento': 'Decretado a... Educación, Juventud y Deporte',
            'proyecto': proyecto,
        }
        seguimiento2 = {
            'fecha': '2013-10-15',
            'evento': 'En comisión Educación, Juventud y Deporte',
            'proyecto': proyecto,
        }
        b = Seguimientos(**seguimiento1)
        b.save()
        b = Seguimientos(**seguimiento2)
        b.save()

        expediente1 = seguimiento1  # Expediente y Seguimiento con casi lo mismo
        expediente2 = seguimiento2  # Expediente y Seguimiento con casi lo mismo
        b = Expedientes(**expediente1)
        b.save()
        b = Expedientes(**expediente2)
        b.save()

    def test_get_proyecto_from_short_url(self):
        short_url = "4zhube"
        expected = {
            "numero_proyecto": "02764/2013-CR",
            "codigo": "02764",
            "titulo": "Propone Ley Universitaria",
            "iniciativas_agrupadas": "['01790', '01800']",
        }
        result = utils.get_proyecto_from_short_url(short_url)
        self.assertEqual(expected['codigo'], result.codigo)
        self.assertEqual(expected['iniciativas_agrupadas'],
                         result.iniciativas_agrupadas)

    def test_get_proyecto_from_short_url_from_string(self):
        proyecto = Proyecto(**{
            "numero_proyecto": "02764/2013-CR",
            "codigo": "02764",
            "short_url": "4zhube",
            "legislatura": 2011,
            "titulo": "Propone Ley Universitaria",
            "iniciativas_agrupadas": '{01790,01800}',
            "fecha_presentacion": "2010-10-10",
            "time_created": datetime.date.today(),
            "id": 1,
        })
        proyecto.save()
        short_url = "4zhube"
        expected = ['01790', '01800']
        result = utils.get_proyecto_from_short_url(short_url)
        self.assertEqual(expected, result.iniciativas_agrupadas)

    def test_hiperlink_congre(self):
        congresista = 'Gamarra Saldivar, Teofilo'
        expected = "<a href='/congresista/gamarra_saldivar_teofilo/' title='ver todos sus proyectos'>Gamarra Saldivar, Teofilo</a>"
        result = utils.hiperlink_congre(congresista)
        self.assertEqual(expected, result)

    def test_convert_name_to_slug(self):
        congresista = "Gamarra Saldivar, Teofilo"
        expected = "gamarra_saldivar_teofilo/"
        result = utils.convert_name_to_slug(congresista)
        self.assertEqual(expected, result)

    def test_get_events_from_expediente(self):
        result = utils.get_events_from_expediente('1')
        expected = '15 Oct, 2013'
        self.assertEqual(expected, result[0].fecha)
