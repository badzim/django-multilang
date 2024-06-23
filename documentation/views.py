from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Document
import json

from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)
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

        # Pré-traitement de la question de l'utilisateur
        personalized_prompt = f"Je suis un développeur débutant qui utilise votre documentation. Pouvez-vous m'aider avec la question suivante : {question}"

        # Appel à l'API OpenAI GPT-3.5 Turbo
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es un assistant utile pour les développeurs débutants."},
            {"role": "user", "content": personalized_prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7)

        answer = response.choices[0].message.content.strip()

        return JsonResponse({'answer': answer})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def chat_interface(request):
    return render(request, 'chat.html')