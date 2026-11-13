# Definimos los servicios que ofrece Software FJ.
# La clase base guarda lo común y cada servicio calcula su propio costo.
from abc import ABC, abstractmethod
import math

from entidad import Entidad
from excepciones import DatoInvalidoError, ServicioNoDisponibleError

# Identificamos los parámetros obligatorios que no fueron enviados.
_FALTANTE = object()


class Servicio(Entidad, ABC):
    """Clase base para todos los servicios de Software FJ."""

    def __init__(self, nombre=_FALTANTE, tarifa_base=_FALTANTE, impuesto=0, descuento=0, disponible=True):
        if nombre is _FALTANTE or tarifa_base is _FALTANTE:
            raise DatoInvalidoError("El servicio necesita un nombre y una tarifa base.")
        self.__nombre = nombre
        self.__tarifa_base = tarifa_base
        self.__impuesto = impuesto
        self.__descuento = descuento
        self.__disponible = disponible
        self.validar_parametros()

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

    @property
    def duracion(self):
        """Duración en horas del servicio, si el servicio la define."""
        return None

    @staticmethod
    def _validar_nombre(nombre):
        if not isinstance(nombre, str) or nombre.strip() == "":
            raise DatoInvalidoError("El nombre del servicio no puede estar vacío.")
        return nombre.strip()

    @staticmethod
    def _validar_tarifa(tarifa_base):
        if isinstance(tarifa_base, bool) or not isinstance(tarifa_base, (int, float)):
            raise DatoInvalidoError("La tarifa base debe ser un número.")
        if not math.isfinite(tarifa_base) or tarifa_base < 0:
            raise DatoInvalidoError("La tarifa base no puede ser negativa.")
        return tarifa_base

    @staticmethod
    def _validar_porcentaje(valor, campo):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatoInvalidoError(f"El {campo} debe ser un número.")
        if not math.isfinite(valor) or valor < 0 or valor > 100:
            raise DatoInvalidoError(f"El {campo} debe estar entre 0 y 100.")
        return valor

    @staticmethod
    def _validar_disponible(disponible):
        if not isinstance(disponible, bool):
            raise DatoInvalidoError("La disponibilidad debe ser verdadera o falsa.")
        return disponible

    @abstractmethod
    def validar_parametros(self):
        """Valida los parámetros comunes y los específicos de cada servicio."""
        self.__nombre = self._validar_nombre(self.__nombre)
        self.__tarifa_base = self._validar_tarifa(self.__tarifa_base)
        self.__impuesto = self._validar_porcentaje(self.__impuesto, "impuesto")
        self.__descuento = self._validar_porcentaje(self.__descuento, "descuento")
        self.__disponible = self._validar_disponible(self.__disponible)
        return True

    @abstractmethod
    def calcular_costo_base(self):
        """Cada servicio define cómo se calcula su valor sin impuestos ni descuentos."""
        pass

    @abstractmethod
    def describir_servicio(self):
        """Cada servicio describe sus propias características."""
        pass

    def describir(self):
        """Implementa la descripción general de la entidad servicio."""
        return self.describir_servicio()

    def calcular_impuesto(self):
        """Calcula el impuesto sobre el costo base."""
        return self.calcular_costo_base() * self.impuesto / 100

    def calcular_descuento(self):
        """Calcula el descuento sobre el costo base."""
        return self.calcular_costo_base() * self.descuento / 100

    def calcular_costo(self, impuesto=None, descuento=None):
        """Devuelve el costo final con impuesto y descuento aplicados.

        Los parámetros opcionales permiten calcular variantes del costo sin
        modificar los valores configurados en el servicio.
        """
        # Si no se envían valores, se usan los registrados en el servicio.
        porcentaje_impuesto = (
            self.impuesto if impuesto is None
            else self._validar_porcentaje(impuesto, "impuesto")
        )
        porcentaje_descuento = (
            self.descuento if descuento is None
            else self._validar_porcentaje(descuento, "descuento")
        )
        try:
            # Validamos el resultado de cada cálculo antes de entregar el total.
            base = self.calcular_costo_base()
            if not math.isfinite(base):
                raise DatoInvalidoError("El costo base no es un número finito.")
            impuesto = base * (porcentaje_impuesto / 100)
            descuento = base * (porcentaje_descuento / 100)
            total = base + impuesto - descuento
            if not math.isfinite(total):
                raise DatoInvalidoError("El costo final no es un número finito.")
            return round(total, 2)
        except OverflowError as error:
            raise DatoInvalidoError("El costo es demasiado grande para calcularlo.") from error

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

    def __init__(self, nombre=_FALTANTE, tarifa_base=_FALTANTE, horas=1, impuesto=0, descuento=0, disponible=True):
        self.__horas = horas
        super().__init__(nombre, tarifa_base, impuesto, descuento, disponible)

    @property
    def horas(self):
        return self.__horas

    @property
    def duracion(self):
        return self.horas

    def validar_parametros(self):
        super().validar_parametros()
        self.__horas = self._validar_horas(self.__horas)
        return True

    @staticmethod
    def _validar_horas(horas):
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise DatoInvalidoError("Las horas de la sala deben ser un número.")
        if not math.isfinite(horas) or horas <= 0:
            raise DatoInvalidoError("Las horas de la sala deben ser mayores que cero.")
        return horas

    def calcular_costo_base(self):
        return self.tarifa_base * self.horas

    def describir_servicio(self):
        # Mostramos las horas que incluye esta reserva.
        return f"Sala {self.nombre}: {self.horas} hora(s)."


class AlquilerEquipo(Servicio):
    """Servicio para alquilar equipos por cantidad de unidades."""

    def __init__(self, nombre=_FALTANTE, tarifa_base=_FALTANTE, cantidad=1, impuesto=0, descuento=0, disponible=True):
        self.__cantidad = cantidad
        super().__init__(nombre, tarifa_base, impuesto, descuento, disponible)

    @property
    def cantidad(self):
        return self.__cantidad

    def validar_parametros(self):
        super().validar_parametros()
        self.__cantidad = self._validar_cantidad(self.__cantidad)
        return True

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise DatoInvalidoError("La cantidad de equipos debe ser un número entero.")
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad de equipos debe ser mayor que cero.")
        return cantidad

    def calcular_costo_base(self):
        return self.tarifa_base * self.cantidad

    def describir_servicio(self):
        # Indicamos cuántos equipos se van a alquilar.
        return f"Equipo {self.nombre}: {self.cantidad} unidad(es)."


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría con un valor fijo por sesión."""

    def validar_parametros(self):
        super().validar_parametros()
        return True

    def calcular_costo_base(self):
        return self.tarifa_base

    def describir_servicio(self):
        # La asesoría tiene una tarifa por sesión.
        return f"Asesoría {self.nombre}: tarifa por sesión."


class SalaCorporativa(ReservaSala):
    """Sala del catálogo que además guarda su capacidad y descripción."""

    def __init__(
        self,
        nombre,
        capacidad,
        descripcion,
        tarifa_base,
        horas=1,
        impuesto=0,
        descuento=0,
        disponible=True,
    ):
        self.__capacidad = capacidad
        self.__descripcion = descripcion
        super().__init__(nombre, tarifa_base, horas, impuesto, descuento, disponible)

    @property
    def capacidad(self):
        return self.__capacidad

    @property
    def descripcion(self):
        return self.__descripcion

    def validar_parametros(self):
        self.__capacidad = self._validar_capacidad(self.__capacidad)
        self.__descripcion = self._validar_descripcion(self.__descripcion)
        super().validar_parametros()
        return True

    @staticmethod
    def _validar_capacidad(capacidad):
        if (
            isinstance(capacidad, bool)
            or not isinstance(capacidad, int)
            or capacidad <= 0
        ):
            raise DatoInvalidoError(
                "La capacidad de la sala debe ser un número entero mayor que cero."
            )
        return capacidad

    @staticmethod
    def _validar_descripcion(descripcion):
        if not isinstance(descripcion, str) or descripcion.strip() == "":
            raise DatoInvalidoError("La descripción de la sala no puede estar vacía.")
        return descripcion.strip()


class ComboEquipos(Servicio):
    """Combo cerrado de equipos con una tarifa fija por jornada de ocho horas."""

    JORNADA_HORAS = 8

    def __init__(
        self,
        nombre,
        tarifa_base,
        componentes,
        impuesto=0,
        descuento=0,
        disponible=True,
    ):
        self.__componentes = componentes
        super().__init__(nombre, tarifa_base, impuesto, descuento, disponible)

    @property
    def componentes(self):
        """Devuelve una copia de los equipos y sus cantidades."""
        return dict(self.__componentes)

    @property
    def jornada_horas(self):
        return self.JORNADA_HORAS

    @property
    def horas(self):
        """Permite consultar la jornada desde la reserva."""
        return self.JORNADA_HORAS

    @property
    def duracion(self):
        return self.JORNADA_HORAS

    def validar_parametros(self):
        super().validar_parametros()
        self.__componentes = self._validar_componentes(self.__componentes)
        return True

    @staticmethod
    def _validar_componentes(componentes):
        if not isinstance(componentes, dict) or not componentes:
            raise DatoInvalidoError("El combo debe incluir al menos un equipo.")

        componentes_validos = {}
        for nombre, cantidad in componentes.items():
            if not isinstance(nombre, str) or nombre.strip() == "":
                raise DatoInvalidoError(
                    "El nombre de cada equipo debe ser un texto válido."
                )
            if (
                isinstance(cantidad, bool)
                or not isinstance(cantidad, int)
                or cantidad <= 0
            ):
                raise DatoInvalidoError(
                    "La cantidad de cada equipo debe ser un entero mayor que cero."
                )
            componentes_validos[nombre.strip()] = cantidad
        return componentes_validos

    def calcular_costo_base(self):
        """El costo del combo es fijo y no se multiplica por sus equipos."""
        return self.tarifa_base

    def describir_servicio(self):
        # Mostramos los equipos incluidos y la jornada del combo.
        equipos = ", ".join(
            f"{cantidad} x {nombre}"
            for nombre, cantidad in self.__componentes.items()
        )
        return f"Combo {self.nombre} ({equipos}): jornada de {self.JORNADA_HORAS} horas."
