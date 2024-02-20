from django.db.models import F
from django.shortcuts import get_object_or_404
from django.template import loader
from django.http.response import HttpResponse
from django.views.generic.base import View

from product.models import ProductModel
from vehicule.forms import Vehicule_CreatedForm
from vehicule.models import VehiculeModel
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext as _
from django.core.cache import cache



class vehicule_frontend(View):

    def get(self, request, pk: int, slug, status=None, *args, **kwargs):
        ui = get_object_or_404(VehiculeModel, pk=pk, slug=slug)

        VehiculeModel.obj.filter(pk=pk).values('vues', 'pk').update(vues=F('vues') + 1, )

        c = {
             'robots':'index, follow',
             'style_css': '/static/css/frontend.css',
             'bodyindex': f'frontend-vehicule',
             'BB' : ProductModel.obj.filter(vp_id=ui.id),

             'title': f'{ui.title[:60]}',
             'description': f'{ui.description[:242]} - {ui.vues} {_("Vues")}',
             'x': ui,


              }

        return HttpResponse(loader.get_template('vehicule/template_vehicule.html').render(cache.get('cF', c), request),
                            content_type='text/html; charset=utf-8', status=status)


class CreatedView(View):

    def __init__(self, **kwargs):
        self.title = self.title
        self.include_name = self.include_name
        self.form_class = self.form_class
        super(CreatedView, self).__init__(**kwargs)

    def get(self, request, status=None):
        c = { 'bodyindex': f'created-vehicule',
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
        #Ia_nlp_form(request, fs)

        fs.title = f'{fs.modele} {fs.marque} {fs.annee}'
        fs.save()
        cache.clear()
        return HttpResponseRedirect(fs.url_frontend)



class vehicule_created(CreatedView):
    include_name = 'vehicule/forms.html'
    title = 'vehicule'
    form_class = Vehicule_CreatedForm


from signalement.views import DeleteView
class vehicule_delete(DeleteView):
    model = VehiculeModel
    title = 'vehicule'
