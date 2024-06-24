from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Document
import json

from django.utils.translation import gettext as _, activate
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
        
        user_language = request.LANGUAGE_CODE  # Get the user's preferred language

        # Activate the user's preferred language
        activate(user_language)

        # Query relevant context from your documentation
        context = get_relevant_context(question)

        # Preprocess the user's question with relevant context
        personalized_prompt = _("As a beginner developer using our documentation, you asked: {question}.").format(question=question)
        

        # Call OpenAI API with the personalized prompt
        if not context:
            answer = _("I'm sorry, I couldn't find the information you are looking for in our documentation.")
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": _("You are a helpful assistant for beginner developers.")},
                    {"role": "user", "content": personalized_prompt},
                    {"role": "assistant", "content": _("Here is the relevant information: {context}.").format(context=context)},
                ],
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.7,
            )

            answer = response.choices[0].message.content.strip()
        return JsonResponse({'answer': answer})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_relevant_context(question):
    # Example logic to find the most relevant document based on the question
    # This could be more sophisticated using search algorithms or libraries
    try:
        relevant_document = Document.objects.filter(content__icontains=question).first()
        return relevant_document.content if relevant_document else None
    except Document.DoesNotExist:
        return None

def chat_interface(request):
    return render(request, 'chat.html')