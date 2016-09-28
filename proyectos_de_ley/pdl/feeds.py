# -*- encoding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from pdl.models import Proyecto
from pdl.utils import convert_string_to_time


class CorrectMimeTypeFeed(Rss201rev2Feed):
    mime_type = 'application/xml'


class LatestEntriesFeed(Feed):
    title = 'Proyectos de ley emitidos por el Congreso de la República del' \
            ' Perú'
    link = 'http://www.proyectosdeley.pe/rss.xml'
    feed_url = 'http://www.proyectosdeley.pe/rss.xml'
    description = 'proyectosdeley.pe es un intento de transparentar el Cong' \
                  'reso y poner al alcance de la mayor cantidad de personas' \
                  'los proyectos de ley presentados y discutidos en el parl' \
                  'amento. La información mostrada es tomada directamente d' \
                  'e la página web del Congreso.'
    feed_type = CorrectMimeTypeFeed

    def items(self):
        return Proyecto.objects.filter(legislatura=2016).order_by('-codigo')[:50]

    def item_title(self, item):
        return item.titulo[:140] + "..."

    def item_description(self, item):
        out = item.titulo + '<br /><br />Autores: '
        out += item.congresistas + '<br /><br />'
        out += '<a href="http://www.proyectosdeley.pe/p/' + item.short_url + '/">'
        out += 'http://www.proyectosdeley.pe/p/' + item.short_url + '</a>'
        out += '<br /><br />'
        if item.pdf_url is not None:
            out += '<a href="' + item.pdf_url + '">PDF</a> '
        if item.expediente is not None:
            out += '<a href="' + item.expediente + '">Expediente</a>'
        out += ' <a href="http://www.proyectosdeley.pe/p/' + item.short_url
        out += '/seguimiento/">Seguimiento</a>'
        return out

    def item_link(self, item):
        return 'http://www.proyectosdeley.pe/p/' + item.short_url

    def item_pubdate(self, item):
        time_object = convert_string_to_time(item.time_created)
        return time_object
