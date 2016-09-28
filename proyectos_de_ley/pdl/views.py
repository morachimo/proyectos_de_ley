# -*- encoding: utf-8 -*-
import ast
import re
import copy

from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from .utils import prettify_item
from .utils import do_pagination
from .utils import find_slug_in_db
from pdl.models import Proyecto
from pdl.forms import SimpleSearchForm
from stats.models import Dispensed

LEGISLATURE = 2016

def index(request):
    all_items = Proyecto.objects.filter(legislatura=LEGISLATURE).order_by('-codigo')
    obj = do_pagination(request, all_items)

    # sin fusionar
    numero_de_proyectos = len(all_items)
    with_iniciativas = Proyecto.objects.filter(legislatura=LEGISLATURE).exclude(
        iniciativas_agrupadas__isnull=True).exclude(
        iniciativas_agrupadas__exact='').count()
    without_iniciativas = numero_de_proyectos - with_iniciativas

    # no son ley
    projects_empty_title = Proyecto.objects.filter(
        titulo_de_ley='',
        legislatura=LEGISLATURE,
    ).count()
    projects_null_title = Proyecto.objects.filter(
        titulo_de_ley__isnull=True,
        legislatura=LEGISLATURE,
    ).count()
    are_not_law = projects_empty_title + projects_null_title

    # total aprobados o sea total proyectos que generaron leyes
    aprobados = len(all_items) - are_not_law

    return render(request, "pdl/index.html", {
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        # stats
        "total": numero_de_proyectos,
        "sin_fusionar": without_iniciativas,
        "no_son_ley": are_not_law,
        "aprobados": aprobados,
    })


def proyecto(request, short_url):
    try:
        item = Proyecto.objects.get(short_url=short_url)
        num_proy = item.numero_proyecto
        item = prettify_item(item)
        return render(request, "pdl/proyecto.html", {'item': item, 'num_proy':
                                                     num_proy,
                                                     }
                      )
    except Proyecto.DoesNotExist:
        msg = [
            "No se pudo encontrar el proyecto.",
            "Quizá ingresó URL incorrecto."
        ]
        return render(request, "pdl/proyecto.html", {"msg": msg})


def about(request):
    return render(request, "pdl/about.html")


def listado(request):
    try:
        keywords = ast.literal_eval(
            request.GET.get('keywords', ''),
        )
    except ValueError:
        keywords = request.GET.get('keywords', '')

    if isinstance(keywords, list):
        query = " ".join(keywords)
    else:
        query = " ".join([keywords])
    project_codes = request.GET.get('list', '').split(",")
    all_items = Proyecto.objects.filter(
        codigo__in=project_codes,
    ).exclude(legislatura=LEGISLATURE)  # exclude projects in current legislature
    obj = do_pagination(request, all_items, search=True, advanced_search=True)

    return render(request, "pdl/listado.html", {
        "result_count": len(all_items),
        "items": obj['items'],
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "keywords": keywords,
        "query": query,
        "pagination_keyword": query,
    })


@csrf_exempt
def search(request):
    if 'q' not in request.GET:
        return redirect('/')
    else:
        query = request.GET['q']
        if query.strip() == '':
            return redirect('/')
        else:
            query = fix_query(request)

    form = SimpleSearchForm(query)
    all_items = form.search()
    items_current_legislature = set()
    items_previous_legislatures = set()
    for i in all_items:
        if i.legislatura == str(LEGISLATURE):
            items_current_legislature.add(i)
        else:
            if len(items_previous_legislatures) < 400:
                items_previous_legislatures.add(i.codigo)
    obj = do_pagination(request, list(items_current_legislature), search=True)

    keywords = clean_my_query(query['q'])

    return render(request, "pdl/search.html", {
        "result_count": len(items_current_legislature),
        "items": obj['items'],
        "items_previous_legislatures": ",".join(items_previous_legislatures),
        "pretty_items": obj['pretty_items'],
        "first_half": obj['first_half'],
        "second_half": obj['second_half'],
        "first_page": obj['first_page'],
        "last_page": obj['last_page'],
        "current": obj['current'],
        "keywords": keywords,
        "query": query['q'],
        "pagination_keyword": query['q'],
    })


def fix_query(request):
    r = copy.copy(request.GET)
    query_parts = []
    for i in r['q'].split(" "):
        try:
            number = int(i)
        except ValueError:
            query_parts.append(i)
            continue

        if number and len(i) < 5:
            padded_number = i.zfill(5)
            query_parts.append(padded_number)
        else:
            query_parts.append(i)
    r['q'] = " ".join(query_parts)
    return r


def clean_my_query(query):
    keywords = re.sub('\s+', ' ', query)
    keywords = re.sub('\s+$', '', keywords)
    keywords = re.sub('^\s+', '', keywords)
    keywords = keywords.split(' ')
    return keywords


def congresista(request, congresista_slug):
    if congresista_slug.strip() == '':
        return redirect('/')

    congresista_ascii = find_slug_in_db(congresista_slug)
    if congresista_ascii:
        all_items = Proyecto.objects.filter(
            congresistas_ascii__contains=congresista_ascii,
        ).filter(
            legislatura=LEGISLATURE,
        ).order_by('-codigo')
        obj = do_pagination(request, all_items)
        return render(request, "pdl/congresista.html", {
            "items": obj['items'],
            "pretty_items": obj['pretty_items'],
            "first_half": obj['first_half'],
            "second_half": obj['second_half'],
            "first_page": obj['first_page'],
            "last_page": obj['last_page'],
            "current": obj['current'],
            "congresista": congresista_ascii,
            "slug": congresista_slug.replace("/", ""),
        })
    else:
        msg = [
            "No se pudo encontrar el congresista.",
            "Quizá el nombre está incorrecto."
        ]
        return render(request, "pdl/congresista.html", {"msg": msg})
