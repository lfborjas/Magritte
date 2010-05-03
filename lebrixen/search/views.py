# Create your views here.
from search.index import DocumentIndexer
from django.http import HttpResponse, HttpResponseBadRequest
try:
    import libjson2 as jsonlib
except ImportError:
    import json as jsonlib
from search.models import DocumentSurrogate
from django.core.serializers import serialize
import logging

def do_search(query, lang):
    """Abstract the search mechanism from the view"""
    indexer = DocumentSurrogate.indexer
    logging.debug('Using indexer %s' % indexer)
    search_results = indexer.search(query).prefetch()
    logging.debug('ResultSet %s' % search_results)
    search_results._stemming_lang=lang    
    #serialize:
    return jsonlib.dumps([{'id': hit.instance.pk,
                           'title': hit.instance.title,
                           'summary': hit.instance.summary,
                           'url': hit.instance.origin,
                           'match': hit.percent,
                           'rank': hit.rank, } for hit in search_results],
                           ensure_ascii=False)

def search_docs(request):
    """Search documents and return a json with the result set"""
    if not 'q' in request.REQUEST:
        return HttpResponseBadRequest()
    
    query = request.REQUEST.get('q')
    #the language defaults to english
    lang = request.REQUEST.get('hl') or 'en'
    
    #search: assume the results are already json encoded
    results = do_search(query, lang)    
    return HttpResponse(results, mimetype="application/json")
    
    
    
        