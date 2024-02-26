import os
import django
from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
django.setup()


class BooksSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Test book 1', price=25,
                                     author_name="Author1")
        book_2 = Book.objects.create(name='Test book 2', price=55,
                                     author_name='Author2')
        expected_data = BookSerializer([book_1, book_2], many=True).data
        data = [
            {'id': book_1.id,
             'name': 'Test book 1',
             'price': '25.00',
             'author_name': 'Author1'
             },

            {'id': book_2.id,
             'name': 'Test book 2',
             'price': '55.00',
             'author_name': 'Author2'
             }

        ]

        self.assertEqual(expected_data, data)
