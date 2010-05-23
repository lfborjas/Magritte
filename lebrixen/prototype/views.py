# Create your views here.
from forms import PrototypePlanningForm, PrototypeSettingsForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
def index(request):
    """Index view for the prototype page"""
    feedbackMode = request.GET.get('fm', 'follow')
    userId = request.GET.get('uid', 'testUser')
    useWidget = request.GET.get('uw', False)
    return render_to_response('prototype_base.html',
                               {'form':PrototypePlanningForm(initial={'lang': 'en'}),
                                'settings_form': PrototypeSettingsForm(initial={'fm': feedbackMode, 'uid': userId, 'uw':useWidget}),
                                'uid': userId,
                                'fm': feedbackMode,
                                'uw': useWidget},
                                context_instance=RequestContext(request))
