from excepciones import ReservaInvalidaError 
from excepciones import OperacionNoPermitidaError
from datetime import datetime,date

class Reserva:
    contador = 0  # Contador de reservas
  
    def __init__(self,cliente, servicio, fecha, hora):
        
        
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
            raise ReservaInvalidaError("La fecha y hora de la reserva no pueden ser anteriores a la fecha y hora actuales.")
            
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
            
        
    