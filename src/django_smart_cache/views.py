from typing import List

from .cache import _cache_function_view, _get_models, _set_model_connection


def cache_view(models: List[str], timeout: int = 900):
    """Adiciona cache a view.

    Args:
        models (List[str]): lista de modelos relacionados que resetam o cache
        timeout (int, optional): duração do cache em segundos. Defaults to 900.
    Returns:
        callable: decorator para aplicar cache à view
    """
    model_classes = _get_models(models)

    def decorator(view_cls):
        prefix = f"{view_cls.__module__}.{view_cls.__name__}"
        _set_model_connection(model_classes, prefix)
        return _cache_function_view(view_cls, prefix, timeout)

    return decorator
