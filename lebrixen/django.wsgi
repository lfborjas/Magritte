import os
import sys
os.putenv('HOME', '/home/norman')
sys.path.append('/home/norman/Magritte/lebrixen')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
