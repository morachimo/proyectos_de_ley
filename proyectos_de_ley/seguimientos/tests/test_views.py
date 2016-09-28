import json

from django.test import TestCase, Client

from pdl.models import Proyecto
from pdl.models import Seguimientos


class TestViews(TestCase):
    def setUp(self):
        b = Proyecto(**{
            'codigo': '00586',
            'legislatura': 2011,
            'numero_proyecto': '00586/2011-CR',
            'fecha_presentacion': '2010-10-10',
            'short_url': '4huj5x',
            'id': 1,
        })
        b.save()

        Seguimientos.objects.create(**{
            'fecha': '2011-01-01',
            'evento': "Decretado a... Trabajo y Seguridad Social",
            'proyecto': b,
        })
        Seguimientos.objects.create(**{
            'fecha': '2012-02-02',
            'evento': "En comisi\u00f3n Trabajo y Seguridad Social",
            'proyecto': b,
        })

    def test_index_view(self):
        c = Client()
        response = c.get('/p/4huj5x/seguimiento/')
        self.assertEqual(200, response.status_code)
