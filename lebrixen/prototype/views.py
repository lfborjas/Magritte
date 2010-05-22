# Create your views here.
from forms import PrototypePlanningForm, DemoToolsForm, DemoSimulationForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from profile.models import ClientApp
import logging

try:
    import jsonlib2 as json
except ImportError:
    import json
except ImportError:
    import django.utils.simplejson as json

def index(request):
    """Index view for the prototype page"""
    feedbackMode = request.GET.get('fm', 'follow')
    userId = request.GET.get('uid', 'testUser')
    return render_to_response('prototype_base.html',
                               {'form':PrototypePlanningForm(initial={'lang': 'en'}),
                                'uid': userId,
                                'fm': feedbackMode},
                                context_instance=RequestContext(request))

def demo(request):
    """The internals demo page"""
    return render_to_response('demo_base.html',
                               {'tools_form':DemoToolsForm(),
                                'simulation_form': DemoSimulationForm()},
                                context_instance=RequestContext(request))

def _get_profile_graph(profile):
    """Get a graphical representation of a profile's graph"""
    #only generate the graph request, I'll let the JS ask for it in google
    #async    
    return "<img src='/static/images/nograph.png' />"

def set_profile(request):
    """Temporal, only for the demo; circumvent the jsonp convention and just get the user's graph
    
       This view can only be called from the same domain, if it is a jsonp call, it will fail, so, 
       that's kinda secure.        
    """
    if hasattr(request, 'profile'):        
        graph = _get_profile_graph(request.profile)
        return HttpResponse(json.dumps({'graph_request': graph}), mimetype='application/json')
    else:
        return HttpResponseBadRequest('No profile could be set')
    
def get_users(request):
    """Given an app, get it's users"""
    if not 'appId' in request.REQUEST:
        return HttpResponseBadRequest()
    else:
        app= ClientApp.get_for_token(request.REQUEST['appId'])
        return HttpResponse(json.dumps([{'k': e.clientId, 'val': e.clientId} for e in app.users.iterator()], 
                                       ensure_ascii=False), mimetype="application/json") 