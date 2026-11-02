"""Gestión de reservas de Software FJ."""

from datetime import date, datetime

from cliente import Cliente
from excepciones import (
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
)
from servicio import Servicio


class Reserva:
    """Relaciona un cliente con un servicio en una fecha y hora determinadas."""

    # Centralizamos los estados para no repetir cadenas en el código.
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_CONFIRMADA = "confirmada"
    ESTADO_CANCELADA = "cancelada"

    contador = 0  # Contador de reservas creadas.

    def __init__(self, cliente, servicio, fecha, hora):
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El cliente debe ser una instancia de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El servicio debe ser una instancia de Servicio.")

        if not isinstance(fecha, str):
            raise ReservaInvalidaError(
                "La fecha de la reserva debe ser una cadena de texto."
            )
        if not isinstance(hora, str):
            raise ReservaInvalidaError(
                "La hora de la reserva debe ser una cadena de texto."
            )

        if fecha.strip() == "":
            raise ReservaInvalidaError("La fecha de la reserva no puede estar vacía.")
        if hora.strip() == "":
            raise ReservaInvalidaError("La hora de la reserva no puede estar vacía.")

        try:
            fecha_reserva = datetime.strptime(fecha, "%Y-%m-%d").date()
            if fecha_reserva < date.today():
                raise ReservaInvalidaError(
                    "La fecha de la reserva no puede ser anterior a la fecha actual."
                )
        except ValueError as error:
            raise ReservaInvalidaError(
                "Formato de fecha inválido. Use YYYY-MM-DD."
            ) from error

        try:
            hora_reserva = datetime.strptime(hora, "%H:%M").time()
        except ValueError as error:
            raise ReservaInvalidaError("Formato de hora inválido. Use HH:MM.") from error

        fecha_hora_reserva = datetime.combine(fecha_reserva, hora_reserva)

        if fecha_hora_reserva < datetime.now():
            raise ReservaInvalidaError(
                "La fecha y hora de la reserva no pueden ser anteriores a la fecha y hora actuales."
            )

        # La disponibilidad se delega en el servicio, sin duplicar su lógica.
        servicio.validar_disponibilidad()

        self.cliente = cliente
        self.servicio = servicio
        self.fecha = fecha
        self.hora = hora
        self.estado = self.ESTADO_PENDIENTE
        Reserva.contador += 1
        self.codigo_reserva = f"RES-{Reserva.contador:03d}"

    @property
    def esta_confirmada(self):
        """Indica si la reserva se encuentra confirmada."""
        return self.estado == self.ESTADO_CONFIRMADA

    @property
    def duracion(self):
        """Devuelve las horas del servicio cuando las maneja y None en otro caso."""
        return getattr(self.servicio, "horas", None)

    @property
    def cantidad(self):
        """Devuelve la cantidad de equipos cuando el servicio la maneja."""
        return getattr(self.servicio, "cantidad", None)

    def calcular_costo(self):
        """Consulta el costo final del servicio sin calcular tarifas propias."""
        return self.servicio.calcular_costo()

    def confirmar_reserva(self):
        """Confirma una reserva pendiente si el servicio sigue disponible."""
        if self.estado != self.ESTADO_PENDIENTE:
            raise OperacionNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )
        self.servicio.validar_disponibilidad()
        self.estado = self.ESTADO_CONFIRMADA
        return f"Reserva {self.codigo_reserva} confirmada el {self.fecha} a las {self.hora}."

    def cancelar_reserva(self):
        """Cancela una reserva pendiente o confirmada."""
        estados_permitidos = (self.ESTADO_PENDIENTE, self.ESTADO_CONFIRMADA)
        if self.estado not in estados_permitidos:
            raise OperacionNoPermitidaError(
                "Solo se pueden cancelar reservas pendientes y confirmadas."
            )
        self.estado = self.ESTADO_CANCELADA
        return f"Reserva {self.codigo_reserva} cancelada el {self.fecha} a las {self.hora}."
