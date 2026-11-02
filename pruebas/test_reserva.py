"""Pruebas automatizadas para la clase Reserva de Software FJ."""

import unittest
from datetime import datetime, timedelta

from cliente import Cliente
from excepciones import (
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from reserva import Reserva
from servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def fecha_futura(dias=10):
    """Devuelve una fecha futura para que las pruebas no caduquen."""
    return (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")


def crear_cliente():
    """Crea un cliente válido para las pruebas."""
    return Cliente("Ana Pérez", "CC", "1234567890")


def crear_sala(disponible=True):
    """Crea una sala válida para las pruebas."""
    return ReservaSala(
        "Sala de reuniones",
        100,
        horas=2,
        impuesto=19,
        descuento=10,
        disponible=disponible,
    )


class TestCreacionReserva(unittest.TestCase):
    """Comprueba la relación entre cliente, servicio, fecha y hora."""

    def test_crear_reserva_con_cliente_y_servicio_validos(self):
        """Una reserva guarda el cliente y el servicio recibidos."""
        cliente = crear_cliente()
        servicio = crear_sala()
        fecha = fecha_futura()

        reserva = Reserva(cliente, servicio, fecha, "10:30")

        self.assertIs(reserva.cliente, cliente)
        self.assertIs(reserva.servicio, servicio)
        self.assertEqual(reserva.fecha, fecha)
        self.assertEqual(reserva.hora, "10:30")
        self.assertTrue(reserva.codigo_reserva.startswith("RES-"))

    def test_rechazar_cliente_que_no_es_cliente(self):
        """El cliente debe ser una instancia de la clase Cliente."""
        with self.assertRaises(DatoInvalidoError) as contexto:
            Reserva("Ana Pérez", crear_sala(), fecha_futura(), "10:30")

        self.assertEqual(
            str(contexto.exception),
            "El cliente debe ser una instancia de Cliente.",
        )

    def test_rechazar_servicio_que_no_es_servicio(self):
        """El servicio debe ser una instancia de Servicio o sus derivadas."""
        with self.assertRaises(DatoInvalidoError) as contexto:
            Reserva(crear_cliente(), "Sala de reuniones", fecha_futura(), "10:30")

        self.assertEqual(
            str(contexto.exception),
            "El servicio debe ser una instancia de Servicio.",
        )

    def test_rechazar_servicio_no_disponible(self):
        """No se puede crear una reserva con un servicio no disponible."""
        servicio = crear_sala(disponible=False)

        with self.assertRaises(ServicioNoDisponibleError):
            Reserva(crear_cliente(), servicio, fecha_futura(), "10:30")

    def test_estado_inicial_pendiente(self):
        """Toda reserva nueva inicia en estado pendiente."""
        reserva = Reserva(crear_cliente(), crear_sala(), fecha_futura(), "10:30")

        self.assertEqual(reserva.estado, Reserva.ESTADO_PENDIENTE)
        self.assertFalse(reserva.esta_confirmada)


class TestEstadosReserva(unittest.TestCase):
    """Comprueba la confirmación y la cancelación de reservas."""

    def test_confirmar_reserva_pendiente(self):
        """Una reserva pendiente se puede confirmar."""
        reserva = Reserva(crear_cliente(), crear_sala(), fecha_futura(), "10:30")

        mensaje = reserva.confirmar_reserva()

        self.assertEqual(reserva.estado, Reserva.ESTADO_CONFIRMADA)
        self.assertTrue(reserva.esta_confirmada)
        self.assertIn("confirmada", mensaje)

    def test_impedir_confirmar_dos_veces(self):
        """Una reserva ya confirmada no se puede volver a confirmar."""
        reserva = Reserva(crear_cliente(), crear_sala(), fecha_futura(), "10:30")
        reserva.confirmar_reserva()

        with self.assertRaises(OperacionNoPermitidaError):
            reserva.confirmar_reserva()

    def test_cancelar_reserva_pendiente(self):
        """Una reserva pendiente se puede cancelar."""
        reserva = Reserva(crear_cliente(), crear_sala(), fecha_futura(), "10:30")

        mensaje = reserva.cancelar_reserva()

        self.assertEqual(reserva.estado, Reserva.ESTADO_CANCELADA)
        self.assertIn("cancelada", mensaje)

    def test_cancelar_reserva_confirmada(self):
        """Una reserva confirmada también se puede cancelar."""
        reserva = Reserva(crear_cliente(), crear_sala(), fecha_futura(), "10:30")
        reserva.confirmar_reserva()

        reserva.cancelar_reserva()

        self.assertEqual(reserva.estado, Reserva.ESTADO_CANCELADA)

    def test_impedir_cancelar_una_reserva_ya_cancelada(self):
        """Una reserva cancelada no se puede volver a cancelar."""
        reserva = Reserva(crear_cliente(), crear_sala(), fecha_futura(), "10:30")
        reserva.cancelar_reserva()

        with self.assertRaises(OperacionNoPermitidaError):
            reserva.cancelar_reserva()

    def test_impedir_cancelar_con_un_estado_no_permitido(self):
        """Solo se cancelan reservas cuyo estado sea pendiente o confirmado."""
        reserva = Reserva(crear_cliente(), crear_sala(), fecha_futura(), "10:30")
        reserva.estado = "estado desconocido"

        with self.assertRaises(OperacionNoPermitidaError) as contexto:
            reserva.cancelar_reserva()

        self.assertEqual(
            str(contexto.exception),
            "Solo se pueden cancelar reservas pendientes y confirmadas.",
        )

    def test_impedir_confirmar_si_el_servicio_dejo_de_estar_disponible(self):
        """La disponibilidad se vuelve a comprobar al confirmar."""
        servicio = crear_sala()
        reserva = Reserva(crear_cliente(), servicio, fecha_futura(), "10:30")
        servicio.establecer_disponibilidad(False)

        with self.assertRaises(ServicioNoDisponibleError):
            reserva.confirmar_reserva()

        self.assertEqual(reserva.estado, Reserva.ESTADO_PENDIENTE)


class TestCostoYDatosDelServicio(unittest.TestCase):
    """Comprueba que la reserva consulte los datos sin duplicar la lógica."""

    def test_costo_coincide_con_el_del_servicio(self):
        """La reserva delega el cálculo del costo en el servicio."""
        servicio = crear_sala()
        reserva = Reserva(crear_cliente(), servicio, fecha_futura(), "10:30")

        self.assertAlmostEqual(reserva.calcular_costo(), servicio.calcular_costo())
        self.assertAlmostEqual(reserva.calcular_costo(), 218)

    def test_costo_de_asesoria_se_consulta_desde_la_reserva(self):
        """La reserva funciona con cualquier servicio especializado."""
        servicio = AsesoriaEspecializada("Asesoría", 200, impuesto=19)
        reserva = Reserva(crear_cliente(), servicio, fecha_futura(), "10:30")

        self.assertAlmostEqual(reserva.calcular_costo(), 238)

    def test_duracion_de_una_sala(self):
        """La duración de una sala corresponde a sus horas."""
        servicio = ReservaSala("Sala", 100, horas=2.5)
        reserva = Reserva(crear_cliente(), servicio, fecha_futura(), "10:30")

        self.assertEqual(reserva.duracion, 2.5)

    def test_duracion_no_definida_en_otros_servicios(self):
        """Los servicios sin horas no inventan una duración."""
        asesoria = AsesoriaEspecializada("Asesoría", 200)
        reserva_asesoria = Reserva(
            crear_cliente(), asesoria, fecha_futura(), "10:30"
        )

        equipo = AlquilerEquipo("Portátil", 50, cantidad=3)
        reserva_equipo = Reserva(crear_cliente(), equipo, fecha_futura(), "11:00")

        self.assertIsNone(reserva_asesoria.duracion)
        self.assertIsNone(reserva_equipo.duracion)

    def test_cantidad_de_equipos(self):
        """La cantidad se consulta desde el servicio de alquiler."""
        servicio = AlquilerEquipo("Portátil", 50, cantidad=3)
        reserva = Reserva(crear_cliente(), servicio, fecha_futura(), "10:30")

        self.assertEqual(reserva.cantidad, 3)


class TestValidacionesFechaHora(unittest.TestCase):
    """Comprueba las validaciones actuales de fecha y hora."""

    def test_rechazar_fecha_que_no_es_texto(self):
        """La fecha debe ser una cadena de texto antes de validar su contenido."""
        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva(crear_cliente(), crear_sala(), None, "10:30")

        self.assertEqual(
            str(contexto.exception),
            "La fecha de la reserva debe ser una cadena de texto.",
        )

    def test_rechazar_hora_que_no_es_texto(self):
        """La hora debe ser una cadena de texto antes de validar su contenido."""
        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva(crear_cliente(), crear_sala(), fecha_futura(), 1030)

        self.assertEqual(
            str(contexto.exception),
            "La hora de la reserva debe ser una cadena de texto.",
        )

    def test_rechazar_fecha_vacia(self):
        """La fecha no puede estar vacía."""
        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva(crear_cliente(), crear_sala(), "", "10:30")

        self.assertEqual(
            str(contexto.exception),
            "La fecha de la reserva no puede estar vacía.",
        )

    def test_rechazar_hora_vacia(self):
        """La hora no puede estar vacía."""
        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva(crear_cliente(), crear_sala(), fecha_futura(), "")

        self.assertEqual(
            str(contexto.exception),
            "La hora de la reserva no puede estar vacía.",
        )

    def test_rechazar_formato_de_fecha_invalido(self):
        """La fecha debe usar el formato YYYY-MM-DD."""
        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva(crear_cliente(), crear_sala(), "10/12/2026", "10:30")

        self.assertEqual(
            str(contexto.exception),
            "Formato de fecha inválido. Use YYYY-MM-DD.",
        )

    def test_rechazar_formato_de_hora_invalido(self):
        """La hora debe usar el formato HH:MM."""
        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva(crear_cliente(), crear_sala(), fecha_futura(), "10:30 PM")

        self.assertEqual(
            str(contexto.exception),
            "Formato de hora inválido. Use HH:MM.",
        )

    def test_rechazar_fecha_anterior_a_hoy(self):
        """No se permite reservar en una fecha pasada."""
        fecha_pasada = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva(crear_cliente(), crear_sala(), fecha_pasada, "10:30")

        self.assertEqual(
            str(contexto.exception),
            "La fecha de la reserva no puede ser anterior a la fecha actual.",
        )

    def test_rechazar_fecha_y_hora_anteriores_al_momento_actual(self):
        """No se permite reservar para un momento que ya pasó."""
        momento_pasado = datetime.now() - timedelta(minutes=5)
        fecha = momento_pasado.strftime("%Y-%m-%d")
        hora = momento_pasado.strftime("%H:%M")

        with self.assertRaises(ReservaInvalidaError):
            Reserva(crear_cliente(), crear_sala(), fecha, hora)


if __name__ == "__main__":
    unittest.main()
