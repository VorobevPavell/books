import os
from collections import OrderedDict

import django
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, F
from django.test import TestCase

from store.models import Book, BookUserRelation
from store.serializers import BookSerializer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
django.setup()


class BooksSerializerTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.user3 = User.objects.create(username='test_username3')

        self.book_1 = Book.objects.create(name='Test book 1',
                                          author_name='Author1', price=25, owner=self.user, discount=15)
        self.book_2 = Book.objects.create(name='Test book 2',
                                          author_name='Author2', price=55, owner=self.user)
        self.relation = BookUserRelation.objects.create(book=self.book_1, user=self.user, like=True, rating=5)
        self.relation2 = BookUserRelation.objects.create(book=self.book_1, user=self.user2, like=True, rating=5)
        self.relation3 = BookUserRelation.objects.create(book=self.book_1, user=self.user3, like=True, rating=4)

        self.relation4 = BookUserRelation.objects.create(book=self.book_2, user=self.user, rating=3)
        self.relation5 = BookUserRelation.objects.create(book=self.book_2, user=self.user2, rating=4)
        self.relation6 = BookUserRelation.objects.create(book=self.book_2, user=self.user2)

    def test_ok(self):
        books_query = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(bookuserrelation__like=True, then=1))),
            rating=Avg('bookuserrelation__rating'),
            discount_price=(F('price') - F('discount'))
        ).order_by('id')
        expected_data = BookSerializer(books_query, many=True).data
        data = [
            {'id': self.book_1.id,
             'name': 'Test book 1',
             'price': '25.00',
             'author_name': 'Author1',
             'like_counter': 3,
             'annotated_likes': 3,
             'rating': '4.67',
             'discount_price': 10
             },

            {'id': self.book_2.id,
             'name': 'Test book 2',
             'price': '55.00',
             'author_name': 'Author2',
             'like_counter': 0,
             'annotated_likes': 0,
             'rating': '3.50',
             'discount_price': 55
             }

        ]
        print('expected_data', expected_data)
        print('data', data)
        self.assertEqual(expected_data, data)


