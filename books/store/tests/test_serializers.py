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
        self.user = User.objects.create(username='test_username',
                                        first_name='Ivan', last_name='Ivanov', is_staff=False)
        self.user2 = User.objects.create(username='test_username2',
                                         first_name='Alexey', last_name='Petrov', is_staff=True)
        self.user3 = User.objects.create(username='test_username3',
                                         first_name='Dmitry', last_name='Alexandrov', is_staff=False)

        self.book_1 = Book.objects.create(name='Test book 1',
                                          author_name='Author1', price=25, owner=self.user, discount=15)
        self.book_2 = Book.objects.create(name='Test book 2',
                                          author_name='Author2', price=55, owner=self.user)

        self.relation = BookUserRelation.objects.create(book=self.book_1, user=self.user, like=True, rating=5)
        self.relation2 = BookUserRelation.objects.create(book=self.book_1, user=self.user2, like=True, rating=5)
        self.relation3 = BookUserRelation.objects.create(book=self.book_1, user=self.user3, like=True, rating=4)

        self.relation4 = BookUserRelation.objects.create(book=self.book_2, user=self.user, rating=3)
        self.relation5 = BookUserRelation.objects.create(book=self.book_2, user=self.user2, rating=4)

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
             'annotated_likes': 3,
             'rating': '4.67',
             'discount_price': 10,
             'owner_name': self.user.username,
             'readers': [
                 {
                     'first_name': 'Ivan',
                     'last_name': 'Ivanov',
                     'is_staff': False
                 },
                 {
                     'first_name': 'Alexey',
                     'last_name': 'Petrov',
                     'is_staff': True
                 },
                 {
                     'first_name': 'Dmitry',
                     'last_name': 'Alexandrov',
                     'is_staff': False
                 }
             ]
             },
            {'id': self.book_2.id,
             'name': 'Test book 2',
             'price': '55.00',
             'author_name': 'Author2',
             'annotated_likes': 0,
             'rating': '3.50',
             'discount_price': 55,
             'owner_name': self.user.username,
             'readers': [
                 {
                     'first_name': 'Ivan',
                     'last_name': 'Ivanov',
                     'is_staff': False
                 },
                 {
                     'first_name': 'Alexey',
                     'last_name': 'Petrov',
                     'is_staff': True
                 }
             ]

             }

        ]
        self.assertEqual(expected_data, data)
