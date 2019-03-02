import copy

from rest_framework.views import APIView
from rest_framework.response import Response
from upaj.settings import logging as logger
from .conversation import chatDriver, ChatDriverFlow
from .models import BotContext
from .translator import translator
from .constants import ENGLISH_LANGUAGE_CODE, HINDI_LANGUAGE_CODE, DOUBLE_DOLLAR_DELIMITER


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
        language = request.data.get('lang', ENGLISH_LANGUAGE_CODE)
        session_key = request.data.get('key', '')
        logger.debug(request.data)
        bot_cotext = BotContext.get_bot_context_from_session(session_key)
        logger.debug(request.data)
        return_data = {}

        text = get_valid_text_for_conversation_api(text, language)

        if text:
            return_data = chatDriver(
                text, location=location, user=bot_cotext.session)
        else:
            return_data = ChatDriverFlow(
                option, location=location, user=bot_cotext.session)
            logger.debug(return_data)
            if not return_data:
            	return_data = {}
        return_data['key'] = bot_cotext.session

        if 'option' not in return_data:
            return_data['option'] = []

        if 'text' not in return_data:
            return_data['text'] = ''

        new_text = get_valid_text_for_response(return_data['text'], language)
        new_options = get_translated_options_for_response(return_data['option'], language)
        return_data['text'] = new_text
        return_data['option'] = new_options
    
        return Response(return_data)


class VoiceChatView(APIView):
    def post(self, request):
        pass


''' Helpers '''
def get_valid_text_for_conversation_api(text, lang):

    logger.debug(f'text is: {text} and lang is: {lang}')
    if text and lang == HINDI_LANGUAGE_CODE:
        new_text = translator.translate(text, ENGLISH_LANGUAGE_CODE)
        # logger.debug(f'Translated Text for {text} is: {new_text}')
        text = new_text
    return text


def get_valid_text_for_response(text, lang):
    if lang == HINDI_LANGUAGE_CODE:
        text = translator.translate(text, HINDI_LANGUAGE_CODE)
    
    return text

def get_translated_options_for_response(options, lang):
    if lang == HINDI_LANGUAGE_CODE and options:
        for ind, option in enumerate(options):
            options[ind] = {
                'key': option['key'],
                'value': translator.get_option_translation(option['key'], HINDI_LANGUAGE_CODE)
            }

    return options