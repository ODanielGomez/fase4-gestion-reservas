"""Catálogo de salas, combos de equipos y asesorías de Software FJ."""

from excepciones import DatoInvalidoError
from servicio import AsesoriaEspecializada, ComboEquipos, SalaCorporativa

# Datos comerciales de las salas corporativas.
SALAS_CORPORATIVAS = (
    {
        "nombre": "Sala Pequeña",
        "capacidad": 40,
        "descripcion": "Reuniones y juntas empresariales.",
        "tarifa_hora": 100000,
    },
    {
        "nombre": "Sala Mediana",
        "capacidad": 80,
        "descripcion": "Capacitaciones y reuniones.",
        "tarifa_hora": 160000,
    },
    {
        "nombre": "Sala Grande",
        "capacidad": 200,
        "descripcion": "Eventos corporativos.",
        "tarifa_hora": 200000,
    },
)

# Cada combo incluye sus equipos y cantidades, pero se cobra como un solo paquete.
COMBOS_EQUIPOS = (
    {
        "nombre": "Reunión empresarial",
        "componentes": {
            "Computador portátil": 1,
            "Equipo de videoconferencia": 1,
        },
        "tarifa_jornada": 160000,
    },
    {
        "nombre": "Capacitación empresarial",
        "componentes": {
            "Computador portátil": 1,
            "Video beam": 1,
            "Sistema de sonido": 1,
        },
        "tarifa_jornada": 300000,
    },
    {
        "nombre": "Evento corporativo",
        "componentes": {
            "Computador portátil": 2,
            "Video beam": 1,
            "Sistema de sonido": 1,
            "Equipo de videoconferencia": 1,
        },
        "tarifa_jornada": 450000,
    },
)

# Asesorías especializadas con una tarifa fija por sesión de una hora.
ASESORIAS_ESPECIALIZADAS = (
    {
        "nombre": "Desarrollo de software",
        "tarifa_sesion": 150000,
    },
    {
        "nombre": "Infraestructura tecnológica y seguridad informática",
        "tarifa_sesion": 180000,
    },
    {
        "nombre": "Transformación digital y automatización",
        "tarifa_sesion": 160000,
    },
)

CAPACIDAD_MAXIMA_SALAS = 200


def _crear_sala(datos_sala, horas=1, disponible=True):
    """Crea una sala del catálogo con los datos comerciales indicados."""
    return SalaCorporativa(
        datos_sala["nombre"],
        datos_sala["capacidad"],
        datos_sala["descripcion"],
        datos_sala["tarifa_hora"],
        horas=horas,
        impuesto=0,
        descuento=0,
        disponible=disponible,
    )


def _validar_asistentes(asistentes):
    """Comprueba que el número de asistentes sea un entero válido."""
    if isinstance(asistentes, bool) or not isinstance(asistentes, int):
        raise DatoInvalidoError(
            "El número de asistentes debe ser un número entero."
        )
    if asistentes <= 0:
        raise DatoInvalidoError("El número de asistentes debe ser mayor que cero.")
    if asistentes > CAPACIDAD_MAXIMA_SALAS:
        raise DatoInvalidoError(
            "No hay salas disponibles para más de 200 asistentes."
        )
    return asistentes


def obtener_salas():
    """Devuelve las salas disponibles en el catálogo."""
    return tuple(_crear_sala(datos) for datos in SALAS_CORPORATIVAS)


def seleccionar_sala(asistentes, horas=1, disponible=True):
    """Selecciona la sala más pequeña que tenga capacidad para los asistentes."""
    asistentes = _validar_asistentes(asistentes)

    for datos_sala in SALAS_CORPORATIVAS:
        if asistentes <= datos_sala["capacidad"]:
            return _crear_sala(datos_sala, horas=horas, disponible=disponible)

    raise DatoInvalidoError("No se encontró una sala adecuada para los asistentes.")


def _crear_combo(datos_combo, disponible=True):
    """Crea un combo con una copia de sus componentes."""
    return ComboEquipos(
        datos_combo["nombre"],
        datos_combo["tarifa_jornada"],
        dict(datos_combo["componentes"]),
        impuesto=0,
        descuento=0,
        disponible=disponible,
    )


def obtener_combos():
    """Devuelve los combos de equipos disponibles en el catálogo."""
    return tuple(_crear_combo(datos) for datos in COMBOS_EQUIPOS)


def obtener_combo(nombre_combo, disponible=True):
    """Busca un combo por su nombre y devuelve una instancia nueva."""
    if not isinstance(nombre_combo, str) or nombre_combo.strip() == "":
        raise DatoInvalidoError("El nombre del combo debe ser un texto válido.")

    nombre_buscado = nombre_combo.strip().casefold()
    for datos_combo in COMBOS_EQUIPOS:
        if datos_combo["nombre"].casefold() == nombre_buscado:
            return _crear_combo(datos_combo, disponible=disponible)

    raise DatoInvalidoError("El combo solicitado no existe en el catálogo.")


def _crear_asesoria(datos_asesoria, disponible=True):
    """Crea una asesoría con la tarifa fija del catálogo."""
    return AsesoriaEspecializada(
        datos_asesoria["nombre"],
        datos_asesoria["tarifa_sesion"],
        impuesto=0,
        descuento=0,
        disponible=disponible,
    )


def obtener_asesorias():
    """Devuelve las asesorías disponibles en el catálogo."""
    return tuple(_crear_asesoria(datos) for datos in ASESORIAS_ESPECIALIZADAS)


def obtener_asesoria(nombre_asesoria, disponible=True):
    """Busca una asesoría por su nombre y devuelve una instancia nueva."""
    if not isinstance(nombre_asesoria, str) or nombre_asesoria.strip() == "":
        raise DatoInvalidoError("El nombre de la asesoría debe ser un texto válido.")

    nombre_buscado = nombre_asesoria.strip().casefold()
    for datos_asesoria in ASESORIAS_ESPECIALIZADAS:
        if datos_asesoria["nombre"].casefold() == nombre_buscado:
            return _crear_asesoria(datos_asesoria, disponible=disponible)

    raise DatoInvalidoError("La asesoría solicitada no existe en el catálogo.")


def obtener_todos_los_servicios():
    """Devuelve todos los servicios del catálogo en una sola tupla."""
    return obtener_salas() + obtener_combos() + obtener_asesorias()
