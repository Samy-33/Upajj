from rest_framework.views import APIView
from rest_framework.response import Response

class ChatView(APIView):
    def post(self, request):
        return Response({'message': 'Hello this works'})