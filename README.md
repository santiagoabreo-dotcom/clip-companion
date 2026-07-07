# Clip Companion

**Asistente IA Ambient Basado en Portapapeles**

Un copiloto discreto que vive en segundo plano y responde solo cuando lo invocás copiando texto: la respuesta aparece en un overlay flotante, sin abrir ventanas ni cambiar de contexto. Pensado para entornos donde la atención sostenida importa (aulas, trabajo profundo, lectura técnica) — un asistente de consulta rápida, no una herramienta para ocultar nada.

## Características

- **Interfaz sin cambio de contexto**: copiás texto, la respuesta aparece en un overlay flotante legible; un clic o `Ctrl+H` lo cierra.
- **Ambient AI**: el asistente actúa solo cuando copiás algo, no hay ventana de chat que atender.
- **Backend intercambiable**: Anthropic (cloud) o Ollama (local) — mismo código, se elige en el setup. Con el backend local, el texto copiado nunca sale de tu máquina.
- **Captura de pantalla opcional** (`Ctrl+L`): pregunta sobre lo que se ve en tu pantalla, usando el mismo backend.

## Stack

- **Core**: Python, threads para monitoreo de portapapeles sin bloquear la UI
- **UI**: overlay flotante nativo (Tkinter)
- **IA**: `backends/` — interfaz común (`LLMBackend`) con implementaciones para Anthropic (cloud) y Ollama (local)

## Arquitectura

```
clip-companion/
├── src/clipcompanion/
│   ├── main.py                # Entry point, orquesta todo
│   ├── config.py              # Persistencia de configuración (~/.clipcompanion.json)
│   ├── clipboard_monitor.py   # Polling de portapapeles + captura de pantalla
│   ├── overlay_window.py      # UI del overlay flotante
│   ├── setup_window.py        # Ventana de configuración inicial (elige backend)
│   └── backends/
│       ├── base.py            # Interfaz LLMBackend (contrato común)
│       ├── anthropic_backend.py  # Backend cloud
│       ├── local_backend.py      # Backend local (Ollama)
│       └── factory.py            # create_backend(provider, ...) — único punto de switch
├── docs/
│   ├── ARCHITECTURE.md
│   └── INTEGRATION.md         # Cómo agregar un backend nuevo
└── requirements.txt
```

El resto de la app (`clipboard_monitor.py`, `main.py`) solo conoce la interfaz `LLMBackend`, nunca un proveedor concreto — así se puede sumar un backend nuevo sin tocar el core (ver `docs/INTEGRATION.md`).

## Instalación

```bash
git clone https://github.com/<tu-usuario>/clip-companion.git
cd clip-companion
pip install -e .
clip-companion
```

(Alternativa sin instalar el paquete: `pip install -r requirements.txt` y después `PYTHONPATH=src python -m clipcompanion.main` — hace falta `PYTHONPATH=src` porque el código usa imports relativos dentro del paquete `clipcompanion`.)

La primera vez se abre una ventana de setup para elegir backend (cloud/local), modelo y esquina del overlay. Queda guardado en `~/.clipcompanion.json` para los próximos arranques.

### Backend cloud (Anthropic)

Necesitás una API key de [console.anthropic.com](https://console.anthropic.com/settings/keys). Se puede precargar por variable de entorno (`ANTHROPIC_API_KEY`, ver `.env.example`) o pegarla directo en el setup.

### Backend local (Ollama, privado)

1. Instalar [Ollama](https://ollama.com) y dejarlo corriendo (`ollama serve`).
2. Descargar un modelo: `ollama pull llama3.2`.
3. En el setup, elegir "Local (Ollama, privado)". El texto copiado nunca sale de tu máquina.

## Uso

1. Copiá cualquier texto (una pregunta, un término, un párrafo largo).
2. El asistente lo procesa en segundo plano.
3. La respuesta aparece en el overlay flotante — un clic o `Ctrl+H` lo oculta.
4. `Ctrl+L` captura la pantalla y le pregunta al mismo backend sobre lo que ve.

## Notas de seguridad

- La API key (backend cloud) se guarda en texto plano en `~/.clipcompanion.json`. Para un uso más robusto, considerar `keyring` en vez de un archivo — queda en el roadmap.
- El backend local no envía nada a internet; el cloud sí envía el texto copiado a la API de Anthropic. La elección de backend es justamente para poder decidir esto según el caso de uso.

## Roadmap

- [ ] Guardar la API key con `keyring` en vez de JSON plano
- [ ] Historial de consultas (opcional, desactivable)
- [ ] Más backends (ej: otra API en la nube) — la arquitectura ya está pensada para esto
- [ ] Tests unitarios de `backends/` con mocks
- [ ] Empaquetado como ejecutable (PyInstaller) para no requerir Python instalado

## Licencia

MIT

---

**Proyecto Personal · Santiago Abreo**
