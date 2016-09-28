from django.conf.urls import url

from . import views


urlpatterns = [
    # '',
    url(r'^proyecto.json/(?P<codigo>[0-9]+\-?[0-9]+)/$', views.proyecto),
    url(r'^proyecto.csv/(?P<codigo>[0-9]+\-?[0-9]+)/$', views.proyecto_csv),

    url(r'^congresista.json/(?P<nombre_corto>.+)/$', views.congresista),
    url(r'^congresista.csv/(?P<nombre_corto>.+)/$', views.congresista_csv),

    url(r'^congresista_y_comision.json/(?P<nombre_corto>.+)/(?P<comision>.+)/$', views.congresista_y_comision),
    url(r'^congresista_y_comision.csv/(?P<nombre_corto>.+)/(?P<comision>.+)/$', views.congresista_y_comision_csv),

    url(r'^exonerados_dictamen.json/$', views.exonerados_dictamen),
    url(r'^exonerados_dictamen.csv/$', views.exonerados_dictamen_csv),

    url(r'^exonerados_2da_votacion.json/$', views.exonerados_2da_votacion),
    url(r'^exonerados_2da_votacion.csv/$', views.exonerados_2da_votacion_csv),

    url(r'^seguimientos.json/(?P<codigo>[0-9]+\-?[0-9]+)/$', views.seguimientos_list),
    url(r'^seguimientos.csv/(?P<codigo>[0-9]+\-?[0-9]+)/$', views.seguimientos_list_csv),

    url(r'^iniciativas.json/(?P<codigo>[0-9a-z]+\-?[0-9]+)/$', views.iniciativa_list),
    url(r'^iniciativas.csv/(?P<codigo>[0-9a-z]+\-?[0-9]+)/$', views.iniciativa_list_csv),
]
