from rest_framework.views import APIView
from rest_framework.response import Response
from .conversation import chatDriver, chatDriver
import logging

class ChatView(APIView):
    def post(self, request):

        text = request.data.get('text', '')
        location = request.data.get('location', '')
        option = request.data.get('option','')
        if text is not '':
        	return_data = chatDriver(text, location=location)
        else:
        	return_data = ChatDriverFlow(option,location=location)
        return Response(return_data)