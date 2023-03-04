
from django.urls import path
from .views import create_conversation

urlpatterns = [
    path('create_conversation/', create_conversation, name='create_conversation'),
]