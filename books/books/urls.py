from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import SimpleRouter

from store.views import BooksViewSet, auth, BookUserRelationView

router = SimpleRouter()
router.register(r'book', BooksViewSet)
router.register(r'book_relations', BookUserRelationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('', include('social_django.urls', namespace='social')),
    path("__debug__/", include("debug_toolbar.urls")),
    path('auth/', auth)
]
urlpatterns += router.urls
