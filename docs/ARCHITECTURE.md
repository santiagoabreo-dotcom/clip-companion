# Arquitectura

## Flujo

```
 usuario copia texto
        │
        ▼
ClipboardMonitor (thread, polling cada poll_interval)
        │  detecta cambio en el portapapeles
        ▼
LLMBackend.query(texto, system_prompt)     ← interfaz común
        │
        ├── AnthropicBackend  (cloud, requiere API key)
        └── LocalOllamaBackend (local, requiere Ollama corriendo)
        │
        ▼
OverlayWindow.show(respuesta)   ← ventana flotante, se cierra con clic o Ctrl+H
```

`Ctrl+L` dispara el mismo flujo pero con una captura de pantalla en vez de
texto del portapapeles (`LLMBackend.query_image`).

## Por qué una interfaz común (`LLMBackend`)

`clipboard_monitor.py` y `main.py` no importan `anthropic` ni `requests`
directamente: solo conocen `LLMBackend` (`backends/base.py`), que define
`query()` y `query_image()`. Esto permite:

- Elegir backend en tiempo de ejecución (`setup_window.py` guarda
  `provider: "cloud" | "local"` en `~/.clipcompanion.json`).
- Priorizar privacidad (local) o calidad/velocidad (cloud) según el caso
  de uso, sin tocar el resto del código.
- Agregar un proveedor nuevo (otra API en la nube, otro runtime local)
  implementando la interfaz — ver `docs/INTEGRATION.md`.

`backends/factory.py` es el único lugar que decide, según `provider`,
qué clase concreta instanciar.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Entry point: arranca la app, decide si mostrar el setup o ir directo con la config guardada |
| `config.py` | Persistencia en `~/.clipcompanion.json`, constantes (modelos disponibles, prompts por defecto) |
| `clipboard_monitor.py` | Thread de polling del portapapeles + captura de pantalla, delega en `LLMBackend` |
| `overlay_window.py` | Ventana flotante minimalista (Tkinter) |
| `setup_window.py` | UI de configuración inicial: elegir backend, modelo, esquina |
| `backends/base.py` | Contrato `LLMBackend` |
| `backends/anthropic_backend.py` | Implementación cloud |
| `backends/local_backend.py` | Implementación local (Ollama) |
| `backends/factory.py` | `create_backend(provider, **kwargs) -> LLMBackend` |

## Decisiones y límites conocidos

- **Threads, no async**: el polling y las consultas al backend corren en
  `threading.Thread` daemon, no en asyncio. Es más simple de integrar con
  Tkinter (que no es async-friendly) a costa de no ser la opción más
  eficiente para I/O concurrente — aceptable para un uso personal de un
  solo usuario.
- **Config en JSON plano**: `~/.clipcompanion.json` guarda la API key en
  texto plano. Suficiente para un MVP de un solo usuario en su propia
  máquina; para algo más robusto habría que usar `keyring`.
- **Polling, no eventos nativos de portapapeles**: se revisa el
  portapapeles cada `poll_interval` segundos en vez de suscribirse a un
  evento del sistema operativo. Más portable (funciona igual en Windows/
  macOS/Linux) a costa de una latencia mínima de detección.
