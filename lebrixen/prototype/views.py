# Create your views here.
from forms import PrototypePlanningForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
def index(request):
    """Index view for the prototype page"""
    return render_to_response('prototype_base.html',
                               {'form':PrototypePlanningForm(initial={'lang': 'en'})},
                                context_instance=RequestContext(request))