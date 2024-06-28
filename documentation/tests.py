from django.test import TestCase
from django.urls import reverse
from .models import Document

class DocumentViewTests(TestCase):

    def setUp(self):
        # Configuration initiale pour les tests
        Document.objects.create(title="Test Document", content="Test Content")

    def test_document_list_view(self):
        response = self.client.get(reverse('document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Document")

    def test_document_detail_view(self):
        document = Document.objects.get(title="Test Document")
        url = reverse('document_detail', args=[document.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Content")

    def test_string_representation(self):
        document = Document(title="Sample Document")
        self.assertEqual(str(document), document.title)

    def test_document_creation(self):
        document = Document.objects.create(title="Another Test Document", content="Test Content")
        self.assertIsInstance(document, Document)
        self.assertEqual(document.title, "Another Test Document")
        self.assertEqual(document.content, "Test Content")
