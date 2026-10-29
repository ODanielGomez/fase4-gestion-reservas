# Importamos las clases y herramientas necesarias para ejecutar el programa.
from cliente import Cliente
from excepciones import DatoInvalidoError, ReservaInvalidaError, OperacionNoPermitidaError
import configuracion_logs
import logging
from reserva import Reserva





# Solicitamos los datos del cliente y controlamos posibles errores de validación.
try:
    nombre = input("Ingrese el nombre del cliente: ")
    tipo_identificacion = input("Ingrese el tipo de identificación del cliente: ")
    numero_identificacion = input("Ingrese el número de identificación del cliente: ")

# Creamos el objeto Cliente con los datos ingresados por el usuario.
    cliente_nuevo = Cliente(nombre, tipo_identificacion, numero_identificacion)
    
# Registramos en el archivo de logs que el cliente fue creado correctamente.   
    logging.info(f"Cliente creado exitosamente: {cliente_nuevo.nombre}")
    
    nombre_del_servicio = input("Ingrese el nombre del servicio que desea reservar: ")
    fecha_reserva = input("Ingrese la fecha de la reserva (YYYY-MM-DD): ")
    hora_reserva = input("Ingrese la hora de la reserva (HH:MM): ")
    
    
    reserva_nueva= Reserva(cliente_nuevo, nombre_del_servicio, fecha_reserva, hora_reserva)

    print(cliente_nuevo.nombre)
    print(cliente_nuevo.obtener_numero_identificacion())

    print(reserva_nueva.codigo_reserva)
    print(reserva_nueva.estado)
    print(reserva_nueva.confirmar_reserva())
    print(reserva_nueva.estado)
    print(reserva_nueva.cancelar_reserva())
    print(reserva_nueva.estado)
    print(reserva_nueva.cancelar_reserva())
    print(reserva_nueva.estado)
# Mostramos un mensaje y registramos el error si algún dato no es válido.    
except (DatoInvalidoError, ReservaInvalidaError, OperacionNoPermitidaError) as error:
    print(f"Error: {error}")
    logging.error(f"Error al crear el cliente: {error}")    
    
    
    
    