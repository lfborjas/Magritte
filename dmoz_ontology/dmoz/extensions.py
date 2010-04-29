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
		dirtree = os.path.join(settings.get('DATA_PATH'), 'Top')
		#get the total size of the corpus (could take a while...)
		mailer = MailSender()
		success = os.path.isdir(dirtree)
		if success:
			content = "Crawling ended succesfully at %s." % time.asctime()
		else:
			content = "Crawling ended abnormally at %s" % time.asctime()

		mailer.send(to = ['lfborjas@unitec.edu', 'luis.borjas@escolarea.com', 'lfborjas@hotmail.com'],
			   subject = "The training corpus has been downloaded" if success else "Error crawling",
			   body =content ,
			   )

