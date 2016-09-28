from django.db import models

from pdl.models import Proyecto


class ComisionCount(models.Model):
    count = models.IntegerField()
    comision = models.CharField(max_length=250)


class ProjectsInCommissions(models.Model):
    project = models.ForeignKey(Proyecto)
    commission = models.TextField()


class Dispensed(models.Model):
    """
    Statistics about total number of approved projects, dispensed by 2nd round
    of votes, etc.
    """
    total_approved = models.IntegerField(
        help_text="Number of projects approved in any instance.",
    )

    total_dispensed = models.IntegerField(
        help_text="Number of projects that did not go to 2nd round of votes.",
    )

    dispensed_by_plenary = models.IntegerField(
        help_text="Those projects dispensed due to `acuerdo del pleno`.",
    )

    dispensed_by_spokesmen = models.IntegerField(
        help_text="Those projects dispensed due to `junta de portavoces`.",
    )

    dispensed_others = models.IntegerField(
        help_text="All other projects dispensed, and those with no specific reason.",
    )


class WithDictamenButNotVoted(models.Model):
    proyect_id = models.IntegerField(
        help_text="Project id as in table pdl_proyecto",
    )
