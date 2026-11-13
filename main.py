"""Punto de entrada del sistema de gestión de reservas de Software FJ."""

import logging
import math
from datetime import datetime

from catalogo_servicios import (
    obtener_asesoria,
    obtener_asesorias,
    obtener_combo,
    obtener_combos,
    obtener_salas,
    seleccionar_sala,
)
from cliente import Cliente
from excepciones import (
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from reserva import Reserva
from servicio import SalaCorporativa


def formatear_pesos(valor):
    """Devuelve un valor monetario con formato colombiano sencillo."""
    if float(valor).is_integer():
        return f"${int(valor):,}".replace(",", ".")
    texto = f"{valor:,.2f}"
    return "$" + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def mostrar_menu():
    """Muestra las opciones principales del programa."""
    print(
        """
===== Software FJ =====
1. Reservar una sala corporativa
2. Reservar un combo de equipos
3. Solicitar una asesoría especializada
4. Consultar las reservas registradas
5. Salir
"""
    )


def mostrar_salas():
    """Muestra las salas disponibles con su capacidad y tarifa."""
    print("\nSalas corporativas disponibles:")
    for sala in obtener_salas():
        print(
            f"- {sala.nombre}: hasta {sala.capacidad} personas "
            f"| {formatear_pesos(sala.tarifa_base)} por hora "
            f"| {sala.descripcion}"
        )


def mostrar_combos():
    """Muestra los combos con sus equipos y su precio por jornada."""
    print("\nCombos de equipos disponibles (jornada de 8 horas):")
    for numero, combo in enumerate(obtener_combos(), start=1):
        print(
            f"{numero}. {combo.nombre} - "
            f"{formatear_pesos(combo.tarifa_base)} por jornada"
        )
        for equipo, cantidad in combo.componentes.items():
            print(f"   - {cantidad} x {equipo}")


def mostrar_asesorias():
    """Muestra las asesorías disponibles y su tarifa por sesión."""
    print("\nAsesorías especializadas disponibles:")
    for numero, asesoria in enumerate(obtener_asesorias(), start=1):
        print(
            f"{numero}. {asesoria.nombre} - "
            f"{formatear_pesos(asesoria.tarifa_base)} por sesión de 1 hora"
        )


def registrar_cliente():
    """Solicita los datos y crea un cliente con las validaciones existentes."""
    nombre = input("Ingrese el nombre del cliente: ")
    tipo_identificacion = input("Ingrese el tipo de identificación: ")
    numero_identificacion = input("Ingrese el número de identificación: ")

    cliente = Cliente(nombre, tipo_identificacion, numero_identificacion)
    logging.info("Cliente registrado: %s", cliente.nombre)
    return cliente


def obtener_cliente_actual(cliente_actual):
    """Reutiliza el cliente de la ejecución o solicita uno nuevo."""
    if cliente_actual is not None:
        print(f"Cliente actual: {cliente_actual.nombre}.")
        return cliente_actual
    return registrar_cliente()


def solicitar_entero(mensaje):
    """Solicita un número entero y repite hasta recibir uno válido."""
    while True:
        texto = input(mensaje).strip()
        try:
            return int(texto)
        except ValueError:
            print("Debe ingresar un número entero.")
            logging.warning("Entrada no entera: %s", texto)


def solicitar_horas(mensaje):
    """Solicita una cantidad de horas mayor que cero."""
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        try:
            horas = float(texto)
        except ValueError:
            print("Debe ingresar un número de horas válido.")
            logging.warning("Entrada de horas no numérica: %s", texto)
            continue

        if math.isfinite(horas) and horas > 0:
            return int(horas) if horas.is_integer() else horas

        print("Las horas deben ser un número mayor que cero.")
        logging.warning("Cantidad de horas inválida: %s", texto)


def convertir_hora_a_24_horas(hora):
    """Convierte una hora AM/PM o de 24 horas al formato HH:MM."""
    if not isinstance(hora, str) or hora.strip() == "":
        raise ReservaInvalidaError("La hora de la reserva no puede estar vacía.")

    texto = hora.strip().upper()
    formatos = (
        "%I:%M %p",
        "%I:%M%p",
        "%I %p",
        "%I%p",
        "%H:%M",
    )
    for formato in formatos:
        try:
            hora_convertida = datetime.strptime(texto, formato)
            return hora_convertida.strftime("%H:%M")
        except ValueError:
            continue

    raise ReservaInvalidaError(
        "Formato de hora inválido. Use por ejemplo 5 pm, 5:30 pm, "
        "8:00 AM, 20:00 u 08:00."
    )


def solicitar_hora():
    """Pide una hora y permite intentarlo de nuevo si el formato es incorrecto."""
    while True:
        texto = input("Ingrese la hora de la reserva: ").strip()
        try:
            return convertir_hora_a_24_horas(texto)
        except ReservaInvalidaError as error:
            print(f"Error: {error}")
            logging.warning("Hora inválida: %s", texto)


def solicitar_reserva(cliente, servicio):
    """Pide fecha y hora hasta crear una reserva válida."""
    while True:
        fecha = input("Ingrese la fecha de la reserva (YYYY-MM-DD): ").strip()
        hora = solicitar_hora()

        try:
            return Reserva(cliente, servicio, fecha, hora)
        except ReservaInvalidaError as error:
            print(f"Error: {error}")
            logging.warning("Reserva inválida: %s", error)


def gestionar_reserva(reserva):
    """Permite confirmar, cancelar o dejar pendiente una reserva."""
    while True:
        print(f"\nReserva {reserva.codigo_reserva} - Estado: {reserva.estado}")
        print("1. Confirmar reserva")
        print("2. Cancelar reserva")
        print("3. Dejar pendiente")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            try:
                print(reserva.procesar_reserva())
                return
            except (OperacionNoPermitidaError, ServicioNoDisponibleError) as error:
                print(f"No se pudo confirmar la reserva: {error}")
                logging.warning(
                    "Error al confirmar la reserva %s: %s",
                    reserva.codigo_reserva,
                    error,
                )
        elif opcion == "2":
            try:
                print(reserva.cancelar_reserva())
                logging.info("Reserva %s cancelada.", reserva.codigo_reserva)
                return
            except OperacionNoPermitidaError as error:
                print(f"No se pudo cancelar la reserva: {error}")
                logging.warning(
                    "Error al cancelar la reserva %s: %s",
                    reserva.codigo_reserva,
                    error,
                )
        elif opcion == "3":
            if reserva.estado == Reserva.ESTADO_PENDIENTE:
                print(f"La reserva {reserva.codigo_reserva} permanece pendiente.")
            else:
                print(
                    f"La reserva {reserva.codigo_reserva} queda en estado "
                    f"{reserva.estado}."
                )
            logging.info(
                "Reserva %s queda en estado %s.",
                reserva.codigo_reserva,
                reserva.estado,
            )
            return
        else:
            print("Opción no válida. Intente nuevamente.")


def validar_cruce_sala(reserva_nueva, reservas):
    """Comprueba cruces entre reservas activas de una misma sala."""
    if not isinstance(reserva_nueva.servicio, SalaCorporativa):
        return

    inicio_nuevo = reserva_nueva.fecha_hora_inicio
    fin_nuevo = reserva_nueva.obtener_fecha_hora_final()

    for existente in reservas:
        if existente.estado == Reserva.ESTADO_CANCELADA:
            continue
        if not isinstance(existente.servicio, SalaCorporativa):
            continue
        if existente.servicio.nombre != reserva_nueva.servicio.nombre:
            continue
        if (inicio_nuevo < existente.obtener_fecha_hora_final()
                and existente.fecha_hora_inicio < fin_nuevo):
            raise ReservaInvalidaError(
                f"La sala {reserva_nueva.servicio.nombre} ya tiene una reserva en ese horario."
            )


def registrar_reserva(reserva, reservas):
    """Guarda la reserva, muestra sus datos y permite gestionarla."""
    validar_cruce_sala(reserva, reservas)
    reservas.append(reserva)

    print(f"\nReserva creada: {reserva.codigo_reserva}")
    print(f"Servicio: {reserva.servicio.nombre}")
    print(f"Fecha: {reserva.fecha} a las {reserva.hora}")
    print(f"Costo total: {formatear_pesos(reserva.calcular_costo())}")
    print(f"Estado inicial: {reserva.estado}")

    logging.info(
        "Reserva %s creada para %s con el servicio %s. Costo: %s.",
        reserva.codigo_reserva,
        reserva.cliente.nombre,
        reserva.servicio.nombre,
        reserva.calcular_costo(),
    )
    gestionar_reserva(reserva)


def reservar_sala(cliente, reservas):
    """Selecciona una sala según los asistentes y registra la reserva."""
    mostrar_salas()

    while True:
        asistentes = solicitar_entero("Ingrese el número de asistentes: ")
        try:
            seleccionar_sala(asistentes)
            break
        except DatoInvalidoError as error:
            print(f"Error: {error}")
            logging.warning("Número de asistentes inválido: %s", error)

    horas = solicitar_horas("Ingrese la cantidad de horas: ")
    sala = seleccionar_sala(asistentes, horas=horas)

    print(f"\nSala seleccionada: {sala.nombre}")
    print(f"Capacidad: {sala.capacidad} personas")
    print(f"Costo por {sala.horas} hora(s): {formatear_pesos(sala.calcular_costo())}")

    reserva = solicitar_reserva(cliente, sala)
    registrar_reserva(reserva, reservas)


def elegir_combo():
    """Muestra los combos y devuelve el seleccionado."""
    mostrar_combos()
    combos = obtener_combos()

    while True:
        opcion = solicitar_entero("Seleccione el número del combo: ")
        if 1 <= opcion <= len(combos):
            return obtener_combo(combos[opcion - 1].nombre)

        print("El número del combo no es válido. Intente nuevamente.")


def reservar_combo(cliente, reservas):
    """Selecciona un combo cerrado y registra la reserva."""
    combo = elegir_combo()

    print(f"\nCombo seleccionado: {combo.nombre}")
    print(f"Precio fijo por jornada de 8 horas: {formatear_pesos(combo.tarifa_base)}")

    reserva = solicitar_reserva(cliente, combo)
    registrar_reserva(reserva, reservas)


def elegir_asesoria():
    """Muestra las asesorías y devuelve la seleccionada."""
    mostrar_asesorias()
    asesorias = obtener_asesorias()

    while True:
        opcion = solicitar_entero("Seleccione el número de la asesoría: ")
        if 1 <= opcion <= len(asesorias):
            return obtener_asesoria(asesorias[opcion - 1].nombre)

        print("El número de la asesoría no es válido. Intente nuevamente.")


def reservar_asesoria(cliente, reservas):
    """Selecciona una asesoría y registra la reserva."""
    asesoria = elegir_asesoria()

    print(f"\nAsesoría seleccionada: {asesoria.nombre}")
    print(
        f"Tarifa fija por sesión de 1 hora: "
        f"{formatear_pesos(asesoria.tarifa_base)}"
    )

    reserva = solicitar_reserva(cliente, asesoria)
    registrar_reserva(reserva, reservas)


def mostrar_reservas(reservas):
    """Muestra los datos y el estado de todas las reservas registradas."""
    if not reservas:
        print("\nNo hay reservas registradas durante esta ejecución.")
        return

    print("\nReservas registradas:")
    for numero, reserva in enumerate(reservas, start=1):
        print(f"\n{numero}. Código: {reserva.codigo_reserva}")
        print(f"   Cliente: {reserva.cliente.nombre}")
        print(f"   Servicio: {reserva.servicio.nombre}")
        print(f"   Fecha: {reserva.fecha}")
        print(f"   Hora: {reserva.hora}")
        print(f"   Costo: {formatear_pesos(reserva.calcular_costo())}")
        print(f"   Estado: {reserva.estado}")


def buscar_reserva(reservas, referencia):
    """Busca una reserva por su código o por su número de posición."""
    if not isinstance(referencia, str):
        return None

    referencia = referencia.strip()
    if referencia == "":
        return None

    codigo_buscado = referencia.upper()
    for reserva in reservas:
        if reserva.codigo_reserva.upper() == codigo_buscado:
            return reserva

    if referencia.isdigit():
        posicion = int(referencia)
        if 1 <= posicion <= len(reservas):
            return reservas[posicion - 1]

    return None


def consultar_reservas(reservas):
    """Muestra las reservas y permite gestionar una de ellas."""
    mostrar_reservas(reservas)
    if not reservas:
        return

    entrada = input(
        "Código o número de la reserva que desea gestionar "
        "(Enter para volver): "
    ).strip()
    if entrada == "":
        return

    reserva = buscar_reserva(reservas, entrada)
    if reserva is None:
        print("No existe una reserva con ese código o número de posición.")
        logging.warning("Reserva no encontrada: %s", entrada)
        return

    gestionar_reserva(reserva)


def main():
    """Ejecuta el menú principal del programa."""
    import configuracion_logs  # noqa: F401

    reservas = []
    cliente_actual = None

    print("Bienvenido al sistema de gestión de reservas de Software FJ.")

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        try:
            if opcion == "1":
                cliente_actual = obtener_cliente_actual(cliente_actual)
                reservar_sala(cliente_actual, reservas)
            elif opcion == "2":
                cliente_actual = obtener_cliente_actual(cliente_actual)
                reservar_combo(cliente_actual, reservas)
            elif opcion == "3":
                cliente_actual = obtener_cliente_actual(cliente_actual)
                reservar_asesoria(cliente_actual, reservas)
            elif opcion == "4":
                consultar_reservas(reservas)
            elif opcion == "5":
                print("Gracias por usar el sistema de Software FJ.")
                logging.info("Programa finalizado por el usuario.")
                break
            else:
                print("Opción no válida. Intente nuevamente.")
        except (
            DatoInvalidoError,
            ReservaInvalidaError,
            ServicioNoDisponibleError,
            OperacionNoPermitidaError,
        ) as error:
            print(f"Error: {error}")
            logging.error("Error controlado durante la ejecución: %s", error)
        finally:
            # Dejamos un registro aunque una operación termine con error.
            logging.info("Finalizó el procesamiento de la opción del menú.")


if __name__ == "__main__":
    main()
