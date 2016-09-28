import unicodedata

import arrow
from pdl.models import Proyecto
from pdl.models import Expedientes
from pdl.utils import convert_string_to_time


def get_proyecto_from_short_url(short_url):
    """
    :param short_url:
    :return: item for Proyecto
    """
    item = Proyecto.objects.get(short_url=short_url)
    if item.iniciativas_agrupadas is not None and \
            item.iniciativas_agrupadas != '' and '{' in \
            item.iniciativas_agrupadas:
        iniciativas = item.iniciativas_agrupadas.replace("{", "")
        iniciativas = iniciativas.replace("}", "")
        item.iniciativas_agrupadas = iniciativas.split(",")
    item.congresistas_with_links = hiperlink_congre(item.congresistas)
    item.fecha_presentacion = convert_string_to_time(item.fecha_presentacion)
    item.fecha_presentacion_human = arrow.get(item.fecha_presentacion).format('DD MMMM, YYYY', locale='es_es')
    item.numero_congresistas = len(item.congresistas.split(";"))
    return item


def get_events_from_expediente(id):
    """
    Uses the `proyecto_id` to obtain a list of events from the `expediente`
    page.

    :param id: proyecto_id as in table pdl_proyecto
    :return: list of events, which are key=>value dictionaries
    """
    events = Expedientes.objects.all().filter(proyecto=id).order_by('-fecha')

    events_with_human_date = []
    append = events_with_human_date.append
    for i in events:
        i.fecha = arrow.get(i.fecha).format('DD MMM, YYYY', locale='es_es')
        append(i)
    return events_with_human_date


def hiperlink_congre(congresistas):
    # tries to make a hiperlink for each congresista name to its own webpage
    if congresistas == '':
        return None

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
