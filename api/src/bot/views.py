from rest_framework.views import APIView
from rest_framework.response import Response
from .conversation import chatDriver
import logging

class ChatView(APIView):
    def post(self, request):

        text = request.data.get('text', '')
        location = request.data.get('location', '')
        
        return_data = chatDriver(text, location=location)

        return Response(return_data)