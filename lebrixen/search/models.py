from __future__ import division
from django.db import models
from time import asctime
from django.conf import settings
import xappy
import logging
# Create your models here.
class DocumentSurrogate(models.Model):
    DOCTYPES =(
               ('pdf', 'Portable Document Format (pdf)'),
               ('html', 'Hypertext Markup Language File (html)'),
               )
    title = models.CharField(max_length=255, db_index = True)
    origin = models.URLField(blank = True, default="", max_length=512, db_index = True)
    summary = models.TextField(blank = True, default="")
    text = models.TextField(blank = True, default="")
    added = models.DateTimeField(null=True, default=asctime)
    lang = models.CharField(max_length = 10, default = 'en')
    category = models.ForeignKey('DmozCategory', null = True)
    type = models.CharField(max_length=10, choices=DOCTYPES)
    def __unicode__(self):
        return self.title #+ self.summary
    
    def get_stemming_lang(self):
        return self.lang
     
class DmozCategory(models.Model):
    """Based loosely on the structure of the dmoz RDF dump"""
    title = models.CharField(max_length = 255, blank= True, default = "") 
    topic_id = models.CharField(max_length = 320, db_index = True)
    dmoz_code = models.IntegerField(null = True)
    last_updated = models.DateTimeField(null = True)
    description = models.TextField(null = True)
    parent = models.ForeignKey('self', null = True)
    es_alt = models.CharField(max_length = 320, blank = True, default = "") #the alternate in spanish
    weight = models.FloatField(null = True, default = 0.0) #the intrinsic weight
    
    #def _get_relative_weight(self, rank):
    #    return self.weight * rank

    @classmethod
    def get_for_query(cls, query, lang='en', as_dict=False, max_results = 5):
        """Given a query, find out to which categories it most probably belongs to, 
           with the weights relative to the query calculated"""
        
        #cf. http://xappy.org/docs/0.5/introduction.html
        
        s_conn = xappy.SearchConnection(settings.CATEGORY_CLASSIFIER_DATA)
        #TODO: use a setting for this:
        lang = lang if lang in ['en', 'es'] else 'en'
        #query = s_conn.spell_correct(query, allow=['%s_text'%lang,])
        xapian_query = s_conn.query_field('%s_text' % lang, query)
        results = s_conn.search(xapian_query, 0, max_results) #only search the best matches
        rval = {}
        logging.debug("Categories matching %s" % query)
        for result in results:            
            logging.debug("Category: %s, relevance: %s, id: %s" % (result.data['category_title'], result.percent, result.data['category_id']))
            #rval += [{'category_id': result.data['category_id'],
            #          'category_title': result.data['category_title'],
            #          'relevance': result.rank},]
            rval.update({int(result.data['category_id'][0]): result.weight/100})
        
        s_conn.close()
        if not rval:
            logging.debug("No categories match query %s" % query)
            return None
            #TODO: try correcting spelling ?
        if as_dict:
            return rval
        #get the categories and set their weight relative to the query:
        categories = cls.objects.filter(pk__in = rval.keys())
        #[setattr(category, 'relative_weight', (rval[category.pk]) * category.weight) for category in categories]
        #for category in categories:
        #    category.relative_weight = rval[category.pk] * category.weight
         
        return categories
             
    def __unicode__(self):
        return u"%s (%s)" %(self.title, self.topic_id)
        
    def get_parents(self):
        parent = self.parent
        while parent:
            p= parent
            parent = p.parent
            yield p.pk
                