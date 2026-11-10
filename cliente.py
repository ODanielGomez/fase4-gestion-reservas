
# Importamos la excepción que usaremos cuando los datos del cliente no sean válidos.
from entidad import Entidad
from excepciones import DatoInvalidoError

# Usamos un valor especial para identificar datos que no se enviaron.
_FALTANTE = object()

# Creamos la clase Cliente para almacenar y validar la información básica de cada cliente.
class Cliente(Entidad):
    def __init__(self, nombre=_FALTANTE, tipo_identificacion=_FALTANTE, numero_identificacion=_FALTANTE):
        # Informamos los parámetros faltantes con un error propio del sistema.
        if any(dato is _FALTANTE for dato in (nombre, tipo_identificacion, numero_identificacion)):
            raise DatoInvalidoError("Faltan datos del cliente: nombre, tipo o número de identificación.")
        if not all(isinstance(dato, str) for dato in (nombre, tipo_identificacion, numero_identificacion)):
            raise DatoInvalidoError("Los datos del cliente deben ser texto.")
 
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

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("El nombre del cliente no puede estar vacío.")
        if not valor.strip().replace(" ", "").isalpha():
            raise DatoInvalidoError("El nombre del cliente debe contener solo letras y espacios.")
        self.__nombre = valor.strip()

    @property
    def tipo_identificacion(self):
        return self.__tipo_identificacion

    @tipo_identificacion.setter
    def tipo_identificacion(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("El tipo de identificación del cliente no puede estar vacío.")
        self.__tipo_identificacion = valor.strip()

    def describir(self):
        """Devuelve una descripción legible del cliente."""
        return (
            f"Cliente: {self.nombre} "
            f"({self.tipo_identificacion} {self.__numero_identificacion})"
        )
