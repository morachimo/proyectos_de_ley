import datetime

from django.test import TestCase, Client

from pdl.models import Proyecto
from stats.models import Dispensed
from stats.models import ComisionCount
from stats import views


class TestStatsViews(TestCase):
    def setUp(self):
        Proyecto.objects.create(**{
            'numero_proyecto': '02764',
            'legislatura': 2011,
            'time_created': datetime.datetime.now(),
            'fecha_presentacion': '2010-10-10',
            'titulo_de_ley': 'Ley No 2261',
        })
        Proyecto.objects.create(**{
            'numero_proyecto': '02764',
            'legislatura': 2016,
            'time_created': datetime.datetime.now(),
            'fecha_presentacion': '2010-10-10',
            'titulo_de_ley': 'Ley No 2261',
        })
        Dispensed.objects.create(**{
            'total_approved': 1444,
            'total_dispensed': 864,
            'dispensed_by_plenary': 23,
            'dispensed_by_spokesmen': 12,
            'dispensed_others': 11,
        })
        ComisionCount.objects.create(**{
            'count': 7,
            'comision': 'Justicia',
        })
        self.c = Client()

    def test_index(self):
        response = self.c.get('/stats/')
        self.assertEqual(200, response.status_code)

    def test_dame_sin_tramitar(self):
        numero_de_proyectos = Proyecto.objects.all().count()
        expected = (100.0, 2)
        result = views.dame_sin_tramitar(numero_de_proyectos)
        self.assertEqual(expected, result)

    def test_dame_sin_dictamen(self):
        queryset = ComisionCount.objects.all().order_by('-count')
        result = views.dame_sin_dictamen(queryset, 1)
        expected = (700.0, 7)
        self.assertEqual(expected, result)

    def test_percentage_arent_law(self):
        result = views.get_projects_that_arent_law(1)
        expected = (0, 0.0, {'Ley No 2261'})
        self.assertEqual(expected, result)
