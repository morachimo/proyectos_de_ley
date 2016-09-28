import datetime
import re
import time
import unicodedata

import arrow

from django.conf import settings
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from pdl.models import Proyecto
from pdl.models import Slug


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print('elapsed time: %f ms' % self.msecs)


def convert_date_to_string(fecha):
    try:
        nueva_fecha = datetime.date.strftime(fecha, '%m/%d/%Y')
        return nueva_fecha
    except TypeError:
        return None


def convert_string_to_time(string):
    if isinstance(string, str):
        this_time = re.sub("\+[0-9]+$", "", string)
        try:
            time_object = datetime.datetime.strptime(this_time, "%Y-%m-%d")
            return time_object
        except ValueError:
            pass

        try:
            time_object = datetime.datetime.strptime(this_time, "%Y-%m-%d %H:%M:%S.%f")
        except TypeError:
            # This exception is only for our test that wants str not date obj
            time_object = item.time_created
        except ValueError:
            time_object = datetime.datetime.strptime(this_time, "%Y-%m-%d %H:%M:%S")

        return time_object
    else:
        # is should be a date object
        return string


def prettify_item(item):
    fecha_pres_humana = arrow.get(item.fecha_presentacion).format('DD MMMM, YYYY', locale='es_es')
    out = "<p>"
    out += "<a href='/p/" + str(item.short_url)
    out += "' title='Permalink'>"
    out += "<b>" + item.numero_proyecto + "</b></a> "
    out += "&nbsp;"
    out += "<small>Presentado: " + fecha_pres_humana + "</small></p>\n"
    out += "<h4>" + item.titulo + "</h4>\n"

    if len(item.congresistas) > 0:
        out += "Autores <span class='badge'>" + str(len(item.congresistas.split(";"))) + "</span>\n"
    out += "<p>" + hiperlink_congre(item.congresistas) + "</p>\n"

    if item.pdf_url != '':
        out += "<a class='btn btn-lg btn-primary'"
        out += " href='" + str(item.pdf_url) + "' role='button'>PDF</a>\n"
    else:
        out += "<a class='btn btn-lg btn-primary disabled'"
        out += " href='#' role='button'>Sin PDF</a>\n"

    if item.expediente != '':
        out += "<a class='btn btn-lg btn-primary'"
        out += " href='" + item.expediente
        out += "' role='button'>EXPEDIENTE</a>\n"
    else:
        out += "<a class='btn btn-lg btn-primary disabled'"
        out += " href='#' role='button'>Sin EXPEDIENTE</a>\n"

    if item.seguimiento_page != '':
        out += "<a class='btn btn-lg btn-primary'"
        out += " href='/p/" + item.short_url + "/seguimiento"
        out += "' role='button'>Seguimiento</a>"
    return out


def hiperlink_congre(congresistas):
    # tries to make a hiperlink for each congresista name to its own webpage
    for name in congresistas.split("; "):
        link = "<a href='/congresista/"
        link += str(convert_name_to_slug(name))
        link += "' title='ver todos sus proyectos'>"
        link += name + "</a>"
        congresistas = congresistas.replace(name, link)
    congresistas = congresistas.replace("; ", ";\n")
    return congresistas

def convert_name_to_slug(name):
    """Takes a congresista name and returns its slug."""
    name = name.strip()
    name = name.replace(",", "").lower()
    name = name.split(" ")

    if len(name) > 2:
        i = 0
        slug = ""
        while i < 3:
            slug += name[i]
            if i < 2:
                slug += "_"
            i += 1
        slug = unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore')
        slug = str(slug, encoding="utf-8")
        return slug + "/"


def do_pagination(request, all_items, search=False, advanced_search=None):
    """
    :param request: contains the current page requested by user
    :param all_items:
    :param search: if search is False items will be prettified in long form.
           if search is True then items will be prettified as small items
           for search results.
    :param advanced_search: True or None to point out that we come from the
           advanced search page.
    :return: dict containing paginated items and pagination bar
    """
    if 'comision' in request.GET and request.GET['comision'] != '':
        comision = request.GET['comision']
    else:
        comision = False

    if search is False:
        paginator = Paginator(all_items, 20)
    else:
        paginator = Paginator(all_items, 40)

    page = request.GET.get('page')

    try:
        items = paginator.page(page)
        cur = int(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
        cur = 1
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)
        cur = 1

    pretty_items = []
    for i in items.object_list:
        if search is False:
            pretty_items.append(prettify_item(i))
        else:
            if settings.TESTING:
                pretty_items.append(prettify_item_small(i))
            elif advanced_search is True:
                pretty_items.append(prettify_item_small(i))
            else:
                pretty_items.append(prettify_item_small(i.object))

    if cur > 20:
        first_half = range(cur - 10, cur)
        # is current less than last page?
        if cur < paginator.page_range[-1] - 10:
            second_half = range(cur + 1, cur + 10)
        else:
            second_half = range(cur + 1, paginator.page_range[-1])
    else:
        first_half = range(1, cur)
        if paginator.page_range[-1] > 20:
            second_half = range(cur + 1, 21)
        else:
            second_half = range(cur + 1, paginator.page_range[-1] + 1)

    obj = {
        'items': items,
        "pretty_items": pretty_items,
        "first_half": first_half,
        "second_half": second_half,
        "first_page": paginator.page_range[0],
        "last_page": paginator.page_range[-1],
        "current": cur,
        "comision": comision,
    }
    return obj


def find_slug_in_db(congresista_slug):
    try:
        item = Slug.objects.get(slug=congresista_slug)
        return item.ascii
    except Slug.DoesNotExist:
        try:
            congresista_slug += '/'
            item = Slug.objects.get(slug=congresista_slug)
            return item.ascii
        except Slug.DoesNotExist:
            return None


def get_last_items():
    """All items from the database are extracted as list of dictionaries."""
    items = Proyecto.objects.all().order_by('-codigo')[:20]
    pretty_items = []
    for i in items:
        pretty_items.append(prettify_item(i))
    return pretty_items


def prettify_item_small(item):
    out = "<p><a href='/p/" + item.short_url
    out += "' title='Permalink'>"
    out += item.codigo
    out += "</a>\n "
    out += item.titulo
    if item.pdf_url != '' and item.pdf_url is not None:
        out += '\n <span class="glyphicon glyphicon-cloud-download"></span>'
        out += ' <a href="' + item.pdf_url + '">PDF</a>'
    else:
        out += ' [sin PDF]'

    if item.expediente != '' and item.expediente is not None:
        out += '\n <span class="glyphicon glyphicon-link"></span>'
        out += ' <a href="' + item.expediente + '">Expediente</a>'
    else:
        out += ' [sin Expediente]'

    if item.seguimiento_page != '' and item.seguimiento_page is not None:
        out += '\n <span class="glyphicon glyphicon-link"></span>'
        out += ' <a href="/p/' + item.short_url + \
               '/seguimiento">Seguimiento</a>'
    else:
        out += '\n [sin Seguimiento]'
    out += '</p>'
    return out
