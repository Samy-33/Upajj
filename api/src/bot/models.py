from django.db import models
import uuid

def get_default_value_for_session():
    return uuid.uuid4().__str__()

class BotContext(models.Model):
    '''Model to store current context of the user queries
    '''

    session = models.CharField(max_length=50, unique=True, default=get_default_value_for_session)
    location = models.CharField(max_length=50, blank=True, default='')
    season = models.CharField(max_length=50, blank=True, default='')
    crop = models.CharField(max_length=50, blank=True, default='')
    context = models.TextField(max_length=1000, null=True)

    @staticmethod
    def get_context_from_session(session_key):
        '''Get context object using session key
        '''
        if session_key:
            context, ignore = BotContext.objects.get_or_create(session=session_key)
        else:
            context = BotContext.objects.create()

        return context.context

    @staticmethod
    def set_context_from_session(session,ctx):
        BotContext.objects.update(session=session,context=ctx)

    @staticmethod
    def get_location_from_session(session):
    	location = BotContext.objects.get_or_create(session=session).location
    	return location

    @staticmethod
    def get_season_from_session(session):
   		season = BotContext.objects.get_or_create(session=session).season
   		return season