"""
This command queries the pdl_seguimientos table to calculate some statictics
for `/stats` page. These stat values go to tables for this app.

* projects that are being accumulated in each `comisión`.
* projects that were aproved without 2nd round of votes.
"""
import re

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

from pdl.models import Proyecto
from pdl.models import Seguimientos
from stats.models import ComisionCount
from stats.models import Dispensed
from stats.models import WithDictamenButNotVoted
from stats.models import ProjectsInCommissions


LEGISLATURE = 2016

class Command(BaseCommand):
    help = 'Parses the table `pdl_seguimientos` and creates a summary table ' \
           'containing `En Comision` events for each proyecto, only if this ' \
           'is the last event for them.'

    def handle(self, *args, **options):
        self.get_projects_in_commissions()

        # Get projects that did not go to 2da round of votes
        self.get_dispensed_projects()

        # Proyectos con dictamen pero sin votación
        self.get_with_dictamen_but_not_voted()

        # Para calcular estadisticas de proyectos que aun no son ley
        self.update_iniciativas_agrupadas_with_title_of_law()

    def get_projects_in_commissions(self):
        queryset = Seguimientos.objects.filter(
            proyecto__legislatura=LEGISLATURE,
        ).order_by('proyecto_id', '-fecha')
        commissions_count = {}
        projects_in_commissions = []
        this_project_id = ''
        for seguimiento in queryset:
            if seguimiento.proyecto_id != this_project_id:
                commission = test_if_event_is_in_commission(seguimiento)
                if commission is not False and commission not in commissions_count:
                    commissions_count[commission] = 0

                if commission is not False:
                    commissions_count[commission] += 1
                    project_and_commission = ProjectsInCommissions(
                        project=seguimiento.proyecto,
                        commission=commission,
                    )
                    projects_in_commissions.append(project_and_commission)
            this_project_id = seguimiento.proyecto_id
        ProjectsInCommissions.objects.all().delete()
        ProjectsInCommissions.objects.bulk_create(projects_in_commissions)

        ComisionCount.objects.all().delete()
        for k, v in commissions_count.items():
            ComisionCount.objects.update_or_create(
                comision=k, defaults={'count': v},
            )

    def get_dispensed_projects(self):
        total_approved = set()

        tmp = Seguimientos.objects.filter(
            evento__icontains='promulgado',
            proyecto__legislatura=LEGISLATURE,
        )
        for i in tmp:
            total_approved.add(i.proyecto_id)

        tmp = Seguimientos.objects.filter(
            evento__icontains='publicado',
            proyecto__legislatura=LEGISLATURE,
        )
        for i in tmp:
            total_approved.add(i.proyecto_id)

        total_dispensed = Seguimientos.objects.filter(
            evento__icontains='dispensado 2da',
            proyecto__legislatura=LEGISLATURE,
        ).count()
        dispensed_by_plenary = Seguimientos.objects.filter(
            evento__icontains='dispensado 2da',
            proyecto__legislatura=LEGISLATURE,
        ).filter(evento__icontains='pleno').count()
        dispensed_by_spokesmen = Seguimientos.objects.filter(
            evento__icontains='dispensado 2da',
            proyecto__legislatura=LEGISLATURE,
        ).filter(evento__icontains='portavoces').count()
        dispensed_others = total_dispensed - dispensed_by_plenary - dispensed_by_spokesmen

        Dispensed.objects.update_or_create(
            id=1, defaults={
                'total_approved': len(total_approved),
                'total_dispensed': total_dispensed,
                'dispensed_by_plenary': dispensed_by_plenary,
                'dispensed_by_spokesmen': dispensed_by_spokesmen,
                'dispensed_others': dispensed_others,
            }
        )

    def get_with_dictamen_but_not_voted(self):
        """
        Proyectos con dictamen pero no votac
        Crea tabla con lista de: proyectos que no figure
          "publicado" || promulgado || votación || en lista de seguimientos,
        pero tenga "dictamen".
        """
        queryset = Seguimientos.objects.filter(
            proyecto__legislatura=LEGISLATURE,
        ).order_by('proyecto_id').values('proyecto_id', 'evento')
        proyect_ids = self.get_proyect_ids(queryset)

        if not settings.TESTING:
            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE stats_withdictamenbutnotvoted RESTART IDENTITY")

        projects = []
        for proyecto_id in proyect_ids:
            if self.has_dictamen(proyecto_id, queryset) is True and \
                    self.is_voted(proyecto_id, queryset) is False:
                projects.append(WithDictamenButNotVoted(proyect_id=proyecto_id))
        WithDictamenButNotVoted.objects.bulk_create(projects)

    def update_iniciativas_agrupadas_with_title_of_law(self):
        projects_with_law = Proyecto.objects.filter(
            legislatura=LEGISLATURE,
        ).exclude(
            titulo_de_ley='').exclude(
            titulo_de_ley__isnull=True).values('codigo', 'titulo_de_ley', 'iniciativas_agrupadas')

        iniciativas_deben_tener_ley = self.get_iniciativas_con_ley(projects_with_law)

        for iniciativa in iniciativas_deben_tener_ley.items():
            for i in iniciativa[1]['iniciativas']:
                if i not in iniciativas_deben_tener_ley.keys():
                    try:
                        p = Proyecto.objects.get(codigo=i, legislatura=LEGISLATURE)
                    except Proyecto.DoesNotExist:
                        continue
                    if p.titulo_de_ley == '':
                        p.titulo_de_ley = iniciativa[1]['titulo_de_ley']
                        p.save()

    def get_iniciativas_con_ley(self, projects_with_law):
        iniciativas_con_ley = {}
        for i in projects_with_law:
            iniciativas = i['iniciativas_agrupadas']
            if iniciativas != '' and iniciativas is not None:
                iniciativas = iniciativas.replace('{', '')
                iniciativas = iniciativas.replace('}', '')
                iniciativas = iniciativas.split(',')

                if i['codigo'] not in iniciativas_con_ley:
                    iniciativas_con_ley[i['codigo']] = {
                        'iniciativas': [],
                        'titulo_de_ley': '',
                    }

                iniciativas_con_ley[i['codigo']]['iniciativas'] += iniciativas
                iniciativas_con_ley[i['codigo']]['titulo_de_ley'] = i['titulo_de_ley']

        return iniciativas_con_ley

    def get_proyect_ids(self, queryset):
        proyect_ids = set()
        for i in queryset:
            proyect_ids.add(i['proyecto_id'])
        return proyect_ids

    def is_voted(self, proyect_id, queryset):
        events = self.get_events(proyect_id, queryset)
        for i in events:
            if 'publicado' in i.lower() or 'promulgado' in i.lower() or 'votación' in i.lower():
                return True
        return False

    def has_dictamen(self, proyect_id, queryset):
        events = self.get_events(proyect_id, queryset)
        for i in events:
            if 'dictamen' in i.lower():
                return True
        return False

    def get_events(self, proyect_id, queryset):
        events = []
        for i in queryset:
            if i['proyecto_id'] == proyect_id:
                events.append(i['evento'])
        return events


def test_if_event_is_in_commission(seguimiento):
    """
    We need to check whether the event in the model Seguimientos is one
    that tells us that the project is in certain Commission.
    :param Seguimiento object:
    :return: If true then return commission short name, else False
    """
    res = re.match("(en\s+comisión(\s\w+)+)", seguimiento.evento, re.I)
    if res:
        full_commission_name = re.sub(r"(?i)En\s+comisión\s+(de\s+)*", "", res.groups()[0])
        this_commission = re.sub("\s+y\s+.+", "", full_commission_name)
        return this_commission
    return False
