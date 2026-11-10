"""Gestión de reservas de Software FJ."""

from datetime import date, datetime, timedelta

from cliente import Cliente
from entidad import Entidad
from excepciones import DatoInvalidoError, OperacionNoPermitidaError, ReservaInvalidaError
from servicio import Servicio

# Señalamos los datos que no se incluyeron al crear una reserva.
_FALTANTE = object()


class Reserva(Entidad):
    """Relaciona un cliente con un servicio en una fecha y hora determinadas."""

    ESTADO_PENDIENTE = "pendiente"
    ESTADO_CONFIRMADA = "confirmada"
    ESTADO_CANCELADA = "cancelada"
    contador = 0

    def __init__(self, cliente=_FALTANTE, servicio=_FALTANTE, fecha=_FALTANTE, hora=_FALTANTE):
        if any(dato is _FALTANTE for dato in (cliente, servicio, fecha, hora)):
            raise ReservaInvalidaError("La reserva necesita cliente, servicio, fecha y hora.")
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El cliente debe ser una instancia de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El servicio debe ser una instancia de Servicio.")
        if not isinstance(fecha, str):
            raise ReservaInvalidaError("La fecha de la reserva debe ser una cadena de texto.")
        if not isinstance(hora, str):
            raise ReservaInvalidaError("La hora de la reserva debe ser una cadena de texto.")
        if fecha.strip() == "":
            raise ReservaInvalidaError("La fecha de la reserva no puede estar vacía.")
        if hora.strip() == "":
            raise ReservaInvalidaError("La hora de la reserva no puede estar vacía.")

        try:
            fecha_reserva = datetime.strptime(fecha, "%Y-%m-%d").date()
            if fecha_reserva < date.today():
                raise ReservaInvalidaError("La fecha de la reserva no puede ser anterior a la fecha actual.")
        except ValueError as error:
            raise ReservaInvalidaError("Formato de fecha inválido. Use YYYY-MM-DD.") from error

        try:
            hora_reserva = datetime.strptime(hora, "%H:%M").time()
        except ValueError as error:
            raise ReservaInvalidaError("Formato de hora inválido. Use HH:MM.") from error

        fecha_hora_reserva = datetime.combine(fecha_reserva, hora_reserva)
        if fecha_hora_reserva < datetime.now():
            raise ReservaInvalidaError(
                "La fecha y hora de la reserva no pueden ser anteriores a la fecha y hora actuales."
            )
        servicio.validar_disponibilidad()
        self.cliente = cliente
        self.servicio = servicio
        self.fecha = fecha
        self.hora = hora
        self.fecha_hora_inicio = fecha_hora_reserva
        self.estado = self.ESTADO_PENDIENTE
        Reserva.contador += 1
        self.codigo_reserva = f"RES-{Reserva.contador:03d}"

    @property
    def esta_confirmada(self):
        return self.estado == self.ESTADO_CONFIRMADA

    @property
    def duracion(self):
        return getattr(self.servicio, "horas", None)

    @property
    def cantidad(self):
        return getattr(self.servicio, "cantidad", None)

    def calcular_costo(self):
        return self.servicio.calcular_costo()

    def confirmar_reserva(self):
        if self.estado != self.ESTADO_PENDIENTE:
            raise OperacionNoPermitidaError("Solo se pueden confirmar reservas pendientes.")
        self.servicio.validar_disponibilidad()
        self.estado = self.ESTADO_CONFIRMADA
        return f"Reserva {self.codigo_reserva} confirmada el {self.fecha} a las {self.hora}."

    def cancelar_reserva(self):
        estados_permitidos = (self.ESTADO_PENDIENTE, self.ESTADO_CONFIRMADA)
        if self.estado not in estados_permitidos:
            raise OperacionNoPermitidaError("Solo se pueden cancelar reservas pendientes y confirmadas.")
        self.estado = self.ESTADO_CANCELADA
        return f"Reserva {self.codigo_reserva} cancelada el {self.fecha} a las {self.hora}."

    def obtener_fecha_hora_final(self):
        """Calcula el final cuando el servicio proporciona una duración en horas."""
        if self.duracion is None:
            return None
        return self.fecha_hora_inicio + timedelta(hours=self.duracion)

    def describir(self):
        """Devuelve una descripción legible de la reserva."""
        return (
            f"Reserva {self.codigo_reserva} de {self.cliente.nombre} "
            f"para {self.servicio.nombre} el {self.fecha} a las {self.hora} "
            f"({self.estado})."
        )
