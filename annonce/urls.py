from outil.login_required import login_required
from django.urls import path
from annonce import views
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path(_('annonce-<int:client>/<str:slug>-<int:pk>'), views.annonce_frontend.as_view(), name='annonce_url'),
    path(_('compte/annonce/creation'), views.annonce_created.as_view(), name='creation_annonce'),
    path(_('compte/annonce/update-<int:pk>'), login_required( views.annonce_update.as_view()), name='update_annonce'),
    path(_('compte/annonce/supression-<int:pk>'), login_required( views.annonce_delete.as_view()), name='supression_annonce'),
    path(_('annonce/signalement-<int:pk>'), views.annonce_signalement.as_view(), name='signalement_annonce'),
]