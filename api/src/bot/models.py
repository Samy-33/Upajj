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
    def get_bot_context_from_session(session_key):
        '''Get context object using session key
        '''
        if session_key:
            bot_context, ignore = BotContext.objects.get_or_create(session=session_key)
        else:
            bot_context = BotContext.objects.create()

        return bot_context

    @staticmethod
    def get_context_from_session(session):
        bot_context = BotContext.get_bot_context_from_session(session)
        return bot_context.context

    @staticmethod
    def set_context_from_session(session,ctx):
        bot_context = BotContext.objects.get(session=session)
        bot_context.context = ctx
        bot_context.save()

    @staticmethod
    def get_location_from_session(session):
        location = BotContext.objects.get(session=session).location
        return location

    @staticmethod
    def set_location_from_session(session,location):
        bot_context = BotContext.objects.get(session=session)
        bot_context.location = location
        bot_context.save()

    @staticmethod
    def get_season_from_session(session):
        season = BotContext.objects.get_or_create(session=session).season
        return season

    @staticmethod
    def set_location_context_from_session(session,location,context):
        bot_context = BotContext.objects.get(session=session)
        bot_context.location = location
        bot_context.context = context
        bot_context.save()

    @staticmethod
    def get_crop_from_session(session):
        bot_context = BotContext.objects.get(session=session)
        return bot_context.crop

    @staticmethod
    def set_crop_from_session(session,crop):
        bot_context = BotContext.objects.get(session=session)
        bot_context.crop = crop
        bot_context.save()