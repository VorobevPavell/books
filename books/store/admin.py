from django.contrib import admin
from django.contrib.admin import ModelAdmin

from store.models import Book, BookUserRelation


@admin.register(Book)
class AdminBook(ModelAdmin):
    pass


@admin.register(BookUserRelation)
class BookUserRelationAdmin(ModelAdmin):
    pass
