from django.urls import path
from contact import views
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path(_('coucou/'), views.contact_admin.as_view(), name='contact_admin'),
    path(_('rachat-moto/'), views.contact_rachat.as_view(), name='contact_rachat'),

]