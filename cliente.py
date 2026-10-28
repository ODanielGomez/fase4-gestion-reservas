
# Importamos la excepción que usaremos cuando los datos del cliente no sean válidos.
from excepciones import DatoInvalidoError

# Creamos la clase Cliente para almacenar y validar la información básica de cada cliente.
class Cliente:
    def __init__(self, nombre, tipo_identificacion, numero_identificacion):
 
 # Validamos que el nombre, el tipo y el número de identificación sean correctos.   
        if nombre.strip() == "":
            raise DatoInvalidoError("El nombre del cliente no puede estar vacío.")
        if nombre.strip().replace(" ", "").isalpha() == False:
            raise DatoInvalidoError("El nombre del cliente debe contener solo letras y espacios.")    
        if tipo_identificacion.strip() == "":
            raise DatoInvalidoError("El tipo de identificación del cliente no puede estar vacío.")
        if numero_identificacion.strip() == "":
            raise DatoInvalidoError("El número de identificación del cliente no puede estar vacío.")
        if not numero_identificacion.strip().isdigit():
            raise DatoInvalidoError("El número de identificación del cliente debe ser un número válido.")
            
# Guardamos el número de identificación como privado para evitar modificaciones directas.        
        self.nombre = nombre
        self.tipo_identificacion = tipo_identificacion
        self.__numero_identificacion = numero_identificacion

# Creamos un getter para consultar el número de identificación de forma controlada.    
    def obtener_numero_identificacion(self):
        return self.__numero_identificacion