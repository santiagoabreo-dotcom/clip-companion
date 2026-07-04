"""
anthropic_backend.py
─────────────────────
Backend "cloud": Anthropic API. Mejor calidad y velocidad; el texto
copiado sale de la máquina hacia la API de Anthropic.
"""

import anthropic

from .base import LLMBackend


class AnthropicBackend(LLMBackend):
    """Backend de nube usando la API de Anthropic."""

    def __init__(self, api_key: str, model: str, max_tokens: int = 300):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def label(self) -> str:
        return f"Cloud (Anthropic · {self.model})"

    def query(self, text: str, system_prompt: str = "") -> tuple[str, bool]:
        try:
            msg = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": text}],
            )
            response = msg.content[0].text.strip()
            return response, False

        except anthropic.AuthenticationError:
            return "❌ API key inválida", True
        except anthropic.RateLimitError:
            return "⚠ Rate limit excedido", True
        except anthropic.APIConnectionError:
            return "🔌 Error de conexión", True
        except Exception as e:
            return f"? {type(e).__name__}", True

    def query_image(self, image_base64: str, text: str, system_prompt: str = "") -> tuple[str, bool]:
        try:
            msg = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64,
                            },
                        },
                        {"type": "text", "text": text},
                    ],
                }],
            )
            response = msg.content[0].text.strip()
            return response, False

        except anthropic.AuthenticationError:
            return "❌ API key inválida", True
        except anthropic.RateLimitError:
            return "⚠ Rate limit excedido", True
        except anthropic.APIConnectionError:
            return "🔌 Error de conexión", True
        except Exception as e:
            return f"? {type(e).__name__}", True
