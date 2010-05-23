# Create your views here.
from register.forms import RegisterForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.template.loader import render_to_string
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']            
            recipient = form.cleaned_data['mail']
            key = form.cleaned_data['app'].get_token()
            message = render_to_string('mail/appkey.html', {'key': key,
                                                            'url': request.build_absolute_uri('/usage/')})
            send_mail(
                'Your T-Recs App key',
                message, 'noreply@trecs.com',
                [recipient, ]
            )
            return HttpResponseRedirect('/usage/')
        else:
            return render_to_response('trecs_register.html', {'form': form})
    else:
        form = RegisterForm()
    return render_to_response('trecs_register.html', {'form': form})