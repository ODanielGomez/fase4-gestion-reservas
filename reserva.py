from excepciones import ReservaInvalidaError 
from excepciones import OperacionNoPermitidaError


class Reserva:
    contador = 0  # Contador de reservas
  
    def __init__(self,cliente, servicio, fecha, hora):
        
        
        if fecha.strip() == "":
            raise ReservaInvalidaError("La fecha de la reserva no puede estar vacía.")
        if hora.strip() == "":
            raise ReservaInvalidaError("La hora de la reserva no puede estar vacía.")
        self.cliente = cliente
        self.servicio = servicio
        self.fecha = fecha
        self.hora = hora
        self.estado = "pendiente"  # Estado inicial de la reserva
        Reserva.contador += 1
        self.codigo_reserva = (f"RES-{Reserva.contador:03d}") # Generamos un código único para la reserva
        
    def confirmar_reserva(self):
        if self.estado != "pendiente":
             raise OperacionNoPermitidaError("Solo se pueden confirmar reservas pendientes.")
        self.estado = "confirmada"
        return f"Reserva {self.codigo_reserva} confirmada el {self.fecha} a las {self.hora}."

    def cancelar_reserva(self):
        if self.estado == "cancelada":
            raise OperacionNoPermitidaError("Solo se pueden cancelar reservas pendientes y confirmadas.")
        self.estado = "cancelada"
        return f"Reserva {self.codigo_reserva} cancelada el {self.fecha} a las {self.hora}."     
            
        
    