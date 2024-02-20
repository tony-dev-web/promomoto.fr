from outil.login_required import login_required
from django.urls import path
from vehicule import views

urlpatterns = [
    path('<str:slug>-moto-<int:pk>', views.vehicule_frontend.as_view(), name='vehicule_url'),
    path('compte/vehicule/creation', login_required(views.vehicule_created.as_view()), name="creation_vehicule"),
    #path('compte/vehicule/update/<int:pk>', login_required(views.vehicule_update.as_view()), name="update_vehicule"),
    path('compte/vehicule/supression-<int:pk>', login_required(views.vehicule_delete.as_view()), name="supression_vehicule"),

]