import datetime

from django.test import TestCase

from pdl.models import Proyecto, Seguimientos, Expedientes
from api import utils


class Object(object):
    """Dummy class for testing."""
    pass


class TestSeguimientos(TestCase):
    def setUp(self):
        proyecto = Proyecto(**{
            "numero_proyecto": "02764/2013-CR",
            "codigo": "02764",
            'legislatura': 2016,
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

    def test_prepare_json_for_d3(self):
        item = Object()
        item.numero_proyecto = "02764/2013-CR"
        item.codigo = "02764"
        item.legislatura = 2016
        item.titulo = "Propone Ley Universitaria"
        item.iniciativas_agrupadas = '{02764}'

        expected = {'iniciativas': [{'codigo': '02764', 'url': '/p/4zhube'}]}
        result = utils.prepare_json_for_d3(item)
        self.assertEqual(expected, result)

    def test_prepare_json_for_d3_no_project(self):
        item = Object()
        item.numero_proyecto = "02764/2013-CR"
        item.codigo = "02764"
        item.legislatura = 2016
        item.titulo = "Propone Ley Universitaria"
        item.iniciativas_agrupadas = '{027640000}'

        expected = {'iniciativas': []}
        result = utils.prepare_json_for_d3(item)
        self.assertEqual(expected, result)

    def test_convert_date_to_string(self):
        fecha = datetime.datetime(2010, 10, 10)
        expected = '2010-10-10'
        result = utils.convert_date_to_string(fecha)
        self.assertEqual(expected, result)

    def test_convert_date_to_string_with_exception(self):
        fecha = '2010-10-10'
        expected = '2010-10-10'
        result = utils.convert_date_to_string(fecha)
        self.assertEqual(expected, result)

    def test_get_seguimientos_from_proyecto_id(self):
        result = utils.get_seguimientos_from_proyecto_id('1')
        expected = 'Decretado a... Educación, Juventud y Deporte'
        self.assertEqual(expected, result[0]['headline'])
