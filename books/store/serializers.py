from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, BookUserRelation


class BookSerializer(ModelSerializer):
    like_counter = serializers.SerializerMethodField()
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    discount_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name',
                  'like_counter', 'annotated_likes', 'rating', 'discount_price')

    @staticmethod
    def get_like_counter(instance: Book):
        return BookUserRelation.objects.filter(book=instance.id, like=True).count()


class BookUserRelationSerializer(ModelSerializer):
    class Meta:
        model = BookUserRelation
        fields = ('book', 'like', 'in_bookmarks', 'rating')
