# Cómo agregar un backend nuevo

La app solo depende de la interfaz `LLMBackend` (`backends/base.py`).
Agregar un proveedor nuevo (otra API en la nube, otro runtime local) no
requiere tocar `main.py`, `clipboard_monitor.py` ni `overlay_window.py`.

## 1. Implementar la interfaz

```python
# backends/mi_backend.py
from .base import LLMBackend

class MiBackend(LLMBackend):
    def __init__(self, **kwargs):
        ...

    def label(self) -> str:
        return "Mi Backend"

    def query(self, text: str, system_prompt: str = "") -> tuple[str, bool]:
        # Devolver (respuesta, hubo_error)
        ...

    def query_image(self, image_base64: str, text: str, system_prompt: str = "") -> tuple[str, bool]:
        # Opcional: si no se implementa, se usa el default de LLMBackend
        # (devuelve un mensaje de "no soportado").
        ...
```

Convención importante: `query()` y `query_image()` no deben levantar
excepciones hacia el llamador — atajarlas y devolver `(mensaje, True)`.
`clipboard_monitor.py` no tiene un `try/except` alrededor del backend
más que para no crashear el thread; el manejo de errores específico es
responsabilidad de cada backend.

## 2. Registrarlo en el factory

```python
# backends/factory.py
def create_backend(provider: str, **kwargs) -> LLMBackend:
    if provider == "mi_backend":
        return MiBackend(**kwargs)
    ...
```

## 3. (Opcional) Agregarlo a la UI de setup

En `setup_window.py`, sumar un `Radiobutton` más al selector de
`provider` y, si hace falta, un frame con los campos específicos del
nuevo backend (mirar cómo están armados `cloud_frame` y `local_frame`
como referencia).

## Backends existentes

- **`AnthropicBackend`** (`provider="cloud"`): usa la API de Anthropic.
  Requiere `api_key`. Mejor calidad/velocidad, el texto sale de la
  máquina.
- **`LocalOllamaBackend`** (`provider="local"`): usa la API HTTP de
  [Ollama](https://ollama.com) corriendo en `localhost`. No requiere API
  key ni conexión a internet una vez descargado el modelo. Pensado para
  cuando la privacidad del texto copiado importa más que la latencia o
  calidad de respuesta.
