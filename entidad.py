"""Entidad general del sistema: base abstracta para clientes, servicios y reservas."""

from abc import ABC, abstractmethod


class Entidad(ABC):
    """Representa cualquier entidad del sistema que puede describirse."""

    @abstractmethod
    def describir(self):
        """Devuelve una descripción legible de la entidad."""
        pass
