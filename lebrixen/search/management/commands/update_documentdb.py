#!/usr/bin/env python
#encoding = utf-8
'''
Created on 02/05/2010

@author: lfborjas
'''
import os
import sys
from django.conf import settings
from search.models import DmozCategory, DocumentSurrogate
from utilities import create_or_update
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import json
import traceback
from django.core.exceptions import MultipleObjectsReturned
import time
import subprocess
from BeautifulSoup import BeautifulSoup, Comment
from django.db.models import Q
from HTMLParser import HTMLParser 
IGNORED_TAGS = ['script', 'style', 'applet', '!DOCTYPE']
SYS_DATE_FORMAT = "%a %B %d %H:%M:%S %Y"
DB_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
from datetime import datetime
parser = HTMLParser()
import logging
logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
        filename = 'doc_update.log',
        filemode = 'w'
    )

def gettextonly(soup):
    """Recursively gather the text in a page.
      Found in the book 'Programming Collective Intelligence' by Toby Seagaran"""
    v=soup.string
    if v==None:
        c=soup.contents
        resulttext=''
        for t in c:
            subtext=gettextonly(t).strip()
            try:
                subtext = parser.unescape(subtext)
            except:
                logging.error("Error parsing html file", exc_info = True)
            if subtext:
                resulttext+=subtext+'\n'
        return resulttext
    else:
        return v.strip()

def cleanup(filename):
    """Takes a filename and, depending on it's being a pdf or an html page, returns relevant raw text"""
    if 'PDF' in filename:
        retcode = subprocess.call(['pdftotext', filename])
        if retcode == 0:
            txtfile = filename.replace('pdf', 'txt')
            if os.path.exists(txtfile):
                return open(txtfile, 'r').read()
            else:
                logging.error( "pdftotext succeeded, but somehow %s can't be found..." % txtfile, exc_info = True)
                return ""
        else:
            logging.error( "Error converting file %s to plain text" % filename, exc_info = True)
            return ""
        
    elif 'HTML' in filename:
        #first, create the soup and remove nasty stuff (comments, inline js and css, etc)
        try:
            f = open(filename, 'r')
            soup=BeautifulSoup(f.read())
            f.close()
        except:
            logging.error("Error parsing file %s as html" %filename, exc_info=True)
        #remove comments, inline js and css:
        try:        
            comments = soup.findAll(text=lambda text:isinstance(text, Comment))\
            + soup.findAll(name=IGNORED_TAGS)
            [comment.extract() for comment in comments]
            txt = gettextonly(soup)       
            return txt
        except:
            logging.error("Error cleaning html in file %s" %filename, exc_info=True)
            return ""
    else:
        logging.error( "Unknown type for file %s" %filename)
        return ""
    

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                  make_option('--dir', dest='dir', default=os.path.join(settings.DATA_PATH, 'Top'),                    
                    help='Which directory to peruse for raw documents'),
                                             )
    help = "Update the document collection"
    args = 'dir'
    
    def handle(self, dir=os.path.join(settings.DATA_PATH, 'Top'), *args, **options):
        c = 0
        p = 0
        for dirpath, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                try:
                    f = open(os.path.join(dirpath, filename), 'r')
                    info = json.load(f)
                    f.close()
                except Exception as e:                    
                    logging.error('Exception "%s" while json-decoding file %s' % (e.message, filename), exc_info = True)
                #get the category:
                try:
                    cat = DmozCategory.objects.get(Q(topic_id='Top/%s'%info['category'][:-1]) | Q(es_alt='Top/%s'%info['category'][:-1]))
                except MultipleObjectsReturned:
                    logging.error("There are multiple entries for category Top/%s !" %info['category'])
                    cat = None
                except DmozCategory.DoesNotExist:
                    logging.error("There is no such category: Top/%s !" %info['category'])
                    cat = None
                
                #create
                date_added = None
                try:
                    date_added = datetime.strftime(datetime.strptime(info.get('retrieved_on', time.asctime()), '%a %b %d %H:%M:%S %Y'),\
                                                     '%Y-%m-%d %H:%M:%S')
                except:
                    logging.error("Error parsing date for file %s"%filename)
                    date_added = datetime.strftime(datetime.strptime(time.asctime(), '%a %b %d %H:%M:%S %Y'),\
                                                     '%Y-%m-%d %H:%M:%S')
                    
                attrs = {'title':info.get('name',''),
                         'origin':info.get('url',''),
                         'summary':info.get('description',''),                         
                         'added': date_added,
                         'type':info.get('type', 'html'),     
                         'text':'',
                         'lang': info.get('lang', 'en'),                                                                 
                         }
                if cat:
                    attrs.update({'category_id': cat.pk})
                    
                #get the contents from a file:
                #THIS ONE USES A LOOOT OF MEMORY!
                if info.get('content'):
                    content = cleanup(info['content'].replace('$HOME', os.environ['HOME']))
                    if content:
                        attrs.update({'text':content})                    
                    else:
                        logging.info("No content could be parsed from file %s" %filename)
                else:
                    logging.info("Document surrogate %s has no content!" % filename)
                try:
                    create_or_update(attrs,{'origin': attrs['origin']},DocumentSurrogate, False)
                    if 'text' in attrs and attrs['text']:
                        c +=1
                except Exception:
                    logging.error("Exception while saving file %s to db" % filename, exc_info=True)
                p += 1
                
        logging.info( "Parsed %s documents \n And added %s documents to the database" % (p,c))
        
