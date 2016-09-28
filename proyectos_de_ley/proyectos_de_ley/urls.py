from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from django.contrib import admin

from pdl.feeds import LatestEntriesFeed
from pdl.sitemaps import ProyectoSitemap, CongresistaSitemap
from seguimientos import views as seg_views
from api.views import schema_view


sitemaps = {
    'static': ProyectoSitemap,
    'congresista': CongresistaSitemap,
}

urlpatterns = [
    # '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^docs/', schema_view),
    url(r'^stats/', include('stats.urls', namespace='stats')),
    url(r'^', include('pdl.urls', namespace='pdl')),
    url(r'^p/', include('pdl.urls', namespace='pdl-proyecto')),
    url(r'^p/(?P<short_url>[0-9a-z]+/seguimiento/)', seg_views.index),
    url(r'^rss.xml$', LatestEntriesFeed(), name='pdl-rss'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),

    url(r'^api/', include('api.urls')),

    url(r'^search-advanced/', include('search_advanced.urls')),
]
