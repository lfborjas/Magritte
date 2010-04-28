# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy.conf import settings
from scrapy.core.exceptions import NotConfigured
from scrapy.contrib.exporter import jsonlines
import re
import os
from scrapy.contrib.exporter import BaseItemExporter
try:
	import json
except:
	import simplejson as json

ROOT_PATH = settings.get("ROOT_PATH")
MAX_FILENAME_LENGTH = 4096
import codecs

if not ROOT_PATH:
	raise NotConfigured('A root path MUST be provided in settings!')

class DmozPipeline(object):
	def __init__(self):
		self.exporter = BaseItemExporter()
	
	def process_item(self, domain, item):
	        """Store the item, serialized as json, in a file within a directory hierarchy corresponding to it's
		   place in the ontology
	        """
        	#the path is of the form: cat/subcat/leaf
	        filedir = os.path.join(ROOT_PATH,'Top',item['category'])	
		#Store the contents in files apart (to optimize the json loadings)
		pdfdir = os.path.join(ROOT_PATH,'PDF')	 
		htmldir = os.path.join(ROOT_PATH,'HTML')	 
		if not os.path.isdir(pdfdir):
			os.makedirs(pdfdir)
		if not os.path.isdir(htmldir):
			os.makedirs(htmldir)
		#replace evil characters for an underscore 
		#cf. http://www.linfo.org/file_name.html
		rawname = re.sub('[ /.$%]+','_',item['name'])
		filename = os.path.join(filedir, rawname)
		#truncate the filename if it exceeds the permitted maximum...
		filename = filename if len(filename) <= MAX_FILENAME_LENGTH else filename[:MAX_FILENAME_LENGTH]
		if item['type'] == 'pdf':
			#content_str = "%s.pdf" % filename.replace(filedir, pdfdir)
			content_str = os.path.join(pdfdir, rawname+".pdf")
			temp = open(content_str, 'wb')
		else:
			#content_str = "%s" % filename.replace(filedir, htmldir)
			content_str = os.path.join(htmldir, rawname)
			temp = codecs.open(content_str, 'w', 'utf-8')
		temp.write(item['content'])
		temp.close()	
		item['content'] = content_str
			
		if not os.path.isdir(filedir):
			os.makedirs(filedir)
		file = open(filename, 'w')
		itemdict = dict(self.exporter._get_serialized_fields(item))
		json.dump(itemdict, file)
		file.close()
		return item
		
       	
