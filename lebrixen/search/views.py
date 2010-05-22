# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest
try:
    import libjson2 as jsonlib
except ImportError:
    import json as jsonlib
from search.models import DocumentSurrogate
from django.core.serializers import serialize
import logging
import xapian
from service import re_rank

def do_search(query, lang='en'):
    """Abstract the search mechanism from the view"""
    indexer = DocumentSurrogate.indexer
    #logging.debug('Using indexer %s' % indexer)     
    search_results = indexer.search(query).prefetch()[:20]
    #logging.debug('ResultSet %s for query %s' % (search_results, query))
    #search_results._stemming_lang=lang    
    #serialize:
    return [{'id': hit.instance.pk,
                           'title': unicode(hit.instance.title),
                           'summary': unicode(hit.instance.summary),
                           'url': hit.instance.origin,                           
                           'percent': hit.percent,
                           'category': hit.instance.category.pk} for hit in search_results]
                           

def search_docs(request, re_rank = True):
    """Search documents and return a json with the original result set and a re-ranked version"""
    if not 'q' in request.REQUEST:
        return HttpResponseBadRequest()
    
    query = request.REQUEST.get('q')
    #the language defaults to english
    lang = request.REQUEST.get('hl') or 'en'
    
    #search: assume the results are already json encoded    
    results = do_search(query, lang)
    reranked =  re_rank(request.profile, results)   
    return HttpResponse(jsonlib.dumps({'results': results,
                                       'reranked': reranked}, ensure_ascii=False), mimetype="application/json")
    
    
    
        
