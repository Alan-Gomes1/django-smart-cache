import hashlib
import json
from functools import wraps
from typing import List

from django.apps import apps
from django.db.models.signals import post_delete, post_save, m2m_changed
from django.core.cache import cache
from rest_framework.response import Response


ERROR_MESSAGE = "O caminho da model deve ser no formato 'app_label.model_name'"
MODEL_CACHE_PREFIXES = {}
REGISTERED_MODELS = set()


def _get_user_part(request) -> str:
    """Obtém a parte do usuário da chave do cache.

    Args:
        request: objeto de requisição

    Returns:
        str: parte do usuário da chave do cache
    """
    if request.user and request.user.is_authenticated:
        user_part = f"u{request.user.pk}"
    elif hasattr(request, "auth") and request.auth:
        user_part = f"t{request.auth.key}"
    else:
        token = request.headers.get('Authorization').split(' ')[1]
        if token:
            user_part = f"t{token}"
    return user_part


def _get_request_part(params, kwargs) -> str:
    """Obtém a parte da requisição da chave do cache.

    Args:
        params: parâmetros da requisição
        kwargs: argumentos da requisição

    Returns:
        str: parte da requisição da chave do cache
    """
    request_part = 'all'
    if 'pk' in kwargs:
        request_part = f"{kwargs['pk']}"
    elif params:
        request_part = hashlib.md5(
            json.dumps(params, sort_keys=True).encode()
        ).hexdigest()
    return request_part


def _cache_method(method: callable, prefix: str, timeout: int):
    @wraps(method)
    def wrapper(self, request, *args, **kwargs):
        try:
            user_part = _get_user_part(request)
        except Exception:
            print("usuário não autenticado")
            return method(self, request, *args, **kwargs)

        params = sorted(request.query_params.items())
        request_part = _get_request_part(params, kwargs)
        key = f"{prefix}:{user_part}:{request_part}"
        cached = cache.get(key)

        if cached is not None:
            data, status = cached
            return Response(data, status=status)

        try:
            response = method(self, request, *args, **kwargs)
        except Exception:
            raise

        if getattr(response, 'status_code', None) == 200:
            cache.set(key, (response.data, 200), timeout)
        return response

    return wrapper


def _cache_function_view(view_func, prefix, timeout):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            user_part = _get_user_part(request)
        except Exception:
            user_part = "anonymous"

        params = sorted(request.GET.items())
        request_part = _get_request_part(params, kwargs)
        key = f"{prefix}:{user_part}:{request_part}"
        cached = cache.get(key)

        if cached is not None:
            return cached

        try:
            response = view_func(request, *args, **kwargs)
        except Exception:
            raise

        if getattr(response, 'render') and callable(response.render):
            response.render()
            if response.status_code == 200:
                cache.set(key, response, timeout)
        return response

    return wrapper


def delete_keys_with_prefix(prefix: str) -> None:
    """Deleta manualmente todas as chaves do cache que começam com um prefixo.

    Args:
        prefix (str): prefixo das chaves a serem deletadas
    """
    for key in cache._cache.keys():
        if key.startswith(prefix):
            cache.delete(key)


def cache_invalidation_handler(sender, instance, **kwargs) -> None:
    prefixes = MODEL_CACHE_PREFIXES.get(sender, set())
    for prefix in prefixes:
        pattern = f"{prefix}:*"
        try:
            cache.delete_pattern(pattern)
        except Exception:
            delete_keys_with_prefix(prefix)


def _get_models(models: List[str]) -> List[object]:
    """Obtém os modelos a partir de uma lista de strings.

    Args:
        models (List[str]): lista de modelos no formato 'app_label.model_name'

    Returns:
        List[object]: lista de classes de modelo correspondentes
    """
    model_classes = []
    for path in models:
        try:
            model_classes.append(apps.get_model(path))
        except (LookupError, ValueError):
            print(f"model não encontrada: {ERROR_MESSAGE}")
            continue
    return model_classes


def _set_model_connection(models: List[object], prefix: str) -> None:
    """Registra os modelos para observar alterações e resetar o cache.

    Args:
        models (List[object]): lista de modelos a serem observados
        prefix (str): prefixo do cache para identificar a view(set)
    """
    for model in models:
        if model not in MODEL_CACHE_PREFIXES:
            MODEL_CACHE_PREFIXES[model] = set()
        MODEL_CACHE_PREFIXES[model].add(prefix)
        if model not in REGISTERED_MODELS:  # impede multiplas conexões
            _register_models(model)
            REGISTERED_MODELS.add(model)


def _register_models(model: object) -> None:
    """Vincula a função de resetar o cache a um modelo para observar as 
    alterações no banco de dados.

    Args:
        models (object): modelo a serem observados
    """
    post_save.connect(cache_invalidation_handler, sender=model, weak=False)
    post_delete.connect(cache_invalidation_handler, sender=model, weak=False)
    for field in model._meta.get_fields():
        if getattr(field, 'many_to_many', False):
            through = getattr(field.remote_field, 'through', None)
            if through:
                m2m_changed.connect(
                    cache_invalidation_handler, sender=through, weak=False,
                )
