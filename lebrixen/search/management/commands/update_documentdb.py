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

def cleanup(filename):
    """Takes a filename and, depending on it's being a pdf or an html page, returns relevant raw text"""
    if 'PDF' in filename:
        retcode = subprocess.call(['pdftotext', filename])
        if retcode == 0:
            txtfile = filename.replace('pdf', 'txt')
            if os.path.exists(txtfile):
                return open(txtfile, 'r').read()
            else:
                print "pdftotext succeed, but somehow %s can't be found..." % txtfile
        else:
            print "Error converting file %s to plain text" % filename
            return ""
        
    elif 'HTML' in filename:
        pass        
    else:
        print "Unknown type for file %s" %filename
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
        for dirpath, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                try:
                    f = open(os.path.join(dirpath, filename), 'r')
                    info = json.load(f)
                    f.close()
                except Exception as e:
                    traceback.print_exc()
                    raise CommandError('Exception "%s" while json-decoding file %s' % (e.message, filename))
                #get the category:
                try:
                    cat = DmozCategory.objects.get(topic_id='Top/%s'%info['category'])
                except MultipleObjectsReturned:
                    print "There are multiple entries for category Top/%s !" %info['category']
                    cat = None
                except DmozCategory.DoesNotExist:
                    print "There is no such category: Top/%s !" %info['category']
                    cat = None
                
                #create
                attrs = {'title':info.get('name',''),
                         'origin':info.get('url',''),
                         'summary':info.get('description',''),
                         'added':info.get('retrieved_on', time.asctime),
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
                    print "Document surrogate %s has no content!" % filename
                try:
                    create_or_update(attrs,{'origin': attrs['origin']},DocumentSurrogate, False)
                except Exception, e:
                    raise CommandError("Exception %s while parsing file %s" % (e.message,filename))
                c += 1
                
        print "Added %s documents to the database" % c