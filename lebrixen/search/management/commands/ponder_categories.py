'''
Created on 09/05/2010

@author: lfborjas
'''
from __future__ import division
from django.conf import settings
from search.models import DmozCategory, DocumentSurrogate
from django.core.management.base import NoArgsCommand, CommandError
import logging
from django.db.models import Count

class Command(NoArgsCommand):
    help = "Update the category classifier"
    
    def handle_noargs(self, **options):
        #get the maximum number of documents any category has
        docs = DocumentSurrogate.objects.values('category').annotate(ccount=Count('category')).iterator()
        maxcount = max(docs, key=lambda x: x['ccount'])['ccount']
        
        #set the utility of the categories relative to that size
        categories = DmozCategory.objects.iterator()
        for category in categories: 
            category_docs = category.documentsurrogate_set.count()
            category.weight = 1 / (maxcount / category_docs) if category_docs else 0
            category.save()

        
        
