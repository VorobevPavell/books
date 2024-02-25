from django.contrib import admin
from django.urls import path
from rest_framework.routers import SimpleRouter

from store.views import BooksViewSet

router = SimpleRouter()
router.register(r'book', BooksViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
]
urlpatterns += router.urls
