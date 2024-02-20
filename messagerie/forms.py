from messagerie.models import MessageModel
from django import forms
#from django.core.mail import send_mass_mail
from django.utils.translation import gettext as _



class MessagerieForms(forms.ModelForm):
    message = forms.CharField(min_length=3, max_length=2000,
                              widget=forms.Textarea(
                                  attrs={'rows': 2, 'cols': 2, 'placeholder': _('Message'), "autocomplete": "off","style":"width:100%",
                                         "spellchek": "false", "tabindex": "0"}))

    class Meta:
        model = MessageModel
        fields = ['message', ]

    #def get_contactform_valid(form):
       # u2 = form.cleaned_data['message']
       # u3b = form.cleaned_data['email']
      #  m1 = (_('Message sur flypii'), u2, 'coucou@flypii.com', [u3b])

      #  send_mass_mail((m1), fail_silently=False)

      #  return form