# documentation/urls.py

from django.urls import path
from .views import document_list, document_detail

urlpatterns = [
    path('', document_list, name='document_list'),
    path('<int:pk>/', document_detail, name='document_detail'),
]
