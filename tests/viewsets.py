from rest_framework import viewsets, serializers

from django_smart_cache.viewsets import cache_viewset
from django_smart_cache.models import CachedModel


class CachedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CachedModel
        fields = ["id", "value"]


@cache_viewset(models=["django_smart_cache.CachedModel"], timeout=30)
class CachedViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    serializer_class = CachedSerializer

    def get_queryset(self):
        return CachedModel.objects.all()
