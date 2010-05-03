'''
Created on 02/05/2010

@author: lfborjas
'''

from django import forms
from django.forms.widgets import HiddenInput

class PrototypePlanningForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea())
    lang = forms.CharField(widget=HiddenInput())