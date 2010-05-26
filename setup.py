#based on http://docs.python.org/distutils/setupscript.html
requires =[ 'django>=1.1.1',
	    'celery',
	    'topia.termextract>=1.1.0',
	    'BeautifulSoup>=3.0.8',
	    'elementsoap>=0.6-20071224',
	    'scrapy',	    
            'jsonlib2',	
	    'South>=0.6',
	    'djapian',
 	    'recaptcha-client',
	    'django-debug-toolbar',
	    'gettext', #not a python pkg
	    'xappy'	
	    'xapian' #cf djapian install page for real pkgs
]
