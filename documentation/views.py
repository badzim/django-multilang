import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _, activate
from django.views.decorators.csrf import csrf_exempt
from .models import Document
from .langchain_utils import get_relevant_context
from .chatbot_utils import call_openai_api, check_time_interval
import logging

logger = logging.getLogger('documentation')


def document_list(request):
    documents = Document.objects.all()
    return render(request, 'document_list.html', {"documents": documents})


def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    return render(request, 'partials/document_detail.html', {'document': document})


@csrf_exempt
def chatbot(request):
    # S'assurer que la méthode de la requête est POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode de requête invalide'}, status=400)
    data = json.loads(request.body)
    question = data.get('question')
    user_language = request.LANGUAGE_CODE
    activate(user_language)  # Activer la langue préférée de l'utilisateur
    # Log de la question de l'utilisateur
    logger.debug(f"User: {request.user}, Question: {question}")
    # Vérifier l'intervalle de temps entre les questions
    interval_ok, message = check_time_interval(request)
    if not interval_ok:
        return JsonResponse({'answer': message})
    # Obtenir le contexte pertinent de votre documentation
    context = get_relevant_context(question)
    if not context:
        answer = _("views.chatbot.question_out_of_context")
        return JsonResponse({'answer': answer})
    answer = call_openai_api(question, context, user_language)
    return JsonResponse({'answer': answer})
