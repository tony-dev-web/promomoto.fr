
from django import forms
from vehicule.models import VehiculeModel
from outil.imagekit.models import ProcessedImageField
from django.utils.translation import gettext_lazy as _

class Vehicule_CreatedForm(forms.ModelForm):

    description = forms.CharField(required=False,min_length=10, max_length=2000,widget=forms.Textarea(attrs={'rows': 5, 'cols': 5, 'placeholder': _('Description'),"autocomplete": "off","spellchek": "false", "tabindex": "0"}))
    modele = forms.CharField(required=False,min_length=3, max_length=60, widget=forms.TextInput(
        attrs={'placeholder': _('Modele'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))
    cylindre = forms.CharField(required=False,min_length=3, max_length=60, widget=forms.TextInput(
        attrs={'placeholder': _('Cylindrée'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))
    annee = forms.CharField(required=False,min_length=3, max_length=5, widget=forms.TextInput(
        attrs={'placeholder': _('Année'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))

    couleur = forms.CharField(required=False,min_length=3, max_length=50, widget=forms.TextInput(
        attrs={'placeholder': _('Couleur'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))

    km = forms.CharField(required=False,min_length=3, max_length=5, widget=forms.TextInput(
        attrs={'placeholder': _('km'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))


    CHOICES_ETAT = [('Bon état', _('Bon état')),
                    ('Souci mécanique', _('Souci mécanique')),
                    ('Abimé', _('Abimé')),
                    ('Accidenté', _('Accidenté')),
                     ('Epave', _('Epave'))]

    etat = forms.ChoiceField(choices=CHOICES_ETAT)

    CHOICES_MARQUE = [('Yamaha', _('Yamaha')),
                    ('Honda', _('Honda')),
                    ('Kawasaki', _('Kawasaki')),
                    ('Suzuki', _('Suzuki')),
                  ('Ducati', _('Ducati')),
                    ('Ktm', _('Epave'))]

    marque = forms.ChoiceField(choices=CHOICES_MARQUE)

    CHOICES_TYPE = [('piece', _('Pièce')),('moto', _('Moto')),('motocross', _('Motocross')),('quad', _('Quad')),('scooter', _('Scooter')),]
    type = forms.ChoiceField(choices=CHOICES_TYPE)

    image1 = ProcessedImageField()

    class Meta:
        model = VehiculeModel
        fields = ( "marque","modele","description","cylindre","annee","etat","type","couleur","km", "image1")