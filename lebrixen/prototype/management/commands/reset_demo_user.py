from django.core.management.base import NoArgsCommand
from profile.models import ClientUser

DEMO_USER = "novice"

class Command(NoArgsCommand):
    
    help = "Delete any preferences for the demo user"
    
    def handle_noargs(self, **options):
        before = ClientUser.objects.get(clientId=DEMO_USER).preferences.count()
        ClientUser.objects.get(clientId=DEMO_USER).preferences.all().delete()
        after = ClientUser.objects.get(clientId=DEMO_USER).preferences.count()
        print "%s had %s preferences" % (DEMO_USER, before)
        if after:
            print "Somehow some preferences remained..."
    