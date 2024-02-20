from __future__ import unicode_literals
import datetime
import importlib
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction

from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.db import models
from django.db.models import Q
from django.utils import timezone
from compte import app_settings as allauth_app_settings
from . import signals

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
    return user_field(user, "email", *args)

def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit(".", 1)
    return getattr(importlib.import_module(pkg), attr)

def get_adapter(request=None):
    return import_attribute("compte.account.adapter.DefaultAccountAdapter")(request)
###

class EmailAddressManager(models.Manager):
    def add_email(self, request, user, email, confirm=False, signup=False):
        email_address, created = self.get_or_create(user=user, email__iexact=email, defaults={"email": email})
        if created and confirm:
            email_address.send_confirmation(request, signup=signup)
        return email_address

    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None

    def get_users_for(self, email):
        return [address.user for address in self.filter(verified=True, email__iexact=email)]

    def fill_cache_for_user(self, user, addresses):
        user._emailaddress_cache = addresses

    def get_for_user(self, user, email):
        if getattr(user, "_emailaddress_cache", None) is None:
            ret = self.get(user=user, email__iexact=email)
            ret.user = user
            return ret
        else:
            for address in getattr(user, "_emailaddress_cache", None):
                if address.email.lower() == email.lower():
                    return address
            raise self.model.DoesNotExist()

class EmailAddress(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(allauth_app_settings.USER_MODEL,verbose_name=_("user"),on_delete=models.CASCADE,)
    email = models.EmailField(unique=True,max_length=40,verbose_name=_("Adresse email"),)
    verified = models.BooleanField(verbose_name=_("verified"), default=False)
    primary = models.BooleanField(verbose_name=_("primary"), default=False)
    objects = EmailAddressManager()

    class Meta:
        verbose_name = _("Adresse email")
        verbose_name_plural = _("Adresse email")
        unique_together = [("user", "email")]

    def __str__(self):
        return self.email

    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        user_email(self.user, self.email)
        self.user.save()
        return True

    def send_confirmation(self, request=None, signup=False):
        return EmailConfirmationHMAC(self).send(request, signup=signup)

    def change(self, request, new_email, confirm=True):
        with transaction.atomic():
            user_email(self.user, new_email)
            self.user.save()
            self.email = new_email
            self.verified = False
            self.save()
            if confirm:
                self.send_confirmation(request)

class EmailConfirmationManager(models.Manager):
    def all_expired(self):
        return self.filter(self.expired_q())

    def all_valid(self):
        return self.exclude(self.expired_q())

    def expired_q(self):
        return Q(sent__lt=timezone.now() - timedelta(days=30))

    def delete_expired_confirmations(self):
        self.all_expired().delete()

class EmailConfirmation(models.Model):
    id = models.AutoField(primary_key=True)
    email_address = models.ForeignKey(EmailAddress, verbose_name=_("Adresse email"),on_delete=models.CASCADE,)
    created = models.DateTimeField(verbose_name=_("created"), default=timezone.now)
    sent = models.DateTimeField(verbose_name=_("sent"), null=True)
    key = models.CharField(verbose_name=_("key"), max_length=64, unique=True)

    objects = EmailConfirmationManager()

    class Meta:
        verbose_name = _("Email confirmation")
        verbose_name_plural = _("Email confirmations")

    def __str__(self):
        return "confirmation for %s" % self.email_address

    @classmethod
    def create(cls, email_address):
        return cls._default_manager.create(email_address=email_address, key=get_random_string(64).lower())

    def key_expired(self):
        return self.sent + datetime.timedelta(days=14) <= timezone.now()

    key_expired.boolean = True

    def confirm(self, request):
        if not self.key_expired() and not self.email_address.verified:
            email_address = self.email_address
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()

            signals.email_confirmed.send(sender=self.__class__,request=request,email_address=email_address,)
            return email_address

    def send(self, request=None, signup=False):
        get_adapter(request).send_confirmation_mail(request, self, signup)
        self.sent = timezone.now()
        self.save()
        signals.email_confirmation_sent.send(sender=self.__class__,request=request,confirmation=self,signup=signup,)


class EmailConfirmationHMAC:
    def __init__(self, email_address):
        self.email_address = email_address

    @property
    def key(self):
        return signing.dumps(obj=self.email_address.pk, salt='account')

    @classmethod
    def from_key(cls, key):
        try:
            ret = EmailConfirmationHMAC(EmailAddress.objects.get(pk=signing.loads(key, max_age=60 * 60 * 24 * 14, salt='account')))
        except (
            signing.SignatureExpired,
            signing.BadSignature,
            EmailAddress.DoesNotExist,
        ):
            ret = None
        return ret

    def confirm(self, request):
        if not self.email_address.verified:
            email_address = self.email_address

            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()

            signals.email_confirmed.send(sender=self.__class__,request=request,email_address=email_address,)
            return email_address

    def send(self, request=None, signup=False):
        get_adapter(request).send_confirmation_mail(request, self, signup)
        signals.email_confirmation_sent.send(sender=self.__class__,request=request,confirmation=self,signup=signup,)
