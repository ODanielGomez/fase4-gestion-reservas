# Definimos los servicios que ofrece Software FJ.
# La clase base guarda lo común y cada servicio calcula su propio costo.
from abc import ABC, abstractmethod

from excepciones import DatoInvalidoError, ServicioNoDisponibleError


class Servicio(ABC):
    """Clase base para todos los servicios de Software FJ."""

    def __init__(self, nombre, tarifa_base, impuesto=0, descuento=0, disponible=True):
        self.__nombre = self._validar_nombre(nombre)
        self.__tarifa_base = self._validar_tarifa(tarifa_base)
        self.__impuesto = self._validar_porcentaje(impuesto, "impuesto")
        self.__descuento = self._validar_porcentaje(descuento, "descuento")
        self.__disponible = self._validar_disponible(disponible)

    # Propiedades de solo lectura para consultar los datos del servicio.
    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa_base(self):
        return self.__tarifa_base

    @property
    def impuesto(self):
        return self.__impuesto

    @property
    def descuento(self):
        return self.__descuento

    @property
    def disponible(self):
        return self.__disponible

    @staticmethod
    def _validar_nombre(nombre):
        if not isinstance(nombre, str) or nombre.strip() == "":
            raise DatoInvalidoError("El nombre del servicio no puede estar vacío.")
        return nombre.strip()

    @staticmethod
    def _validar_tarifa(tarifa_base):
        if isinstance(tarifa_base, bool) or not isinstance(tarifa_base, (int, float)):
            raise DatoInvalidoError("La tarifa base debe ser un número.")
        if tarifa_base < 0:
            raise DatoInvalidoError("La tarifa base no puede ser negativa.")
        return tarifa_base

    @staticmethod
    def _validar_porcentaje(valor, campo):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatoInvalidoError(f"El {campo} debe ser un número.")
        if valor < 0 or valor > 100:
            raise DatoInvalidoError(f"El {campo} debe estar entre 0 y 100.")
        return valor

    @staticmethod
    def _validar_disponible(disponible):
        if not isinstance(disponible, bool):
            raise DatoInvalidoError("La disponibilidad debe ser verdadera o falsa.")
        return disponible

    @abstractmethod
    def calcular_costo_base(self):
        """Cada servicio define cómo se calcula su valor sin impuestos ni descuentos."""
        pass

    def calcular_impuesto(self):
        """Calcula el impuesto sobre el costo base."""
        return self.calcular_costo_base() * self.impuesto / 100

    def calcular_descuento(self):
        """Calcula el descuento sobre el costo base."""
        return self.calcular_costo_base() * self.descuento / 100

    def calcular_costo(self):
        """Devuelve el costo final con impuesto y descuento aplicados."""
        total = self.calcular_costo_base() + self.calcular_impuesto() - self.calcular_descuento()
        return round(total, 2)

    def validar_disponibilidad(self):
        """Impide usar el servicio cuando no está disponible."""
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible en este momento."
            )

    def establecer_disponibilidad(self, disponible):
        """Permite activar o desactivar el servicio."""
        self.__disponible = self._validar_disponible(disponible)

    def __str__(self):
        return f"{self.nombre} - Tarifa base: {self.tarifa_base}"


class ReservaSala(Servicio):
    """Servicio para reservar una sala por horas."""

    def __init__(self, nombre, tarifa_base, horas=1, impuesto=0, descuento=0, disponible=True):
        super().__init__(nombre, tarifa_base, impuesto, descuento, disponible)
        self.__horas = self._validar_horas(horas)

    @property
    def horas(self):
        return self.__horas

    @staticmethod
    def _validar_horas(horas):
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise DatoInvalidoError("Las horas de la sala deben ser un número.")
        if horas <= 0:
            raise DatoInvalidoError("Las horas de la sala deben ser mayores que cero.")
        return horas

    def calcular_costo_base(self):
        return self.tarifa_base * self.horas


class AlquilerEquipo(Servicio):
    """Servicio para alquilar equipos por cantidad de unidades."""

    def __init__(self, nombre, tarifa_base, cantidad=1, impuesto=0, descuento=0, disponible=True):
        super().__init__(nombre, tarifa_base, impuesto, descuento, disponible)
        self.__cantidad = self._validar_cantidad(cantidad)

    @property
    def cantidad(self):
        return self.__cantidad

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise DatoInvalidoError("La cantidad de equipos debe ser un número entero.")
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad de equipos debe ser mayor que cero.")
        return cantidad

    def calcular_costo_base(self):
        return self.tarifa_base * self.cantidad


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría con un valor fijo por sesión."""

    def calcular_costo_base(self):
        return self.tarifa_base
