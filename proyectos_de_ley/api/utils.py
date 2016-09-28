import datetime
import re
import unicodedata

from django.db.models import Q

from pdl.models import Proyecto
from pdl.models import Seguimientos
from pdl.models import Slug


LEGISLATURE = 2016

def get_projects_for_person(names):
    projects_and_person = []
    for name in names:
        queryset = Proyecto.objects.filter(
            congresistas__icontains=name,
            legislatura=LEGISLATURE,
        ).order_by('-codigo')
        projects_list = [
            "{}-{}".format(i.codigo, LEGISLATURE)
            for i in queryset
        ]
        obj = {'nombre': name, 'proyectos': projects_list}
        projects_and_person.append(obj)
    return projects_and_person


def get_projects_by_comission_for_person(comision, names):
    projects_and_person = []
    for name in names:
        queryset = Proyecto.objects.filter(
            congresistas__icontains=name,
            legislatura=LEGISLATURE,
        ).order_by('-codigo')
        if comision != '':
            queryset = queryset.filter(nombre_comision__icontains=comision)
        projects_list = [
            "{}-{}".format(i.codigo, LEGISLATURE)
            for i in queryset
        ]
        obj = {'nombre': name, 'proyectos': projects_list}
        projects_and_person.append(obj)
    return projects_and_person


def find_name_from_short_name(nombre_corto):
    nombre_corto = unicodedata.normalize('NFKD', nombre_corto).encode('ascii', 'ignore')
    nombre_corto = re.sub('\s+', ' ', nombre_corto.decode('utf-8'))
    nombre_corto = nombre_corto.split(' ')
    if len(nombre_corto) < 2:
        return ['---error---', 'ingrese un nombre y un apellido']

    nombre_corto = nombre_corto[:2]
    res = Slug.objects.filter(Q(ascii__icontains=nombre_corto[0]) & Q(ascii__icontains=nombre_corto[1]))

    if len(res) > 0:
        return [i.nombre for i in res]
    else:
        return ['---error---', 'no se pudo encontrar congresista']


def prepare_json_for_d3(proyecto):
    nodes = []
    append = nodes.append

    iniciativas_agrupadas = proyecto.iniciativas_agrupadas.replace('{', '').replace('}', '').split(',')

    for i in iniciativas_agrupadas:
        try:
            queryset = Proyecto.objects.get(
                codigo=i,
                legislatura=int(proyecto.legislatura),
            )
        except Proyecto.DoesNotExist:
            continue
        node = {"codigo": i, "url": "/p/" + queryset.short_url}
        append(node)

    sorted_nodes_by_code = sorted(nodes, key=lambda k: k['codigo'])
    return {'iniciativas': sorted_nodes_by_code}


def get_seguimientos_from_proyecto_id(id):
    res = Seguimientos.objects.all().filter(proyecto_id=id)
    seguimientos = []
    append = seguimientos.append
    for i in res:
        obj = {}
        obj['startDate'] = str(i.fecha).replace("-", ",")
        obj['headline'] = i.evento
        append(obj)
    return seguimientos


def convert_date_to_string(dateobj):
    try:
        fecha = datetime.datetime.strftime(dateobj, '%Y-%m-%d')
    except TypeError:
        return dateobj
    return fecha


class MyObj(object):
    pass
