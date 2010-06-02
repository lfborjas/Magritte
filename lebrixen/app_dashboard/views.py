# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse
try:
    import jsonlib2 as json
except ImportError:
    import json
except ImportError:
    import django.utils.simplejson as json
import logging
from app_dashboard.forms import UserFormset
from profile.models import ClientUser

@login_required
def dashboard(request):
    if request.method == 'POST':
        formset = UserFormset(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                u = ClientUser(clientId = form.cleaned_data['name'], app = request.user.get_profile())
                u.save()                  
    else:
        formset  = UserFormset()
    
    return render_to_response('dashboard_index.html', 
                              {'formset': formset},
                               context_instance=RequestContext(request))

@login_required
def get_users(request):
    raw_page = render_to_string('dashboard_users.html', {'users': request.user.get_profile().users.all()})
    return HttpResponse(raw_page, mimetype="text/html")

@login_required
def remove_user(request):
    uid = request.REQUEST.get('uid', '')
    try:
        u = ClientUser.objects.get(pk=uid)
        u.delete()
        return HttpResponse(json.dumps({'id': uid, 'valid': True, 'message': ''}), mimetype="application/json")
    except:
        logging.info("Error deleting user", exc_info=True)
        return HttpResponse(json.dumps({'valid': False, 'message': 'Error deleting user'}), mimetype="application/json")
    
