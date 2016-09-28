from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from pdl.models import Proyecto


class ProyectoAdmin(ImportExportActionModelAdmin):
    list_display = [
        'legislatura',
        'numero_proyecto',
        'codigo',
        'titulo',
        'congresistas',
    ]


admin.site.register(Proyecto, ProyectoAdmin)
