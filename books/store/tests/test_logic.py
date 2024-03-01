from decimal import Decimal

import django
import os

from django.contrib.auth.models import User
from django.test import TestCase

from store.logic import set_rating
from store.models import BookUserRelation, Book

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
django.setup()


class SetRatingTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_username',
                                        first_name='Ivan', last_name='Ivanov', is_staff=False)
        self.user2 = User.objects.create(username='test_username2',
                                         first_name='Alexey', last_name='Petrov', is_staff=True)

        self.book_1 = Book.objects.create(name='Test book 1',
                                          author_name='Author1', price=25, owner=self.user, discount=15)

        self.relation = BookUserRelation.objects.create(book=self.book_1, user=self.user, like=True, rating=5)
        self.relation2 = BookUserRelation.objects.create(book=self.book_1, user=self.user2, like=True, rating=2)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(Decimal('3.50'), self.book_1.rating)
