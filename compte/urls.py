from outil.login_required import login_required
from django.urls import path, include
from compte import views
from django.utils.translation import gettext_lazy as _


urlpatterns = [
    path('compte/', login_required(views.compte.as_view()), name='compte'),
    path('compte/information/', login_required(views.information_motard.as_view()), name='info-motard'),
]
