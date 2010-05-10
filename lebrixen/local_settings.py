#settings only for lfborjas-laptop:
import os
from settings import MIDDLEWARE_CLASSES, INSTALLED_APPS, DATA_PATH, DATABASE_ENGINE
DEBUG = False
#in development, I use a sqlite db:
#DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = os.path.join(DATA_PATH,'lebrixen')             # Or path to database file if using sqlite3.

#in development, I use the django debug toolbar and south
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INTERNAL_IPS = ('127.0.0.1',)
INSTALLED_APPS += ('debug_toolbar', 'south')
DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False
}

#settings for south:
SOUTH_AUTO_FREEZE_APP = True
if DATABASE_ENGINE == 'mysql':
    DATABASE_STORAGE_ENGINE= "InnoDB"

