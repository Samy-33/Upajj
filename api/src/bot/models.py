from django.db import models


class BotContext(models.Model):
    session = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=50, blank=True, default='')
    season = models.CharField(max_length=50, blank=True, default='')
    crop = models.CharField(max_length=50, blank=True, default='')
    context = models.TextField(max_length=1000, null=True)

    @staticmethod
    def get_context_from_session(session):
        context = BotContext.objects.get_or_create(session=session)
        return context

   	@staticmethod
   	def set_context_from_session(session,ctx):
   		BotContext.objects.update(session=session,context=ctx)

   	@staticmethod
   	def get_location_from_session(session):
   		location = BotContext.objects.get_or_create(session=session)
   		return location

   	@staticmethod
   	def get_season_from_session(session):
   		season = BotContext.objects.get_or_create(session=session)
   		return season