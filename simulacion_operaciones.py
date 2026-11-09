"""Simulación de operaciones válidas e inválidas del sistema."""

import logging
import math
from datetime import date, timedelta
# Configuramos el archivo de eventos.
import configuracion_logs  
from cliente import Cliente
from excepciones import DatoInvalidoError, OperacionNoPermitidaError, ReservaInvalidaError, ServicioNoDisponibleError
from reserva import Reserva
from servicio import ReservaSala


def ejecutar_operacion(numero, descripcion, operacion, error_esperado=None):
    """Ejecutamos cada caso por separado para continuar si ocurre un error."""
    print(f"\nOperación {numero}: {descripcion}")
    try:
        resultado = operacion()
    except (DatoInvalidoError, ReservaInvalidaError, OperacionNoPermitidaError,
            ServicioNoDisponibleError, TypeError) as error:
        # Guardamos los errores detectados en el archivo de eventos.
        logging.warning("Operación %s: %s", numero, error)
        if error_esperado is not None and isinstance(error, error_esperado):
            print(f"Resultado esperado: {error}")
        else:
            print(f"Fallo inesperado: {error}")
    else:
        # Si debía fallar, avisamos que el resultado no fue el esperado.
        if error_esperado is not None:
            print("Fallo: se esperaba que la operación fuera rechazada.")
        else:
            print(f"Resultado correcto: {resultado}")
            logging.info("Operación %s realizada correctamente.", numero)
    finally:
        # Registramos el final de la operación tanto si pasa como si falla.
        logging.info("Finalizó la operación %s de la simulación.", numero)


def calcular_costo_controlado(servicio):
    """Validamos el costo sin cambiar la clase de servicio existente."""
    costo = servicio.calcular_costo()
    if not math.isfinite(costo):
        raise DatoInvalidoError("El costo calculado no es un número válido.")
    return costo


def main():
    # Usamos datos ficticios y una fecha futura para repetir la simulación.
    cliente = Cliente("Omar Gomez", "CC", "123456")
    servicio = ReservaSala("Sala de prueba", 100000, horas=2)
    fecha = (date.today() + timedelta(days=2)).isoformat()
    reserva_confirmada = Reserva(cliente, servicio, fecha, "09:00")
    reserva_cancelada = Reserva(cliente, servicio, fecha, "12:00")
    reserva_cancelada.cancelar_reserva()

    ejecutar_operacion(1, "Crear un cliente válido", lambda: Cliente("Ana Gomez", "CC", "12345").nombre)
    ejecutar_operacion(2, "Rechazar un cliente sin nombre", lambda: Cliente("", "CC", "12345"), DatoInvalidoError)
    ejecutar_operacion(3, "Rechazar una identificación con letras", lambda: Cliente("Ana", "CC", "12a"), DatoInvalidoError)
    ejecutar_operacion(4, "Crear un servicio válido", lambda: ReservaSala("Sala", 100000).nombre)
    ejecutar_operacion(5, "Rechazar una tarifa negativa", lambda: ReservaSala("Sala", -1), DatoInvalidoError)
    ejecutar_operacion(6, "Crear una reserva válida", lambda: Reserva(cliente, servicio, fecha, "15:00").codigo_reserva)
    ejecutar_operacion(7, "Rechazar una reserva con fecha pasada", lambda: Reserva(cliente, servicio, "2024-01-01", "09:00"), ReservaInvalidaError)
    ejecutar_operacion(8, "Confirmar una reserva pendiente", reserva_confirmada.confirmar_reserva)
    ejecutar_operacion(9, "Impedir confirmar una reserva dos veces", reserva_confirmada.confirmar_reserva, OperacionNoPermitidaError)
    ejecutar_operacion(10, "Impedir cancelar una reserva dos veces", reserva_cancelada.cancelar_reserva, OperacionNoPermitidaError)
    ejecutar_operacion(11, "Detectar un parámetro faltante", lambda: Cliente("Omar", "CC"), DatoInvalidoError)
    ejecutar_operacion(12, "Detectar un costo inconsistente", lambda: calcular_costo_controlado(ReservaSala("Sala", 1e308, horas=2)), DatoInvalidoError)
    print("\nSimulación terminada. Consulta logs/eventos.log para revisar los eventos.")


if __name__ == "__main__":
    main()
