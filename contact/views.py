
from django.utils import translation
from django.views import View
from django.template import loader
from django.core.cache import cache
from contact.forms import ContactForm, ContactAdminForm, ContactRachatForm
#from contact.ia_messagerie import Ia_messagerie
from django.http.response import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext as _
from django.core.mail import send_mass_mail


class contact_admin(View):

    def get(self, request, status=None):
        c = {'style_css': '/static/css/registrer.css',
             'bodyindex': 'contact-admin',
             'title': _('Formulaire pour nous contactez'),
             'form': ContactAdminForm() }
        return HttpResponse(loader.get_template('page/contact_admin.html').render(cache.get('cF', c), request), content_type='text/html; charset=utf-8', status=status)

    def post(self, request, *args, **kwargs):
        f = ContactAdminForm(request.POST or None )
        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')
        fs = f.save()
        fs.save()
        cache.clear()
        return HttpResponseRedirect('/remerciement/')

class contact_rachat(View):

    def get(self, request, status=None):
        c = {'style_css': '/static/css/registrer.css',
             'bodyindex': 'contact-rachat',
             'title': _('Formulaire de rachat'),
             'form': ContactRachatForm() }
        return HttpResponse(loader.get_template('page/contact_rachat.html').render(cache.get('cF', c), request), content_type='text/html; charset=utf-8', status=status)

    def post(self, request, *args, **kwargs):
        f = ContactRachatForm(request.POST or None )
        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')
        fs = f.save()
        fs.save()
        cache.clear()
        return HttpResponseRedirect('/remerciement/')
