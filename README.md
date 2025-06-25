# django-smart-cache

Biblioteca de cache inteligente e automática para Django e Django Rest Framework.

## Visão Geral

O `django-smart-cache` oferece decorators e utilitários para adicionar cache automático em views e viewsets do Django/DRF, invalidando o cache sempre que modelos relacionados sofrem alterações. Ideal para APIs e páginas que precisam de alta performance sem perder a atualização dos dados.

- Cache automático para views e viewsets
- Invalidação automática ao alterar modelos relacionados
- Suporte a autenticação (cache por usuário/token)
- Fácil integração com projetos Django existentes

## Instalação

Requisitos:
- Python >= 3.8
- Django == 2.2
- djangorestframework == 3.10

Instale via pip:
```bash
pip install django-smart-cache
```

## Configuração

Adicione `django_smart_cache` ao seu `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    "django_smart_cache.apps.DjangoSmartCacheConfig",
]
```

Configure o cache do Django normalmente (exemplo com memória local):
```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}
```

## Como Usar

### Cache em Viewsets (DRF)

```python
from django_smart_cache.viewsets import cache_viewset


@cache_viewset(models=["myapp.MyModel"], timeout=60)
class MyViewSet(viewsets.ModelViewSet):
    ...
```
- `models`: lista de modelos que, ao serem alterados, invalidam o cache.
- `timeout`: tempo do cache em segundos (padrão: 900).

### Cache em Views (função ou classe)

```python
from django_smart_cache.views import cache_view


@cache_view(models=["myapp.MyModel"], timeout=60)
def minha_view(request):
    ...
```

### Exemplo Completo

```python
from rest_framework import viewsets, serializers
from django_smart_cache.viewsets import cache_viewset
from .models import MyModel


class MySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = "__all__"


@cache_viewset(models=["myapp.MyModel"], timeout=60)
class MyViewSet(viewsets.ModelViewSet):
    serializer_class = MySerializer
    queryset = MyModel.objects.all()
```

## Funcionamento Interno

- O decorator gera uma chave de cache única por usuário/token e parâmetros da requisição.
- O cache é invalidado automaticamente via signals (`post_save`, `post_delete`, `m2m_changed`) dos modelos informados.
- Suporta cache para métodos `list` e `retrieve` em viewsets, e qualquer view baseada em função/classe.

## Testes

O projeto já inclui testes automatizados com `pytest` e `pytest-django`.

Para rodar os testes:
```bash
pytest
```

## Desenvolvimento

- Código-fonte: `src/django_smart_cache/`
- Testes: `src/tests/`
- Exemplo de template: `src/tests/templates/cached_template.html`

## Autor

Alan Gomes (<alan.gomes.ag28@gmail.com>)

## Licença

MIT
