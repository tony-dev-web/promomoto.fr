from django import forms
from order.models import OrderModel
from django.utils.translation import gettext_lazy as _

class Order_CreatedForm(forms.ModelForm):
    moto = forms.CharField(required=False, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Votre moto'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    nom = forms.CharField(min_length=1, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Nom'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    prenom = forms.CharField(required=False, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Prenom'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    societe = forms.CharField(required=False, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Societe'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    adresse = forms.CharField( min_length=1, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Adresse'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    code_postale = forms.CharField( min_length=1, max_length=7, widget=forms.NumberInput(attrs={'placeholder': _('Code postale'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    ville = forms.CharField( min_length=1, max_length=80, widget=forms.TextInput(attrs={'placeholder': _('Ville'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    email = forms.CharField( min_length=1, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('E-mail'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    phone = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': _('Telephone'),"min_length":"10","max_length":"10", "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))
    commentaire = forms.CharField(required=False, max_length=2000, widget=forms.Textarea(attrs={'rows': 2, 'cols': 5, 'placeholder': _('Commentaire'), "autocomplete": "off", "spellchek": "false","tabindex": "0"}))
    CHOICES_EXPE = [ ('mondial relay', _('Modial Relay')),
                        ('Colissimo', _('Colissimo'))]


    expedition = forms.ChoiceField(choices=CHOICES_EXPE)

    class Meta:
        model = OrderModel
        fields = ( "nom","moto", "prenom", "adresse","code_postale","ville", "email", "expedition")


