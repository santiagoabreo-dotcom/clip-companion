"""
factory.py
──────────
Punto único donde se decide qué backend concreto instanciar según la
configuración guardada por el usuario. Agregar un proveedor nuevo (por
ejemplo, otra API en la nube) significa: crear una clase que implemente
`LLMBackend` y sumar un `elif` acá — nada más del código cambia.
"""

from .anthropic_backend import AnthropicBackend
from .base import LLMBackend
from .local_backend import DEFAULT_HOST as OLLAMA_DEFAULT_HOST
from .local_backend import DEFAULT_MODEL as OLLAMA_DEFAULT_MODEL
from .local_backend import LocalOllamaBackend


def create_backend(provider: str, **kwargs) -> LLMBackend:
    """Crea el backend correspondiente al `provider` ("cloud" o "local")."""
    if provider == "local":
        return LocalOllamaBackend(
            model=kwargs.get("model") or OLLAMA_DEFAULT_MODEL,
            host=kwargs.get("ollama_host") or OLLAMA_DEFAULT_HOST,
        )

    # "cloud" (default): Anthropic
    api_key = kwargs.get("api_key")
    if not api_key:
        raise ValueError("El backend 'cloud' requiere api_key")
    return AnthropicBackend(
        api_key=api_key,
        model=kwargs.get("model", "claude-haiku-4-5-20251001"),
        max_tokens=kwargs.get("max_tokens", 300),
    )
