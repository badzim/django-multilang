from .models import Document

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np


class SimpleDocument:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata else {}


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
    # Diviser les documents en morceaux plus petits pour faciliter le traitement
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    # Créer un vecteurstore pour la recherche de documents basée sur des embeddings
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    # Utiliser `invoke` pour récupérer les documents pertinents à partir de la question posée
    relevant_docs = retriever.invoke(question)
    # Calculer la similarité entre l'embedding de la question et les documents récupérés
    embedding_model = OpenAIEmbeddings()
    question_embedding = embedding_model.embed_query(question)
    relevant_docs_filtered = []
    # Définir un seuil de similarité approprié pour filtrer les documents
    similarity_threshold = 0.7
    for doc in relevant_docs:
        doc_embedding = embedding_model.embed_query(doc.page_content)
        similarity = cosine_similarity(question_embedding, doc_embedding)
        # Conserver uniquement les documents qui dépassent le seuil de similarité
        if similarity > similarity_threshold:
            relevant_docs_filtered.append((doc, similarity))
    # Trier les documents par similarité décroissante pour présenter les plus pertinents en premier
    relevant_docs_filtered.sort(key=lambda x: x[1], reverse=True)
    # Retourner les contenus des documents pertinents si disponibles
    if relevant_docs_filtered:
        return "\n\n".join(doc.page_content for doc, _ in relevant_docs_filtered)
    # Si aucun document pertinent n'est trouvé, retourner None
    return None
