from django import forms
from django.utils.translation import gettext as _
from signalement.models import SignalementModel

class Signalement_Form(forms.ModelForm):
    objet = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': _('Objet du signalement'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': _('Description du signalement'), "autocomplete": "off", "spellchek": "false",
               "tabindex": "0"}))
    class Meta:
        model = SignalementModel
        fields = ("objet", 'description')