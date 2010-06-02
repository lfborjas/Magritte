'''
Created on 01/06/2010

@author: lfborjas
'''
from django import forms
from django.forms.formsets import formset_factory

class UserForm(forms.Form):
    name = forms.CharField(max_length=320)
    
UserFormset = formset_factory(UserForm)