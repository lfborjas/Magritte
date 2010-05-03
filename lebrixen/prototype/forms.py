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
    content = forms.CharField(widget=forms.Textarea())
    lang = forms.CharField(widget=HiddenInput())
    service = forms.ChoiceField(label="Web Service for extraction", choices = SERVICE_CHOICES)