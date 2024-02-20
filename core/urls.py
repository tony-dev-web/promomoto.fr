
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap

from core.sitemaps import IndexSitemap,ProductSitemap,VehiculeSitemap

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('lalala/', admin.site.urls),
    path('sitemaps.xml', sitemap, {'sitemaps': { 'static': IndexSitemap, 'product':ProductSitemap, 'vehicule':VehiculeSitemap }}, name="sitemap_static"),

]


urlpatterns += i18n_patterns(
    path('', include('layout.urls')),
    path('', include('search.urls')),
    path('', include('compte.urls')),
    path('', include('annonce.urls')),
    path('', include('compte.account.urls')),
    path('', include('contact.urls')),
    path('', include('messagerie.urls')),
    path('', include('order.urls')),
    path('', include('publication.urls')),
    path('', include('panier.urls')),
    path('', include('messagerie.urls')),
    path('', include('motard.urls')),
    path('', include('vehicule.urls')),
    path('', include('product.urls')),
    prefix_default_language=False,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)