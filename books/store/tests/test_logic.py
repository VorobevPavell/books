import django
import os

from django.test import TestCase

from store.logic import operations


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books.settings")
django.setup()


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(22, 8, '+')
        self.assertEqual(30, result)

    def test_minus(self):
        result = operations(22, 8, '-')
        self.assertEqual(14, result)

    def test_multiply(self):
        result = operations(22, 8, '*')
        self.assertEqual(176, result)



