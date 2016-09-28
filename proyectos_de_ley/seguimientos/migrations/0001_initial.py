# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Iniciativas',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('nodes', models.TextField(blank=True)),
                ('links', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeguimientosJson',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('headline', models.TextField(blank=True)),
                ('codigo', models.TextField(blank=True)),
                ('date', models.TextField(blank=True)),
                ('type', models.TextField(blank=True)),
                ('text', models.TextField(blank=True)),
                ('timeline', models.TextField(blank=True)),
            ],
        ),
    ]
