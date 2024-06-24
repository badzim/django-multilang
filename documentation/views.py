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
        activate(user_language)  # Activate the user's preferred language

        # Query relevant context from your documentation
        context = get_relevant_context(question)

        # Preprocess the user's question with relevant context
        

        # Call OpenAI API with the personalized prompt
        if not context:
            answer = _("I'm sorry, I couldn't find the information you are looking for in our documentation.")
            return JsonResponse({'answer': answer})
        
        print(context)
        personalized_prompt = _("As a beginner developer using our documentation, you asked: {question}.").format(question=question)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": _("You are a helpful assistant for users to help users with our documentation ")},
                {"role": "user", "content": personalized_prompt},
                {"role": "assistant", "content": _("Here is the relevant information: {context}. don't give answers non based on this context ! ").format(context=context)},
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
    
    print(relevant_docs)
    
    if relevant_docs:
        return "\n\n".join(doc.page_content for doc in relevant_docs)
    return None

def chat_interface(request):
    return render(request, 'chat.html')