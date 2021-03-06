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

        if not option:
            return_data = chatDriver(
                text, location=location, user=bot_cotext.session)
        else:
            return_data = ChatDriverFlow(
                option, location=location, user=bot_cotext.session)
            logger.debug(return_data)
            if not return_data:
            	return_data = {}
        return_data['key'] = bot_cotext.session

        if 'options' not in return_data:
            return_data['options'] = []

        if 'text' not in return_data:
            return_data['text'] = ''

        new_text = get_valid_text_for_response(return_data['text'], language)
        # new_options = get_translated_options_for_response(return_data['options'], language)
        new_options = get_translated_options_for_response(return_data['options'], language)
        return_data['text'] = new_text
        return_data['options'] = new_options
    
        return Response(return_data)


class VoiceChatView(APIView):
    def post(self, request):
        pass


''' Helpers '''
def get_valid_text_for_conversation_api(text, lang):

    logger.debug(f'text is: {text} and lang is: {lang}')
    if text and lang != ENGLISH_LANGUAGE_CODE:
        new_text = translator.translate(text, ENGLISH_LANGUAGE_CODE)
        # logger.debug(f'Translated Text for {text} is: {new_text}')
        text = new_text
    return text


def get_valid_text_for_response(text, lang):
    if lang != ENGLISH_LANGUAGE_CODE:
        text = translator.translate(text, lang)
    
    return text

def get_translated_options_for_response(options, lang):
    if lang != ENGLISH_LANGUAGE_CODE and options:
        for ind, option in enumerate(options):
            options[ind] = {
                'key': option['key'],
                'value': translator.get_option_translation(option['key'], lang)
            }

    return options

def get_translated_options_for_response(options, lang):
    if lang != ENGLISH_LANGUAGE_CODE and options:
        option_values = list(option['value'] for option in options)
        translated_values = translator.get_all_option_translations(option_values, lang)
        for ind, value in enumerate(translated_values):
            options[ind]['value'] = value
    
    return options