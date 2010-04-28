from celery.decorators import task
from celery.task import PeriodicTask
from datetime import timedelta
from django.conf import settings 
from subprocess import call

class UpdateIndex(PeriodicTask):
    run_every = timedelta(seconds=settings.UPDATE_INDEX_INTERVAL)

    def run(self, **kwargs):
        #as presented in http://docs.python.org/library/subprocess.html#replacing-os-system
        logger = self.get_logger(**kwargs)
        try:
            #as explained in http://code.google.com/p/djapian/wiki/RunningTheIndexer
            retcode = call(['%s/manage.py'%settings.ROOT_PATH, 'index'])
            if retcode < 0:
                logger.debug("Update index terminated by signal")
            else:
                logger.debug("Update index returned")
            return True
        except OSError as e:
            logger.error("Execution of update_index failed")
            return False

@task 
def update_index(**kwargs):
    """Update the djapian index on demand"""
    logger = update_index.get_logger(**kwargs)
    try:
    #as explained in http://code.google.com/p/djapian/wiki/RunningTheIndexer
        retcode = call(['%s/manage.py'%settings.ROOT_PATH, 'index'])
        if retcode < 0:
            logger.debug("Update index terminated by signal")
        else:
            logger.debug("Update index returned")
            return True
    except OSError as e:
        logger.error("Execution of update_index failed")
        return False
    
    
