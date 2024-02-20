from outil.login_required import login_required
from django.urls import path

from order import views

urlpatterns = [
    path('commande-<int:pk>/', login_required(views.order_add.as_view()), name='order_add'),
    path('commande/', login_required(views.order.as_view()), name='order'),
    path('compte/liste-commande/', login_required(views.list_order.as_view()), name='list_order'),

    path('compte/paiement/validation/', login_required(views.paiement_validaion.as_view()), name='paiement_valide'),
    path('compte/paiement/refuse/', login_required(views.paiement_error.as_view()), name='paiement_refus'),

]