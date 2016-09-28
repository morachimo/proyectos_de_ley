# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Expedientes',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('fecha', models.DateField(blank=True)),
                ('evento', models.TextField(blank=True)),
                ('pdf_url', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('codigo', models.CharField(max_length=20)),
                ('numero_proyecto', models.CharField(max_length=50)),
                ('short_url', models.CharField(max_length=20)),
                ('congresistas', models.TextField(blank=True)),
                ('fecha_presentacion', models.DateField()),
                ('titulo', models.TextField(blank=True)),
                ('expediente', models.URLField(blank=True)),
                ('pdf_url', models.URLField(blank=True)),
                ('seguimiento_page', models.URLField(blank=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_edited', models.DateTimeField(auto_now=True)),
                ('proponente', models.TextField(blank=True, null=True, default='')),
                ('grupo_parlamentario', models.TextField(blank=True, default='')),
                ('iniciativas_agrupadas', models.TextField(blank=True, null=True, default='')),
                ('nombre_comision', models.TextField(blank=True, null=True, default='')),
                ('titulo_de_ley', models.TextField(blank=True, null=True, default='')),
                ('numero_de_ley', models.TextField(blank=True, null=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Seguimientos',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('fecha', models.DateField(blank=True)),
                ('evento', models.TextField(blank=True)),
                ('proyecto', models.ForeignKey(to='pdl.Proyecto')),
            ],
        ),
        migrations.CreateModel(
            name='Slug',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=200)),
                ('ascii', models.CharField(max_length=200, help_text='nombre sin caracteres escpeciales')),
                ('slug', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='expedientes',
            name='proyecto',
            field=models.ForeignKey(to='pdl.Proyecto'),
        ),
    ]
