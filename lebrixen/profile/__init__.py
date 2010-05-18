#the private user id 
PROFILE_KEY = '_profile_user'
#the app token
APP_ID = 'appId'
#the unique identifier in the external app
PROFILE_ID  = 'appUser'
#the app key:
APP_KEY = '_client_app'
#an optional verbose name given by the external app
PROFILE_NAME = 'appUsername'
#optional contextual information given by the external app
PROFILE_INFO = 'appUserInfo'
 
def get_profile(request, app_id):
    """Given a request an the real id of an app, try to retrieve a user profile
        
       As I don't know when the external app will change contexts (a new user is being profiled, etc), 
       then, if they call a service with 'appUser', I assume that a context is changing, so a row is 
       retrieved or updated based on that. If no context change is apparent, then use what was already
       stored in the session. This violates REST, but is more efficient (less queries, etc).
       However, calls *could* be REST-ful, because both this method and the middleware ignore
       the session if the user provides the stateless required parameteres ('appId' and 'appUser') 
    """
    from profile.models import ClientUser
    #if the profile id comes, take it as a reset of context (a new user or course is being profiled)    
    if PROFILE_ID in request.REQUEST:
        #If the external id is provided, get or create a user instance
        u , created= ClientUser.objects.get_or_create(clientId = request.REQUEST[PROFILE_ID], app_id = app_id)
        if created:
            #Try to fill the other info
            changed = False
            if PROFILE_NAME in request.REQUEST:
                u.clientName = request.REQUEST[PROFILE_NAME]
                changed = True
            if PROFILE_INFO in request.REQUEST:
                u.info = request.REQUEST[PROFILE_INFO]
                changed = True
            if changed:
                u.save()
        #Once retrieved by app and app-specific id, store the pk in session for faster retrieval in future calls
        request.session[PROFILE_KEY] = u.pk
        return u
    
    #if it is not a reset, then it must already be in the session        
    elif PROFILE_KEY in request.session:
        #get the user by it's primary key:
        return ClientUser.objects.get(pk = request.session[PROFILE_KEY])
    else:
        raise Exception('Insufficient data to retrieve a profile, the app token and user id should have been provided in a call to startSession or this request')

        
        