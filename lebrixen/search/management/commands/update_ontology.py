#!/usr/bin/env python
#encoding = utf-8
import os
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lebrixen.settings')
import codecs
from xml.etree import cElementTree as ElementTree
from django.conf import settings
from search.models import DmozCategory

ROOT_SPEC = u"http://dmoz.org/rdf/"
r = u"http://www.w3.org/TR/RDF/"
d = u"http://purl.org/dc/elements/1.0/"
ROOT_DOMAIN = u"http://www.dmoz.org"
DESIRED_LANGS = [u'spanish',]

def populate(tree=None):
    #obtain the topic tree:
    if not tree:
        tree = ElementTree.parse(settings.ONTOLOGY_FILE)
    #get the tree root:
    root = tree.getroot()
    #now, get the topics:
    topics = root.findall('{%s}Topic' % ROOT_SPEC)
    #create an entry for all the topics:
    for topic in topics:
        id = topic.get('{%s}id' % r)
        title = topic.find('{%s}Title' % d).text
        code = topic.find('{%s}catid'%ROOT_SPEC).text
        last_update = topic.find('{%s}lastUpdate'%ROOT_SPEC).text
        description = topic.find('{%s}Description'%d).text
        es_alt = ""  
        for res in topic.findall('{%s}altlang' % ROOT_SPEC):
            lang, url = res.get('{%s}resource' % r).split(':') 
            if lang.lower() in DESIRED_LANGS :
                es_alt = url.replace(u'Top/', u'')
        #create or update the category:
        category = DmozCategory(title = title,
                                topic_id = id,
                                dmoz_code = code,
                                last_updated = last_update,
                                description = description,
                                es_alt = es_alt)
        category.save()

def set_parents(tree=None):
    if not tree:
        tree = ElementTree.parse(settings.ONTOLOGY_FILE)
    
    categories = DmozCategory.objects.all()
    #WARNING: this is a BIG query
    for category in categories:
        #get the topic in the tree which pertains to this topic:
        #NEEDS ELEMENT TREE 1.3
	topic = tree.find("{%s}Topic[@{%s}id='%s']" % (ROOT_SPEC, r,category.topic_id))
        narrow_topics = topic.findall('{%s}narrow' % ROOT_SPEC)+topic.findall('{%s}narrow1' % ROOT_SPEC) +\
                        topic.findall('{%s}narrow2' % ROOT_SPEC)
        for sub_category in narrow_topics:
            sc = DmozCategory.objects.get(topic_id = sub_category.get('{%s}resource' % r))
            sc.parent = category
            sc.save()
 
     
if __name__ == "__main__":
    t = ElementTree.parse(os.path.join(settings.DATA_PATH,'2010-03-04_science_sub-structure.rdf.u8'))
    populate(t)
    set_parents(t)


