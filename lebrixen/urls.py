from django.conf.urls.defaults import *
from django.conf import settings
from djapian import load_indexes
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#load the djapian indexes:
load_indexes()

urlpatterns = patterns('',
    # Example:
    # (r'^lebrixen/', include('lebrixen.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

#to serve static files only in development:
if settings.DEBUG:
        urlpatterns += patterns('',
                (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
        )

