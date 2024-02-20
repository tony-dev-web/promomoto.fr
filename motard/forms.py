from django import forms
from django.utils.translation import gettext as _
from motard.models import MotardModel

class MotardGroupsForm(forms.ModelForm):

     surnom = forms.CharField(min_length=1, max_length=60, widget=forms.TextInput(
        attrs={'placeholder': _('Votre surnom'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )


     CHOICES_ROLE = [('Particulier', _('particulier')),
                     ('Professionnel', _('Professionnel')),
                     ('Club', _('Club'))
                     ]

     role = forms.ChoiceField(choices=CHOICES_ROLE)

     class Meta:
        model = MotardModel
        fields = ("role","surnom")