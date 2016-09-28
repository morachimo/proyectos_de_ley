|Build Status| |Cover alls| |Gemnasium|


Proyectos de Ley del Congreso
=============================

`http://proyectosdeley.pe` es un intento de transparentar el Congreso y poner
al alcance de la mayor cantidad de personas los proyectos de ley presentados y
discutidos en el parlamento. La información mostrada es tomada directamente de
la página web del Congreso.

Esta página ha sido desarrollada en forma independiente por la ONG Hiperderecho
y la asociación Contribuyentes por Respeto, organizaciones sin fines de lucro
dedicadas a investigar, facilitar el entendimiento público y promover
el respeto de los derechos y libertades en entornos digitales.

`http://proyectosdeley.pe`

Configuración
-------------

Esta aplicación se basa en el siguiente *software*:

* Python v3.4
* django v1.8.4
* PostgreSQL
* elasticsearch

Crear y un activar un virtualenv_ que use Python3. En un terminal, instalar 
las dependencias para desarrollo local::

    $ pip install -r requirements/dev.txt

.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Para correr el software, reemplazar ``yourapp`` con el nombre
del folder que contiene el proyecto de Django::

    $ python yourapp/manage.py runserver --settings=yourapp.settings.local

Recasting DateField as DateTimeField::

    alter table pdl_proyecto alter column fecha_presentacion TYPE timestamp using fecha_presentacion::timestamp;

Obteniendo información
----------------------
Toda la info se obtiene desde las páginas web del Congreso mediante el uso de
un *scraper* basado en el *framework* Scrapy. El *scraper* se encuentra en
este repositorio_.

.. _repositorio: https://github.com/proyectosdeley/proyectos_de_ley_scraper

Custom commands
---------------

Para generar una tabla resúmen del número de proyectos que ha quedado estancado
en cada comisión del Congreso::

    > python manage.py create_stats --settings=proyectos_de_ley.settings.local

Plantilla HTML
--------------
* El archivo ``base.html`` funciona como plantilla para crear las páginas HTML.
  Cualquier cambio al estilo se debe realizar en este archivo. Esta plantilla
  usa un estilo basado en Twitter Bootstrap con *responsive features* para que
  se vea bien en computadoras y dispositivos móbiles.
* Esos campos se usan para introducir en contenido en la plantilla y generar
  los archivos HTML.

.. |Build Status| image:: https://travis-ci.org/proyectosdeley/proyectos_de_ley.svg?branch=master
   :target: https://travis-ci.org/proyectosdeley/proyectos_de_ley
.. |Cover alls| image:: https://coveralls.io/repos/proyectosdeley/proyectos_de_ley/badge.png
   :target: https://coveralls.io/r/proyectosdeley/proyectos_de_ley
.. |Gemnasium| image:: https://gemnasium.com/proyectosdeley/proyectos_de_ley.svg
   :target: https://gemnasium.com/proyectosdeley/proyectos_de_ley

