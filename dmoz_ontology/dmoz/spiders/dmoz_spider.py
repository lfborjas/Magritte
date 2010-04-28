#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
#from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import BaseSpider
from dmoz.items import DmozItem, DmozResource
from scrapy.conf import settings
from scrapy.http import Request
import time
import os
ROOT_DOMAIN= "http://www.dmoz.org/"
ROOT_PATH = os.path.join(settings.get('ROOT_PATH'),'spiders')
def find_lang(url):
	m = re.match(r'.*/World/(?P<lang>\S+)/.*', url)
	if m and m.groups('lang'):
		return m.groups('lang')[0]

class DmozSpider(BaseSpider):
    domain_name = 'dmoz.org'

    if settings.get('IS_TEST'):
	urls = open(os.path.join(ROOT_PATH, 'test_topic_urls'), 'r')
    else:
	urls = open(os.path.join(ROOT_PATH, 'topics_urls'), 'r')

    def start_requests(self):
	for url in self.urls:
		url = url.strip()
		if url:
			self.log('returning "%s" as url' % url)
			yield Request(url.replace('\n', ''), callback=self.parse_starters)
	
    def parse_starters(self, response):
	""" Find the resources and download them, if they exist"""	
	xs = HtmlXPathSelector(response)
	resources = xs.select('//ul[2]/li') + xs.select('//ul[1]/li')
	#rlist = []
	for resource in resources:
		description = resource.select('text()').extract()
		title = resource.select('a/text()').extract()
		link =  resource.select('a/@href').extract()
		#path = str(response.url).replace(ROOT_DOMAIN, '')i
		#TODO: make this sensible to any lang
		#lang = 'es' if u'World/Español' in str(response.url) else 'en'
		#only allow outgoing links:
		if link and title:
			#self.log('%s info: %s, %s' % (response.url, title, link))
			f = lambda r, desc = description, name = title: self.parse_item(r,
					 name = name[0],
					 lang = 'es' if u'World/Español' in str(response.url) else 'en', 
					 category = str(response.url).replace(ROOT_DOMAIN, ''),
					 desc = desc[0] if len(desc) else '')
			#rlist += [Request(link[0], callback= f),]
			yield Request(link[0], callback= f)
	
	#return rlist
				

    def parse_item(self, response, name='',lang='en', category = '', desc = ''):
	i = DmozResource()
	i['category'] = category
	i['name'] = name
	i['url'] = response.url
	i['type'] = 'pdf' if 'pdf' in response.url.strip()[-4:].lower() else 'html'
	i['description'] = desc
	i['retrieved_on'] = time.asctime()
	i['lang'] = lang
	if hasattr(response, 'body_as_unicode'):
		self.log("%s returned a unicode-able body" % response.url)
		i['content'] = response.body_as_unicode()
	else:
		self.log("%s DID NOT return a unicode-able body" % response.url)
		i['content'] = response.body
        return i

SPIDER = DmozSpider()
