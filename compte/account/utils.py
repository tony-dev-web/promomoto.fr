import importlib
import unicodedata
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.http import int_to_base36

from django.http import HttpResponseRedirect 
#from outil.django.response import HttpResponseRedirect
from . import signals
from compte.account.app_settings import EmailVerificationMethod

#####
def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit(".", 1)
    return getattr(importlib.import_module(pkg), attr)


def get_adapter(request=None):
    return import_attribute("compte.account.adapter.DefaultAccountAdapter")(request)

class ImmediateHttpResponse(Exception):
    def __init__(self, response):
       self.response = response
#####

def get_request_param(request, param, default=None):
    if request is None:
        return default
    return request.POST.get(param) or request.GET.get(param, default)

def get_login_redirect_url(request, url=None, redirect_field_name="next", signup=False):
    ret = url
    if url and callable(url):
        ret = url()
    if not ret:
        ret = get_request_param(request, redirect_field_name)
    if not ret:
        if signup:
            ret = get_adapter(request).get_signup_redirect_url(request)
        else:
            ret = get_adapter(request).get_login_redirect_url(request)
    return ret


def perform_login(request, user,email_verification,redirect_url=None,signal_kwargs=None,signup=False,email=None, level=None,):
    if not user.is_active:
        return HttpResponseRedirect(reverse("account_inactive"), request, user)

    #if email_verification == "optionnal" and not _has_verified_for_login(user, email) and signup:

    send_email_confirmation(request, user, signup=signup, email=email)

    try:

        from django.contrib.auth import (get_backends,login as django_login,)
        if not hasattr(user, "backend"):
            from .auth_backends import AuthenticationBackend
            backend = None
            for b in get_backends():
                if isinstance(b, AuthenticationBackend):
                    backend = b
                    break
                elif not backend and hasattr(b, "get_user"):
                    backend = b

            user.backend =  ".".join([backend.__module__, backend.__class__.__name__])
        django_login(request, user)

        response = HttpResponseRedirect(get_login_redirect_url(request, redirect_url, signup=signup))

        if signal_kwargs is None:
            signal_kwargs = {}
        signals.user_logged_in.send(sender=user.__class__, request=request, response=response, user=user, **signal_kwargs, )

        from django.contrib import messages
        from django.template import TemplateDoesNotExist
        from django.template.loader import render_to_string
        try:
            message = render_to_string("account/messages/logged_in.txt",{"user": user}, request).strip()
            if message:
                messages.add_message(request, level, message, extra_tags="")
        except TemplateDoesNotExist:
            pass

    # adapter message //
    except ImmediateHttpResponse as e:
        response = e.response
    return response


def user_field(user, field, *args):
    if not field:
        return
    try:
        field_meta = get_user_model()._meta.get_field(field)
        max_length = field_meta.max_length
    except FieldDoesNotExist:
        if not hasattr(user, field):
           return
        max_length = None
    if args:
        v = args[0]
        if v:
            v = v[0:max_length]
        setattr(user, field, v)
    else:
        return getattr(user, field)

def user_email(user, *args):
 return user_field(user,"email", *args)

def send_email_confirmation(request, user, signup=False, email=None):
    from compte.account.models import EmailAddress
    if not email:
        email = user_email(user)
    if email:
        try:
            email_address = EmailAddress.objects.get_for_user(user, email)
            if not email_address.verified:
                send_email = True
                if send_email:
                    email_address.send_confirmation(request, signup=signup)
            else:
                send_email = False
        except EmailAddress.DoesNotExist:
            send_email = True
            email_address = EmailAddress.objects.add_email(request, user, email, signup=signup, confirm=True)
            assert email_address

        if send_email:
            get_adapter(request).add_message( request, messages.INFO,"account/messages/email_confirmation_sent.txt",{"email": email},)
    if signup:
        get_adapter(request).stash_user(request, user_pk_to_url_str(user))


def sync_user_email_addresses(user):
    from compte.account.models import EmailAddress
    if (user_email(user) and not EmailAddress.objects.filter(user=user, email__iexact=user_email(user)).exists() ) and (True and EmailAddress.objects.filter(mail__iexact=user_email(user)).exists()):
        return EmailAddress.objects.create(user=user, email=user_email(user), primary=False, verified=False )

def _unicode_ci_compare(s1, s2):
    return unicodedata.normalize("NFKC", s1).casefold() == unicodedata.normalize("NFKC", s2).casefold()

def filter_users_by_email(email):
    from compte.account.models import EmailAddress
    for user in User.objects.filter(Q(email__iexact=email)).iterator():
        if _unicode_ci_compare(getattr(user, 'email'), email):
                [ e.user for e in EmailAddress.objects.filter(email__iexact=email).prefetch_related("user") if _unicode_ci_compare(e.email, email) ].append(user)
    return list({e.user for e in EmailAddress.objects.filter(email__iexact=email).prefetch_related("user") if _unicode_ci_compare(e.email, email)})

def user_pk_to_url_str(user):
    if issubclass(type(get_user_model()._meta.pk), models.UUIDField):
        if isinstance(user.pk, str):
            return user.pk
        return user.pk.hex

    ret = user.pk
    if isinstance(ret, int):
        ret = int_to_base36(user.pk)
    return str(ret)