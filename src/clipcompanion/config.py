"""
config.py
─────────
Manejo de configuración para Clip Companion.
"""

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

# Modelos de Anthropic disponibles (backend "cloud").
CLOUD_MODELS = [
    ("Haiku 4.5  — rápido y barato", "claude-haiku-4-5-20251001"),
    ("Sonnet 4   — equilibrado", "claude-sonnet-4-20250514"),
    ("Opus 4     — más capaz", "claude-opus-4-20250514"),
]

# Modelos locales sugeridos para el backend "local" (vía Ollama). El
# usuario puede tipear cualquier otro nombre que tenga descargado.
LOCAL_MODELS = [
    ("Llama 3.2 (3B) — liviano", "llama3.2"),
    ("Llama 3.1 (8B) — más capaz", "llama3.1"),
    ("Mistral 7B", "mistral"),
]

# Alias retrocompatible: código previo importaba `MODELS` a secas
# asumiendo el backend cloud.
MODELS = CLOUD_MODELS

DEFAULT_OLLAMA_HOST = "http://localhost:11434"

# Prompt de propósito general: explica, traduce o resume lo que el
# usuario copió. Nada de "solo la letra correcta" — este es un asistente,
# no una herramienta para responder exámenes a escondidas.
DEFAULT_SYSTEM_PROMPT = (
    "Sos un asistente conciso que ayuda a entender rápido lo que el usuario "
    "acaba de copiar al portapapeles. Si es una pregunta, respondela. Si es "
    "un término, frase o texto en otro idioma, explicalo o traducilo "
    "brevemente. Si es un fragmento largo, resumilo en 1-2 frases. Respondé "
    "siempre en pocas líneas, sin relleno ni explicaciones innecesarias."
)

DEFAULT_SCREENSHOT_PROMPT = (
    "Mirá esta captura de pantalla y respondé de forma breve y útil sobre "
    "su contenido (explicá, resumí o respondé la pregunta que se vea, según "
    "corresponda)."
)


class OverlayConfig(BaseModel):
    """Configuración del overlay."""

    corner: str = Field(default="se", description="Esquina: ne, nw, se, sw, sc")
    alpha: float = Field(default=0.92, ge=0.0, le=1.0)
    poll_interval: float = Field(default=1.5, description="Segundos entre checks de clipboard")


class APIConfig(BaseModel):
    """Configuración del backend cloud (retenida por compatibilidad)."""

    api_key: str = Field(..., description="API Key de Anthropic")
    model: str = Field(default=CLOUD_MODELS[0][1])
    max_tokens: int = Field(default=300, ge=1, le=4096)


class Config(BaseModel):
    """Configuración completa."""

    api: APIConfig
    overlay: OverlayConfig = Field(default_factory=OverlayConfig)


class ConfigManager:
    """Gestor de configuración persistente.

    Nota de seguridad: la API key se guarda en texto plano en
    `~/.clipcompanion.json` (permisos del sistema operativo del usuario).
    Para un uso más robusto, considerar `keyring` en vez de un archivo.
    """

    CONFIG_FILE = Path.home() / ".clipcompanion.json"

    @classmethod
    def load(cls) -> dict:
        """Cargar configuración del archivo."""
        try:
            if cls.CONFIG_FILE.exists():
                with open(cls.CONFIG_FILE) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @classmethod
    def save(cls, data: dict) -> bool:
        """Guardar configuración a archivo."""
        try:
            with open(cls.CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def validate(cls, data: dict) -> Optional[Config]:
        """Validar configuración."""
        try:
            return Config(**data)
        except Exception:
            return None
