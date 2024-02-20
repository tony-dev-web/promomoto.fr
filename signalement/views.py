from signalement.forms import Signalement_Form
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.translation import gettext as _
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views import View


class SignalementView(View):

    def __init__(self, **kwargs):
        self.model = self.model
        super(SignalementView, self).__init__(**kwargs)

    def get(self, request, pk, status=None, *args, **kwargs):
        ui = get_object_or_404(self.model, pk=pk)

        c = {
            'bodyindex': 'signalement',
            'style_css': '/static/css/registrer.css',
            'title': _('Signalement'),
            'titleh1': _('Signalement'),
            'optim': _('Aidez-nous à nettoyer le contenu de Flypii'),
            'description': _('Signalement'),
            'Signalement': ui,
            'form': Signalement_Form(),
        }

        return HttpResponse(loader.get_template('error/signalement.html').render(cache.get('cF', c), request), content_type='text/html; charset=utf-8', status=status)

    def post(self, request, pk):
        f = Signalement_Form(request.POST or None)
        if not f.is_valid():
            return HttpResponseRedirect('/erreur/')
        fs = f.save()
        self.model.obj.filter(pk=pk).update(signalement="0")
        fs.client_signalement = request.user.id
        fs.save()
        return HttpResponseRedirect('/remerciement/')




class DeleteView(View):

    def __init__(self, **kwargs):
        self.model = self.model
        self.title = self.title
        super(DeleteView, self).__init__(**kwargs)

    def get(self, request,pk, status=None, *args, **kwargs):
        get_object_or_404(self.model, pk=pk, client=request.user.id )
        c = {
        'bodyindex': f'supresion',
        'style_css': '/static/css/registrer.css',
        'title': _(f'Supression de la demande {self.title}')}

        return HttpResponse(loader.get_template('error/delete.html').render(cache.get('cF', c), request), content_type='text/html; charset=utf-8', status=status)

    def post(self, request, pk, *args, **kwargs):
        get_object_or_404(self.model, pk=pk, client=request.user.id).delete()
        cache.clear()
        return HttpResponseRedirect("/supression/")
