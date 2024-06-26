from django.urls import path
from .views import document_list, document_detail, chatbot

urlpatterns = [
    path('', document_list, name='document_list'),
    path('<int:pk>/', document_detail, name='document_detail'),
    path('chatbot/', chatbot, name='chatbot'),
]
