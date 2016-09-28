import re

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer

from . import utils


def index(request, short_url):
    short_url = re.sub("/seguimiento/", "", short_url)
    item = utils.get_proyecto_from_short_url(short_url)
    item.expediente_events = utils.get_events_from_expediente(item.id)
    friendly_code = "{}-{}".format(
        item.codigo,
        item.legislatura,
    )
    return render(request, "seguimientos/index.html",
                  {
                      "item": item,
                      "friendly_code": friendly_code,
                  })


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        super(JSONResponse, self).__init__(content, **kwargs)
