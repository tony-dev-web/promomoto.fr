from __future__ import unicode_literals

import hashlib
import json
import time

from django import forms
#from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, get_backends,login as django_login, get_user_model)
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from . import app_settings
####

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

def user_username(user, *args):
    return user_field(user, app_settings.USER_MODEL_USERNAME_FIELD, *args)

def build_absolute_uri(request, location):
    if request is None:
        return location
    else:
        return f"http:{request.build_absolute_uri(location).partition(':')[2]}"

####


class DefaultAccountAdapter(object):

    error_messages = {
        "username_blacklisted": _(
            "Username can not be used. Please use other username."
        ),
        "username_taken": AbstractUser._meta.get_field("username").error_messages["unique"],
        "too_many_login_attempts": _(
            "Too many failed login attempts. Try again later."
        ),
        "email_taken": _("A user is already registered with this e-mail address."),
    }

    def __init__(self, request=None):
        self.request = request

    def stash_verified_email(self, request, email):
        request.session["account_verified_email"] = email

    def unstash_verified_email(self, request):
        ret = request.session.get("account_verified_email")
        request.session["account_verified_email"] = None
        return ret

    def stash_user(self, request, user):
        request.session["account_user"] = user

    def unstash_user(self, request):
        return request.session.pop("account_user", None)

    def is_email_verified(self, request, email):
        ret = False
        if request.session.get("account_verified_email"):
            ret = request.session.get("account_verified_email").lower() == email.lower()
        return ret

    def render_mail(self, template_prefix, email, context):
        subject = force_str(" ".join(render_to_string(f"{template_prefix}_subject.txt", context).splitlines()).strip())

        bodies = {}
        for ext in ["html", "txt"]:
            try:
                bodies[ext] = render_to_string(f"{template_prefix}_message.{ext}",context,self.request,).strip()
            except TemplateDoesNotExist:
                if ext == "txt" and not bodies:
                    raise
        if "txt" in bodies:
            msg = EmailMultiAlternatives(subject, bodies["txt"], 'inscription@promomoto.fr',[email] if isinstance(email, str) else email)
            if "html" in bodies:
                msg.attach_alternative(bodies["html"], "text/html")
        else:
            msg = EmailMessage(subject, bodies["html"], 'contact@promomoto.fr', [email] if isinstance(email, str) else email)
            msg.content_subtype = "html"
        return msg

    def send_mail(self, template_prefix, email, context):
        self.render_mail(template_prefix, email, context).send()

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        self.send_mail("account/email/email_confirmation_signup", emailconfirmation.email_address.email, {
            "user": emailconfirmation.email_address.user,
            "activate_url": build_absolute_uri(request, reverse("account_confirm_email", args=[emailconfirmation.key])),
            "key": emailconfirmation.key,
        })

    def new_user(self, request):
        return get_user_model()()

    def save_user(self, request, user, form, commit=True):

        user_email(user, form.cleaned_data.get("email"))
        user_username(user, form.cleaned_data.get("email"))

        if "password1" in form.cleaned_data:
            user.set_password(form.cleaned_data["password1"])
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user


    def clean_email(self, email):
       return email

    def clean_password(self, password, user=None):
        min_length = 6
        if min_length and len(password) < min_length:
            raise forms.ValidationError(_(f"Password must be a minimum of {min_length} " "characters."))
        validate_password(password, user)
        return password

    def validate_unique_email(self, email):
        from django.contrib.auth.models import User
        if User.objects.filter(Q(email__iexact=email)).exists():
            raise forms.ValidationError(self.error_messages["email_taken"])
        return email

    def add_message(self, request, level, message_template, message_context=None, extra_tags="", ):
        try:
            if message_context is None:
                message_context = {}
            message = render_to_string(
                message_template,
                message_context,
                self.request,
            ).strip()
            if message:
                messages.add_message(request, level, message, extra_tags=extra_tags)
        except TemplateDoesNotExist:
            pass

    def ajax_response(self, request, response, redirect_to=None, form=None, data=None):
        resp = {}
        status = response.status_code

        if redirect_to:
            status = 200
            resp["location"] = redirect_to
        if form:
            if ( request.method == "POST" and form.is_valid() or request.method != "POST"):
                status = 200
            else:
                status = 400
            resp["form"] = self.ajax_response_form(form)
            if hasattr(response, "render"):
                response.render()
            resp["html"] = response.content.decode("utf8")
        if data is not None:
            resp["data"] = data
        return HttpResponse(
            json.dumps(resp), status=status, content_type="application/json"
        )

    def ajax_response_form(self, form):
        form_spec = {
            "fields": {},
            "field_order": [],
            "errors": form.non_field_errors(),
        }
        for field in form:
            field_spec = {
                "label": force_str(field.label),
                "value": field.value(),
                "help_text": force_str(field.help_text),
                "errors": [force_str(e) for e in field.errors],
                "widget": {
                    "attrs": {
                        k: force_str(v) for k, v in field.field.widget.attrs.items()
                    }
                },
            }
            form_spec["fields"][field.html_name] = field_spec
            form_spec["field_order"].append(field.html_name)
        return form_spec

    def login(self, request, user):
        if not hasattr(user, "backend"):
            from compte.account.auth_backends import AuthenticationBackend
            backend = None
            for b in get_backends():
                if isinstance(b, AuthenticationBackend):
                    backend = b
                    break
                elif not backend and hasattr(b, "get_user"):
                    backend = b
            user.backend = ".".join([backend.__module__, backend.__class__.__name__])
        django_login(request, user)

    #def confirm_email(self, request, email_address):
        #email_address.verified = True
        #email_address.set_as_primary(conditional=True)
        #email_address.save()

    def is_safe_url(self, url):
        try:
            from django.utils.http import url_has_allowed_host_and_scheme
        except ImportError:
            from django.utils.http import (is_safe_url as url_has_allowed_host_and_scheme, )
        return url_has_allowed_host_and_scheme(url, allowed_hosts=None)



    def _get_login_attempts_cache_key(self, request, **credentials):
        return f"allauth/login_attempts@:{hashlib.sha256(credentials.get('email').lower().encode('utf8')).hexdigest()}"


    def authenticate(self, request, **credentials):
        from compte.account.auth_backends import AuthenticationBackend

        if app_settings.LOGIN_ATTEMPTS_LIMIT:
            login_data = cache.get(self._get_login_attempts_cache_key(request, **credentials), None)
            if (login_data and len(login_data) >= 10 and time.mktime(timezone.now().timetuple()) < ( login_data[-1] + 30 * 60)):
                raise forms.ValidationError(self.error_messages["too_many_login_attempts"])

        AuthenticationBackend.unstash_authenticated_user()
        user = authenticate(request, **credentials) or AuthenticationBackend.unstash_authenticated_user()

        if user and app_settings.LOGIN_ATTEMPTS_LIMIT:
            cache.delete(self._get_login_attempts_cache_key(request, **credentials))
        else:
            if app_settings.LOGIN_ATTEMPTS_LIMIT:
                cache_key = self._get_login_attempts_cache_key(request, **credentials)
                cache.get(cache_key, []).append(time.mktime(timezone.now().timetuple()))
                cache.set(cache_key, cache.get(cache_key, []), 15 * 60)
        return user