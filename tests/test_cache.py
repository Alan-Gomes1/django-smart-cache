import pytest

from unittest.mock import patch
from django.core.cache import cache
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
