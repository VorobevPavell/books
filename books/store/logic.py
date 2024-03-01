from django.db.models import Avg

from store.models import BookUserRelation


def set_rating(book):
    rating = BookUserRelation.objects.filter(book=book).aggregate(rating=Avg('rating')).get('rating', 'null')
    book.rating = rating
    book.save()
