import json
import re

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.decorators import renderer_classes
from rest_framework.permissions import AllowAny

from pdl.models import Proyecto
from pdl.models import Seguimientos
from .serializers import CongresistaSerializer
from .serializers import ExoneradoDictamenSerializer
from .serializers import Exonerados2daVotacionSerializer
from .serializers import IniciativasSerializer
from .serializers import ProyectoSerializer
from .serializers import SeguimientosSerializer
from .api_responses import CSVRenderer
from .api_responses import CSVResponse
from .api_responses import JSONResponse
from .utils import convert_date_to_string
from .utils import find_name_from_short_name
from .utils import get_projects_by_comission_for_person
from .utils import get_projects_for_person
from .utils import get_seguimientos_from_proyecto_id
from .utils import prepare_json_for_d3
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import response, schemas
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

LEGISLATURE = 2016

@api_view(['GET'])
@permission_classes((AllowAny, ))
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_view(request):
    generator = schemas.SchemaGenerator(title='Documentación del API de Proyectos de ley.')
    return response.Response(generator.get_schema(request=request))


@api_view(['GET'])
@permission_classes((AllowAny, ))
def proyecto(request, codigo):
    """
    Lista metadatos de cada proyecto de ley.

    # Puedes obtener los resultados en archivo CSV (fácil de importar a MS Excel)

    Solo es necesario usar la dirección `proyecto.csv`:

    * <http://proyectosdeley.pe/api/proyecto.csv/00002-2011/>
    ---
    type:
      codigo:
        required: true
        type: string

    parameters:
      - name: codigo
        description: código del proyecto de ley incluyendo legislatura, por ejemplo 00002-2011
        type: string
        paramType: path
        required: true
    """
    codigo, legislatura = split_code_input(codigo)

    try:
        proy = Proyecto.objects.get(
            codigo=codigo,
            legislatura=legislatura,
        )
    except Proyecto.DoesNotExist:
        msg = {'error': 'proyecto no existe'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    if request.method == 'GET':
        serializer = ProyectoSerializer(proy)
        return JSONResponse(serializer.data)


@permission_classes((AllowAny, ))
@renderer_classes((CSVRenderer,))
def proyecto_csv(request, codigo):
    """
    Lista metadatos de cada proyecto de ley.
    ---
    type:
      codigo:
        required: true
        type: string

    parameters:
      - name: codigo
        description: código del proyecto de ley incluyendo legislatura, por ejemplo 00002-2011
        type: string
        paramType: path
        required: true
    """
    codigo, legislatura = split_code_input(codigo)

    proyectos = Proyecto.objects.filter(
        codigo=codigo,
        legislatura=legislatura,
    ).values()
    if len(proyectos) < 1:
        msg = 'error,proyecto no existe'
        return HttpResponse(msg, content_type='text/csv')

    data = [i for i in proyectos]
    if request.method == 'GET':
        return CSVResponse(data)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def congresista(request, nombre_corto):
    """
    Lista proyectos de ley de cada congresista.

    # Por ejemplo:

    * <http://proyectosdeley.pe/api/congresista.json/Manuel+Zerillo/>

    # Puedes obtener los resultados en archivo CSV (fácil de importar a MS Excel)

    Solo es necesario usar la dirección `congresista.csv`:

    * <http://proyectosdeley.pe/api/congresista.csv/Manuel+Zerillo/>
    ---
    type:
      nombre_corto:
        required: true
        type: string

    parameters:
      - name: nombre_corto
        description: Nombre y apellido del congresista, por ejemplo<br /> Manuel+Zerillo
        type: string
        paramType: path
        required: true
    """
    nombre_corto = nombre_corto.replace('+', ' ')
    names = find_name_from_short_name(nombre_corto)

    if '---error---' in names:
        msg = {'error': names[1]}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    projects_and_person = get_projects_for_person(names)
    data = {
        'resultado': projects_and_person,
        'numero_de_congresistas': len(projects_and_person),
    }
    if request.method == 'GET':
        serializer = CongresistaSerializer(data)
        return JSONResponse(serializer.data)


@permission_classes((AllowAny,))
@renderer_classes((CSVRenderer,))
def congresista_csv(request, nombre_corto):
    """
    Lista proyectos de ley de cada congresista.

    # Por ejemplo:

    * <http://proyectosdeley.pe/api/congresista.csv/Manuel+Zerillo/>
    ---
    type:
      nombre_corto:
        required: true
        type: string
        omit_serializer: true

    parameters:
      - name: nombre_corto
        description: Nombre y apellido del congresista, por ejemplo<br /> Manuel+Zerillo
        type: string
        paramType: path
        required: true
    """
    nombre_corto = nombre_corto.replace('+', ' ')
    names = find_name_from_short_name(nombre_corto)

    if '---error---' in names:
        msg = 'error,{}'.format(names[1])
        return HttpResponse(msg, content_type='text/csv')

    projects_and_person = get_projects_for_person(names)
    data = []
    for i in projects_and_person:
        for p in i['proyectos']:
            data.append({'proyecto': p, 'nombre': i['nombre']})
    if request.method == 'GET':
        return CSVResponse(data)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def congresista_y_comision(request, nombre_corto, comision):
    """
    Lista proyectos de ley de cada congresista y la comisión que derivó.

    # Por ejemplo:

    * <http://proyectosdeley.pe/api/congresista.json/Manuel+Zerillo/Economía/>

    # Puedes obtener los resultados en archivo CSV (fácil de importar a MS Excel)

    Solo es necesario usar la dirección `congresista.csv`:

    * <http://proyectosdeley.pe/api/congresista.csv/Manuel+Zerillo/Economía/>
    ---
    type:
      nombre_corto:
        required: true
        type: string
      comision:
        required: true
        type: string

    parameters:
      - name: nombre_corto
        description: Nombre y apellido del congresista, por ejemplo<br /> Manuel+Zerillo
        type: string
        paramType: path
        required: true
      - name: comision
        description: Comisión congresal, por ejemplo<br /> Economía
        type: string
        paramType: path
        required: true
    """
    nombre_corto = nombre_corto.replace('+', ' ')
    names = find_name_from_short_name(nombre_corto)

    if '---error---' in names:
        msg = {'error': names[1]}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    comision = comision.strip()
    projects_and_person = get_projects_by_comission_for_person(comision, names)
    data = {
        'resultado': projects_and_person,
        'numero_de_congresistas': len(projects_and_person),
    }
    if request.method == 'GET':
        serializer = CongresistaSerializer(data)
        return JSONResponse(serializer.data)


@permission_classes((AllowAny, ))
@renderer_classes((CSVRenderer,))
def congresista_y_comision_csv(request, nombre_corto, comision):
    """
    Lista proyectos de ley de cada congresista y la comisión que derivó.

    # Puedes obtener los resultados en archivo CSV (fácil de importar a MS Excel)

    Solo es necesario usar la dirección `congresista.csv`:

    * <http://proyectosdeley.pe/api/congresista.csv/Manuel+Zerillo/Economía/>
    ---
    type:
      nombre_corto:
        required: true
        type: string
      comision:
        required: true
        type: string

    parameters:
      - name: nombre_corto
        description: Nombre y apellido del congresista, por ejemplo<br /> Manuel+Zerillo
        type: string
        paramType: path
        required: true
      - name: comision
        description: Comisión congresal, por ejemplo<br /> Economía
        type: string
        paramType: path
        required: true
    """
    nombre_corto = nombre_corto.replace('+', ' ')
    names = find_name_from_short_name(nombre_corto)

    if '---error---' in names:
        msg = 'error,{}'.format(names[1])
        return HttpResponse(msg, content_type='text/csv')

    comision = comision.strip()
    projects_and_person = get_projects_by_comission_for_person(comision, names)
    data = []
    for i in projects_and_person:
        for p in i['proyectos']:
            data.append({'proyecto': p, 'nombre': i['nombre']})
    if request.method == 'GET':
        return CSVResponse(data)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def exonerados_dictamen(request):
    """
    Lista proyectos que han sido aprobados y exonerados de dictamen.

    # Puedes obtener los resultados en archivo CSV (fácil de importar a MS Excel)

    Solo es necesario usar la dirección `exonerados_dictamen.csv`:

    * <http://proyectosdeley.pe/api/exonerados_dictamen.csv/>
    """
    exonerado_de_dictamen = [
        '{}-{}'.format(i.proyecto.codigo, LEGISLATURE)
        for i in Seguimientos.objects.select_related(
            'proyecto',
        ).filter(
            evento__icontains='exoneración de dictamen',
        ).filter(
            proyecto__legislatura=LEGISLATURE,
        ).distinct()
    ]
    exonerado_de_dictamen = list(set(exonerado_de_dictamen))

    if len(exonerado_de_dictamen) > 0:
        data = {'resultado': exonerado_de_dictamen}
        if request.method == 'GET':
            serializer = ExoneradoDictamenSerializer(data)
            return JSONResponse(serializer.data)
    else:
        msg = {'error': 'no se encontraron resultados'}
        return HttpResponse(json.dumps(msg), content_type='application/json')


@permission_classes((AllowAny, ))
@renderer_classes((CSVRenderer,))
def exonerados_dictamen_csv(request):
    """
    Lista proyectos que han sido aprobados y exonerados de dictamen.

    # Puedes obtener los resultados en archivo CSV (fácil de importar a MS Excel)

    Solo es necesario usar la dirección `exonerados_2da_votacion.csv`:

    * <http://proyectosdeley.pe/api/exonerados_2da_votacion.csv/>
    """
    exonerado_de_dictamen = [
        '{}-{}'.format(i.proyecto.codigo, LEGISLATURE)
        for i in Seguimientos.objects.select_related(
            'proyecto',
        ).filter(
            evento__icontains='exoneración de dictamen',
        ).filter(
            proyecto__legislatura=LEGISLATURE,
        ).distinct()
        ]
    data = list(set(exonerado_de_dictamen))

    if len(exonerado_de_dictamen) > 0:
        if request.method == 'GET':
            return CSVResponse(data)
    else:
        msg = 'error,no se encontraron resultados'
        return HttpResponse(msg, content_type='text/csv')


@api_view(['GET'])
@permission_classes((AllowAny, ))
def exonerados_2da_votacion(request):
    """
    Lista proyectos que han sido exonerados de 2da votación en el pleno.
    ---
    """
    total_dispensed = [
        "{}-{}".format(i.proyecto.codigo, LEGISLATURE)
        for i in Seguimientos.objects.select_related(
            'proyecto',
        ).filter(
            evento__icontains='dispensado 2da',
        ).filter(
            proyecto__legislatura=LEGISLATURE,
        )
    ]

    if len(total_dispensed) > 0:
        data = {'resultado': total_dispensed}
        if request.method == 'GET':
            serializer = Exonerados2daVotacionSerializer(data)
            return JSONResponse(serializer.data)
    else:
        msg = {'error': 'no se encontraron resultados'}
        return HttpResponse(json.dumps(msg), content_type='application/json')


@permission_classes((AllowAny, ))
@renderer_classes((CSVRenderer,))
def exonerados_2da_votacion_csv(request):
    """
    Lista proyectos que han sido exonerados de 2da votación en el pleno.
    ---
    """
    data = [
        "{}-{}".format(i.proyecto.codigo, LEGISLATURE)
        for i in Seguimientos.objects.select_related(
            'proyecto',
        ).filter(
            evento__icontains='dispensado 2da',
        ).filter(
            proyecto__legislatura=LEGISLATURE,
        )
    ]

    if len(data) > 0:
        if request.method == 'GET':
            return CSVResponse(data)
    else:
        msg = 'error,no se encontraron resultados'
        return HttpResponse(msg, content_type='text/csv')


@api_view(['GET'])
@permission_classes((AllowAny, ))
def iniciativa_list(request, codigo):
    """Lista todas las iniciativas que se agruparon para proyecto de ley.

    # Puedes obtener los resultados en archivo CSV (fácil de importar a MS Excel)

    Solo es necesario usar la dirección `iniciativas.csv`:

    * <http://proyectosdeley.pe/api/iniciativas.csv/00002-2011/>
    ---
    type:
      codigo:
        required: true
        type: string

    parameters:
      - name: codigo
        description: código del proyecto de ley incluyendo legislatura, por ejemplo 00002-2011
        type: string
        paramType: path
        required: true
    """
    codigo, legislatura = split_code_input(codigo)
    try:
        proy = Proyecto.objects.get(
            codigo=codigo,
            legislatura=legislatura,
        )
    except Proyecto.DoesNotExist:
        msg = {'error': 'proyecto no existe'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    if not proy.iniciativas_agrupadas:
        msg = {'error': 'sin iniciativas agrupadas'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    data = prepare_json_for_d3(proy)

    if request.method == 'GET':
        serializer = IniciativasSerializer(data)
        return JSONResponse(serializer.data)


@permission_classes((AllowAny, ))
@renderer_classes((CSVRenderer,))
def iniciativa_list_csv(request, codigo):
    """Lista todas las iniciativas que se agruparon para proyecto de ley.
    ---
    type:
      codigo:
        required: true
        type: string

    parameters:
      - name: codigo
        description: código del proyecto de ley incluyendo legislatura, por ejemplo 00002-2011
        type: string
        paramType: path
        required: true
    """
    codigo, legislatura = split_code_input(codigo)
    try:
        proy = Proyecto.objects.get(
            codigo=codigo,
            legislatura=legislatura,
        )
    except Proyecto.DoesNotExist:
        msg = 'error,proyecto no existe'
        return HttpResponse(msg, content_type='text/csv')

    if proy.iniciativas_agrupadas is None or proy.iniciativas_agrupadas.strip() == '':
        msg = 'error,sin iniciativas agrupadas'
        return HttpResponse(msg, content_type='text/csv')

    data = prepare_json_for_d3(proy)

    if request.method == 'GET':
        return CSVResponse(data['iniciativas'])


@api_view(['GET'])
@permission_classes((AllowAny, ))
def seguimientos_list(request, codigo):
    """Lista todos los eventos de seguimiento para cada proyecto de ley.

    # Puedes obtener los resultados en archivo CSV (fácil de importar a MS Excel)

    Solo es necesario usar la dirección `seguimientos.csv`:

    * <http://proyectosdeley.pe/api/seguimientos.csv/00002-2011/>
    ---
    type:
      codigo:
        required: true
        type: string

    parameters:
      - name: codigo
        description: código del proyecto de ley incluyendo legislatura, por ejemplo 00002-2011
        type: string
        paramType: path
        required: true
    """
    codigo, legislatura = split_code_input(codigo)
    try:
        proy = Proyecto.objects.get(
            codigo=codigo,
            legislatura=legislatura,
        )
    except Proyecto.DoesNotExist:
        msg = {'error': 'proyecto no existe'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    seguimientos = get_seguimientos_from_proyecto_id(proy.id)
    seguimientos.append({
        'headline': 'Fecha de presentación',
        'startDate': convert_date_to_string(proy.fecha_presentacion).replace("-", ","),
    })

    my_dict = dict()
    my_dict['type'] = 'default'
    my_dict['text'] = "Proyecto No: " + str(proy.numero_proyecto).replace("/", "_")
    my_dict['date'] = seguimientos

    data = {'timeline': my_dict}

    if request.method == 'GET':
        serializer = SeguimientosSerializer(data)
        return JSONResponse(serializer.data)


@permission_classes((AllowAny, ))
def seguimientos_list_csv(request, codigo):
    """Lista todos los eventos de seguimiento para cada proyecto de ley.
    ---
    type:
      codigo:
        required: true
        type: string

    parameters:
      - name: codigo
        description: código del proyecto de ley incluyendo legislatura, por ejemplo 00002-2011
        type: string
        paramType: path
        required: true
    """
    codigo, legislatura = split_code_input(codigo)
    try:
        proy = Proyecto.objects.get(
            codigo=codigo,
            legislatura=legislatura,
        )
    except Proyecto.DoesNotExist:
        msg = 'error,proyecto no existe'
        return HttpResponse(msg, content_type='text/csv')

    seguimientos = get_seguimientos_from_proyecto_id(proy.id)
    seguimientos.append({
        'headline': 'Fecha de presentación',
        'startDate': convert_date_to_string(proy.fecha_presentacion),
    })

    proyecto = "Proyecto No: " + str(proy.numero_proyecto).replace("/", "_")
    data = []

    for i in seguimientos:
        data.append({
            'proyecto': proyecto,
            'headline': i['headline'],
            'startDate': i['startDate'].replace(',', '-'),
        })

    if request.method == 'GET':
        return CSVResponse(data)


def split_code_input(codigo):
    print(codigo)
    codigo = codigo.split("-")
    if len(codigo) > 1:
        legislatura = int(codigo[1])
    else:
        legislatura = LEGISLATURE
    codigo = codigo[0]
    return codigo, legislatura


