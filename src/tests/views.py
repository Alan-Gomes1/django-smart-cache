from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django_smart_cache.models import CachedModel
from django_smart_cache.views import cache_view


@cache_view(models=["django_smart_cache.CachedModel"], timeout=30)
@api_view(["GET"])
def cached_api_view(request):
    count = CachedModel.objects.count()
    return Response({"count": count})

@cache_view(models=["django_smart_cache.CachedModel"], timeout=30)
def cached_template_view(request):
    count = CachedModel.objects.count()
    return render(request, "cached_template.html", {"count": count})
