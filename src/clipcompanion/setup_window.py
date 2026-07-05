"""
setup_window.py
───────────────
Ventana de configuración inicial. Permite elegir entre backend cloud
(Anthropic) o local (Ollama), sin tocar código.
"""

import os
import tkinter as tk
from tkinter import font as tkfont
from typing import Callable

from .config import CLOUD_MODELS, DEFAULT_OLLAMA_HOST, LOCAL_MODELS, ConfigManager


class SetupWindow:
    """Ventana de setup inicial."""

    BG_COLOR = "#1a1a2e"
    TEXT_COLOR = "#ffffff"
    INPUT_BG = "#313244"
    INPUT_FG = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    BTN_CLOSE_BG = "#f38ba8"
    BTN_OK_BG = "#a6e3a1"
    BTN_FG = "#1e1e2e"

    def __init__(self, root: tk.Tk, on_start: Callable):
        self.root = root
        self.on_start = on_start
        self._build()

    def _build(self) -> None:
        cfg = ConfigManager.load()
        # Si no hay config guardada todavía, usar variables de entorno
        # (.env) como valores iniciales, si están presentes.
        env_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        env_provider = os.getenv("CLIP_COMPANION_PROVIDER", "")
        env_ollama_host = os.getenv("CLIP_COMPANION_OLLAMA_HOST", "")

        win = tk.Toplevel(self.root)
        self.win = win
        win.title("Clip Companion — Configuración")
        win.configure(bg=self.BG_COLOR)
        win.resizable(False, False)
        win.protocol("WM_DELETE_WINDOW", self.root.quit)

        font_title = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        font_label = tkfont.Font(family="Segoe UI", size=9)
        font_btn = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        font_small = tkfont.Font(family="Segoe UI", size=8)

        tk.Label(
            win, text="✦ Clip Companion", bg=self.BG_COLOR, fg=self.ACCENT_COLOR, font=font_title,
        ).pack(pady=(20, 2))

        tk.Label(
            win, text="Asistente ambient basado en portapapeles",
            bg=self.BG_COLOR, fg="#6c7086", font=font_small,
        ).pack(pady=(0, 16))

        # ── Backend: cloud o local ──────────────────────────────
        tk.Label(
            win, text="Backend de IA", bg=self.BG_COLOR, fg=self.TEXT_COLOR, font=font_label,
        ).pack(padx=24, pady=(0, 4), anchor="w")

        self.provider_var = tk.StringVar(value=cfg.get("provider") or env_provider or "cloud")
        provider_frame = tk.Frame(win, bg=self.BG_COLOR)
        provider_frame.pack(padx=24, pady=(0, 8), anchor="w")

        def _on_provider_change():
            self._refresh_provider_fields()

        tk.Radiobutton(
            provider_frame, text="☁ Cloud (Anthropic)", variable=self.provider_var, value="cloud",
            bg=self.BG_COLOR, fg=self.TEXT_COLOR, selectcolor=self.BG_COLOR,
            activebackground=self.BG_COLOR, activeforeground=self.ACCENT_COLOR,
            font=font_small, cursor="hand2", command=_on_provider_change,
        ).pack(side="left", padx=(0, 12))

        tk.Radiobutton(
            provider_frame, text="🔒 Local (Ollama, privado)", variable=self.provider_var, value="local",
            bg=self.BG_COLOR, fg=self.TEXT_COLOR, selectcolor=self.BG_COLOR,
            activebackground=self.BG_COLOR, activeforeground=self.ACCENT_COLOR,
            font=font_small, cursor="hand2", command=_on_provider_change,
        ).pack(side="left")

        # Contenedor fijo para los campos de cloud/local: se packea una
        # sola vez para no alterar el orden del resto de los widgets al
        # alternar de proveedor (pack_forget + pack reordenaría todo si
        # los frames colgaran directo de `win`).
        self.provider_fields_container = tk.Frame(win, bg=self.BG_COLOR)
        self.provider_fields_container.pack(padx=24, fill="x")

        # ── Campos específicos de "cloud" ───────────────────────
        self.cloud_frame = tk.Frame(self.provider_fields_container, bg=self.BG_COLOR)

        tk.Label(
            self.cloud_frame, text="API Key de Anthropic", bg=self.BG_COLOR, fg=self.TEXT_COLOR, font=font_label,
        ).pack(padx=0, pady=6, anchor="w")

        key_frame = tk.Frame(self.cloud_frame, bg=self.BG_COLOR)
        key_frame.pack(pady=(0, 4), fill="x")

        self.key_var = tk.StringVar(value=cfg.get("api_key") or env_api_key)
        key_entry = tk.Entry(
            key_frame, textvariable=self.key_var, show="•", bg=self.INPUT_BG, fg=self.INPUT_FG,
            insertbackground=self.INPUT_FG, relief="flat", bd=0,
            font=tkfont.Font(family="Segoe UI", size=10), width=38,
        )
        key_entry.pack(side="left", ipady=6, padx=(0, 6))
        self._key_entry = key_entry

        self._show_key = False

        def toggle_key():
            self._show_key = not self._show_key
            key_entry.configure(show="" if self._show_key else "•")
            btn_eye.configure(text="🙈" if self._show_key else "👁")

        btn_eye = tk.Button(
            key_frame, text="👁", bg=self.INPUT_BG, fg=self.TEXT_COLOR, relief="flat", bd=0,
            cursor="hand2", command=toggle_key, font=font_small,
        )
        btn_eye.pack(side="left")

        tk.Label(
            self.cloud_frame, text="Obtené tu key en console.anthropic.com/settings/keys",
            bg=self.BG_COLOR, fg="#6c7086", font=font_small,
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            self.cloud_frame, text="Modelo", bg=self.BG_COLOR, fg=self.TEXT_COLOR, font=font_label,
        ).pack(pady=(0, 4), anchor="w")

        self.cloud_model_var = tk.StringVar(value=cfg.get("model") if cfg.get("provider", "cloud") == "cloud" else CLOUD_MODELS[0][1])
        for label, value in CLOUD_MODELS:
            tk.Radiobutton(
                self.cloud_frame, text=label, variable=self.cloud_model_var, value=value,
                bg=self.BG_COLOR, fg=self.TEXT_COLOR, selectcolor=self.BG_COLOR,
                activebackground=self.BG_COLOR, activeforeground=self.ACCENT_COLOR,
                font=font_small, cursor="hand2",
            ).pack(padx=8, anchor="w")

        # ── Campos específicos de "local" ───────────────────────
        self.local_frame = tk.Frame(self.provider_fields_container, bg=self.BG_COLOR)

        tk.Label(
            self.local_frame, text="Servidor Ollama", bg=self.BG_COLOR, fg=self.TEXT_COLOR, font=font_label,
        ).pack(pady=6, anchor="w")

        self.ollama_host_var = tk.StringVar(value=cfg.get("ollama_host") or env_ollama_host or DEFAULT_OLLAMA_HOST)
        tk.Entry(
            self.local_frame, textvariable=self.ollama_host_var, bg=self.INPUT_BG, fg=self.INPUT_FG,
            insertbackground=self.INPUT_FG, relief="flat", bd=0,
            font=tkfont.Font(family="Segoe UI", size=10), width=38,
        ).pack(ipady=6, pady=(0, 8), fill="x")

        tk.Label(
            self.local_frame, text="Modelo (debe estar descargado con 'ollama pull')",
            bg=self.BG_COLOR, fg=self.TEXT_COLOR, font=font_label,
        ).pack(pady=(0, 4), anchor="w")

        self.local_model_var = tk.StringVar(value=cfg.get("model") if cfg.get("provider") == "local" else LOCAL_MODELS[0][1])
        for label, value in LOCAL_MODELS:
            tk.Radiobutton(
                self.local_frame, text=label, variable=self.local_model_var, value=value,
                bg=self.BG_COLOR, fg=self.TEXT_COLOR, selectcolor=self.BG_COLOR,
                activebackground=self.BG_COLOR, activeforeground=self.ACCENT_COLOR,
                font=font_small, cursor="hand2",
            ).pack(padx=8, anchor="w")

        tk.Label(
            self.local_frame, text="Requiere Ollama corriendo en tu máquina (ollama.com)",
            bg=self.BG_COLOR, fg="#6c7086", font=font_small,
        ).pack(anchor="w", pady=(4, 0))

        # Ambos frames viven dentro de provider_fields_container; se alterna
        # cuál está visible con pack/forget sin afectar al resto de la ventana.
        self._refresh_provider_fields()

        # ── Esquina del overlay ──────────────────────────────────
        tk.Label(
            win, text="Esquina del overlay", bg=self.BG_COLOR, fg=self.TEXT_COLOR, font=font_label,
        ).pack(padx=24, pady=(12, 4), anchor="w")

        corners = [
            ("↗ Superior derecha", "ne"),
            ("↖ Superior izquierda", "nw"),
            ("↘ Inferior derecha", "se"),
            ("↙ Inferior izquierda", "sw"),
            ("↓ Inferior centrada", "sc"),
        ]

        self.corner_var = tk.StringVar(value=cfg.get("corner", "se"))
        corner_frame = tk.Frame(win, bg=self.BG_COLOR)
        corner_frame.pack(padx=24, pady=(0, 16), anchor="w")

        for i, (label, value) in enumerate(corners):
            tk.Radiobutton(
                corner_frame, text=label, variable=self.corner_var, value=value,
                bg=self.BG_COLOR, fg=self.TEXT_COLOR, selectcolor=self.BG_COLOR,
                activebackground=self.BG_COLOR, activeforeground=self.ACCENT_COLOR,
                font=font_small, cursor="hand2",
            ).grid(row=i // 2, column=i % 2, sticky="w", padx=8, pady=1)

        # Error message
        self.err_var = tk.StringVar()
        tk.Label(
            win, textvariable=self.err_var, bg=self.BG_COLOR, fg=self.BTN_CLOSE_BG, font=font_small,
        ).pack()

        def _start():
            provider = self.provider_var.get()

            if provider == "cloud":
                key = self.key_var.get().strip()
                if not key or not key.startswith("sk-"):
                    self.err_var.set("⚠ Ingresá una API key válida (comienza con sk-)")
                    return
                model = self.cloud_model_var.get()
                ConfigManager.save({
                    "provider": "cloud",
                    "api_key": key,
                    "model": model,
                    "corner": self.corner_var.get(),
                })
                win.destroy()
                self.on_start(provider="cloud", api_key=key, model=model, corner=self.corner_var.get(), ollama_host="")
            else:
                host = self.ollama_host_var.get().strip() or DEFAULT_OLLAMA_HOST
                model = self.local_model_var.get()
                ConfigManager.save({
                    "provider": "local",
                    "ollama_host": host,
                    "model": model,
                    "corner": self.corner_var.get(),
                })
                win.destroy()
                self.on_start(provider="local", api_key="", model=model, corner=self.corner_var.get(), ollama_host=host)

        tk.Button(
            win, text="▶  Iniciar monitor", bg=self.ACCENT_COLOR, fg=self.BTN_FG, font=font_btn,
            bd=0, padx=20, pady=8, cursor="hand2", command=_start, relief="flat",
        ).pack(pady=(4, 20))

        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        win.deiconify()
        win.bind("<Return>", lambda e: _start())

    def _refresh_provider_fields(self) -> None:
        if self.provider_var.get() == "cloud":
            self.local_frame.pack_forget()
            self.cloud_frame.pack(fill="x")
            self._key_entry.focus_set()
        else:
            self.cloud_frame.pack_forget()
            self.local_frame.pack(fill="x")
