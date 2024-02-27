import json
import os
from decimal import Decimal

import django
from django.contrib.auth.models import User

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
django.setup()


class BooksApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_username')

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

    def test_post(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')

        data = {

            'name': 'testbook',
            'price': '700.00',
            'author_name': 'Author1'

        }
        json_data = json.dumps(data)
        test_user = self.client.force_login(self.user, backend=None)
        response = self.client.post(url, data=json_data, user=test_user,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(1, Book.objects.filter(name=data['name'], price=data['price'],
                                                author_name=data['author_name']).count())

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": "Test book 1",
            "price": "666.00",
            "author_name": "Author1"
        }
        json_data = json.dumps(data)

        user = self.client.force_login(user=self.user)

        response = self.client.put(url, data=json_data,
                                   content_type='application/json', user=user)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(self.book_1.price, Decimal(data['price']))

    def test_delete(self):
        self.book_test = Book.objects.create(name='Test book test', price=55,
                                             author_name='Author test')

        book_counter = Book.objects.all().count()

        url = reverse('book-detail', args=(self.book_test.id,))
        user = self.client.force_login(self.user)

        response = self.client.delete(url, content_type='application/json', user=user)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Book.objects.all().count(), book_counter - 1)
