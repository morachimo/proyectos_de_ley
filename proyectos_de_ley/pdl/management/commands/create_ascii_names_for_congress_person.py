"""
This command populates the database for Proyecto models which will include the
ascii form for names of Congress men and women.

Run once a week.
"""
from django.core.management.base import BaseCommand

from pdl.models import Proyecto
from pdl.management.commands.create_congress_person_slugs import convert_to_ascii


class Command(BaseCommand):
    help = 'Creates ascii form for names of congress men and women names'

    def handle(self, *args, **options):
        projects_to_process = Proyecto.objects.filter(
            congresistas_ascii="",
        ).exclude(
            congresistas="",
        )
        for p in projects_to_process:
            ascii_name = convert_to_ascii(
                p.congresistas,
            )
            p.congresistas_ascii = ascii_name
            p.save()
