from django.urls import path
from .views import ChatView

app_name = 'bot'

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat')
]