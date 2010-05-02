# Create your views here.
from search.index import DocumentIndexer
from django.http import HttpResponse, HttpResponseBadRequest
try:
    import libjson2 as jsonlib
except ImportError:
    import json as jsonlib
from search.models import DocumentSurrogate
from django.core.serializers import serialize

def search_docs(request):
    """Search documents and return a json with the result set"""
    if not 'q' in request.REQUEST:
        return HttpResponseBadRequest()
    
    query = request.REQUEST.get('q')
    #the language defaults to english
    lang = request.REQUEST.get('hl') or 'en'
    
    #search:
    indexer = DocumentSurrogate.indexer
    search_results = indexer.search(query, lang).prefetch()
    
    #serialize:
    return HttpResponse(jsonlib.dumps([hit for hit in search_results], ensure_ascii = False), mimetype="application/json")
    
    
        