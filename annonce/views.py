from django.shortcuts import get_object_or_404
from annonce.forms import Annonce_CreatedForm
from annonce.inteligent import Ia
from annonce.models import AnnonceModel
from django.db.models import F
from contact.forms import ContactForm
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.views import View
#from contact.ia_messagerie import Ia_messagerie
from django.http.response import HttpResponseRedirect
from datetime import date, timedelta
from django.http.response import HttpResponse
from django.core.cache import cache
from django.template import loader
from django.utils.translation import gettext as _
from django.core.mail import send_mass_mail


class annonce_frontend(View):

    def get(self, request, pk: int, client: int, slug, status=None, *args, **kwargs):

        ui = get_object_or_404( AnnonceModel, client=client, pk=pk, slug=slug)
        AnnonceModel.obj.filter(pk=pk).values('vues', 'pk').update(vues=F('vues') + 1, )
        c = {
             'style_css': '/static/css/frontend.css',
             'bodyindex': f'frontend-annonce',
             'title': f'{ui.title[:60]}',
             'description': f'{ui.description[:242]} - {ui.vues} {_("Vues")}',
             'x': ui,
             #'utilisateurs': UtilisateurModel.obj.client(client),
             'form': ContactForm()}

        return HttpResponse(loader.get_template('annonce/template_annonce.html').render(cache.get('cF', c), request),
                            content_type='text/html; charset=utf-8', status=status)

    def post(self, request,client, *args, **kwargs):

        if client == request.user.id :
           return HttpResponseRedirect('/interdiction-email/')

        f = ContactForm(request.POST or None)
        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')

        fs = f.save()

        text = f'{fs.nom_contact} {fs.objet_contact} {fs.message_contact}'
        #Ia_messagerie(request, fs, text)

        fs.client = client
        fs.client_envoie = request.user.id
        fs.langue = translation.get_language()
        fs.email = request.user.email

        u1 = f.cleaned_data['objet_contact']
        u2 = f.cleaned_data['message_contact']
        u3a = f.cleaned_data['email_contact']
        u3b = fs.email

        m1 = (_('Confirmation d envoi de votre mail via Promomoto.fr'), u2, 'contact@promomoto.fr', [u3a])
        m2 = (u1, u2, 'contact@promomoto.fr', [u3b])

        send_mass_mail((m1, m2), fail_silently=False)

        fs.save()
        #return HttpResponseRedirect(fs.url_update_envoie)
        return HttpResponseRedirect('/remerciement/')



class CreatedView(View):

    def __init__(self, **kwargs):
        self.title = self.title
        self.include_name = self.include_name
        self.form_class = self.form_class
        super(CreatedView, self).__init__(**kwargs)

    def get(self, request, status=None):
        c = { 'bodyindex': f'created-{self.title}',
            'style_css': '/static/css/forms.css',
            'title': _(f'Formulaire pour {self.title}'),
            'description': _(f'Formulaire pour {self.title}'),
            'include_name': self.include_name,
            'form': self.form_class(),
        }
        return HttpResponse(loader.get_template('layout/created-forms.html').render(cache.get('cF', c), request), content_type='text/html; charset=utf-8', status=status)

    def post(self, request, *args, **kwargs):

        f = self.form_class(request.POST, request.FILES)

        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')

        fs = f.save()
        fs.client = request.user.id
        Ia(request, fs)
        fs.date_update = (date.today() + timedelta(5))
        fs.save()
        cache.clear()
        return HttpResponseRedirect(fs.url_update)

class annonce_created(CreatedView):
    include_name = 'annonce/forms.html'
    title = 'annonce'
    form_class = Annonce_CreatedForm

class AnnonceUpdate(View):

    def __init__(self, **kwargs):
        self.model = self.model
        self.title = self.title
        self.include_name = self.include_name
        self.form_class = self.form_class
        self.template = self.template

        super(AnnonceUpdate, self).__init__(**kwargs)


    def get(self, request, pk, *args, **kwargs):
        ui = get_object_or_404(self.model, pk=pk, client=request.user.id)

        c = {'extends_name': 'element/element-update-solution.html',
             'include_name': self.include_name,
             'style_css': self.css,
             'bodyindex': f'update-{self.title}',
             'title': f'Mise à jour {_(self.title)}',
             'x': ui,
             'form': self.form_class(instance=ui)}

        return HttpResponse(loader.get_template(self.template).render(cache.get('cF', c), request),
                            content_type='text/html; charset=utf-8')


    def post(self, request,pk, *args, **kwargs):
        ui = get_object_or_404(self.model, pk=pk, client=request.user.id)
        f = self.form_class(request.POST or None, request.FILES or None, instance=ui)

        #if not GroupsWeb.obj.filter(client=request.user.id).exists() or UtilisateurModel.obj.filter(client=request.user.id, doudou__lte=0).exists() :
           # return HttpResponseRedirect('/stop/')

        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')
        fs = f.save()
        #Ia_nlp_form(request, fs)
        fs.date_update = (date.today() + timedelta(10))
        fs.save()
        cache.clear()
        return HttpResponseRedirect(fs.url_update)

class annonce_update(AnnonceUpdate):
    form_class = Annonce_CreatedForm
    template = 'annonce/update.html'
    include_name = 'annonce/forms.html'
    css = '/static/css/frontend.css'
    model = AnnonceModel
    title = 'annonce'

from signalement.views import SignalementView, DeleteView
class annonce_delete(DeleteView):
    model = AnnonceModel
    title = 'annonce'

class annonce_signalement(SignalementView):
    model = AnnonceModel