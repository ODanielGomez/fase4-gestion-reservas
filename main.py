# Importamos las clases y herramientas necesarias para ejecutar el programa.
from cliente import Cliente
from excepciones import DatoInvalidoError
import configuracion_logs
import logging


# Solicitamos los datos del cliente y controlamos posibles errores de validación.
try:
    nombre = input("Ingrese el nombre del cliente: ")
    tipo_identificacion = input("Ingrese el tipo de identificación del cliente: ")
    numero_identificacion = input("Ingrese el número de identificación del cliente: ")

# Creamos el objeto Cliente con los datos ingresados por el usuario.
    cliente_nuevo = Cliente(nombre, tipo_identificacion, numero_identificacion)
# Registramos en el archivo de logs que el cliente fue creado correctamente.   
    logging.info(f"Cliente creado exitosamente: {cliente_nuevo.nombre}")

    print(cliente_nuevo.nombre)
    print(cliente_nuevo.obtener_numero_identificacion())
    
# Mostramos un mensaje y registramos el error si algún dato no es válido.    
except DatoInvalidoError as error:
    print(f"Error: {error}")
    logging.error(f"Error al crear el cliente: {error}")
    
    
    
    
    