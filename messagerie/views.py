
from django.core.cache import cache

#from app.fusion.profil.models import UtilisateurModel
#from app.signalement.client_views import Signalement_client
#from contact.forms_messagerie import MessagerieForms
#from contact.ia_messagerie import Ia_messagerie
from django.http.response import HttpResponseRedirect

#from outil.django.httpresponse import HttpResponse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.cache import never_cache

from contact.models import ContactModel
from messagerie.forms import MessagerieForms
from messagerie.models import MessageModel
from django.utils.translation import gettext as _
from django.template import loader


class messagerie(View):
    extra_context = {}

    @never_cache
    def get(self, request, status=None):
        c = {
            'bodyindex': 'messagerie',
            'sta_css': '/static/css/messagerie.css',
            'title': _('Messagerie'),
            'description': _('Mesagerie'),
            "contact_client": ContactModel.obj.client_email(request),
            "contact_user": ContactModel.obj.client(request),
        }
        return HttpResponse(loader.get_template('messagerie/messagerie.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)






class messagerie_categorie_reception(View):

        @never_cache
        def get(self, request,pk, status=None):
            ui = get_object_or_404(ContactModel,  pk=pk )
            c = {
                'bodyindex': 'messagerie',
                'sta_css': '/static/css/messagerie.css',
                'title': _('Messagerie'),
                'description': _('Mesagerie'),
                "contact_client": ContactModel.obj.client_email(request),
                "contact_user": ContactModel.obj.client(request),

                #"MM": UtilisateurModel.obj.filter(client=ui.client_envoie)[:1],
                "NN": MessageModel.obj.filter( uid=pk),

                'form': MessagerieForms(),
                'mes': ui,}

            return HttpResponse(loader.get_template('messagerie/messagerie-reception.html').render(c, request),content_type='text/html; charset=utf-8', status=status)

        def post(self, request,pk, slug, *args, **kwargs):

            f = MessagerieForms(request.POST or None)

            if not f.is_valid():
                return HttpResponseRedirect('/erreur/')
            fs = f.save()
            fs.uid = pk
            #fs.categorie = slug

            fs.client = request.user.id

            text = fs.message
            #Ia_messagerie(request, fs, text)

            fs.save()
            cache.clear()
            return HttpResponseRedirect(request.build_absolute_uri())


class messagerie_categorie_envoie(View):

    @never_cache
    def get(self, request, slug, pk, status=None):
        ui = get_object_or_404(ContactModel, pk=pk)

        c = {
            'bodyindex': 'messagerie',
            'sta_css': '/static/css/messagerie.css',
            'title': _('Messagerie'),
            'description': _('Mesagerie'),
            "contact_client": ContactModel.obj.client_email(request),
            "contact_user": ContactModel.obj.client(request),
            #"MM": UtilisateurModel.obj.filter(client=ui.client)[:1],
            "NN": MessageModel.obj.filter( uid=pk),
            'form': MessagerieForms(),
            'mes': ui, }

        return HttpResponse(loader.get_template('messagerie/messagerie-envoie.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)

    def post(self, request, pk, slug, *args, **kwargs):
        f = MessagerieForms(request.POST or None)

        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')
        fs = f.save()
        fs.uid = pk
        #fs.categorie = slug
        fs.client_envoie = request.user.id
        text = fs.message
        #Ia_messagerie(request, fs, text)
        fs.save()
        cache.clear()
        return HttpResponseRedirect( request.build_absolute_uri() )

#class contact_reception_signalement(#Signalement_client):
    ##model = UtilisateurModel

#class contact_envoie_signalement(Signalement_client):
    #model = UtilisateurModel




