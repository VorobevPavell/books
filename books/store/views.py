from django.db.models import Count, Case, When, Avg, F
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, BookUserRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializer, BookUserRelationSerializer


class BooksViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(bookuserrelation__like=True, then=1))),
        rating=Avg('bookuserrelation__rating'),
        discount_price=F('price') - F('discount')
    ).select_related('owner').prefetch_related('readers')
    serializer_class = BookSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class BookUserRelationView(mixins.UpdateModelMixin,
                           GenericViewSet):
    queryset = BookUserRelation.objects.all()
    serializer_class = BookUserRelationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'book'

    def get_object(self):
        obj, created = BookUserRelation.objects.get_or_create(user=self.request.user,
                                                              book_id=self.kwargs['book'])

        print('created', created)
        return obj


def auth(request):
    return render(request, 'oauth.html')
