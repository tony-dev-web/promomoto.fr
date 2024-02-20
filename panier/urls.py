from outil.login_required import login_required
from django.urls import path
from panier import views
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path(_('panier/'), views.panier.as_view(), name='panier'),
    path('panier-<str:session>/supression', views.panier_delete.as_view(), name="supression_panier"),
]