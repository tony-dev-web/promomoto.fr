from outil.login_required import login_required
from django.urls import path, re_path
from motard import views


urlpatterns = [
    path("compte/motard/groups/", login_required(views.MotardGroupsView.as_view()), name="groups"),

]