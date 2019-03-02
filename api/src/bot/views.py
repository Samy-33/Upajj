from rest_framework.views import APIView
from rest_framework.response import Response
from upaj.settings import logging as logger
from .conversation import chatDriver, ChatDriverFlow
from .models import BotContext


class ChatView(APIView):
    '''Chat API View for bot
    '''

    def post(self, request):
        '''Handles post requests from user in chat-app
        Returns: dictionary with text and options to show
        '''
        logger.debug(dir(request.data))
        text = request.data.get('text', '')
        location = request.data.get('location', '')
        option = request.data.get('option', '')
        session_key = request.data.get('key', '')

        bot_cotext = BotContext.get_context_from_session(session_key)
        logger.debug(request.data)
        if text:
            return_data = chatDriver(
                text, location=location, user=bot_cotext.session)
        else:
            return_data = ChatDriverFlow(
                option, location=location, user=bot_cotext.session)
        return_data.update({'key': bot_cotext.session})

        return Response(return_data)
