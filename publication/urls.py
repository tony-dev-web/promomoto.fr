from outil.login_required import login_required
from django.urls import path
from publication import views
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path(_('compte/publication-<int:pk>/supression'), login_required( views.publication_delete.as_view()), name='supression_publication'),
    path(_('compte/publication/signalement-<int:pk>'), views.publication_signalement.as_view(), name='signalement_publication'),
]