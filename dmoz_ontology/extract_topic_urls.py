#!/usr/bin/env python
#encoding = utf-8
import codecs
from xml.etree import cElementTree as ElementTree
ROOT_SPEC = u"http://dmoz.org/rdf/"
GEN_SPEC = u"http://www.w3.org/TR/RDF/"
ROOT_DOMAIN = u"http://www.dmoz.org"
DESIRED_LANGS = [u'spanish',]

#obtain the topic tree:
tree = ElementTree.parse('2010-03-04_science_sub-structure.rdf.u8')

#get the tree root:
root = tree.getroot()
#now, get the topics:
topics = root.findall('{%s}Topic' % ROOT_SPEC)
print "Found %d topics" % len(topics)

#for each topic, save the link and the link to the alternate topics, if they exist
urls_file = codecs.open('topics_urls', 'w', 'utf-8')
print "writing urls to file..."
for topic in topics:
	urls_file.write(u"%s/%s/\n" % (ROOT_DOMAIN, topic.get('{%s}id' % GEN_SPEC).replace('Top/', '')))
	for res in topic.findall('{%s}altlang' % ROOT_SPEC):
		lang, url = res.get('{%s}resource' % GEN_SPEC).split(':') 
		if lang.lower() in DESIRED_LANGS :
			url = url.replace(u'Top/', u'')
			urls_file.write(u"%s/%s/\n"%(ROOT_DOMAIN, url))
urls_file.close()
	
