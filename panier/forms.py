from django.shortcuts import render
from django import forms

from order.models import OrderModel
from outil.imagekit.models import ProcessedImageField
from django.utils.translation import gettext_lazy as _

from panier.models import PanierModel


class Panier_CreatedForm(forms.ModelForm):
    class Meta:
        model = PanierModel
        fields = ( "client","pr_id")


