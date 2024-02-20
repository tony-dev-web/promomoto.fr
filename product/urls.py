
from outil.login_required import login_required
from django.urls import path
from product import views

urlpatterns = [
    path('<str:slug>-<int:pk>', views.product_frontend.as_view(), name='product_url'),
    path('compte/produit/creation', login_required(views.product_created.as_view()), name="creation_product"),
    #path('compte/produit/update/<int:pk>', login_required(views.product_update.as_view()), name="update_product"),
    #path('compte/produit/supression-<int:pk>', login_required(views.product_delete.as_view()), name="supression_product"),

]