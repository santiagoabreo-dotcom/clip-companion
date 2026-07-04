"""
api_client.py
─────────────
Obsoleto: reemplazado por el paquete `backends/` (arquitectura
intercambiable cloud/local). Se mantiene este alias para no romper
imports externos que apunten a `AnthropicClient`.
"""

from .backends.anthropic_backend import AnthropicBackend as AnthropicClient

__all__ = ["AnthropicClient"]
