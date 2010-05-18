#encoding=utf-8
'''
Created on 09/05/2010
author: lfborjas
'''
from __future__ import division
from django.conf import settings
from search.models import DmozCategory
from django.core.management.base import NoArgsCommand
import logging
#import guppy.heapy.RM
#from django.db.models import Count

class Command(NoArgsCommand):
    help = "Ponder the edges in the ontology graph by an inclusion statistical approximation"
    
    def handle_noargs(self, **options):
        #get the maximum number of documents any category has
        #docs = DocumentSurrogate.objects.values('category').annotate(ccount=Count('category')).iterator()        
        #maxcount = max(docs, key=lambda x: x['ccount'])['ccount']
        
        #set the utility of the categories relative to that size
        categories = DmozCategory.objects.iterator()
        c = 0
        for category in categories:             
            s = category.documentsurrogate_set.count()
            sub_categories = category.dmozcategory_set.all() 
            for sc in sub_categories:
                #if it has no documents, count the category as a document
                s += sc.documentsurrogate_set.count() or 1            
            #logging.debug("Category %s has %s documents" % (category.topic_id, s))
            for sc in sub_categories:
                sub_docs = sc.documentsurrogate_set.count()
                #give a minimum non-zero weight if this category has no documents:
                #sc.weight = sub_docs / s if sub_docs else 1 / s
                #logging.debug("From a total of %s, category %s has %s documents (%s percent)" % (s, sc.topic_id, sub_docs, sub_docs/s*100))
                sc.weight = 1 - sub_docs / s 
                sc.save()
            c += 1
        
        logging.debug("Done pondering %s categories" % c)
                

        
        
