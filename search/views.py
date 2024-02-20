from datetime import date, timedelta
from django.views.generic.base import View
from django.utils.translation import gettext as _
from itertools import chain

from annonce.models import AnnonceModel
from product.models import ProductModel
from vehicule.models import VehiculeModel
from django.core.cache import cache
from django.http.response import HttpResponse
from django.template import loader


class Recherche_template(View):


    def get(self, request, ):

        aa = sorted(chain(VehiculeModel.obj.filter(),ProductModel.obj.filter()), key=lambda instance: instance.date_add, reverse=True)[:4]

        s = self.request.GET.get('s')
        t = self.request.GET.get('t')

        bb = sorted(chain(AnnonceModel.obj.search(s, t),ProductModel.obj.search(s,t),VehiculeModel.obj.search(s,t)), key=lambda instance: instance.date_add, reverse=True)[:100]

        bbb = (AnnonceModel.obj.search(s ,t).count() + ProductModel.obj.search(s,t).count() + VehiculeModel.obj.search(s,t).count())
        bbbb = (AnnonceModel.obj.count() + VehiculeModel.obj.count() + ProductModel.obj.count())

        c = {
             'AA' : aa,
             'BB' : bb,
             'BB_count_search': bbb,
             'BB_count': bbbb,
             'retour_date' : (date.today() + timedelta(14)),
             'style_css': '/static/css/frontend.css',
             'bodyindex': 'home-recherche',
             'title': f'{ _("Recherche") } {self.request.GET.get("s")}'}

        return HttpResponse(loader.get_template('layout/search.html').render(cache.get('cF', c), request),content_type='text/html; charset=utf-8')