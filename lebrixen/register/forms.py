from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from recaptcha.client import captcha
from django import forms
from django.conf import settings
from django.forms.util import ErrorList
import logging

class ReCaptchaWidget(forms.widgets.Widget):
        """
            A widget to display a recaptcha field
        """
        recaptcha_challenge_name = 'recaptcha_challenge_field'
        recaptcha_response_name = 'recaptcha_response_field'
    
        def render(self, name, value, attrs=None):
            return mark_safe(u'%s' % captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY))
    
        def value_from_datadict(self, data, files, name):
            return [data.get(self.recaptcha_challenge_name, None), 
                data.get(self.recaptcha_response_name, None)]
            
class ReCaptchaField(forms.CharField):
        default_error_messages = {
            'captcha_invalid': u'Invalid captcha'
        }
    
        def __init__(self, *args, **kwargs):
            self.widget = ReCaptchaWidget
            self.required = True
            super(ReCaptchaField, self).__init__(*args, **kwargs)
    
        def clean(self, values):
            super(ReCaptchaField, self).clean(values[1])
            recaptcha_challenge_value = smart_unicode(values[0])
            recaptcha_response_value = smart_unicode(values[1])
            check_captcha = captcha.submit(recaptcha_challenge_value, 
                recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
            if not check_captcha.is_valid:
                raise forms.util.ValidationError(self.error_messages['captcha_invalid'])
            return values[0]

class RegisterForm(forms.Form):
    url = forms.CharField(label="Your app's url/name")
    mail = forms.EmailField(label="E-mail", help_text="Write a valid email, we will send your app key there!")
    recaptcha = ReCaptchaField(label="Are you human enough?")
    
    def clean(self):
        from profile.models import ClientApp
        from django.contrib.auth.models import User
        """Register the app"""
        super(RegisterForm, self).clean()        
        if any(self.errors):
            return self.cleaned_data
        if ClientApp.objects.filter(url__iexact=self.cleaned_data['url']).count() > 0:
            self._errors['url']=ErrorList(['There is an app with that name already registered',])
            del self.cleaned_data['url']
        else:
            key = ""
            try:
                app = ClientApp(url=self.cleaned_data['url'])
                app.save()                
                key = app.get_token()
                
                raw_pass = User.objects.make_random_password()
                u = User.objects.create_user(app.url, self.cleaned_data['mail'], raw_pass)
                u.save()                                           
                #logging.debug('pass for %s: %s' % (app.url, raw_pass))
                app.user = u
                app.save()
                self.cleaned_data['key'] = key
                self.cleaned_data['pass']= raw_pass
            except:
                pass
            return self.cleaned_data