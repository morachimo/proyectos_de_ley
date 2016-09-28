# -*- encoding: utf-8 -*-
import datetime

from django.shortcuts import render
from django.db.models import Q

from .forms import SearchAdvancedForm
from pdl.models import Proyecto
from pdl.models import Seguimientos
from pdl.utils import do_pagination

LEGISLATURE = 2016

def index(request):
    if request.method == 'GET':
        form = SearchAdvancedForm(request.GET)
        if form.is_valid():
            keywords = clean_keywords_for_combined_search(form.cleaned_data)
            if keywords:
                return combined_search(keywords, form, request)

            # requests from stats view
            if form.cleaned_data['dictamen'] == 'NÚMERO TOTAL DE LEYES':
                return search_total_leyes(form, request)

            if form.cleaned_data['dictamen'] == 'Exonerados de dictamen':
                return search_exonerados_dictamen(form, request)

            if form.cleaned_data['dispensados_2da_votacion'] == 'TOTAL dispensados':
                return search_dispensados_todos(form, request)

            if form.cleaned_data['dispensados_2da_votacion'] == 'TOTAL aprobados':
                return search_total_aprobados(form, request)

            if form.cleaned_data['dispensados_2da_votacion'] == 'Dispensados por acuerdo del pleno':
                return search_dispensados_acuerdo_pleno(form, request)

            if form.cleaned_data['dispensados_2da_votacion'] == 'Dispensados por junta portavoces':
                return search_dispensados_junta_portavoces(form, request)

            if form.cleaned_data['dispensados_2da_votacion'] == 'Otros proyectos dispensados':
                return search_dispensados_otros(form, request)

            return render(request, "search_advanced/index.html", {
                "form": form,
            })
        else:
            return render(request, "search_advanced/index.html", {
                "form": form,
            })


def clean_keywords_for_combined_search(cleaned_data):
    keywords = {}
    for k, v in cleaned_data.items():
        if v != '' and v is not None:
            if v in ['---', '--Escoger bancada--']:
                continue
            if k in ['dispensados_2da_votacion', 'dictamen']:
                continue
            keywords[k] = v
    return keywords


def combined_search(keywords, form, request):
    queryset1 = Proyecto.objects.filter(legislatura=LEGISLATURE).order_by('-codigo')
    queryset2 = Proyecto.objects.all().order_by('-codigo').exclude(legislatura=LEGISLATURE)
    comision, congresista, grupo_parlamentario, msg, query, queryset2 = filter_queryset(
        keywords,
        request,
        queryset2,
    )
    comision, congresista, grupo_parlamentario, msg, query, queryset1 = filter_queryset(
        keywords,
        request,
        queryset1,
    )
    date_from, date_to = convert_to_iso_dates(keywords)

    if queryset1 or queryset2:
        if queryset2:
            items_previous_legislatures = ",".join([i.codigo for i in queryset2])
        else:
            items_previous_legislatures = ""
        obj = do_pagination(request, queryset1, search=True, advanced_search=True)
        return render(request, "search_advanced/index.html", {
            "query": query,
            "comision": comision,
            "congresista": congresista,
            "grupo_parlamentario": grupo_parlamentario,
            "items_previous_legislatures": items_previous_legislatures,
            "date_from": date_from,
            "date_to": date_to,
            "result_count": len(queryset1),
            "extra_result_msg": msg,
            "items": obj['items'],
            "pretty_items": obj['pretty_items'],
            "first_half": obj['first_half'],
            "second_half": obj['second_half'],
            "first_page": obj['first_page'],
            "last_page": obj['last_page'],
            "current": obj['current'],
            "form": form,
        })
    else:
        return render(request, "search_advanced/index.html", {
            "form": form,
            "info_msg": 'No se encontraron resultados para esa combinación de términos de búsqueda',
        })


def filter_queryset(keywords, request, queryset):
    msg = ""
    if 'query' in keywords:
        query = keywords['query']
        msg = "Número de proyectos encontrados"
        queryset = queryset.filter(titulo__icontains=keywords['query'])
        print(len(queryset), queryset)
    else:
        query = ""
    if 'date_to' in keywords and 'date_from' in keywords:
        msg = "Número de proyectos entre fecha indicada"
        queryset = queryset.filter(fecha_presentacion__range=(
        keywords['date_from'], keywords['date_to']))
    if 'congresista' in keywords:
        msg = "Número de proyectos de congresista {}".format(
            keywords['congresista'])
        queryset = queryset.filter(
            congresistas__icontains=keywords['congresista'])
    try:
        congresista = request.GET['congresista']
    except KeyError:
        congresista = ""
    if 'grupo_parlamentario' in keywords:
        msg = "Número de proyectos de bancada {}".format(
            keywords['grupo_parlamentario'])
        queryset = queryset.filter(
            grupo_parlamentario=keywords['grupo_parlamentario'])
        grupo_parlamentario = keywords['grupo_parlamentario']
    else:
        grupo_parlamentario = ""
    if 'comision' in keywords:
        comision = keywords['comision']
        msg = "Número de proyectos de comisión {}".format(keywords['comision'])
        queryset = filter_by_comision(keywords, queryset)
    else:
        comision = ""
    return comision, congresista, grupo_parlamentario, msg, query, queryset


def convert_to_iso_dates(keywords):
    try:
        date_from = datetime.datetime.strftime(keywords['date_from'], '%m/%d/%Y')
    except KeyError:
        date_from = ""

    try:
        date_to = datetime.datetime.strftime(keywords['date_to'], '%m/%d/%Y')
    except KeyError:
        date_to = ""

    return date_from, date_to


def filter_by_comision(keywords, queryset):
    commission = keywords['comision']
    return queryset.filter(projectsincommissions__commission=commission)


def search_dispensados_todos(form, request):
    total_dispensed = [
        i.proyecto
        for i in Seguimientos.objects.select_related('proyecto').filter(
            evento__icontains='dispensado 2da',
        ).filter(
            proyecto__legislatura=LEGISLATURE,
        )
    ]

    obj = do_pagination(request, total_dispensed, search=True, advanced_search=True)
    return render(request, "search_advanced/index.html", {
        "result_count": len(total_dispensed),
        "extra_result_msg": "Total número de proyectos dispensados de 2da votación",
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "form": form,
        "comision": obj['comision'],
    })


def search_total_leyes(form, request):
    are_law = Proyecto.objects.exclude(
        titulo_de_ley__isnull=True,
    ).exclude(
        titulo_de_ley__exact='',
    ).filter(
        legislatura=LEGISLATURE,
    )

    obj = do_pagination(request, are_law, search=True, advanced_search=True)
    return render(request, "search_advanced/index.html", {
        "result_count": len(are_law),
        "extra_result_msg": "Total número de proyectos que han generado leyes",
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "form": form,
        "comision": obj['comision'],
    })


def search_exonerados_dictamen(form, request):
    exonerado_de_dictamen = [
        i.proyecto
        for i in Seguimientos.objects.select_related('proyecto').filter(
            evento__icontains='exoneración de dictamen',
        ).filter(
            proyecto__legislatura=LEGISLATURE,
        ).distinct()
    ]
    exonerado_de_dictamen = list(set(exonerado_de_dictamen))

    obj = do_pagination(request, exonerado_de_dictamen, search=True, advanced_search=True)
    return render(request, "search_advanced/index.html", {
        "result_count": len(exonerado_de_dictamen),
        "extra_result_msg": "Proyectos Exonerados de dictamen",
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "form": form,
        "comision": obj['comision'],
    })


def search_total_aprobados(form, request):
    total_approved = [
        i.proyecto
        for i in Seguimientos.objects.select_related('proyecto').filter(
            Q(evento__icontains='promulgado') | Q(evento__icontains='publicado'),
        ).filter(
            proyecto__legislatura=LEGISLATURE,
        )
    ]
    total_approved = list(set(total_approved))

    obj = do_pagination(request, total_approved, search=True, advanced_search=True)
    return render(request, "search_advanced/index.html", {
        "result_count": len(total_approved),
        "extra_result_msg": "Total número de proyectos aprobados",
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "form": form,
        "comision": obj['comision'],
    })


def search_dispensados_acuerdo_pleno(form, request):
    dispensed_by_plenary = [
        i.proyecto
        for i in Seguimientos.objects.select_related('proyecto').filter(
            evento__icontains='dispensado 2da',
        ).filter(
            evento__icontains='pleno',
        ).filter(
            proyecto__legislatura=LEGISLATURE,
        )
    ]

    obj = do_pagination(request, dispensed_by_plenary, search=True, advanced_search=True)
    return render(request, "search_advanced/index.html", {
        "result_count": len(dispensed_by_plenary),
        "extra_result_msg": "Dispensados 2da votación por acuerdo del pleno",
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "form": form,
        "comision": obj['comision'],
    })


def search_dispensados_junta_portavoces(form, request):
    dispensed_by_spokesmen = [
        i.proyecto
        for i in Seguimientos.objects.select_related('proyecto').filter(
            evento__icontains='dispensado 2da',
        ).filter(
            evento__icontains='portavoces',
        )
    ]

    obj = do_pagination(request, dispensed_by_spokesmen, search=True, advanced_search=True)
    return render(request, "search_advanced/index.html", {
        "result_count": len(dispensed_by_spokesmen),
        "extra_result_msg": "Dispensados 2da votación por junta de portavoces",
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "form": form,
        "comision": obj['comision'],
    })


def search_dispensados_otros(form, request):
    otros_dispensados = [
        i.proyecto
        for i in Seguimientos.objects.select_related('proyecto').filter(
            evento__icontains='dispensado 2da',
        ).exclude(
            evento__icontains='pleno',
        ).exclude(
            evento__icontains='portavoces',
        )
    ]

    obj = do_pagination(request, otros_dispensados, search=True, advanced_search=True)
    return render(request, "search_advanced/index.html", {
        "result_count": len(otros_dispensados),
        "extra_result_msg": "Dispensados 2da votación por otras razones",
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "form": form,
        "comision": obj['comision'],
    })
