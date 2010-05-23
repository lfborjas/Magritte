#encoding=utf-8
'''
Created on 02/05/2010

@author: lfborjas
'''
from django import forms
from django.forms.widgets import HiddenInput
from service import WEB_SERVICES

class PrototypePlanningForm(forms.Form):
    SERVICE_CHOICES=(
                     ('', 'No Service'),
                     ('alchemy', 'Alchemy'),
                     ('wordsfinder', 'WordsFinder'),
                     ('yahoo','Yahoo Extraction Service'),
                     ('tagthe', 'Tagthe content tagger'),
                     ('opencalais', 'OpenCalais'),
                     )
    content = forms.CharField(widget=forms.Textarea(), label ="Contenido")
    lang = forms.CharField(widget=HiddenInput())
    service = forms.ChoiceField(label=u"Servicio web para extracción", choices = SERVICE_CHOICES, widget=HiddenInput())

class PrototypeSettingsForm(forms.Form):
    """Settings for the widget"""
    uid = forms.CharField(label="Usuario ")
    fm = forms.ChoiceField(label="Retroalimentación", choices=[('follow', 'Implícita'), ('select', 'Explícita')])
    uw = forms.BooleanField(label="Usar widget", initial=True)