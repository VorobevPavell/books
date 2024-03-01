from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, BookUserRelation


class BookReadersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'is_staff')


class BookSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    discount_price = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(source='owner.username', default='null',
                                       read_only=True)
    readers = BookReadersSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name',
                  'annotated_likes', 'rating', 'discount_price', 'owner_name', 'readers')


class BookUserRelationSerializer(ModelSerializer):
    class Meta:
        model = BookUserRelation
        fields = ('book', 'like', 'in_bookmarks', 'rating')
