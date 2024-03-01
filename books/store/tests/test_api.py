import json
import os
from decimal import Decimal

import django
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When, Avg, F
from django.test.utils import CaptureQueriesContext

from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, BookUserRelation
from store.serializers import BookSerializer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
django.setup()


class BooksApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_username',
                                        first_name='Ivan', last_name='Ivanov')
        self.user2 = User.objects.create(username='test_username2',
                                         first_name='Alexey', last_name='Red')

        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=50,
                                          author_name='Author2', owner=self.user, discount=38)
        self.book_3 = Book.objects.create(name='Test book Author1', price=55,
                                          author_name='Author3', owner=self.user)

        self.relation = BookUserRelation.objects.create(book=self.book_1, user=self.user, like=True, rating=5)

    def test_get(self):
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(bookuserrelation__like=True, then=1))),
            discount_price=F('price') - F('discount')
        ).order_by('id')
        serializer_data = BookSerializer(books, many=True).data
        url = reverse('book-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)

        sorted_serializer_data = sorted(serializer_data, key=lambda x: x['id'])
        sorted_response_data = sorted(response.data, key=lambda x: x['id'])

        self.assertEqual(sorted_serializer_data, sorted_response_data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('5.00', serializer_data[0]['rating'])
        self.assertEqual(1, serializer_data[0]['annotated_likes'])
        self.assertEqual(12, serializer_data[1]['discount_price'])
        self.assertEqual(2, len(queries))

    def test_get_filter(self):
        books = Book.objects.filter(id__in=[self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(bookuserrelation__like=True, then=1))),
            discount_price=F('price') - F('discount')
        )
        serializer_data = BookSerializer(books, many=True).data
        url = reverse('book-list')
        response = self.client.get(url, data={
            'price': '55.00'
        })
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_search(self):
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(bookuserrelation__like=True, then=1))),
            discount_price=F('price') - F('discount'),
            owner_name=F('readers__username')
        )
        serializer_data = BookSerializer(books, many=True).data
        url = reverse('book-list')
        response = self.client.get(url, data={
            'search': 'Author1'
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(bookuserrelation__like=True, then=1))),
            discount_price=F('price') - F('discount')
        ).order_by('price')
        serializer_data = BookSerializer(books, many=True).data
        url = reverse('book-list')
        response = self.client.get(url, data={
            "ordering": 'price'
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expect = response.data[0]['price'] < response.data[1]['price']
        self.assertTrue(expect)
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
        self.assertEqual(self.user, Book.objects.last().owner)

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
                                             author_name='Author test', owner=self.user)
        book_counter = Book.objects.all().count()

        url = reverse('book-detail', args=(self.book_test.id,))
        user = self.client.force_login(self.user)

        response = self.client.delete(url, content_type='application/json', user=user)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Book.objects.all().count(), book_counter - 1)

    def test_update_not_owner(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        user = self.client.force_login(user=self.user2)
        data = {
            "name": "Test book 1",
            "price": "666.00",
            "author_name": "Author1"
        }
        json_data = json.dumps(data)
        response = self.client.put(url, user=user,
                                   content_type='application/json', data=json_data)

        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()
        self.assertNotEqual(self.book_1.price, data['price'])

    def test_delete_not_owner(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        user = self.client.force_login(self.user2)

        response = self.client.delete(url, content_type='application/json', user=user)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)

    def test_update_not_owner_but_staff(self):
        staff_user = User.objects.create(username='staff_user',
                                         is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        user = self.client.force_login(user=staff_user)
        data = {
            "name": "Test book 1",
            "price": '666.00',
            "author_name": "Author1"
        }
        json_data = json.dumps(data)
        response = self.client.put(url, user=user,
                                   content_type='application/json', data=json_data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(self.book_1.price, Decimal(data['price']))


class BookUserRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
        self.book_1 = Book.objects.create(name='book1', author_name='author1', owner=self.user, price=23)
        self.book_2 = Book.objects.create(name='book2', author_name='author2', owner=self.user, price=50)

    def test_like(self):
        url = reverse('bookuserrelation-detail', args=(self.book_1.id,))

        data = {
            'like': True
        }
        json_data = json.dumps(data)
        user = self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     user=user, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = BookUserRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)

        data_bm = {
            'in_bookmarks': True
        }
        json_data_bm = json.dumps(data_bm)
        response = self.client.patch(url, data=json_data_bm,
                                     user=user, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = BookUserRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('bookuserrelation-detail', args=(self.book_1.id,))

        data = {
            'rating': 3
        }
        json_data = json.dumps(data)
        user = self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     user=user, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = BookUserRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rating)

    def test_rate_wrong(self):
        url = reverse('bookuserrelation-detail', args=(self.book_1.id,))

        data = {
            'rating': 6
        }
        json_data = json.dumps(data)
        user = self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     user=user, content_type='application/json')
        self.assertNotEqual(status.HTTP_200_OK, response.status_code, response.data)
