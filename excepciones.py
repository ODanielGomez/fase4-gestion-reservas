# Creamos excepciones personalizadas para controlar los errores del sistema de forma clara.

# Se usa cuando el usuario ingresa información vacía o con un formato inválido.
class DatoInvalidoError(Exception):
    """Excepción personalizada para indicar que un dato es inválido."""
    pass


# Se usa cuando se intenta reservar un servicio que no se encuentra disponible.
class ServicioNoDisponibleError(Exception):
    """Excepción personalizada para indicar que un servicio no está disponible."""
    pass


# Se usa cuando una reserva contiene datos incorrectos o no puede procesarse.
class ReservaInvalidaError(Exception):
    """Excepción personalizada para indicar que una reserva no está disponible."""
    pass

# Se usa cuando se intenta realizar una acción que no está permitida en el sistema.
class OperacionNoPermitidaError(Exception):
    """Excepción personalizada para indicar que una operación no está permitida."""
    pass



