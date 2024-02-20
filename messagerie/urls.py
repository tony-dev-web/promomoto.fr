from outil.login_required import login_required
from django.urls import path
from messagerie import views
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path(_('compte/messagerie/'), login_required(views.messagerie.as_view()), name='messagerie'),
    path(_('compte/messagerie-reception-<str:slug>-<int:pk>'),
         login_required(views.messagerie_categorie_reception.as_view()), name='messagerie_categorie_reception'),
    path(_('compte/messagerie-envoie-<str:slug>-<int:pk>'), login_required(views.messagerie_categorie_envoie.as_view()),
         name='messagerie_categorie_envoie'),

   # path(_('signalement/contact-r-<int:client>'), views.contact_reception_signalement.as_view(),
    #     name="signalement_contact_envoie"),
   # path(_('signalement/contact-e-<int:client>'), views.contact_reception_signalement.as_view(),
   #      name="signalement_contact_reception"),

]