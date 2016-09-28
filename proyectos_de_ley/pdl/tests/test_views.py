# -*- encoding: utf-8 -*-
import json
import os
import re

from bs4 import BeautifulSoup

from django.test import Client
from django.test import TestCase

from pdl import views
from pdl import utils
from pdl.models import Proyecto
from pdl.models import Slug
from stats.models import Dispensed


class SimpleTest(TestCase):
    def setUp(self):
        self.maxDiff = None

        this_folder = os.path.abspath(os.path.dirname(__file__))
        dummy_db_json = os.path.join(this_folder, 'dummy_db.json')
        self.dummy_items = json.loads(open(dummy_db_json, 'r').read())

        dummy_slugs = os.path.join(this_folder, 'dummy_slugs.json')
        dummy_slugs = json.loads(open(dummy_slugs, 'r').read())
        for i in dummy_slugs:
            b = Slug(**i)
            b.save()

        Dispensed.objects.create(**{
            'total_approved': 1444,
            'total_dispensed': 864,
            'dispensed_by_plenary': 23,
            'dispensed_by_spokesmen': 12,
            'dispensed_others': 11,
        })

    def test_index(self):
        c = Client()
        response = c.get('/')
        soup = BeautifulSoup(response.content)
        result = soup.find_all('h1')[0].get_text()
        self.assertEqual('Proyectos recientes', result)

    def test_get_last_items(self):
        for i in self.dummy_items:
            b = Proyecto(**i)
            b.save()

        expected = '03774'
        item = utils.get_last_items()[0]
        result = re.search("<b>([0-9]{5})/[0-9]{4}-CR</b>", item).groups()[0]
        self.assertEqual(expected, result)

    def test_prettify_item1(self):
        this_folder = os.path.abspath(os.path.dirname(__file__))
        prettified_file = os.path.join(this_folder, 'prettified_03774.txt')
        with open(prettified_file, "r") as f:
            prettified_item = f.read()
        item = self.dummy_items[1]

        # save it to test database
        b = Proyecto(**item)
        b.save()
        # now get it as QuerySet object
        item = Proyecto.objects.get(codigo='03774')
        result = views.prettify_item(item)
        self.assertEqual(prettified_item[0:100], result[0:100])

    def test_prettify_item2(self):
        """Test when no pdf_url and no expediente are Blank in object."""
        this_folder = os.path.abspath(os.path.dirname(__file__))
        prettified_file = os.path.join(this_folder, 'prettified_03774_2.txt')
        with open(prettified_file, "r") as f:
            prettified_item = f.read()
        item = self.dummy_items[1]
        item['pdf_url'] = ''
        item['expediente'] = ''
        item['seguimiento_page'] = ''

        # save it to test database
        b = Proyecto(**item)
        b.save()
        # now get it as QuerySet object
        item = Proyecto.objects.get(codigo='03774')
        result = views.prettify_item(item)
        self.assertEqual(prettified_item, result)

    def test_prettify_item_small(self):
        this_folder = os.path.abspath(os.path.dirname(__file__))
        prettified_file = os.path.join(this_folder,
                                       'prettified_03774_small.txt')
        with open(prettified_file, "r") as f:
            prettified_item = f.read()
        item = self.dummy_items[1]

        # save it to test database
        b = Proyecto(**item)
        b.save()
        # now get it as QuerySet object
        item = Proyecto.objects.get(codigo='03774')
        result = utils.prettify_item_small(item)
        self.assertEqual(prettified_item, result)

        # no PDF
        item.pdf_url = ''
        result = utils.prettify_item_small(item)
        self.assertTrue('sin PDF' in result)

        # no expediente
        item.expediente = ''
        result = utils.prettify_item_small(item)
        self.assertTrue('sin Expediente' in result)

        # no seguimiento_page
        item.seguimiento_page = ''
        result = utils.prettify_item_small(item)
        self.assertTrue('sin Seguimiento' in result)

    def test_hiperlink_congre(self):
        expected = "<a href='/congresista/dammert_ego_aguirre/' title='ver " \
                   "todos sus proyectos'>Dammert Ego Aguirre, Manuel " \
                   "Enrique Ernesto</a>;\n" \
                   "<a href='/congresista/lescano_ancieta_yonhy/' " \
                   "title='ver todos sus proyectos'>Lescano Ancieta, " \
                   "Yonhy</a>"
        congresistas = "Dammert Ego Aguirre, Manuel Enrique Ernesto; " \
                       "Lescano Ancieta, Yonhy"
        result = utils.hiperlink_congre(congresistas)
        self.assertEqual(expected, result)

    def test_convert_name_to_slug(self):
        name = 'Eguren Neuenschwander, Juan Carlos'
        expected = 'eguren_neuenschwander_juan/'
        result = utils.convert_name_to_slug(name)
        self.assertEqual(expected, result)

    def test_proyecto_view(self):
        i = self.dummy_items[1]
        b = Proyecto(**i)
        b.save()

        c = Client()
        response = c.get('/p/4aw8ym/')
        soup = BeautifulSoup(response.content)
        result = soup.title.get_text().strip()
        print(result)
        expected = 'Proyectos de ley emitidos por el Congreso | 03774/2014-CR'
        self.assertEqual(expected, result)

        response = c.get('/p/4aw8ymaaaaaaaaaaaaaa/')
        self.assertTrue(b'No se pudo encontrar el proyecto' in
                        response.content)

    def test_about_view(self):
        c = Client()
        response = c.get('/about/')
        soup = BeautifulSoup(response.content)
        result = soup.title.get_text().strip()
        expected = 'Proyectos de ley emitidos por el Congreso de la ' \
                   'República del Perú | About'
        self.assertEqual(expected, result)

    def test_congresista_view(self):
        c = Client()
        response = c.get('/congresista/')
        self.assertEqual(302, response.status_code)

        response = c.get('/congresista/pacheco_yoni/')
        self.assertTrue(b'No se pudo encontrar el congresista' in
                        response.content)

        response = c.get('/congresista/dammert_ego_aguirre/')
        self.assertTrue(b'Dammert Ego Aguirre' in response.content)

    def test_do_pagination(self):
        # get first page for not giving integer as page number
        c = Client()
        response = c.get('/?page=bad_page_number')
        self.assertTrue(b'Proyectos de Ley' in response.content)

        # user gives empty page
        response = c.get('/?page=')
        self.assertTrue(b'Proyectos de Ley' in response.content)

        # user gives empty page
        response = c.get('/?page=100')
        self.assertTrue(b'Proyectos de Ley' in response.content)

        # user gives pagination more than 20
        entries = []
        j = 1
        for i in self.dummy_items:
            i['id'] = j
            entries.append(Proyecto(**i))
            j += 1
        Proyecto.objects.bulk_create(entries)
        response = c.get('/?page=21')
        self.assertFalse(b'/?page=10' in response.content)

    def test_congresista_view_pagination(self):
        entries = []
        j = 1
        for i in self.dummy_items:
            i['id'] = j
            entries.append(Proyecto(**i))
            j += 1
        Proyecto.objects.bulk_create(entries)

        c = Client()
        response = c.get('/congresista/dammert_ego_aguirre/?page=2')
        self.assertTrue(b'endless_page_link' in response.content)

    def test_find_slug_in_db(self):
        item = self.dummy_items[0]

        # save it to test database
        b = Proyecto(**item)
        b.save()

        # now get it as QuerySet object
        slug = 'dammert_ego_aguirre'
        expected = 'Dammert Ego Aguirre, Manuel Enrique Ernesto'
        result = utils.find_slug_in_db(slug)
        self.assertEqual(expected, result)

        # find elements not in our database
        slug = 'dammert_ego_aguirre/'
        result = utils.find_slug_in_db(slug)
        self.assertEqual(expected, result)

        slug = 'dammert_ego_aguirre'
        result = utils.find_slug_in_db(slug)
        self.assertEqual(expected, result)

        slug = 'dammert_ego_aguirreaaaaaaaa'
        result = utils.find_slug_in_db(slug)
        self.assertEqual(None, result)

    def test_search1(self):
        """Search attempt is redirected to index."""
        c = Client()
        response = c.get('/search/')
        self.assertEqual(302, response.status_code)

    def test_search2(self):
        """Search attempt returns page with no result."""
        query = "'*;/"
        c = Client()
        response = c.get('/search/?q=' + query)
        self.assertTrue('No se encontraron resultados' in str(response.content))

    def test_search_empty_query(self):
        query = " "
        c = Client()
        response = c.get('/search/?q=' + query)
        self.assertEqual(302, response.status_code)
