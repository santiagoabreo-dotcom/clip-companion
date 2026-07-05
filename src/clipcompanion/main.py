"""
main.py
───────
Clip Companion — Asistente IA Ambient Basado en Portapapeles

Entry point de la aplicación. Maneja inicialización y ciclo de vida.

Uso:
    python main.py
"""

from typing import Optional

import keyboard
import tkinter as tk
from dotenv import load_dotenv

from .backends import create_backend
from .clipboard_monitor import ClipboardMonitor
from .config import DEFAULT_SCREENSHOT_PROMPT, DEFAULT_SYSTEM_PROMPT, ConfigManager
from .overlay_window import OverlayWindow

# Si hay un .env en el directorio de trabajo, lo carga (ANTHROPIC_API_KEY,
# CLIP_COMPANION_PROVIDER, CLIP_COMPANION_OLLAMA_HOST). No es obligatorio:
# sin .env, la app pide estos datos por la ventana de setup.
load_dotenv()
from .setup_window import SetupWindow

# Hotkeys
HOTKEY = "ctrl+h"  # Ocultar/mostrar overlay
SCREENSHOT_HOTKEY = "ctrl+l"  # Capturar pantalla y preguntar


class App:
    """Aplicación principal de Clip Companion."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Clip Companion")
        self.monitor: Optional[ClipboardMonitor] = None
        self.overlay: Optional[OverlayWindow] = None

    def run(self) -> None:
        """Iniciar la aplicación."""
        cfg = ConfigManager.load()

        # Si hay configuración guardada y es utilizable, arrancar directo.
        has_saved_config = cfg and (
            (cfg.get("provider", "cloud") == "cloud" and cfg.get("api_key"))
            or (cfg.get("provider") == "local")
        )

        if has_saved_config:
            self.root.after(
                0,
                self._on_start,
                cfg.get("provider", "cloud"),
                cfg.get("api_key", ""),
                cfg.get("model", ""),
                cfg.get("corner", "se"),
                cfg.get("ollama_host", ""),
            )
        else:
            SetupWindow(self.root, on_start=self._on_start)

        self.root.mainloop()

    def _on_start(
        self,
        provider: str,
        api_key: str,
        model: str,
        corner: str,
        ollama_host: str,
    ) -> None:
        """Callback cuando se inicia con configuración válida."""
        backend = create_backend(
            provider,
            api_key=api_key,
            model=model,
            ollama_host=ollama_host,
        )

        overlay_cfg = ConfigManager.load()
        alpha = overlay_cfg.get("alpha", 0.92)

        self.overlay = OverlayWindow(self.root, corner=corner, alpha=alpha)

        self.monitor = ClipboardMonitor(
            backend=backend,
            on_response=self.overlay.show,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            screenshot_prompt=DEFAULT_SCREENSHOT_PROMPT,
            poll_interval=1.5,
        )
        self.monitor.start()

        keyboard.add_hotkey(HOTKEY, self.overlay.toggle, suppress=True)
        keyboard.add_hotkey(SCREENSHOT_HOTKEY, self.monitor.screenshot_and_ask, suppress=True)

        print("✓ Clip Companion iniciado")
        print(f"  Backend: {backend.label()}")
        print(f"  Overlay: esquina {corner}")
        print(f"  Hotkey mostrar/ocultar: {HOTKEY}")
        print(f"  Hotkey preguntar sobre la pantalla: {SCREENSHOT_HOTKEY}")


def main():
    """Entry point."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
