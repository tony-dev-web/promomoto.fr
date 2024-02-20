from django.views import View
from annonce.models import AnnonceModel
from motard.models import MotardModel
from publication.forms import Publication_CreatedForm
from publication.models import PublicationModel
from vehicule.models import VehiculeModel
from product.models import ProductModel
from django.views.decorators.cache import never_cache

from compte.account.models import EmailAddress
from django.http.response import HttpResponse, HttpResponseRedirect

from django.utils.translation import gettext as _
from django.template import loader
from django.core.cache import cache

class compte(View):
    @never_cache
    def get(self, request, status=None):

        c = {'AA': AnnonceModel.obj.compte(request),
            'BB': PublicationModel.obj.compte(request)[:10],
             'CC': MotardModel.obj.compte(request),
            'bodyindex': 'home-compte',
            'style_css': '/static/css/compte.css',
            'title': _('Mon compte'),
            'description': _('Mon compte'),
            #"verif": EmailAddress.objects.filter(user=request.user, verified=True).values('user', 'verified'),
            'form': Publication_CreatedForm(),
        }

        return HttpResponse(loader.get_template('page/compte.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)



    def post(self, request, *args, **kwargs):
        f = Publication_CreatedForm(request.POST, request.FILES)

        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')

        fs = f.save()
        fs.client = request.user.id
        # Ia_nlp_form(request, fs)
        fs.save()
        cache.clear()
        return HttpResponseRedirect('/compte/')

class information_motard(View):

    @never_cache
    def get(self, request, status=None):

        aa = MotardModel.obj.filter(client=request.user.id)

        c = {
            'AA': aa ,
            'bodyindex': 'home-list-information',
            'style_css': '/static/css/panier.css',
            'title': _('Liste des informations'),
        }

        return HttpResponse(loader.get_template('page/information-motard.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)