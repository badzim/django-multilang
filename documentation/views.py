from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Document
import json
import time
# Create your views here.

def document_list(request):
    documents = Document.objects.all()
    return render(request, 'partials/document_list.html', {"documents": documents})

def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    return render(request, 'document_detail.html', {'document': document})

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')
        
        # Simuler une latence de réponse
        time.sleep(2)  # Simule un délai de 2 secondes
        
        answer = "hello"
        return JsonResponse({'answer': answer})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def chat_interface(request):
    return render(request, 'chat.html')