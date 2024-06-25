import json
import time

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _, activate
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

from .langchain_utils import get_relevant_context
from .models import Document

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def document_list(request):
    documents = Document.objects.all()
    return render(request, 'document_list.html', {"documents": documents})


def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    return render(request, 'partials/document_detail.html', {'document': document})


def chat_interface(request):
    return render(request, 'chat.html')


@csrf_exempt
def chatbot(request):
    # S'assurer que la méthode de la requête est POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode de requête invalide'}, status=400)
    data = json.loads(request.body)
    question = data.get('question')
    user_language = request.LANGUAGE_CODE
    activate(user_language)  # Activer la langue préférée de l'utilisateur
    # Vérifier l'intervalle de temps entre les questions
    last_question_time_key = 'last_question_time'
    last_question_time = request.session.get(last_question_time_key, 0)
    current_time = time.time()
    time_diff = current_time - last_question_time
    if time_diff < settings.CHAT_INTERVAL_SECONDS:
        return JsonResponse({'answer': _("views.chatbot.wait_before_retry")})
    # Mise à jour du temps de la dernière question
    request.session[last_question_time_key] = current_time
    # Obtenir le contexte pertinent de votre documentation
    context = get_relevant_context(question)
    if not context:
        answer = _("views.chatbot.question_out_of_context")
        return JsonResponse({'answer': answer})
    personalized_prompt = _(f"views.chatbot.personalized_user_prompt : {question}.")
    system_prompt = _(f"views.chatbot.system_prompt {user_language}.")
    assistant_prompt = _(f"views.chatbot.assistant_prompt {context}.")
    # Appel à l'API OpenAI avec l'invite personnalisée
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": personalized_prompt},
            {"role": "assistant", "content": assistant_prompt},
        ],
        **settings.GPT_SETUP,
    )
    answer = response.choices[0].message.content.strip()
    return JsonResponse({'answer': answer})
