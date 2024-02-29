import os
from collections import OrderedDict

import django
from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
django.setup()


class BooksSerializerTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_username')

        self.book_1 = Book.objects.create(name='Test book 1',
                                          author_name='Author1', price=25, owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2',
                                          author_name='Author2', price=55, owner=self.user)

    def test_ok(self):
        expected_data = BookSerializer([self.book_1, self.book_2], many=True).data
        data = [
            {'id': self.book_1.id,
             'name': 'Test book 1',
             'price': '25.00',
             'author_name': 'Author1',
             'owner': self.user.id,
             'readers': []
             },

            {'id': self.book_2.id,
             'name': 'Test book 2',
             'price': '55.00',
             'author_name': 'Author2',
             'owner': self.user.id,
             'readers': []
             }

        ]

        self.assertEqual(expected_data, data, data)
