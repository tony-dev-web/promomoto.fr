import importlib
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.http import base36_to_int, urlencode
from django.utils.translation import gettext as _

from django.http import (Http404,HttpResponsePermanentRedirect,HttpResponseRedirect,)
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from django.db import models


from django.views.generic import FormView
from django.views.generic.base import TemplateResponseMixin, View, TemplateView

from . import signals
from compte.account.forms import (LoginForm,ResetPasswordForm,ResetPasswordKeyForm,SignupForm,UserTokenForm)
from compte.account.models import EmailConfirmation, EmailConfirmationHMAC
from compte.account.utils import perform_login


sensitive_post_parameters_m = method_decorator(sensitive_post_parameters("oldpassword", "password", "password1", "password2"))
####
def passthrough_next_redirect_url(request, url, redirect_field_name):
    assert url.find("?") < 0  # TODO: Handle this case properly
    if get_request_param(request, redirect_field_name):
        url = url + "?" + urlencode({redirect_field_name: get_request_param(request, redirect_field_name)})
    return url

def get_form_class(forms, form_id, default_form):
    form_class = forms.get(form_id, default_form)
    if isinstance(form_class, str):
        form_class = import_attribute(form_class)
    return form_class

def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit(".", 1)
    return getattr(importlib.import_module(pkg), attr)

def get_adapter(request=None):
    return import_attribute("compte.account.adapter.DefaultAccountAdapter")(request)

def get_request_param(request, param, default=None):
    if request is None:
        return default
    return request.POST.get(param) or request.GET.get(param, default)

def url_str_to_user_pk(s):
    if getattr(get_user_model()._meta.pk, "remote_field", None):
        pk_field = get_user_model()._meta.pk.remote_field.to._meta.pk
    else:
        pk_field = get_user_model()._meta.pk
    if issubclass(type(pk_field), models.UUIDField):
        return pk_field.to_python(s)
    try:
        pk_field.to_python("a")
        pk = s
    except ValidationError:
        pk = base36_to_int(s)
    return pk

class ImmediateHttpResponse(Exception):
    def __init__(self, response):
       self.response = response

####



def _ajax_response(request, response, form=None, data=None):
    if any([ request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest", request.content_type == "application/json", request.META.get("HTTP_ACCEPT") == "application/json",]):
        if isinstance(response, (HttpResponseRedirect, HttpResponsePermanentRedirect)):
            redirect_to = response["Location"]
        else:
            redirect_to = None
        response = get_adapter(request).ajax_response(request, response, form=form, data=data, redirect_to=redirect_to)
    return response



class LoginView(FormView):
    template_name = "account/login.html"


    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_form_class(self):
        return get_form_class( {}, "login", LoginForm)

    def form_valid(self, form):
        try:
            return form.login(self.request, redirect_url=reverse('compte'))
        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):
        c = super(LoginView, self).get_context_data(**kwargs)

        c.update(
            {"style_css": '/static/css/registrer.css',
             'bodyindex': 'compte-login',
             'title': _('Connexion'),
             'description': _('Connexion à mon compte')})
        return c


#class CloseableSignupMixin(object):
#fermeture inscription
    #def dispatch(self, request, *args, **kwargs):
       # return self.closed()

    #def closed(self):
        #response_kwargs = {"request": self.request,"template": "compte/account/signup_closed.html",}
        #return self.response_class(**response_kwargs)


class SignupView(FormView):
    template_name = "account/signup.html"
    redirect_field_name = "next"


    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_form_class({}, "signup", SignupForm)

    def get_success_url(self):
        return get_request_param(self.request, self.redirect_field_name)

    def form_valid(self, form):
        self.user = form.save(self.request)
        try:
            signals.user_signed_up.send(sender=self.user.__class__, request=self.request, user=self.user)
            return perform_login(self.request,self.user, email_verification="optionnal",signup=True, redirect_url=self.success_url,signal_kwargs=None,)

        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):
        c = super(SignupView, self).get_context_data(**kwargs)

        if self.request.session.get("account_verified_email"):
            for email_key in ["email"]:
                c["form"].fields[email_key].initial = self.request.session.get("account_verified_email")

        c.update({   'bodyindex': 'compte-signup',
                'style_css': '/static/css/registrer.css',
                'title': _('Inscription'),
                'description': _('Inscription à mon compte'),
                "login_url": passthrough_next_redirect_url(self.request, reverse("account_login"), self.redirect_field_name),
                "redirect_field_name": self.redirect_field_name,
                "redirect_field_value": get_request_param(self.request, self.redirect_field_name),
               # "site": get_current_site(self.request),
            }
        )
        return c

class LogoutFunctionalityMixin(object):

    def logout(self, request):
        from django.contrib.auth import logout as django_logout
        django_logout(request)

class ConfirmEmailView(TemplateResponseMixin, LogoutFunctionalityMixin, View):
    template_name = "account/email_confirm.html"


    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            self.object = None

        return self.render_to_response(self.get_context_data())

    def post(self,request, *args, **kwargs):

        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        cache.clear()
        if (self.request.user.is_authenticated and self.request.user.pk != confirmation.email_address.user_id):
            self.logout(request)

        get_adapter(self.request).add_message(self.request,messages.SUCCESS, "account/messages/email_confirmed.txt", {"email": confirmation.email_address.email},)

        if not reverse('compte'):
            return self.render_to_response(self.get_context_data())
        return redirect(reverse('compte'))

    def login_on_confirm(self, confirmation):
        user_pk = None
        user_pk_str = get_adapter(self.request).unstash_user(self.request)
        if user_pk_str:
            user_pk = url_str_to_user_pk(user_pk_str)
        user = confirmation.email_address.user
        if user_pk == user.pk and self.request.user.is_anonymous:
            return perform_login( self.request, user, redirect_url=reverse('compte'))


        return None

    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        emailconfirmation = EmailConfirmationHMAC.from_key(key)
        if not emailconfirmation:
            if queryset is None:
                queryset = self
            try:
                emailconfirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                raise Http404()
        return emailconfirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx["confirmation"] = self.object
        ctx['style_css'] = '/static/css/registrer.css'
        #ctx.update({"site": get_current_site(self.request)})
        return ctx


class PasswordResetView(FormView):
    template_name = "account/password_reset.html"
    success_url = reverse_lazy("account_reset_password_done")
    redirect_field_name = "next"


    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super(PasswordResetView, self).dispatch(request, *args, **kwargs)


    def get_form_class(self):
        return get_form_class({}, "reset_password", ResetPasswordForm)

    def form_valid(self, form):
        form.save(self.request)
        return super(PasswordResetView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordResetView, self).get_context_data(**kwargs)
        ret["password_reset_form"] = ret.get("form")
        ret["style_css"] = '/static/css/registrer.css'
        ret["title"] = 'Réinitialisation du mot de passe'
        ret["description"] = 'Modification de votre de mot de passe'
        ret.update({"login_url": passthrough_next_redirect_url(self.request, reverse("account_login"), self.redirect_field_name)})
        return ret


class PasswordResetDoneView(TemplateView):
    template_name = "account/password_reset_done.html"

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret["style_css"] = '/static/css/registrer.css'
        ret["title"] = 'Réinitialisation du mot de passe'
        ret["description"] = 'Modification de votre de mot de passe'
        return ret

class PasswordResetFromKeyView(LogoutFunctionalityMixin, FormView):
    template_name = "account/password_reset_from_key.html"
    success_url = reverse_lazy("account_reset_password_from_key_done")

    def get_form_class(self):
        return get_form_class({}, "reset_password_from_key", ResetPasswordKeyForm)

    def dispatch(self, request, uidb36, key, **kwargs):
        self.request = request
        self.key = key

        if self.key == "set-password":
            self.key = self.request.session.get("_password_reset_key", "")

            token_form = UserTokenForm(data={"uidb36": uidb36, "key": self.key})
            if token_form.is_valid():
                self.reset_user = token_form.reset_user

                if (
                    self.request.user.is_authenticated
                    and self.request.user.pk != self.reset_user.pk
                ):
                    self.logout(request)
                    self.request.session["_password_reset_key"] = self.key

                return super(PasswordResetFromKeyView, self).dispatch(request, uidb36, self.key, **kwargs)
        else:
            token_form = UserTokenForm(data={"uidb36": uidb36, "key": self.key})
            if token_form.is_valid():
                self.request.session["_password_reset_key"] = self.key
                redirect_url = self.request.path.replace(
                    self.key, "set-password"
                )
                return redirect(redirect_url)

        self.reset_user = None

        return _ajax_response(self.request, self.render_to_response(self.get_context_data(token_fail=True)), form=token_form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordResetFromKeyView, self).get_context_data(**kwargs)
        ret["action_url"] = reverse( "account_reset_password_from_key", kwargs={ "uidb36": self.kwargs["uidb36"], "key": self.kwargs["key"],},)
        ret["style_css"] = '/static/css/registrer.css'

        return ret

    def get_form_kwargs(self):
        kwargs = super(PasswordResetFromKeyView, self).get_form_kwargs()
        kwargs["user"] = self.reset_user
        kwargs["temp_key"] = self.key
        return kwargs

    def form_valid(self, form):
        form.save()

        if self.reset_user:
            for email in self.reset_user.emailaddress_set.all():
                get_adapter(self.request)._delete_login_attempts_cached_email(self.request, email=email.email)

        get_adapter(self.request).add_message(self.request, messages.SUCCESS,"account/messages/password_changed.txt",)
        signals.password_reset.send( sender=self.reset_user.__class__,request=self.request, user=self.reset_user,)

        return super(PasswordResetFromKeyView, self).form_valid(form)


class LogoutView(TemplateResponseMixin, LogoutFunctionalityMixin, View):
    template_name = "account/logout.html"
    redirect_field_name = "next"

    def get(self, *args, **kwargs):
        return _ajax_response(self.request, self.render_to_response({'style_css': '/static/css/registrer.css'}))

    def post(self,request, *args, **kwargs):
        if request.user.is_authenticated:
            self.logout(request)
        return _ajax_response(request, redirect('/'))

#class AccountInactiveView(View):
    #template_name = "compte/account/account_inactive.html"
