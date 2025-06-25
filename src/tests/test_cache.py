import pytest

from unittest.mock import patch
from django.core.cache import cache
from django.test import Client
from rest_framework.test import APIClient

from django_smart_cache.models import CachedModel

# Marca todos os testes neste arquivo para terem acesso ao BD
pytestmark = pytest.mark.django_db

def test_cache_set_and_get():
    """Testa se o cache funciona corretamente."""    
    cache.set("my_key", "my_value", 30)
    value = cache.get("my_key")
    assert value == "my_value"


def test_viewset_list_caching():
    """Testa se a action 'list' é cacheada."""
    obj = CachedModel.objects.create(value="My Value")
    cache.clear()
    client = APIClient()
    url = "/cached/"
    target = "tests.viewsets.CachedModel.objects.all"
    client.credentials(HTTP_AUTHORIZATION='Bearer token')

    with patch(target) as mock_queryset:
        mock_queryset.return_value = [obj]

        # Primeira Requisição (Cache Miss)
        response1 = client.get(url)
        assert response1.status_code == 200
        assert "My Value" in response1.content.decode()
        # Verificamos: A consulta ao banco de dados foi feita UMA vez.
        assert mock_queryset.call_count == 1

        # Segunda Requisição (Cache Hit)
        response2 = client.get(url)
        assert response2.status_code == 200
        assert "My Value" in response2.content.decode()
        # O contador de chamadas do mock AINDA deve ser 1.
        assert mock_queryset.call_count == 1

        # Terceira Requisição cache limpo
        cache.clear()
        response3 = client.get(url)
        assert response3.status_code == 200
        # Agora, a consulta ao banco deve ter sido chamada novamente.
        assert mock_queryset.call_count == 2


def test_cache_view_decorator(db):
    """Testa se o decorator cache_view funciona corretamente em views 
    baseadas em função."""

    cache.clear()
    client = APIClient()
    url = "/cached-api/"

    # Cria um objeto para contar
    CachedModel.objects.create(value="A")

    # Primeira chamada (cache miss)
    key = cache.get("tests.cached_api_view")
    assert key is None
    response1 = client.get(url)
    assert response1.status_code == 200
    assert response1.json()["count"] == 1
    # Verifica se o cache foi criado
    key = cache.get("tests.cached_api_view")
    assert key is not None

    # Adiciona outro objeto, mas o cache deve ser resetado
    CachedModel.objects.create(value="B")
    key = cache.get("tests.cached_api_view")
    assert key is None
    response2 = client.get(url)
    assert response2.status_code == 200
    # Ainda deve ser 1, pois está cacheado
    assert response2.json()["count"] == 2
    key = cache.get("tests.cached_api_view")
    assert key is not None


def test_cache_view_decorator_template(db, settings):
    """Testa se o decorator cache_view funciona corretamente em views 
    Django que renderizam template."""
    settings.TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ["src/tests/templates"],
            'APP_DIRS': True,
            'OPTIONS': {},
        },
    ]

    cache.clear()
    client = Client()
    url = "/cached-template/"

    CachedModel.objects.create(value="A")
    response1 = client.get(url)
    assert response1.status_code == 200
    assert "Count: 1" in response1.content.decode()

    CachedModel.objects.create(value="B")
    response2 = client.get(url)
    assert response2.status_code == 200
    # Ainda deve ser 1, pois está cacheado
    assert "Count: 1" in response2.content.decode()

    cache.clear()
    response3 = client.get(url)
    assert response3.status_code == 200
    assert "Count: 2" in response3.content.decode()
