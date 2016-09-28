# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pdl', '0001_initial'),
        ('stats', '0003_withdictamenbutnotvoted'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectsInCommissions',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('commission', models.TextField()),
                ('project', models.ForeignKey(to='pdl.Proyecto')),
            ],
        ),
    ]
