import os
import django

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
django.setup()


class BooksApiTestCase(APITestCase):
    def test_get(self):
        book_1 = Book.objects.create(name='Test book 1', price=25)
        book_2 = Book.objects.create(name='Test book 2', price=55)
        serializer_data = BookSerializer([book_1, book_2], many=True).data
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
