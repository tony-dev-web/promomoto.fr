from __future__ import absolute_import

import importlib
import warnings
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core import exceptions, validators
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.urls import reverse
from django.utils.http import int_to_base36, base36_to_int
from django.utils.translation import gettext, gettext_lazy as _
from collections import OrderedDict
from . import app_settings

from compte.account.utils import perform_login, filter_users_by_email
from django.db import models
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.utils.translation import gettext_lazy as _
from compte.account.models import EmailAddress
from compte.account.utils import sync_user_email_addresses


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


def set_form_field_order(form, field_order):
    if field_order is None:
        return
    fields = OrderedDict()
    for key in field_order:
        try:
            fields[key] = form.fields.pop(key)
        except KeyError:
            pass
    fields.update(form.fields)
    form.fields = fields


def build_absolute_uri(request, location):
    if request is None:
        return location
    else:
        return f"http:{request.build_absolute_uri(location).partition(':')[2]}"


def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit(".", 1)
    return getattr(importlib.import_module(pkg), attr)

def get_adapter(request=None):
    return import_attribute("compte.account.adapter.DefaultAccountAdapter")(request)



def valid_email_or_none(email):
    ret = None
    try:
        if email:
            validate_email(email)
            if len(email) <= 50 :
                ret = email
    except ValidationError:
        pass
    return ret


def cleanup_email_addresses(request, addresses):

    e2a = OrderedDict()
    primary_addresses = []
    verified_addresses = []
    primary_verified_addresses = []
    for address in addresses:
        email = valid_email_or_none(address.email)
        if not email:
            continue
        from compte.account.models import EmailAddress
        if EmailAddress.objects.filter(email__iexact=email).exists():
            continue
        a = e2a.get(email.lower())
        if a:
            a.primary = a.primary or address.primary
            a.verified = a.verified or address.verified
        else:
            a = address
            a.verified = a.verified or get_adapter(request).is_email_verified(request, a.email)
            e2a[email.lower()] = a
        if a.primary:
            primary_addresses.append(a)
            if a.verified:
                primary_verified_addresses.append(a)
        if a.verified:
            verified_addresses.append(a)

    if primary_verified_addresses:
        primary_address = primary_verified_addresses[0]
    elif verified_addresses:
        primary_address = verified_addresses[0]
    elif primary_addresses:
        primary_address = primary_addresses[0]
    elif e2a:
        primary_address = e2a.keys()[0]
    else:
        primary_address = None

    for a in e2a.values():
        a.primary = primary_address.email.lower() == a.email.lower()
    return list(e2a.values()), primary_address

def setup_user_email(request, user, addresses):
    from compte.account.models import EmailAddress
    assert not EmailAddress.objects.filter(user=user).exists()
    priority_addresses = []

    stashed_email = get_adapter(request).unstash_verified_email(request)
    if stashed_email:
        priority_addresses.append(EmailAddress(user=user, email=stashed_email, primary=True, verified=True))

    if user_email(user):
        priority_addresses.append(EmailAddress(user=user, email=user_email(user), primary=True, verified=False))
    addresses, primary = cleanup_email_addresses(request, priority_addresses + addresses)
    for a in addresses:
        a.user = user
        a.save()
    EmailAddress.objects.fill_cache_for_user(user, addresses)
    if primary and user_email(user) and user_email(user).lower() != primary.email.lower():
        user_email(user, primary.email)
        user.save()
    return primary

def user_pk_to_url_str(user):
    if issubclass(type(get_user_model()._meta.pk), models.UUIDField):
        if isinstance(user.pk, str):
            return user.pk
        return user.pk.hex

    ret = user.pk
    if isinstance(ret, int):
        ret = int_to_base36(user.pk)
    return str(ret)


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
###



class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = forms.PasswordInput(render_value=kwargs.pop("render_value", False),)
        kwargs["widget"].attrs["autocomplete"] = kwargs.pop("autocomplete", None)
        super(PasswordField, self).__init__(*args, **kwargs)



###

class LoginForm(forms.Form):

    password = PasswordField(label=_("Password"), autocomplete="current-password")
    remember = forms.BooleanField(label=_("Remember Me"), required=False)
    user = None

    error_messages = {
        "account_inactive": _("Ce compte est actuellement inactif."),
        "email_password_mismatch": _("L\'adresse e-mail etou le mot de passe que vous avez spécifié ne sont pas corrects." ),
        "username_password_mismatch": _("Le nom d'utilisateur ou le mot de passe que vous avez spécifié ne sont pas corrects."),
    }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LoginForm, self).__init__(*args, **kwargs)

        login_widget = forms.TextInput(attrs={"type": "email","placeholder": _("Adresse email"),"autocomplete": "email",})
        login_field = forms.EmailField(label=_("E-mail"), widget=login_widget)

        self.fields["login"] = login_field
        set_form_field_order(self, ["login", "password", "remember"])

        del self.fields["remember"]

    def user_credentials(self):
        return {"email": self.cleaned_data["login"],
                "password": self.cleaned_data["password"],}

    def clean_login(self):
        return self.cleaned_data["login"].strip()

    def _is_login_email(self, login):
        try:
            validators.validate_email(login)
            ret = True
        except exceptions.ValidationError:
            ret = False
        return ret

    def clean(self):
        super(LoginForm, self).clean()
        cache.clear()
        if self._errors:
            return
        credentials = self.user_credentials()
        user = get_adapter(self.request).authenticate(self.request, **credentials)
        if user:
            self.user = user
        else:
            auth_method = app_settings.AUTHENTICATION_METHOD
            if auth_method == "email" and self._is_login_email(self.cleaned_data["login"]):
                auth_method = "email"
            raise forms.ValidationError(self.error_messages["%s_password_mismatch" % auth_method])
        return self.cleaned_data

    def login(self, request, redirect_url=None):
        return perform_login(request,self.user, email_verification="optional",redirect_url=redirect_url, email=self.user_credentials().get("email"),)


class _DummyCustomSignupForm(forms.Form):
    def signup(self, request, user):
        pass


def _base_signup_form_class():
    return _DummyCustomSignupForm


class BaseSignupForm(_base_signup_form_class()):
    #CHOICES_ROLE = [('Particulier', _('particulier')),
           #         ('Entreprise', _('entreprise'))]

   # role = forms.ChoiceField(choices=CHOICES_ROLE)


    email = forms.EmailField(widget=forms.TextInput(attrs={"type": "email","placeholder": _("Adresse email"),"autocomplete": "email",}))

    def __init__(self, *args, **kwargs):
        super(BaseSignupForm, self).__init__(*args, **kwargs)

        if kwargs.pop("email_required", False):
            self.fields["email"].label = gettext("E-mail")
            self.fields["email"].required = True
        else:
            self.fields["email"].label = gettext("E-mail")
            self.fields["email"].required = False
            self.fields["email"].widget.is_required = False


        set_form_field_order(self, ["email","password1","password2"])


    def clean_email(self):
        value = self.cleaned_data["email"]
        value = get_adapter().clean_email(value)
        if value:
            value = self.validate_unique_email(value)
        return value

    def validate_unique_email(self, value):
        return get_adapter().validate_unique_email(value)

    def custom_signup(self, request, user):
        custom_form = super(BaseSignupForm, self)
        if hasattr(custom_form, "signup") and callable(custom_form.signup):
            custom_form.signup(request, user)
        else:
            warnings.warn("The custom signup form must offer a `def signup(self, request, user)` method",DeprecationWarning,)
            custom_form.save(user)


class SignupForm(BaseSignupForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields["password1"] = PasswordField(label=_("Password"), autocomplete="new-password")
        self.fields["password2"] = PasswordField(label=_("Password (again)"))

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    def clean(self):
        super(SignupForm, self).clean()
        cache.clear()
        user_email(User, self.cleaned_data.get("email"))

        if self.cleaned_data.get("password1"):
            try:
                get_adapter().clean_password(self.cleaned_data.get("password1"), user=User)
            except forms.ValidationError as e:
                self.add_error("password1", e)

        if ( "password1" in self.cleaned_data and "password2" in self.cleaned_data and self.cleaned_data["password1"] != self.cleaned_data["password2"]):
            self.add_error( "password2", _("You must type the same password each time."),  )
        return self.cleaned_data

    def save(self, request):
        user = get_adapter(request).new_user(request)
        get_adapter(request).save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class UserForm(forms.Form):
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class PasswordVerificationMixin(object):
    def clean(self):
        cleaned_data = super(PasswordVerificationMixin, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if (password1 and password2) and password1 != password2:
            self.add_error("password2", _("You must type the same password each time."))
        return cleaned_data



class SetPasswordField(PasswordField):
    def __init__(self, *args, **kwargs):
        kwargs["autocomplete"] = "new-password"
        super(SetPasswordField, self).__init__(*args, **kwargs)
        self.user = None

    def clean(self, value):
        cache.clear()
        value = super(SetPasswordField, self).clean(value)
        value = get_adapter().clean_password(value, user=self.user)
        return value



class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("Adresse email"),
                "autocomplete": "email",} ),)

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email)
        if not self.users:
            raise forms.ValidationError(
                _("L'adresse e-mail n'est attribuée à aucun compte utilisateur")
            )
        return self.cleaned_data["email"]

    def save(self, request, **kwargs):
        for user in self.users:
            context = {
               # "current_site": get_current_site(request),
                "user": user,
                "password_reset_url": build_absolute_uri(request, reverse("account_reset_password_from_key", kwargs=dict(uidb36=user_pk_to_url_str(user), key=kwargs.get("token_generator", default_token_generator).make_token(user)),)),
                "request": request,
            }

            get_adapter(request).send_mail("account/email/password_reset_key", self.cleaned_data["email"], context)
        return self.cleaned_data["email"]


def set_password(self, user, password):
        user.set_password(password)
        user.save()


class ResetPasswordKeyForm(PasswordVerificationMixin, forms.Form):

    password1 = SetPasswordField(label=_("Mot de passe"))
    password2 = PasswordField(label=_("Re-Nouveau Mot de passe"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields["password1"].user = self.user



    def save(self):
         set_password(self.user, self.cleaned_data["password1"])


class EmailAwarePasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        ret = super(EmailAwarePasswordResetTokenGenerator, self)._make_hash_value(user, timestamp)
        sync_user_email_addresses(user)
        emails = set([user.email] if user.email else [])
        emails.update(EmailAddress.objects.filter(user=user).values_list("email", flat=True))
        ret += "|".join(sorted(emails))
        return ret

class UserTokenForm(forms.Form):
    uidb36 = forms.CharField()
    key = forms.CharField()
    reset_user = None
    token_generator = EmailAwarePasswordResetTokenGenerator()
    error_messages = {"token_invalid": _("Le Token du mot de passe n'était pas valide."),}

    def _get_user(self, uidb36):
        try:
            pk = url_str_to_user_pk(uidb36)
            return get_user_model().objects.get(pk=pk)
        except (ValueError, get_user_model().DoesNotExist):
            return None