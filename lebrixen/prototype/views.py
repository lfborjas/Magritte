# Create your views here.
from prototype.forms import PrototypePlanningForm, DemoToolsForm, DemoSimulationForm, PrototypeSettingsForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from profile.models import ClientApp
import logging
from django.utils.translation import check_for_language

try:
    import jsonlib2 as json
except ImportError:
    import json
except ImportError:
    import django.utils.simplejson as json
from django.utils.http import urlencode
from django.conf import settings
import os
DEFAULT_APP = {'key': "2f8c6f5b6f58aef9f371a2ff06d6fc20",
               'user': 'veteran'}

def index(request):
    """Index view for the prototype page"""
    feedbackMode = request.GET.get('fm', 'follow')
    userId = request.GET.get('uid', DEFAULT_APP['user'])
    useWidget = request.GET.get('uw', True)
    appId = request.GET.get('appId', DEFAULT_APP['key'])
    lang = request.REQUEST.get('lang', request.LANGUAGE_CODE)
    if hasattr(request, 'session') and check_for_language(lang):
        request.session['django_language'] = lang
    return render_to_response('prototype_base.html',
                               {'form':PrototypePlanningForm(initial={'lang': 'en'}),
                                'settings_form': PrototypeSettingsForm(initial={'fm': feedbackMode, 'uid': userId, 'uw':useWidget,
                                                                                'appId': appId, 'lang':lang}),
                                'uid': userId,
                                'fm': feedbackMode,
                                'uw': useWidget,
                                'appId': appId,
                                'lang': lang},
                                context_instance=RequestContext(request))

def demo(request):
    """The internals demo page"""
    return render_to_response('demo_base.html',
                               {'tools_form':DemoToolsForm(),
                                'simulation_form': DemoSimulationForm(initial={'hl': request.LANGUAGE_CODE})},
                                context_instance=RequestContext(request))

def _get_profile_graph(profile, use_google=False):
    """Get a graphical representation of a profile's graph
    
       Uses the GraphViz DOT language: http://www.graphviz.org/doc/info/lang.html
    """
    #only generate the graph request, I'll let the JS ask for it in google
    #async    
    base_call = "http://chart.apis.google.com/chart"
    graph_data=""
    for pref in profile.preferences.iterator():
        #create the individual node:
        par_data= r'"%s\n%s"' % (pref.category.title, pref.score * 100)        
        #add the edges with it's children:
        if profile.preferences.filter(category__parent=pref.category).count() > 0:
            for sub_pref in profile.preferences.filter(category__parent=pref.category).iterator():
                graph_data += r'%s--"%s\n%s"[type=s];' % (par_data, sub_pref.category.title, sub_pref.score * 100)
        else:
            graph_data += r'%s;' % par_data
        
    graph=r"graph{%s}" % graph_data     
    if not graph_data:
        return '/static/images/nograph.png'
    else:
        #ils ont des restrictions: http://code.google.com/intl/es/apis/chart/docs/chart_params.html#gcharts_chs
        if use_google and len(graph+base_call+"?cht=gv&chl=")<2048: #for the URI restrictions in browsers
            return '%s?cht=gv&chl=%s' % (base_call, graph.replace('"', '%22'))
        else:
            #create a static doc:
            try:
                name = ("%s/images/%s" % (settings.STATIC_DOC_ROOT, profile)).replace(' ', '_').replace('.', '_')
                f = open(name+".dot", 'w')
                f.write(graph)
                f.close()
                os.system(' '.join(["dot", "-Tpng", "-o", name+".png", name+".dot"]))
                return name.replace(settings.ROOT_PATH, '')+".png"                                 
            except:
                logging.debug("error creating graph", exc_info=True)
                return '/static/images/error.png'
                
        
        
        

def set_profile(request):
    """Temporal, only for the demo; circumvent the jsonp convention and just get the user's graph
    
       This view can only be called from the same domain, if it is a jsonp call, it will fail, so, 
       that's kinda secure.        
    """
    if hasattr(request, 'profile'):        
        graph = _get_profile_graph(request.profile)
        return HttpResponse(json.dumps({'graph': graph}), mimetype='application/json')
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
