# tests/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import cached_api_view, cached_template_view
from .viewsets import CachedViewSet

router = DefaultRouter()
router.register(r'cached', CachedViewSet, basename='cached')

urlpatterns = [
    path('cached-api/', cached_api_view, name='cached-func'),
    path('cached-template/', cached_template_view, name='cached-template'),
    path('', include(router.urls)),
]
