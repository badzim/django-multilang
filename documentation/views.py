from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Document
import json

from django.utils.translation import gettext as _, activate
from django.conf import settings
from openai import OpenAI

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .langchain_utils import SimpleDocument
import numpy as np
import markdown

import time

client = OpenAI(api_key=settings.OPENAI_API_KEY)
# Create your views here.

def document_list(request):
    documents = Document.objects.all()
    return render(request, 'document_list.html', {"documents": documents})

def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    document.content = markdown.markdown(document.content)  # Convertir le Markdown en HTML
    return render(request, 'partials/document_detail.html', {'document': document})

def chat_interface(request):
    return render(request, 'chat.html')

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')
        
        user_language = request.LANGUAGE_CODE  # Get the user's preferred language
        activate(user_language)  # Activate the user's preferred language

        # Vérifier l'intervalle de temps entre les questions
        last_question_time = request.session.get('last_question_time', 0)
        current_time = time.time()
        time_diff = current_time - last_question_time

        if time_diff < 5:
            return JsonResponse({'answer': _("Please wait a few seconds before asking another question.")})

        try:
            # Mettre à jour l'heure de la dernière question
            request.session['last_question_time'] = current_time
            # Query relevant context from your documentation
            context = get_relevant_context(question)

            # Call OpenAI API with the personalized prompt
            if not context:
                answer = _("I'm sorry, I couldn't find the information you are looking for in our documentation.")
                return JsonResponse({'answer': answer})
            
            
            personalized_prompt = _("As a beginner developer using our documentation, you asked: {question}.").format(question=question)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": _("You are a helpful assistant for users, specifically helping them with our documentation. You must answer in {user_language}.").format(user_language=user_language)},
                    {"role": "user", "content": personalized_prompt},
                    {"role": "assistant", "content": _("Base your response strictly on the following context: {context}").format(context=context)},
                ],
                max_tokens=4096,
                n=1,
                stop=None,
                temperature=0.7,
            )

            answer = response.choices[0].message.content.strip()
            return JsonResponse({'answer': answer})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

def get_relevant_context(question):
    # Récupérer tous les documents de la base de données
    documents = Document.objects.all()
    
    # Charger les documents dans un format compatible avec LangChain
    docs = [SimpleDocument(page_content=doc.content, metadata={"title": doc.title}) for doc in documents]
    
    # Diviser les documents en morceaux plus petits
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # Créer un vecteurstore pour la recherche de documents
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # Utiliser `invoke` pour récupérer les documents pertinents
    relevant_docs = retriever.invoke(question)
    
    # Calculer la similarité entre la question et les documents récupérés
    embedding_model = OpenAIEmbeddings()
    question_embedding = embedding_model.embed_query(question)
    
    relevant_docs_filtered = []
    similarity_threshold = 0.7  # Définir un seuil de similarité approprié
    
    for doc in relevant_docs:
        doc_embedding = embedding_model.embed_query(doc.page_content)
        similarity = cosine_similarity(question_embedding, doc_embedding)
        if similarity > similarity_threshold:
            relevant_docs_filtered.append((doc, similarity))
    
    # Trier les documents par similarité décroissante
    relevant_docs_filtered.sort(key=lambda x: x[1], reverse=True)
    
    print(relevant_docs_filtered)
    
    if relevant_docs_filtered:
        return "\n\n".join(doc.page_content for doc, _ in relevant_docs_filtered)
    
    # Si aucun document pertinent n'est trouvé
    return None

