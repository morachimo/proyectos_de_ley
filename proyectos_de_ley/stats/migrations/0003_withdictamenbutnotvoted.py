# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_dispensed'),
    ]

    operations = [
        migrations.CreateModel(
            name='WithDictamenButNotVoted',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('proyect_id', models.IntegerField(help_text='Project id as in table pdl_proyecto')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
