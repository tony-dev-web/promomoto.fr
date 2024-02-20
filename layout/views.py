from itertools import chain
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.utils.translation import gettext as _
from annonce.models import AnnonceModel
from product.models import ProductModel
from vehicule.models import VehiculeModel


class PageView(View):

    def __init__(self, **kwargs):
        self.title = self.title
        self.description = self.description
        self.template_name = self.template_name
        super(PageView, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        c = {'style_css': '/static/css/frontend.css',
             'bodyindex': 'home-{}'.format(self.title) ,
             'robots': 'index, follow',
             'title': _(self.title),
             'description': _(self.description) }
        return HttpResponse(loader.get_template(self.template_name).render(cache.get('cF', c), request), content_type='text/html; charset=utf-8')

def autocompletesearch(request):
    import json
    qs = request.GET.get('term','')
    aa = sorted(chain(AnnonceModel.obj.autocomplete(qs), VehiculeModel.obj.autocomplete(qs), ProductModel.obj.autocomplete(qs)), key=lambda instance: instance.id, reverse=True)
    return HttpResponse(json.dumps([s.title for s in aa ]), 'application/json')


class index(View):

    def get(self, request, *args, **kwargs):
        c = {
        'count_produit':ProductModel.obj.count() ,
        'count_annonce':AnnonceModel.obj.count(),
        'count_motard': User.objects.count(),
        'AA': sorted(chain(AnnonceModel.obj.filter(),ProductModel.obj.filter()), key=lambda instance: instance.date_add, reverse=True)[:5]}

        return HttpResponse(loader.get_template('layout/index.html').render(cache.get('cF', c), request),content_type='text/html; charset=utf-8')


class mentions(PageView):
    template_name = 'page/mentions.html'
    title = _('Mentions légales')
    description = _('Découvrez les mentions légales de Promomoto spécialiser dans la distribution de pièces et accessoires moto')


class concept(PageView):
    template_name = 'page/concept.html'
    title = _('Concept de notre nouvelle plateforme')
    description = _('Déposer des annonces moto gratuites grâce a notre nouveau concept pour le secteur du deux roues, de plus retrouvez notre site e-commerce d\'occasion')


from django.utils.translation import gettext as _
from django.core.cache import cache


class Annexe(View):

    def __init__(self, **kwargs):
        self.title = self.title
        self.template = self.template
        super(Annexe, self).__init__(**kwargs)

    def get(self, request, status=None, *args, **kwargs):
        c = {
             'style_css': '/static/css/error.css',
             'bodyindex': self.title,
             'title': _(self.title)}

        return HttpResponse(loader.get_template(self.template).render(cache.get('cF', c), request), content_type='text/html; charset=utf-8', status=status)



from django.http.response import HttpResponse
from django.template import loader



class annexe():

    def error404(request):
        return HttpResponse(loader.render_to_string('error/404.html', request), content_type='text/html; charset=utf-8',
                            status=404)

    def opensearch_xml(request):
        return HttpResponse(loader.get_template('opensearch.xml').render({}, request), content_type='text/xml',
                            status=200)

    def error500(request):
        return HttpResponse(loader.render_to_string('error/500.html', request), content_type='text/html; charset=utf-8',
                            status=500)

    def error403(request):
        return HttpResponse(loader.render_to_string('error/403.html', request), content_type='text/html; charset=utf-8',
                            status=403)

    def error400(request):
        return HttpResponse(loader.render_to_string('error/400.html', request), content_type='text/html; charset=utf-8',
                            status=403)

    def manifest(request):
        return HttpResponse(loader.get_template('manifest.json').render({}, request), content_type='application/json',
                            status=200)

    def offline(request):
        return HttpResponse(loader.get_template("offline.html").render({}, request),
                            content_type='text/html; charset=utf-8', status=200)


class erreur(Annexe):
    template = 'error/erreur.html'
    title = 'erreur'

class stop(Annexe):
    template = 'error/stop.html'
    title = 'stop'

class interdiction_email(Annexe):
    template = 'error/interdiction-email.html'
    title = 'interdiction-email'

class supression(Annexe):
    template = 'error/supression.html'
    title = 'supression'

class remerciement(Annexe):
    template = 'error/validation.html'
    title = 'remerciement'

class login_groups(Annexe):
    template = 'error/login-groups.html'
    title = 'Redirection'

