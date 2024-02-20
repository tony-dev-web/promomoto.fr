from django import forms
from annonce.models import AnnonceModel
from outil.imagekit.models import ProcessedImageField
from django.utils.translation import gettext_lazy as _



class Annonce_CreatedForm(forms.ModelForm):

    title = forms.CharField(min_length=5, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Titre'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    description = forms.CharField(min_length=5, max_length=2000,widget=forms.Textarea(attrs={'rows': 10, 'cols': 10, 'placeholder': _('Description'),"autocomplete": "off","spellchek": "false", "tabindex": "0"}))
    ville = forms.CharField(required=False,min_length=3, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Ville'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))
    marque = forms.CharField(required=False, min_length=3, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Marque'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))
    prix = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': _('Prix'), "autocomplete": "off", "spellchek" : "false", "tabindex" : "0"}))
    phone = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': _('Telephone'),"min_length":"10","max_length":"10", "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))

    CHOICES_ETAT = [('Bon état', _('Bon état')),
                    ('Très bon état', _('Très bon état')),
                    ('Très peu servi', _('Très peu servi')),
                    ('Correct', _('Correct')),
                    ('Abimé', _('Abimé')),
                    ('Comme neuf', _('Comme neuf'))]

    etat = forms.ChoiceField(choices=CHOICES_ETAT)


    CHOICES_TYPE = [
                        ('piece', _('Piece')),
                        ('moto', _('Moto')),
                        ('accessoire', _('Accessoire'))]

    type = forms.ChoiceField(choices=CHOICES_TYPE)

    image1 = ProcessedImageField()
    image2 = ProcessedImageField()
    image3 = ProcessedImageField()
    image4 = ProcessedImageField()


    class Meta:
        model = AnnonceModel
        fields = ( "title", "description","ville","marque","prix","phone","etat","type", "image1", "image2", "image3", "image4")
