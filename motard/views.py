from django.views import View
from django.template import loader
from django.core.cache import cache
from django.http.response import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext as _

from motard.forms import MotardGroupsForm


class MotardGroupsView(View):

    def get(self, request, status=None):
        c = {'style_css': '/static/css/registrer.css',
             'bodyindex': 'groups',
             'title': _('Groupe utilisateur'),
             'form': MotardGroupsForm() }
        return HttpResponse(loader.get_template('page/groups.html').render(cache.get('cF', c), request), content_type='text/html; charset=utf-8', status=status)

    def post(self, request, *args, **kwargs):
        f = MotardGroupsForm(request.POST or None )
        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')
        fs = f.save()
        fs.client = request.user.id
        fs.save()
        cache.clear()
        return HttpResponseRedirect('/compte/')