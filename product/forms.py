from django.shortcuts import render
from django import forms
from product.models import ProductModel
from outil.imagekit.models import ProcessedImageField
from django.utils.translation import gettext_lazy as _



class Product_CreatedForm(forms.ModelForm):
    title = forms.CharField(min_length=5, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Titre'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}), )
    description = forms.CharField(required=False, max_length=2000,widget=forms.Textarea(attrs={'rows': 3, 'cols': 3, 'placeholder': _('Description'),"autocomplete": "off","spellchek": "false", "tabindex": "0"}))
    prix = forms.IntegerField( widget=forms.NumberInput(attrs={'placeholder': _('Prix'),  "autocomplete": "off", "spellchek" : "false", "tabindex" : "0"}))
    stock = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={'placeholder': _('Stock'),'value':'1', "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))
    etat = forms.CharField(required=False,min_length=3, max_length=60, widget=forms.TextInput(attrs={'placeholder': _('Etat de la pièce'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))
    vp_id = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': _('Vehicule id'), "autocomplete": "off", "spellchek": "false", "tabindex": "0"}))


    CHOICES_CATE = [    ('Carenage', _('carenage')),
                        ('Electrique', _('electrique')),
                        ('Moteur', _('moteur')),
                        ('Chassis', _('chassis')),
                        ('Securiter', _('securiter')),
                        ('Commande', _('commande')),
                        ]
    categorie = forms.ChoiceField(choices=CHOICES_CATE)

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
        model = ProductModel
        fields = ( "title", "description","etat","categorie", "prix","vp_id","stock","type", "image1", "image2", "image3", "image4")