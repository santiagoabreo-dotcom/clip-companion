"""
local_backend.py
─────────────────
Backend "local": usa Ollama (https://ollama.com) corriendo en la propia
máquina. El texto copiado nunca sale del equipo — pensado para casos
donde la privacidad importa más que la velocidad o la calidad de
respuesta que da un modelo de nube.

Requiere tener Ollama instalado y corriendo (`ollama serve`) y al menos
un modelo descargado (`ollama pull llama3.2`).
"""

import requests

from .base import LLMBackend

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"


class LocalOllamaBackend(LLMBackend):
    """Backend local vía la API HTTP de Ollama."""

    def __init__(self, model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST, timeout: float = 30.0):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def label(self) -> str:
        return f"Local (Ollama · {self.model})"

    def _chat(self, content: str, system_prompt: str, images: list[str] | None = None) -> tuple[str, bool]:
        user_message: dict = {"role": "user", "content": content}
        if images:
            user_message["images"] = images

        try:
            resp = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        user_message,
                    ],
                    "stream": False,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            text = (data.get("message") or {}).get("content", "").strip()
            return text or "(sin respuesta)", False

        except requests.exceptions.ConnectionError:
            return "🔌 No se pudo conectar a Ollama. ¿Está corriendo (`ollama serve`)?", True
        except requests.exceptions.Timeout:
            return "⏱ Tiempo de espera agotado", True
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return f"❌ Modelo '{self.model}' no encontrado (¿corriste `ollama pull {self.model}`?)", True
            return f"❌ Error HTTP {e.response.status_code if e.response is not None else ''}", True
        except Exception as e:
            return f"? {type(e).__name__}", True

    def query(self, text: str, system_prompt: str = "") -> tuple[str, bool]:
        return self._chat(text, system_prompt)

    def query_image(self, image_base64: str, text: str, system_prompt: str = "") -> tuple[str, bool]:
        # Requiere un modelo multimodal descargado localmente (ej: llava).
        return self._chat(text, system_prompt, images=[image_base64])
