"""
base.py
───────
Interfaz común para los backends de IA. La app (clipboard_monitor,
main) solo conoce esta interfaz, nunca un proveedor concreto — así se
puede intercambiar cloud <-> local sin tocar el resto del código.
"""

from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """Contrato que debe cumplir cualquier backend de IA."""

    @abstractmethod
    def query(self, text: str, system_prompt: str = "") -> tuple[str, bool]:
        """Consulta con texto plano.

        Returns:
            (respuesta, hubo_error)
        """
        raise NotImplementedError

    def query_image(self, image_base64: str, text: str, system_prompt: str = "") -> tuple[str, bool]:
        """Consulta con una imagen (screenshot). Los backends que no
        soporten imágenes pueden dejar la implementación por defecto."""
        return "Este backend no soporta imágenes.", True

    def label(self) -> str:
        """Nombre corto para mostrar en la UI (ej: en el setup)."""
        return self.__class__.__name__
