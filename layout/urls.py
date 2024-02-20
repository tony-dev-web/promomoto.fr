from django.urls import path
from layout import views
from django.utils.translation import gettext_lazy as _
urlpatterns = [
    path(_(''),  views.index.as_view(), name='index'),
    path(_('mentions-legales/'), views.mentions.as_view(), name='mentions'),
    path(_('concept-moto-innovation/'), views.concept.as_view(), name='concept'),
    path('search_s/', views.autocompletesearch),


    path('manifest.json', views.annexe.manifest),
    path('opensearch.xml', views.annexe.opensearch_xml),

    path('interdiction-email/', views.interdiction_email.as_view(), name='interdiction_email'),
    path('stop/', views.stop.as_view(), name='stop'),
    path('remerciement/', views.remerciement.as_view(), name='remerciement'),
    path('supression/', views.supression.as_view(), name='supression'),
    path('erreur/', views.erreur.as_view(), name='erreur'),
    path("compte/redirection/", views.login_groups.as_view(), name="login_groups"),

]