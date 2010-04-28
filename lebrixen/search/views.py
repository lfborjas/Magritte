# Create your views here.
from search.index import DocumentIndexer
from django.http import HttpResponse, HttpResponseBadRequest
try:
    import libjson2 as jsonlib
except ImportError:
    import simplejson as jsonlib

def search_docs(request):
    """Search documents and return a json with the result set"""
    if not 'q' in request.REQUEST:
        return HttpResponseBadRequest()
    
    query = request.REQUEST.get('q')
    #the language defaults to english
    lang = request.REQUEST.get('hl') or 'en'
    
    #search:
    search_results = DocumentIndexer.search(query, lang).prefetch()
    
    #serialize:
    return HttpResponse(jsonlib.dumps(search_results, ensure_ascii=False), mimetype="")
    
    
        