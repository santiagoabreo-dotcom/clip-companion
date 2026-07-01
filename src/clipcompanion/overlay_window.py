"""
overlay_window.py
─────────────────
Overlay minimalista para mostrar respuestas.
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Optional

MAX_WIDTH_PX = 360


class OverlayWindow:
    """Overlay flotante minimalista, pensado para leerse de un vistazo
    (no para pasar desapercibido: si el usuario copió algo, quiere ver
    la respuesta)."""

    POSITIONS = {
        "se": lambda w, h, sw, sh: (sw - w - 16, sh - h - 56),
        "sw": lambda w, h, sw, sh: (16, sh - h - 56),
        "ne": lambda w, h, sw, sh: (sw - w - 16, 16),
        "nw": lambda w, h, sw, sh: (16, 16),
        "sc": lambda w, h, sw, sh: ((sw - w) // 2, sh - h - 56),
    }

    def __init__(self, root: tk.Tk, corner: str = "se", alpha: float = 0.92):
        self.root = root
        self.corner = corner
        self.alpha = alpha
        self.win: Optional[tk.Toplevel] = None
        self._last_text = ""
        self._font = tkfont.Font(family="Segoe UI", size=11)

    def show(self, text: str) -> None:
        """Mostrar texto en el overlay."""
        self._last_text = text.strip()
        self.root.after(0, self._show_impl, self._last_text)

    def toggle(self) -> None:
        """Ocultar/mostrar overlay."""
        if self.win and self.win.winfo_exists():
            self.root.after(0, self._close_impl)
        elif self._last_text:
            self.root.after(0, self._show_impl, self._last_text)

    def close(self) -> None:
        """Cerrar overlay."""
        self.root.after(0, self._close_impl)

    def _close_impl(self) -> None:
        """Implementación de cerrar (thread-safe)."""
        if self.win and self.win.winfo_exists():
            self.win.destroy()
            self.win = None

    def _show_impl(self, text: str) -> None:
        """Implementación de mostrar (thread-safe)."""
        self._close_impl()

        win = tk.Toplevel(self.root)
        self.win = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", self.alpha)
        win.configure(bg="#1e1e2e", highlightbackground="#89b4fa", highlightthickness=1)

        lbl = tk.Label(
            win,
            text=text,
            bg="#1e1e2e",
            fg="#e6e6e6",
            font=self._font,
            padx=12,
            pady=10,
            bd=0,
            relief="flat",
            highlightthickness=0,
            justify="left",
            wraplength=MAX_WIDTH_PX,
        )
        lbl.pack()

        # Click para cerrar
        lbl.bind("<Button-1>", lambda e: self._close_impl())
        win.bind("<Button-1>", lambda e: self._close_impl())

        # Posicionar
        win.update_idletasks()
        w = win.winfo_reqwidth()
        h = win.winfo_reqheight()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()

        pos_func = self.POSITIONS.get(self.corner, self.POSITIONS["se"])
        x, y = pos_func(w, h, sw, sh)
        win.geometry(f"+{x}+{y}")
