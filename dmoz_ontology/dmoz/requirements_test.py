#! /usr/bin/env python

print "Checking version..."
req_version = 2.6
try:
	import platform
except ImportError:
	print "Your python is TOO old (<=2.3)"	
	sys.exit(0)
if not float(platform.python_version()[:3]) >= 2.6:
	print "You need python 2.6 or newer"
	sys.exit(0)

print "Checking for permissions..."
import os
import sys
import stat
hier = os.path.dirname(os.path.abspath(__file__))
st = os.stat(hier)
#masks defined here: http://docs.python.org/library/stat.html?highlight=stat#stat.S%5FIRWXU
if not bool(st.st_mode & (stat.S_IRUSR + stat.S_IWUSR + stat.S_IXUSR)):
	print "You MUST have read, write and execute permissions in %s" % hier
	sys.exit(0)

print "Checking dependencies..."
try:
	import scrapy
except ImportError:
	print "Scrapy not installed, trying to download it"
	os.system('easy_install Scrapy')

print "Adding the temp.html file to the topics urls"
data_path = os.path.join(os.environ['HOME'], 'Magritte', 'data')
os.system('echo %s >> %s' % ("file://%s/temp.html" % data_path, "%s/test_topic_urls" % data_path))

print "All set, ready to crawl!"
