from django.urls import path
from outil.login_required import login_required
from search import views

urlpatterns = [
    path('recherche/', views.Recherche_template.as_view(), name='recherche'),


]