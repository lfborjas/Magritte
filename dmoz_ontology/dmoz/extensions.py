from scrapy.xlib.pydispatch import dispatcher
from scrapy.core import signals
import os
from scrapy.mail import MailSender
from scrapy.conf import settings
import time

class EmailInClosing(object):
	def __init__(self):
	        dispatcher.connect(self.engine_closed, signal=signals.engine_stopped)
	
	def engine_closed(self):
		script = os.path.join(settings.get('ROOT_PATH'), 'asciitree.py')		
		result = os.path.join(settings.get('ROOT_PATH'), 'dirtree.txt')
		dirtree = os.path.join(settings.get('ROOT_PATH'), 'Top')
		os.system("%s -f %s > %s" % (script, dirtree, result))
		attached_file = open(result, 'r')
		#get the total size of the corpus (could take a while...)
		stats = "ND"
		try:
			stats = os.popen('du -sh %s' % dirtree).read()
		except:
			pass
		finally:
			mailer = MailSender()
			content = "Crawling ended at %s, the corpus length is %s Attached is the structure"\
				   %(time.asctime(), stats)
			mailer.send(to = ['lfborjas@unitec.edu', 'luis.borjas@escolarea.com', 'lfborjas@hotmail.com'],
				   subject = "The training corpus has been downloaded",
				   body =content ,
				   attachs = [('structure', 'text/plain', attached_file)])
			attached_file.close()

