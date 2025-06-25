from typing import List

from .cache import _cache_method, _get_models, _set_model_connection


def cache_viewset(
    models: List[str], methods: tuple=('list', 'retrieve'), timeout: int = 900,
):
    """Adiciona cache a viewset.

    Args:
        models (List[str]): lista de modelos relacionados que resetam o cache
        methods (tuple, optional): méthodos a serem cacheados. 
            Defaults to ('list', 'retrieve').
        timeout (int, optional): duração do cache em segundos. Defaults to 900.

    Returns:
        HttpResponse: resposta da requisição em cache
    """
    model_classes = _get_models(models)

    def decorator(view_cls):
        for name in methods:
            prefix = f"{view_cls.__module__}.{view_cls.__name__}.{name}"
            method = getattr(view_cls, name, None)
            if callable(method):
                setattr(view_cls, name, _cache_method(method, prefix, timeout))

            _set_model_connection(model_classes, prefix)

        return view_cls

    return decorator
