from django.shortcuts import render
from django.db.models import Sum

from pdl.models import Proyecto
from pdl.models import Seguimientos
from stats.models import ComisionCount
from stats.models import Dispensed
from stats.models import WithDictamenButNotVoted


LEGISLATURE = 2016

def dame_sin_tramitar(numero_de_proyectos):
    print(numero_de_proyectos, "dame sin tramitar")
    with_seguimientos = Seguimientos.objects.filter(
        proyecto__legislatura=LEGISLATURE,
    ).values_list('proyecto_id', flat=True).distinct().count()
    without_seguimientos = numero_de_proyectos - with_seguimientos
    percentage_without_seguimientos = round(
        (without_seguimientos * 100) / numero_de_proyectos, 1)
    return percentage_without_seguimientos, without_seguimientos


def dame_sin_dictamen(queryset, numero_de_proyectos):
    # thanks to @eyscode
    count = queryset.aggregate(Sum('count'))['count__sum']
    if count:
        percentage = round((count * 100) / numero_de_proyectos, 1)
    else:
        percentage = 0
    return percentage, count


def index(request):
    numero_de_proyectos = Proyecto.objects.filter(
        legislatura=LEGISLATURE,
    ).count()

    with_pdf_url = Proyecto.objects.filter(
        legislatura=LEGISLATURE,
    ).exclude(
        pdf_url__isnull=True).exclude(
        pdf_url__exact='').count()
    without_pdf_url = numero_de_proyectos - with_pdf_url
    percentage_without_pdf_url = round(
        (without_pdf_url * 100) / numero_de_proyectos, 1)

    # con dictamen y sin votación en el pleno
    total_dictamen_sin_votacion = WithDictamenButNotVoted.objects.count()
    percentage_dictamen_sin_votacion = round(
        (total_dictamen_sin_votacion * 100) / numero_de_proyectos, 1
    )

    # Sin Tramitar
    percentage_without_seguimientos, without_seguimientos = dame_sin_tramitar(
        numero_de_proyectos)

    # Proyectos no son ley
    are_not_law, percentage_are_not_law, laws = get_projects_that_arent_law(numero_de_proyectos)

    # Projects by comision count
    total = 0
    comision_names = ""
    comision_count = ""
    queryset = ComisionCount.objects.all().order_by('-count')
    for i in queryset:
        comision_names += "{}', '".format(i.comision)
        total += i.count
        comision_count += "{}, ".format(i.count)
    comision_names_str = "['# Total en comisiones', '{}']".format(comision_names)
    comision_count_str = "[{0}, {1}]".format(total, comision_count)

    # sin dictamen?
    percentage_total_in_commissions, total_in_commissions = dame_sin_dictamen(queryset, numero_de_proyectos)

    # Projects dispensed of 2nd round of votes
    res = Dispensed.objects.all()[0]
    dispensed_values = "[" + str(res.total_approved) + ", " \
                       + str(res.total_dispensed) + ", " \
                       + str(res.dispensed_by_plenary) + ", " \
                       + str(res.dispensed_by_spokesmen) + ", " \
                       + str(res.dispensed_others) + "]"
    dispensed_categories = "['TOTAL aprobados', 'TOTAL dispensados', " \
                           "'Dispensados por acuerdo del pleno', " \
                           "'Dispensados por junta portavoces', " \
                           "'Otros proyectos dispensados']"

    exonerado_de_dictamen = Seguimientos.objects.filter(
        evento__icontains='exoneración de dictamen').values_list('proyecto_id', flat=True).distinct().count()
    dictamen_values = "[" + str(len(laws)) + ", " + str(exonerado_de_dictamen) + "]"
    dictamen_categories = "['NÚMERO TOTAL DE LEYES', 'Exonerados de dictamen']"

    return render(request, "stats/index.html",
                  {'percentage_without_seguimientos': percentage_without_seguimientos,
                   'percentage_total_in_commissions': percentage_total_in_commissions,
                   'total_in_commissions': total_in_commissions,

                   'total_dictamen_sin_votacion': total_dictamen_sin_votacion,
                   'percentage_dictamen_sin_votacion': percentage_dictamen_sin_votacion,

                   'numero_de_proyectos': numero_de_proyectos,
                   'without_pdf_url': without_pdf_url,
                   'percentage_without_pdf_url': percentage_without_pdf_url,
                   'without_seguimientos': without_seguimientos,
                   'are_not_law': are_not_law,
                   'percentage_are_not_law': percentage_are_not_law,
                   'comision_names': comision_names_str,
                   'comision_count': comision_count_str,
                   'dispensed_values': dispensed_values,
                   'dispensed_categories': dispensed_categories,

                   'dictamen_values': dictamen_values,
                   'dictamen_categories': dictamen_categories,
                   }
                  )


def get_projects_that_arent_law(numero_de_proyectos):
    laws = set()
    are_law = Proyecto.objects.filter(
        legislatura=LEGISLATURE
    ).exclude(
        titulo_de_ley__isnull=True).exclude(
        titulo_de_ley__exact='')
    print("are_law", len(are_law), [(i.codigo, i.titulo_de_ley) for i in are_law])

    for i in are_law:
        laws.add(i.titulo_de_ley)

    are_not_law = Proyecto.objects.filter(
        legislatura=LEGISLATURE,
        titulo_de_ley='',
    ).count() + Proyecto.objects.filter(
        legislatura=LEGISLATURE,
        titulo_de_ley__isnull=True,
    ).count()
    percentage_are_not_law = round(
        (are_not_law * 100) / numero_de_proyectos, 1)
    return are_not_law, percentage_are_not_law, laws
