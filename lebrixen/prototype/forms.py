#encoding=utf-8
'''
Created on 02/05/2010

@author: lfborjas
'''
from django import forms
from django.forms.widgets import HiddenInput
from service import WEB_SERVICES
from profile.models import ClientApp, ClientUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

class PrototypePlanningForm(forms.Form):
    SERVICE_CHOICES=(
                     ('', 'No Service'),
                     ('alchemy', 'Alchemy'),
                     ('wordsfinder', 'WordsFinder'),
                     ('yahoo','Yahoo Extraction Service'),
                     ('tagthe', 'Tagthe content tagger'),
                     ('opencalais', 'OpenCalais'),
                     )
    content = forms.CharField(widget=forms.Textarea(), label =_('Content'))
    lang = forms.CharField(widget=HiddenInput())
    service = forms.ChoiceField(label=u"Servicio web para extracción", choices = SERVICE_CHOICES, widget=HiddenInput())

class PrototypeSettingsForm(forms.Form):
    """Settings for the widget"""
    uid = forms.CharField(label=_('User'))
    fm = forms.ChoiceField(label=_('Feedback'), choices=[('follow', _('Implicit')), ('select', _('Explicit'))])
    uw = forms.BooleanField(label=_('Use Widget'), initial=True)
    appId = forms.ChoiceField(label=_('Application'),
                             choices=[(e.get_token(), e.url) for e in ClientApp.objects.iterator()],
                             )
    lang = forms.ChoiceField(label=_("Language"), choices = settings.LANGUAGES)
    
class DemoToolsForm(forms.Form):
    """A form to select an app an a user"""    
    appId = forms.ChoiceField(label=_("Application"),
                             choices=[('', '')]+[(e.get_token(), e.url) for e in ClientApp.objects.iterator()],
                             )
    appUser = forms.ChoiceField(label=_('User'), choices=[])    
    
class DemoSimulationForm(forms.Form):
    q = forms.CharField(label="")
    #hl = forms.ChoiceField(label="", choices=[('en', 'English'), ('es', 'Español')])
    hl = forms.CharField(widget=forms.HiddenInput())
    
