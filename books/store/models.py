from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255, default='')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='BookUserRelation',
                                     related_name='books')
    discount = models.IntegerField(default=0)

    def __str__(self):
        return f"Id {self.id}: {self.name}"


class BookUserRelation(models.Model):
    RATING_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rating = models.SmallIntegerField(choices=RATING_CHOICES, null=True)

    def __str__(self):
        return f"USER: {self.user.username}, BOOK: {self.book.name}, RATING: {self.rating}"
