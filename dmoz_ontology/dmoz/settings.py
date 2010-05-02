# Scrapy settings for dmoz project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
# Or you can copy and paste them from where they're defined in Scrapy:
# 
#     scrapy/conf/default_settings.py
#
import os

BOT_NAME = 'dmoz'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['dmoz.spiders']
NEWSPIDER_MODULE = 'dmoz.spiders'
DEFAULT_ITEM_CLASS = 'dmoz.items.DmozItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = ['dmoz.pipelines.DmozPipeline',]


#EXPORT_FORMAT = 'json'
#EXPORT_FILE = 'en_Science-scraped_items.py'
#EXPORT_EMPTY = True

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(os.environ['HOME'], 'Magritte', 'data')
EXTENSIONS = {'dmoz.extensions.EmailInClosing':0,}

#MAIL_HOST = 'localhost'
#MAIL_FROM = 'scrapy@localhost.com'

IS_TEST = False 

SPIDER_MIDDLEWARES = {'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,}

SCHEDULER_ORDER = 'DFO'
