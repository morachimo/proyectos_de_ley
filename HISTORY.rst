History
=======

v2.2.0 (2016-09-07)
~~~~~~~~~~~~~~~~~~~
* agregada capacidad de soportar proyectos de Legislatura 2011 y 2016.
* agregada interface administrador en Django.
* mostrar proyectos de actual legislatura y menor prominencia a proyectos de
  legislaturas pasadas.
* actualización de spiders.
* actualización de dependencias: Django, rest_framework, rest_framework_swagger.
* actualización de layout de docs en API.
* bug fixed: número de proyectos aprovados en front-page
* bug fixed: búsqueda de proyecto "209" resultará en búsqueda de proyecto 00209-2016.
* bug fixed: ya no se muestra código 404 en el API.
* bug fixed: logo de Hiperderecho está hosteado en nuestro server.
* bug fixed: lista de proyectos de legislatura pasada ya no genera error 500.
* bug fixed: modificación de modelos para casos en que congresistas tengan nombres
  con y sin tildes. Cualquier variación mostrará proyectos de cada congresista.

v2.1.1 (2015-10-29)
~~~~~~~~~~~~~~~~~~~
* script para hacer backups de base de datos
* Stats. Agregado "sin votación en el pleno" para velocímetro "proyectos con
  dictamen pero sin votación". Además agregué explicación para ese número.
* Búsqueda avanzada por comisiones dan el mismo número de proyectos que los que
  aparecen en el cuadro de estadísticas.
* Arreglado bug en paginación de búsqueda avanzada. Gracias a @skraelings.

v2.1.0 (2015-07-16)
~~~~~~~~~~~~~~~~~~~
* Footer: ahora aparece en posición inferior en todas las páginas.
* Stats: "proyectos con dictamen pero sin votación"
* Stats: reemplazados los 2 primeros velocímetros.
* Stats: ahora muestra exonerados de dictamen.
* Stats: corregidos números de proyetos exonerados de 2da votación.
* Stats: corregido número de proyectos que aún no son ley.
* Búsqueda avanzada: permite buscar combinación de campos como: fechas, palabra
  clave, comisión, nombre de congresista y grupo parlamentario.
* Corregido: bug cuando query contenía espacios en blanco el navegador entraba
  en loop infinito.
* Corregido: número de proyectos que no son ley (considerando que en las leyes
  promulgadas hay numerosos proyectos que han sido fusionados).
* API: tenemos API que emite datos en formato abierto en JSON y CSV.
  Ver http://proyectosdeley.pe/docs/
* API: documentación automática.
* API: nuevo ícono para acceder a la documentación en la barra de navegación.
* Corregido schema de la base de datos.
* Nueva columna `ascii` en tabla Slug.

v2.0.1 (2015-03-31)
~~~~~~~~~~~~~~~~~~~
* Fixed with of stats counter.
* Better search engine. Now query words will match accented and unaccented words.
* Stats: "en comisión sin dictamen"
* Stats: "sin tramitar"

v2.0.0 (2015-03-30)
~~~~~~~~~~~~~~~~~~~
* Using haystack and elasticsearch.
* Indexing ascii and accented chars for search fields by overriding
  the ``prepare_text`` function in Haystack.
* Stats: chart "by commission" has links on the bars. Click them to see projects
  stuck in each commission'
* Advanced search: now we can search projects by comission.
* Update stats.

v1.7.0 (2015-02-04)
~~~~~~~~~~~~~~~~~~~
* Humanized dates using ``arrow``.
* Added *legislatura*.

v1.6.0 (2015-01-31)
~~~~~~~~~~~~~~~~~~~
* Fixed bug that showed number of authors + 1 in `seguimientos`.
* Updated about page.
* Timeline starts at end.
* Pull proyectosdeley logo from morachimo domain.
* Show stats in frontpage.
* Fix title of stats page.
* Added counter for number of authors of project in frontpage and project page.

v1.5.3 (2014-12-28)
~~~~~~~~~~~~~~~~~~~
Stats: fixing bug for "otros proyectos dispensados".

v1.5.2 (2014-12-24)
~~~~~~~~~~~~~~~~~~~
Adding respeto.pe logo, new proyectosdeley log and update "About" page.

v1.5.1 (2014-12-16)
~~~~~~~~~~~~~~~~~~~
Fixing create_stats custom command. The update_or_create
command was creating an extra set of items in the database instead of doing
an update. Fixed.

v1.5.0 (2014-12-11)
~~~~~~~~~~~~~~~~~~~
* Only accept as search keywords strings with len > 2.
* Sort simple search result by codigo desc.
* Fix bug on pagination links.
* Keywords were shown with brackets.
* Search box of simple search show user's query.
* Added links to PDF and Expediente in Seguimientos page.
* Added custom command in `stats` app: `create_stats` which should run once a day.
* Added charts to stats page: Number of projects in comisiones and Number of projects that
  did not go to 2nd round of votes. New table expedients to keep events and
  URLs from the `Expediente` page.

v1.4.1 (2014-11-11)
~~~~~~~~~~~~~~~~~~~
* Improved general search engine, also events in `seguimientos` are queried.
* Autofocus on search box when page loads.
* Better highlighting of keywords.
* Check errors in datefield widget (advanced search).
* Show error fields in datefield widget.
* Resize advanced search according to screen sizes.
* Add link to production site.

v1.4.0 (2014-11-08)
~~~~~~~~~~~~~~~~~~~
* Advanced search by *fecha presentación*.
* Stats.
* Improved RSS feed.
* Now we have our own `Seguimiento` page.
* Many more additional fields are scrapped (*seguimientos*, *iniciativas agrupadas*).
* Better scrapping of PDF urls.
* The scrapping functions have been moved to another project: `proyectos_de_ley_scraper`.
* Added version to footer of pages.

v1.2.0 (2014-09-24)
~~~~~~~~~~~~~~~~~~~
* Scrapping more metadata from seguimiento_page.
* Killed bug to get PDF url when the filename includes funny characters.
* Custom command to update `seguimiento` events for each project in our database.

v1.1.1 (2014-09-22)
~~~~~~~~~~~~~~~~~~~
* Favicon.
* Don't show navigation bar if there are no results.

v1.1.0 (2014-09-21)
~~~~~~~~~~~~~~~~~~~
Pagination for search results (40 items per page).

v1.0.1 (2014-09-20)
~~~~~~~~~~~~~~~~~~~
Own pagination for index and congresista pages.

v1.0.0 (2014-09-15)
~~~~~~~~~~~~~~~~~~~
Migrated to Django.
