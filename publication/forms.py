from django.shortcuts import render
from django import forms
from publication.models import PublicationModel
from outil.imagekit.models import ProcessedImageField
from django.utils.translation import gettext_lazy as _



class Publication_CreatedForm(forms.ModelForm):
    publication = forms.CharField(min_length=10, max_length=2000,widget=forms.Textarea(attrs={'rows': 2, 'cols': 2, 'placeholder': _('Publication'),"autocomplete": "off","spellchek": "false", "tabindex": "0"}))
    image1 = ProcessedImageField()


    class Meta:
        model = PublicationModel
        fields = ("publication", "image1")


