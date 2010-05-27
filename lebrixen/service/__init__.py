from __future__ import division
#utility functions to support the web service
try:
    import json
except:
    import simplejson as json
from django.http import HttpResponse, HttpResponseBadRequest
from topia.termextract import extract
from django.utils.html import strip_tags
from urllib2 import urlopen
from django.utils.http import urlencode
from django.conf import settings
from xml.dom.minidom import parseString
import re
import logging
from django.utils.encoding import smart_unicode
import re, htmlentitydefs
from calais import Calais
from extractor import ExtractorService
import validate_jsonp
from django.utils.encoding import smart_unicode
from django.core.exceptions import ObjectDoesNotExist
#some more listed here: http://en.wikipedia.org/wiki/Term_extraction
#and here: http://maui-indexer.blogspot.com/2009/07/useful-web-resources-related-to.html
#and here: http://stackoverflow.com/questions/1100549/term-extraction-generatings-tags-out-of-text
#also here: http://faganm.com/blog/2010/01/02/1009/
#and here!: http://fivefilters.org/term-extraction/
WEB_SERVICES = {
    #http://www.alchemyapi.com/api/keyword/textc.html
    'alchemy': 'http://access.alchemyapi.com/calls/text/TextGetRankedKeywords',
    #http://wordsfinder.com/api_Keyword_Extractor.php
    'wordsfinder': 'http://www.wordsfinder.com/extraction/api1.php',
    #http://developer.yahoo.com/search/content/V1/termExtraction.html
    'yahoo': 'http://search.yahooapis.com/ContentAnalysisService/V1/termExtraction',
    #http://tagthe.net/fordevelopers
    'tagthe': 'http://tagthe.net/api/',
    #http://www.opencalais.com/documentation/calais-web-service-api/
    'opencalais': 'http://api.opencalais.com/enlighten/rest/',
    #http://www.picofocus.com/DemoEngine/dbiExtractorDemoWebService.asmx?op=ProcessXtraction
    'extractor': 'http://www.picofocus.com/DemoEngine/DBIExtractorDemoWebService.asmx',
}

class WebServiceException(Exception):
    def __init__(self, service, msg):
        self.service = service
        self.msg= msg
    def __str__(self):
        return "An error ocurred with a call to %s: %s" % (self.service, self.msg)

def json_view(func):
	"""
		Decorator for web-service views: takes the request and json-izes it, and
		also takes any response that is not a direct HttpResponse and json-izes it
		taken from: http://andrewwilkinson.wordpress.com/2009/04/08/building-better-web-services-with-django-part-1/
	"""
	def wrap(req, *args, **kwargs):
		try:
		    j = json.loads(req.raw_post_data)
		except ValueError:
		    #this means that the necessary data is in the request.REQUEST
		    #j = None
		    j = req.REQUEST or None

		resp = func(req, j, *args, **kwargs)

		if isinstance(resp, HttpResponse):
		    return resp

		return HttpResponse(json.dumps(resp, ensure_ascii=False), mimetype="application/json")

	return wrap

def _sanitize_text(raw_text):
    """
        Does whatever is needed to get just unicode text from the input
    """
    return smart_unicode(strip_tags(raw_text.strip()))

def unescape(text):
    """

    Removes HTML or XML character references and entities from a text string.
    retrieved from: http://effbot.org/zone/re-sub.htm#unescape-html

     @param text The HTML (or XML) source text.
     @return The plain text, as a Unicode string, if necessary.
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return unicode(re.sub("&#?\w+;", fixup, text))

def web_extract_terms(text, raw_query='',service='yahoo'):
    """
        Given a text, extract keyword terms with the selected web_service.
        Args:
            text: raw text from where to extract terms
            query: a query which may contextualize the extraction (only used by yahoo)
            service: which web service to use
        Returns:
            query: a sequence of query terms

    """
    service = service.lower().strip()

    if not service in WEB_SERVICES.keys():
        raise Exception('%s is an invalid web service, possible choices are %s' % (service, repr(WEB_SERVICES.keys())))

    #1. Build the query:
    query = {}
    apikey = settings.WEB_SERVICES_KEYS.get(service, '')

    if service == 'wordsfinder':
        query = {
            'apikey' : apikey,
            'context': text + raw_query,
        }
    elif service == 'alchemy':
        query = {
            'apikey' : apikey,
            'text' : text + raw_query,
            'outputMode' : 'json'
        }
    elif service == 'yahoo':
        query = {
            'appid': apikey,
            'context': text,
            'output': 'json',
        }
        if raw_query:
            query.update({'query': raw_query})
    elif service == 'tagthe':
        query = {
            'text': text + raw_query,
            'view': 'json',
        }
    elif service == 'opencalais':
        #use the python interface, obtained from:
        #http://www.opencalais.com/applications/python-calais-python-interface-opencalais-api
        logging.debug('Using the opencalais interface with key %s' % apikey)
        s = Calais(apikey)
        res = s.analyze(text + raw_query)
        logging.debug('The raw response: %s'  % res.raw_response)
        if hasattr(res, 'topics') or hasattr(res, 'entities'):
            retval = [t['categoryName'] for t in res.topics] if hasattr(res, 'topics') else []
            retval += [t['name'] for t in res.entities] if hasattr(res, 'entities') else []
            return retval
        else:
            #raise WebServiceException(service, 'No topics or entities found')
            logging.info("OpenCalais didn't return topics|entities for %s" %text)
            return ["",]
    elif service == 'extractor':
        #use the python interface
        logging.debug('using the extractor interface with key %s' % apikey)
        extractor=ExtractorService(key=apikey, url=WEB_SERVICES[service])
        raw_response = extractor.extract(text + raw_query)
        logging.debug('The raw response: %s' % raw_response)

        if raw_response.get('ExtractionStatus') == '-1':
            print "failure!"
            raise WebServiceException(service, "Failure in request")
        else:
            #TODO: what DOES it return?
            return raw_response



    #2. Try to call the service:
    resp = None
    logging.debug('requesting %s' % WEB_SERVICES[service]+'?%s'%urlencode(query))
    try:        
        resp_url = urlopen(WEB_SERVICES[service], urlencode(query))
        resp = resp_url.read()
        #this causes the exception...
        logging.debug( u"%s returned %s" % (service, resp))        
    except Exception as e:
        #TODO: retry in timeouts and stuff
        logging.debug('Error in request: %s' % e)
        pass
            
    #3. Process the response:    
    if resp:
        result = ''
        if service == 'alchemy':
            data = json.loads(resp)
            if data['status'] == 'ERROR':
                raise WebServiceException(service, 'call returned error status')
            result = [re.sub('-[^ ] ', '', e['text']) for e in data['keywords']]
            
        elif service == 'yahoo':
            data = json.loads(resp)
            result = data['ResultSet']['Result']

        elif service == 'wordsfinder':
            parsed_response = parseString(resp)
            e = parsed_response.getElementsByTagName('error')
            if e:
                raise WebServiceException(service, 'error code %s' % e.firstChild.datad)
            else:
                result = [node.firstChild.data for node in parsed_response.getElementsByTagName('keyword')]
        elif service == 'tagthe':
            data = json.loads(resp)
            if 'memes' in data and 'dimensions' in data['memes'][0] and 'topic' in data['memes'][0]['dimensions']:
                result = data['memes'][0]['dimensions']['topic']
            else:
                raise WebServiceException(service, "The data didn't contain the topics!")
            

        return [unescape(w) for w in result]


    # TODO: maybe find a way to call 'em all and have a super-set of kws?
    else:
        return ''

def build_query(text, extra_query='', language='', use_web_service = False, web_service='yahoo'):
    """
        Given raw text and a language, build a query to submit to the search engine.
        The use of a web service is optional only for english. For other languages,
        a web service will be used regardless of the use_web_service param.
    """
    query_terms = []
    #sanitize the text (remove html tags and convert it to unicode)
    text = _sanitize_text(text)
    extra_query = _sanitize_text(extra_query)
    
    #process english language queries, use the topia.termextract utility
    if 'en' in language.lower() and not use_web_service:
        #currently, there's a bug in the topia software which initializes incorrectly if
        #another tagger is passed in the constructor
        extractor = extract.TermExtractor()
        #tweak the extractor filter:
        extractor.filter = extract.permissiveFilter
        #extract terms from the text:
        query_tuples = extractor(text)
        #the extractor returns tuples, we only need strings:
        logging.debug("Topia term extractor suggested: %s" % query_tuples)
        query_terms = [e[0] for e in query_tuples]
    else:
        #if not in english, use a webservice to get the terms:
        query_terms = web_extract_terms(text, extra_query, service=web_service)

    return extra_query + u' '.join(query_terms)

     
def jsonp_view(v):
    """Decorator, make a function return a jsonp compatible result
	
	    Given a regular view, find a callback in it's request and return
        the result value wrapped in the callback function. 
		
		Args:
			A regular django view that returns a json string
		
		Returns:
			An HttpResponse with the same body as the original, but wrapped
			in a call to the callback function
     """
     
    def jsonp_transform(request, *args, **kwargs):
        response = v(request, *args, **kwargs)
        #assert isinstance(response, HttpResponse), "The function MUST return an HttpResponse object"
        if 'callback' in request.REQUEST and response.status_code == 200:
            cb = request.REQUEST['callback']            
            response['Content-type'] = 'application/json'
            if not validate_jsonp.is_valid_jsonp_callback_value(cb):
                return HttpResponse(json.dumps({'valid': False, 'message': '%s is not a valid jsonp callback identifier' % cb,
                                                'status': 400}),
                                     mimetype='application/json')
            response.content = (u'%s(%s)' % (cb, response.content.decode('utf-8')))            
            return response
        elif 'callback' in request.REQUEST and response.status_code >= 400: #is an error
            return HttpResponse(json.dumps({'valid': False, 'message': response.content, 'status': response.status_code}),
                                 mimetype='application/json')
        else:    
            return HttpResponse(json.dumps({'valid': False, 'message': 'No jsonp callback provided'}), mimetype='application/json')
    
    return jsonp_transform

def api_call(v):
    """Checks that the request contains the REST-ful parameters and returns a json or a jsonp."""   
    
    from profile import APP_ID, PROFILE_ID
    def api_validate(request, *args, **kwargs):
        
        cb = ''
        if 'callback' in request.REQUEST:
            cb = request.REQUEST['callback']            
            if not validate_jsonp.is_valid_jsonp_callback_value(cb):
                return HttpResponseBadRequest('%s is not a valid jsonp callback identifier' % cb,
                                     mimetype='text/plain')
                        
        if not (APP_ID in request.REQUEST and PROFILE_ID in request.REQUEST):
            retval = json.dumps({'valid': False,
                                 'message': 'Both %s and %s must be provided in this call' % (APP_ID, PROFILE_ID),
                                 'status': 400})
            if cb:
                retval = '%s(%s)' % (cb, retval)
            
            return HttpResponse(retval, mimetype='application/json')
            
        else:  #has the params                      
            response = v(request, *args, **kwargs)           
                                    
            if response.status_code < 400: #not error:
                if cb: 
                    response.content = (u'%s(%s)' % (cb, response.content.decode('utf-8')))            
                return response
            else: #somehow invalid:
                retval = json.dumps({'valid': False, 'message': response.content, 'status': response.status_code})
                if cb:
                    retval = '%s(%s)' % (cb, retval)
                    
                return HttpResponse(retval,mimetype='application/json')
    
    return api_validate
    
PENALTY = 0.3 #as recommended in Daoud2008
def re_rank(profile, results):
    """Based on the profile preferences, re-rank the results"""    
    for result in results:
        interest_score = 0.0
        try:
            interest_score = profile.preferences.get(category__pk=result['category']).score
        except ObjectDoesNotExist:
            interest_score = 0.0 #though Daoud searches for the best match, I need speed, so if it's not there, just zero it
        #The first term is the original score, attenuated by the penalty constant
        #the second is the contextual score (the user preference), boosted by the penalty inverse
        #thus, it gives preference to those results with a non-zero interest score.
        #Though the original paper is more lax in the contextual score, I assume that only past preferred categories are worth boosting
        result['weight'] = PENALTY * (result['percent']/100) + (1-PENALTY)*interest_score
        
    #re-order them     
    return sorted(results, key= lambda x: x['weight'])        


