from django.db.models import F
from django.shortcuts import get_object_or_404
from django.template import loader
from django.http.response import HttpResponse
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext as _
from django.core.cache import cache
from panier.forms import Panier_CreatedForm
from product.forms import Product_CreatedForm
from product.models import ProductModel
from vehicule.models import VehiculeModel


class product_frontend(View):

    def get(self, request, pk: int, slug, status=None, *args, **kwargs):

        ui = get_object_or_404( ProductModel, pk=pk, slug=slug)
        ProductModel.obj.filter(pk=pk).values('vues', 'pk').update(vues=F('vues') + 1, )

        c = {
             'robots':'index, follow',
             'style_css': '/static/css/frontend.css',
             'bodyindex': f'frontend-product',
             'title': f'{ui.title[:60]}',
             'description': f'{ui.description[:242]} - {ui.vues} {_("Vues")}',

             'BB': VehiculeModel.obj.filter(id=ui.vp_id),
             'x': ui,
             'form': Panier_CreatedForm(), }

        return HttpResponse(loader.get_template('product/template_product.html').render(cache.get('cF', c), request),
                            content_type='text/html; charset=utf-8', status=status)


    def post(self, request, *args, **kwargs):
        f = Panier_CreatedForm(request.POST or None)
        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')

        fs = f.save()
        fs.session = request.session.session_key

        #ui = ProductModel.obj.filter(pk=id)
        #fs.product = ui.pk
        fs.save()
        return HttpResponseRedirect('/panier/')


class CreatedView(View):

    def __init__(self, **kwargs):

        self.title = self.title
        self.include_name = self.include_name
        self.form_class = self.form_class
        super(CreatedView, self).__init__(**kwargs)

    def get(self, request, status=None):
        c = { 'bodyindex': f'created-product',
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
        #Ia_nlp_form(request, fs)
        ui = get_object_or_404(VehiculeModel, id=fs.vp_id)
        fs.annee = ui.annee
        fs.modele = ui.modele
        fs.marque = ui.marque
        fs.title = f'{fs.title} {ui.modele} {ui.marque} {ui.annee}'
        fs.description = f'{fs.title} {fs.description} {fs.etat}'

        fs.save()
        cache.clear()
        return HttpResponseRedirect('/compte/produit/creation')


class product_created(CreatedView):
    include_name = 'product/forms.html'
    title = 'produit'
    form_class = Product_CreatedForm


from signalement.views import DeleteView
class product_delete(DeleteView):
    model = ProductModel
    title = 'produit'
