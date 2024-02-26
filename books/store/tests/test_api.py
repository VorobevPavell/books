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

    def setUp(self):
        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author1')
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                          author_name='Author2')
        self.book_3 = Book.objects.create(name='Test book Author1', price=55,
                                          author_name='Author3')

    def test_get(self):

        serializer_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_filter(self):

        serializer_data = BookSerializer([self.book_2, self.book_3], many=True).data
        url = reverse('book-list')
        response = self.client.get(url, data={
            'price': '55.00'
        })
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_search(self):
        serializer_data = BookSerializer([self.book_1, self.book_3], many=True).data
        url = reverse('book-list')
        response = self.client.get(url, data={
            'search': 'Author1'
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        serializer_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        url = reverse('book-list')
        response = self.client.get(url, data={
            "ordering": 'price'
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
