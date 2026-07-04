"""
clipboard_monitor.py
────────────────────
Monitor del portapapeles con procesamiento en threads.
"""

import base64
import io
import threading
import time
from typing import Callable, Optional

import pyperclip
from PIL import ImageGrab

from .backends.base import LLMBackend


class ClipboardMonitor:
    """Monitorea el clipboard y procesa cambios con el backend de IA configurado."""

    def __init__(
        self,
        backend: LLMBackend,
        on_response: Callable[[str], None],
        system_prompt: str = "",
        screenshot_prompt: str = "",
        poll_interval: float = 1.5,
    ):
        self.backend = backend
        self.on_response = on_response
        self.system_prompt = system_prompt
        self.screenshot_prompt = screenshot_prompt or "Describí brevemente el contenido de esta captura."
        self.poll_interval = poll_interval

        self._last = ""
        self._running = True
        self._lock = threading.Lock()
        self._busy = False
        self._screenshot_busy = False
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self) -> None:
        """Iniciar monitoreo."""
        self._thread.start()

    def stop(self) -> None:
        """Detener monitoreo."""
        self._running = False

    def screenshot_and_ask(self) -> None:
        """Capturar pantalla y enviar al backend configurado."""
        if self._screenshot_busy:
            return
        self._screenshot_busy = True
        threading.Thread(target=self._process_screenshot, daemon=True).start()

    def _loop(self) -> None:
        """Loop principal de monitoreo."""
        while self._running:
            try:
                current = pyperclip.paste()
                with self._lock:
                    changed = bool(current) and current != self._last and current.strip()
                    if changed:
                        self._last = current

                if changed and not self._busy:
                    self._busy = True
                    threading.Thread(
                        target=self._process,
                        args=(current,),
                        daemon=True,
                    ).start()
            except Exception:
                pass
            time.sleep(self.poll_interval)

    def _process(self, text: str) -> None:
        """Procesar texto con el backend configurado."""
        try:
            response, _is_error = self.backend.query(text, self.system_prompt)
            self.on_response(response)
        finally:
            self._busy = False

    def _process_screenshot(self) -> None:
        """Capturar pantalla y procesar con el backend configurado."""
        try:
            img = ImageGrab.grab(all_screens=True)

            # Redimensionar a un tamaño razonable para no mandar imágenes gigantes.
            max_side = 1568
            w, h = img.size
            if max(w, h) > max_side:
                scale = max_side / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)))

            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=85)
            img_b64 = base64.standard_b64encode(buf.getvalue()).decode()

            response, _is_error = self.backend.query_image(
                img_b64,
                self.screenshot_prompt,
                self.system_prompt,
            )
            self.on_response(response)
        except Exception:
            self.on_response("❌ No se pudo procesar la captura de pantalla")
        finally:
            self._screenshot_busy = False
