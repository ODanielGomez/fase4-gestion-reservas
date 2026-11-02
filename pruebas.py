from cliente import Cliente
from excepciones import DatoInvalidoError, ReservaInvalidaError, OperacionNoPermitidaError
from reserva import Reserva
from datetime import timedelta, datetime


# Calculamos una fecha futura para que la prueba siga siendo válida.
fecha_futura = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


# Prueba 1: crear un cliente con datos válidos.
try:
    objeto_nuevo = Cliente("Consumidor final", "cc", "2222222222")
    print("Prueba exitosa: el cliente se creó correctamente.")

except DatoInvalidoError as error:
    print(f"Fallo: no se pudo crear el cliente. {error}")

else:
    # Prueba 2: intentar crear una reserva con una fecha pasada.
    try:
        reserva_pasada = Reserva(objeto_nuevo, "Servicio de prueba", "2024-01-01", "10:00")
        print("Fallo: se permitió crear una reserva con fecha pasada.")

    except ReservaInvalidaError as error:
        print(f"Prueba exitosa: se rechazó la fecha pasada. {error}")

    # Prueba 3: crear una reserva con una fecha futura.
    try:
        reserva_nueva = Reserva(objeto_nuevo, "Servicio de prueba", fecha_futura, "10:00")
        print("Prueba exitosa: la reserva se creó correctamente.")

    except ReservaInvalidaError as error:
        print(f"Fallo: no se pudo crear la reserva. {error}")

    else:
        # Prueba 4: comprobar el estado inicial.
        if reserva_nueva.estado == "pendiente":
            print("Prueba exitosa: la reserva inició en estado pendiente.")
        else:
            print("Fallo: la reserva debería iniciar en estado pendiente.")

        # Prueba 5: confirmar la reserva.
        try:
            reserva_nueva.confirmar_reserva()

            if reserva_nueva.estado == "confirmada":
                print("Prueba exitosa: la reserva quedó confirmada.")
            else:
                print("Fallo: la reserva debería estar confirmada.")

        except OperacionNoPermitidaError as error:
            print(f"Fallo: no se pudo confirmar la reserva. {error}")

        # Prueba 6: intentar confirmar una reserva ya confirmada.
        try:
            reserva_nueva.confirmar_reserva()
            print("Fallo: se permitió confirmar una reserva ya confirmada.")

        except OperacionNoPermitidaError as error:
            print(f"Prueba exitosa: no se permitió confirmar nuevamente. {error}")

        # Prueba 7: cancelar la reserva.
        try:
            reserva_nueva.cancelar_reserva()

            if reserva_nueva.estado == "cancelada":
                print("Prueba exitosa: la reserva quedó cancelada.")
            else:
                print("Fallo: la reserva debería estar cancelada.")

        except OperacionNoPermitidaError as error:
            print(f"Fallo: no se pudo cancelar la reserva. {error}")

        # Prueba 8: intentar cancelar una reserva ya cancelada.
        try:
            reserva_nueva.cancelar_reserva()
            print("Fallo: se permitió cancelar una reserva ya cancelada.")

        except OperacionNoPermitidaError as error:
            print(f"Prueba exitosa: no se permitió cancelar nuevamente. {error}")


# Prueba 9: intentar crear un cliente con el nombre vacío.
try:
    cliente_nombre_vacio = Cliente("", "cc", "2222222222")
    print("Fallo: se permitió crear un cliente con nombre vacío.")

except DatoInvalidoError as error:
    print(f"Prueba exitosa: se rechazó el nombre vacío. {error}")


# Prueba 10: intentar crear un cliente con letras en la identificación.
try:
    cedula_incorrecta = Cliente("Consumidor final", "cc", "2222222a22")
    print("Fallo: se permitió una identificación con letras.")

except DatoInvalidoError as error:
    print(f"Prueba exitosa: se rechazó la identificación inválida. {error}")