from rest_framework.viewsets import ModelViewSet

from store.models import Book
from store.serializers import BookSerializer


class BooksViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
