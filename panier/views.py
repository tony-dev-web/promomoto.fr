from __future__ import unicode_literals
import array
import decimal
import json
from datetime import timedelta, date
from decimal import Decimal
from functools import cached_property
from itertools import chain

from django.conf import settings
from django.db.models import Value
from django.core.cache import cache
from django.db.models import Sum, Avg, F
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
from django.views.generic.base import View
from panier.models import PanierModel
from product.models import ProductModel
from django.utils.translation import gettext as _
from django import template

class panier(View):

    def get(self, request, *args, **kwargs):

        global bb, aa, items_g
        result = PanierModel.obj.filter(session=request.session.session_key).values_list('pr_id', flat=True)
        items_a = ProductModel.obj.filter(id__in=result)
        items_c = ProductModel.obj.filter(id__in=result).values('id').count()


        if items_c == 0:
            aa = '0'
            bb = '0'
            items_g = f'Plus que <span class="c2">99 €</span> pour benéficier de la livraison offerte'
            items_b = '0'
        else:

            items_b = ProductModel.obj.filter(id__in=result).values_list('prix', flat=True).aggregate(Sum('prix'))['prix__sum']
            items_e = float(items_b)-99.90
            if items_e < 99.90:
                aa = '8 €'
                bb = items_b + 8
                items_g = f'Plus que Frais <span class="c2">{float(items_e)} €</span> pur benéficier de la livraison offerte'
            elif items_e > 99.90:
                aa = 'Gratuite'
                bb = items_b
                items_g = f'Vous bénéficier de livraison offerte'

        c = { 'AA': items_a,
            'livraison_date': (date.today() + timedelta(4)),
            'retour_date': (date.today() + timedelta(14)),
            'article': items_c ,
            'total_art': items_b,
            'total': bb,
            'livr_1': aa ,
            'livr_2': items_g,
            'style_css': '/static/css/panier.css',
            'bodyindex': 'home-panier' ,
            'title': 'panier',
            'description': 'panier'}

        return HttpResponse(loader.get_template('page/panier.html').render(cache.get('cF', c), request), content_type='text/html; charset=utf-8')


class panier_delete(View):

    def get(self, request, status=None, *args, **kwargs):
        get_object_or_404(PanierModel, session=request.session.session_key )
        c = {
        'bodyindex': f'supresion',
        'style_css': '/static/css/registrer.css',
        'title': _(f'Supression du panier')}
        return HttpResponse(loader.get_template('error/delete.html').render(cache.get('cF', c), request), content_type='text/html; charset=utf-8', status=status)

    def post(self, request, pk, *args, **kwargs):
        get_object_or_404(PanierModel, session=request.session.session_key).delete()
        cache.clear()
        return HttpResponseRedirect("/supression/")



