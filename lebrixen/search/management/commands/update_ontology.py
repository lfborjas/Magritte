#!/usr/bin/env python
#encoding = utf-8
import os
import sys
#from xml.etree import cElementTree as ElementTree
import cElementTree as ElementTree
from django.conf import settings
from search.models import DmozCategory
from utilities import create_or_update
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import traceback

ROOT_SPEC = u"http://dmoz.org/rdf/"
r = u"http://www.w3.org/TR/RDF/"
d = u"http://purl.org/dc/elements/1.0/"
ROOT_DOMAIN = u"http://www.dmoz.org"
DESIRED_LANGS = [u'spanish',]

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                  make_option('--file', dest='ontology_file', default=settings.ONTOLOGY_FILE,                    
                    help='Which ontology file to use'),
                                             )
    help = "Update the ontology table"
    args = 'file'
    
    def populate(self, tree):
        #get the tree root:
        root = tree.getroot()
        #now, get the topics:
        topics = root.findall('{%s}Topic' % ROOT_SPEC)
        #create an entry for all the topics:
        for topic in topics:
            attributes={
                        'topic_id' : topic.get('{%s}id' % r),
                        'title' : topic.find('{%s}Title' % d).text,
                        'dmoz_code' : topic.find('{%s}catid'%ROOT_SPEC).text,
                        'last_updated' : topic.find('{%s}lastUpdate'%ROOT_SPEC).text,
                        'description' : topic.find('{%s}Description'%d).text,
                        'es_alt' : "", 
            }
            es_alt = "" 
            for res in topic.findall('{%s}altlang' % ROOT_SPEC):
                lang, url = res.get('{%s}resource' % r).split(':') 
                if lang.lower() in DESIRED_LANGS :
                    es_alt = url.replace(u'World/', u'')
            if es_alt:
                attributes.update({'es_alt': es_alt})
            #create or update the category:
            try:        
                category = create_or_update(attributes, {'topic_id': attributes['topic_id']}, DmozCategory)
            except Exception, e:                              
                raise CommandError(e.message)
    
    def set_parents(self, tree):
        """Given that the categories exist, set their parents"""
                
        categories = DmozCategory.objects.all()
        if not categories:
            raise CommandError('The ontology is empty!')
        #WARNING: this is a BIG query
        for category in categories:
            #get the topic in the tree which pertains to this topic:
            #NEEDS ELEMENT TREE 1.3
            topic = tree.find('{%s}Topic[@{%s}id="%s"]' % (ROOT_SPEC, r,category.topic_id))
            narrow_topics = []
            if topic:
                narrow_topics = topic.findall('{%s}narrow' % ROOT_SPEC)+topic.findall('{%s}narrow1' % ROOT_SPEC) +\
                                topic.findall('{%s}narrow2' % ROOT_SPEC)
            else:
                print "Though in database, the topic %s can't be found in the RDF" % category.topic_id
            #all of the subtopics:
            #[tree.find('{%s}Topic[@{%s}id="%s"]' % (ROOT_SPEC, r,n.get('{%s}resource' % r))) for n in narrows]
            for sub_category in narrow_topics:
                id = sub_category.get('{%s}resource' % r)
                try:
                    sc = DmozCategory.objects.get(topic_id = id)
                    sc.parent = category
                    sc.save()
                except DmozCategory.DoesNotExist:   
                    print "The category with id %s does not exist!" % id
                    pass
                
    def handle(self, ontology_file=settings.ONTOLOGY_FILE, *args, **options):
        try:
            file = open(ontology_file)
            tree = ElementTree.parse(file) 
        except Exception, e:
            raise CommandError(e.message)
            sys.exit(0)
        
        print "Parsing %s for categories" % file.name
        self.populate(tree)
                
        print "Setting the hierarchy"
        self.set_parents(tree) 
        
        print "Ontology successfully created! "
     



