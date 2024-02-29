from rest_framework.serializers import ModelSerializer

from store.models import Book, BookUserRelation


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookUserRelationSerializer(ModelSerializer):

    class Meta:
        model = BookUserRelation
        fields = ('book', 'like', 'in_bookmarks', 'rating')
