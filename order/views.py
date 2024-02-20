from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from order.forms import Order_CreatedForm
from order.models import OrderModel
from panier.models import PanierModel
from product.models import ProductModel
from django.views.decorators.cache import never_cache
from django.http.response import HttpResponse, HttpResponseRedirect

from django.utils.translation import gettext as _
from django.template import loader
from django.core.cache import cache

#payplug.set_secret_key('sk_test_6yh5D5zkTDBDlkT2OTDt7Y')


class order(View):
    @never_cache
    def get(self, request, status=None):
        global bb, aa, items_g
        result = PanierModel.obj.filter(session=request.session.session_key).values_list('pr_id', flat=True)
        items_a = ProductModel.obj.filter(id__in=result)
        items_c = ProductModel.obj.filter(id__in=result).values('id').count()
        items_b = ProductModel.obj.filter(id__in=result).values_list('prix', flat=True).aggregate(Sum('prix'))['prix__sum']
        items_e = float(items_b)-99.90
        PanierModel.obj.filter(session=request.session.session_key).update(payment='Attente_Panier')
        if items_e < 99.90:
                aa = '8 €'
                bb = items_b + 8
        elif items_e > 99.90:
                aa = 'Gratuite'
                bb = items_b

        c = {
            'menu': '',
            'AA': items_a,
            'total': bb,
            'quantite':items_c ,
            'livraison': aa,
            'bodyindex': 'home-order',
            'style_css': '/static/css/order.css',
            'title': _('Commande'),
            'description': _('Commande'),
            'form': Order_CreatedForm()
        }

        return HttpResponse(loader.get_template('order/order.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)


    def post(self, request, *args, **kwargs):
        f = Order_CreatedForm(request.POST or None )

        if not f.is_valid():
            OrderModel.obj.filter(session=request.session.session_key).update(payment='Erreur_commande')
            return HttpResponseRedirect(reverse('paiement_refus'))

        result = PanierModel.obj.filter(session=request.session.session_key).values_list('pr_id', flat=True)
        items_a = ProductModel.obj.filter(id__in=result)
        items_c = ProductModel.obj.filter(id__in=result).values('id').count()
        items_b = ProductModel.obj.filter(id__in=result).values_list('prix', flat=True).aggregate(Sum('prix'))['prix__sum']


        fs = f.save()
        fs.client = request.user.id
        fs.payment = 'En attente'
        fs.products = [items_a]
        fs.total = items_c
        fs.stock = items_b
        fs.save()
        OrderModel.obj.filter(session=request.session.session_key).update(payment='Attente_commande')

        cache.clear()
        return HttpResponseRedirect(reverse('paiement_valide'))




class order_add(View):
    @never_cache
    def get(self, request,pk, status=None):
        global bb, aa
        ui = get_object_or_404(ProductModel, pk=pk)

        result = PanierModel.obj.filter(session=request.session.session_key).values_list('pr_id', flat=True)
        items_a = ProductModel.obj.filter(id__in=result)
        items_c = ProductModel.obj.filter(id__in=result).values('id').count()
        items_b = ProductModel.obj.filter(id__in=result).values_list('prix', flat=True).aggregate(Sum('prix'))['prix__sum']

        items_e = float(items_b) - 99.90
        if items_e < 99.90:
            aa = '8 €'
            bb = items_b + 8
        elif items_e > 99.90:
            aa = 'Gratuite'
            bb = items_b


        c = {
            'menu':'',
            'AA': items_a,
            'total': bb,
            'quantite':items_c ,
            'livraison': aa,
            'bodyindex': 'home-order-add',
            'style_css': '/static/css/order.css',
            'title': _('Commande direct'),
            'form': Order_CreatedForm(),
            'x': ui
        }

        return HttpResponse(loader.get_template('order/order.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)

    def post(self, request,pk, *args, **kwargs):
        ui = get_object_or_404(ProductModel, pk=pk)

        items_a = ProductModel.obj.filter(id=ui.pk)
        items_b = ProductModel.obj.filter(id=ui.pk).values_list('prix', flat=True).aggregate(Sum('prix'))['prix__sum']
        items_c = ProductModel.obj.filter(id=ui.pk).values('id').count()

        f = Order_CreatedForm(request.POST or None )
        if not f.is_valid():
            OrderModel.obj.filter(session=request.session.session_key).update(payment='Erreur_commande')
            return HttpResponseRedirect(reverse('paiement_refus'))

        fs = f.save()
        fs.client = request.user.id
        fs.products = items_a
        fs.total = items_b
        fs.stock = items_c
        fs.save()
        OrderModel.obj.filter(session=request.session.session_key).update(payment='Attente_commande')
        cache.clear()
        return redirect(reverse('paiement_valide'))


class list_order(View):
    @never_cache
    def get(self, request, status=None):
        aa = OrderModel.obj.filter(client=request.user.id)
        c = {
            'AA': aa ,
            'bodyindex': 'home-list-order',
            'style_css': '/static/css/panier.css',
            'title': _('Liste des commandes'),
        }

        return HttpResponse(loader.get_template('order/list-order.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)


class paiement_validaion(View):
    @never_cache
    def get(self, request, status=None):

        OrderModel.obj.filter(session=request.session.session_key).update(payment='validation')
        PanierModel.obj.filter(session=request.session.session_key).update(payment='validation')


        result = PanierModel.obj.filter(session=request.session.session_key).values_list('pr_id', flat=True)
        ProductModel.obj.filter(id__in=result).update(stock=0)
        c = {
            'bodyindex': 'paiemant-error',
            'style_css': '/static/css/panier.css',
            'title': _('Liste des commandes'),
        }

        return HttpResponse(loader.get_template('order/paiement-confirmation.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)

class paiement_error(View):
    @never_cache
    def get(self, request, status=None):
        c = {
            'bodyindex': 'paiemant-error',
            'style_css': '/static/css/panier.css',
            'title': _('Paiement refusé'),
        }

        return HttpResponse(loader.get_template('order/paiement-error.html').render(c, request),
                            content_type='text/html; charset=utf-8', status=status)







