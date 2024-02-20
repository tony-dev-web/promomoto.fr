from django.forms import ModelForm

from contact.models import ContactModel, ContactAdminModel, ContactRachatModel
from outil.imagekit.models import ProcessedImageField


class ContactForm(ModelForm):
    class Meta:
        model = ContactModel
        fields = [ 'nom_contact', 'email_contact', 'objet_contact', 'message_contact']


from django import forms
from django.utils.translation import gettext as _

class ContactAdminForm(forms.ModelForm):
    objet_coucou = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('objet du mail')}))
    email_coucou = forms.EmailField(required=True,widget=forms.EmailInput(attrs={'placeholder': _('adresse email')}))
    texte_coucou = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 10, 'placeholder': _('Description')}))
    connaissance_coucou = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Comment avez-vous connu Flypii')}))

    class Meta:
        model = ContactAdminModel
        fields = ("objet_coucou", "email_coucou", "texte_coucou", "connaissance_coucou")

class ContactRachatForm(forms.ModelForm):

    marque = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Marque')}))
    modele = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Modele')}))
    carnet = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Carnet d\' entretien')}))
    facture = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Facture d\' entretien')}))
    cylindre = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Cylindrée')}))
    annee = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Année')}))
    km = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('kilometrage')}))
    cle_rouge = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Clé rouge')}))
    etat = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Etat')}))
    nom = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Nom')}))
    ville = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Ville')}))
    estimation = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Estimation')}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Téléphone')}))
    email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={'placeholder': _('adresse email')}))
    commentaire = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 10, 'placeholder': _('Description')}))

    image1 = ProcessedImageField()
    image2 = ProcessedImageField()

    class Meta:
        model = ContactRachatModel
        fields = ("marque","modele","carnet","facture","cylindre","annee","km","cle_rouge","etat","nom","ville","estimation","phone","email","commentaire","image1","image2")
