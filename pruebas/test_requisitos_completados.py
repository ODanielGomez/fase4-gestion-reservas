"""Pruebas de los requisitos completados: validación, duración y procesamiento."""

import unittest
from contextlib import redirect_stdout
from datetime import date, datetime, time, timedelta
from io import StringIO
from unittest.mock import patch

import main
from catalogo_servicios import seleccionar_sala
from cliente import Cliente
from excepciones import (
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from reserva import Reserva
from servicio import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    ComboEquipos,
    ReservaSala,
    SalaCorporativa,
    Servicio,
)


def fecha_futura(dias=10):
    """Devuelve una fecha futura para que las pruebas no caduquen."""
    return (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")


def crear_cliente():
    """Crea un cliente válido para las pruebas."""
    return Cliente("Ana Pérez", "CC", "1234567890")


def crear_sala(horas=2):
    """Crea una sala válida para las pruebas."""
    return ReservaSala("Sala de reuniones", 100, horas=horas)


class ServicioDuracionInvalida(Servicio):
    """Servicio de prueba que expone una duración inválida."""

    def __init__(self):
        super().__init__("Servicio con duración inválida", 100)

    @property
    def duracion(self):
        return 0

    def validar_parametros(self):
        return super().validar_parametros()

    def calcular_costo_base(self):
        return self.tarifa_base

    def describir_servicio(self):
        return "Servicio con duración inválida"


class TestValidacionPolimorfica(unittest.TestCase):
    """Comprueba que cada servicio implemente y ejecute su validación."""

    def test_validar_parametros_es_parte_del_contrato_de_servicio(self):
        """La clase base exige implementar validar_parametros."""
        self.assertIn("validar_parametros", Servicio.__abstractmethods__)

    def test_cada_servicio_especializado_sobrescribe_su_validacion(self):
        """Cada servicio concreto define su propio método de validación."""
        clases = (
            ReservaSala,
            AlquilerEquipo,
            AsesoriaEspecializada,
            SalaCorporativa,
            ComboEquipos,
        )

        for clase in clases:
            with self.subTest(clase=clase.__name__):
                self.assertIn("validar_parametros", clase.__dict__)
                self.assertIsNot(clase.validar_parametros, Servicio.validar_parametros)

    def test_la_validacion_retorna_verdadero_con_datos_validos(self):
        """La validación se puede ejecutar explícitamente sobre servicios válidos."""
        servicios = (
            ReservaSala("Sala", 100, horas=2),
            AlquilerEquipo("Equipo", 100, cantidad=2),
            AsesoriaEspecializada("Asesoría", 100),
            SalaCorporativa("Sala Grande", 200, "Eventos", 200000),
            ComboEquipos("Combo", 500, {"Computador": 1}),
        )

        for servicio in servicios:
            with self.subTest(servicio=type(servicio).__name__):
                self.assertTrue(servicio.validar_parametros())

    def test_la_validacion_rechaza_parametros_invalidos(self):
        """Los parámetros inválidos se rechazan durante la construcción."""
        casos = (
            lambda: ReservaSala("Sala", 100, horas=0),
            lambda: AlquilerEquipo("Equipo", 100, cantidad=0),
            lambda: AsesoriaEspecializada("", 100),
            lambda: SalaCorporativa("Sala", 0, "Eventos", 100),
            lambda: ComboEquipos("Combo", 500, {}),
        )

        for indice, crear in enumerate(casos, start=1):
            with self.subTest(caso=indice):
                with self.assertRaises(DatoInvalidoError):
                    crear()

    def test_validar_parametros_revalida_el_estado_actual(self):
        """Llamar la validación detecta un estado interno inválido."""
        sala = ReservaSala("Sala", 100, horas=2)
        sala._ReservaSala__horas = 0

        with self.assertRaises(DatoInvalidoError):
            sala.validar_parametros()


class TestDuracionEnReserva(unittest.TestCase):
    """Comprueba la duración explícita y su relación con el servicio."""

    def test_duracion_de_sala_coincide_con_el_servicio(self):
        """La reserva guarda la duración que define la sala."""
        sala = crear_sala(horas=2.5)
        reserva = Reserva(crear_cliente(), sala, fecha_futura(), "10:30")

        self.assertEqual(reserva.duracion, 2.5)
        self.assertEqual(reserva.duracion, sala.duracion)

    def test_duracion_de_combo_coincide_con_el_servicio(self):
        """La reserva guarda la jornada de ocho horas del combo."""
        combo = ComboEquipos("Combo", 500, {"Computador": 1})
        reserva = Reserva(crear_cliente(), combo, fecha_futura(), "10:30")

        self.assertEqual(reserva.duracion, 8)
        self.assertEqual(reserva.duracion, combo.duracion)

    def test_duracion_no_definida_se_mantiene_en_none(self):
        """Los servicios sin duración no inventan un valor."""
        asesoria = AsesoriaEspecializada("Asesoría", 200)
        equipo = AlquilerEquipo("Equipo", 50, cantidad=2)

        reserva_asesoria = Reserva(
            crear_cliente(), asesoria, fecha_futura(), "10:30"
        )
        reserva_equipo = Reserva(crear_cliente(), equipo, fecha_futura(), "11:00")

        self.assertIsNone(reserva_asesoria.duracion)
        self.assertIsNone(reserva_equipo.duracion)

    def test_duracion_permite_calcular_el_fin_de_la_reserva(self):
        """El fin de la reserva se calcula con la duración almacenada."""
        fecha = fecha_futura()
        sala = crear_sala(horas=2.5)
        reserva = Reserva(crear_cliente(), sala, fecha, "10:30")

        inicio = datetime.combine(date.fromisoformat(fecha), time(10, 30))
        self.assertEqual(
            reserva.obtener_fecha_hora_final(),
            inicio + timedelta(hours=2.5),
        )

    def test_sin_duracion_no_se_calcula_un_fin(self):
        """Si el servicio no define duración, no se calcula un fin."""
        asesoria = AsesoriaEspecializada("Asesoría", 200)
        reserva = Reserva(crear_cliente(), asesoria, fecha_futura(), "10:30")

        self.assertIsNone(reserva.obtener_fecha_hora_final())

    def test_reserva_rechaza_una_duracion_invalida_del_servicio(self):
        """La duración se valida al integrarse en la reserva."""
        servicio = ServicioDuracionInvalida()

        with self.assertRaises(ReservaInvalidaError):
            Reserva(crear_cliente(), servicio, fecha_futura(), "10:30")


class TestProcesamientoEnReserva(unittest.TestCase):
    """Comprueba el procesamiento con manejo de excepciones dentro de Reserva."""

    def test_procesar_reserva_pendiente_la_confirma(self):
        """Una reserva pendiente se procesa confirmándola."""
        reserva = Reserva(
            crear_cliente(), crear_sala(), fecha_futura(), "10:30"
        )

        with patch("reserva.logging.info") as info_log:
            mensaje = reserva.procesar_reserva()

        self.assertEqual(reserva.estado, Reserva.ESTADO_CONFIRMADA)
        self.assertIn("confirmada", mensaje)
        self.assertEqual(info_log.call_count, 2)

    def test_procesar_reserva_ya_confirmada_registra_y_relanza(self):
        """Un estado no procesable se registra y se relanza el error."""
        reserva = Reserva(
            crear_cliente(), crear_sala(), fecha_futura(), "10:30"
        )
        reserva.confirmar_reserva()

        with patch("reserva.logging.info"), patch(
            "reserva.logging.error"
        ) as error_log:
            with self.assertRaises(OperacionNoPermitidaError):
                reserva.procesar_reserva()

        error_log.assert_called_once()
        self.assertEqual(reserva.estado, Reserva.ESTADO_CONFIRMADA)

    def test_procesar_reserva_cancelada_registra_y_relanza(self):
        """Una reserva cancelada no se puede procesar."""
        reserva = Reserva(
            crear_cliente(), crear_sala(), fecha_futura(), "10:30"
        )
        reserva.cancelar_reserva()

        with patch("reserva.logging.info"), patch(
            "reserva.logging.error"
        ) as error_log:
            with self.assertRaises(OperacionNoPermitidaError):
                reserva.procesar_reserva()

        error_log.assert_called_once()
        self.assertEqual(reserva.estado, Reserva.ESTADO_CANCELADA)

    def test_procesar_reserva_con_servicio_no_disponible(self):
        """La falta de disponibilidad se maneja sin cambiar el estado."""
        servicio = crear_sala()
        reserva = Reserva(crear_cliente(), servicio, fecha_futura(), "10:30")
        servicio.establecer_disponibilidad(False)

        with patch("reserva.logging.info"), patch("reserva.logging.error"):
            with self.assertRaises(ServicioNoDisponibleError):
                reserva.procesar_reserva()

        self.assertEqual(reserva.estado, Reserva.ESTADO_PENDIENTE)


class TestRegresionesFuncionales(unittest.TestCase):
    """Comprueba que los cambios no alteren el comportamiento existente."""

    def test_confirmacion_y_cancelacion_siguen_funcionando(self):
        """Los estados y mensajes de confirmación y cancelación se conservan."""
        reserva = Reserva(
            crear_cliente(), crear_sala(), fecha_futura(), "10:30"
        )

        self.assertIn("confirmada", reserva.confirmar_reserva())
        self.assertEqual(reserva.estado, Reserva.ESTADO_CONFIRMADA)

        self.assertIn("cancelada", reserva.cancelar_reserva())
        self.assertEqual(reserva.estado, Reserva.ESTADO_CANCELADA)

    def test_los_cruces_de_horario_siguen_funcionando(self):
        """La validación de cruces de salas conserva su comportamiento."""
        cliente = crear_cliente()
        fecha = fecha_futura()

        existente = Reserva(cliente, seleccionar_sala(50, horas=2), fecha, "09:00")
        cruce = Reserva(cliente, seleccionar_sala(50), fecha, "10:00")
        consecutiva = Reserva(cliente, seleccionar_sala(50), fecha, "11:00")

        with self.assertRaises(ReservaInvalidaError):
            main.validar_cruce_sala(cruce, [existente])

        main.validar_cruce_sala(consecutiva, [existente])

    def test_el_menu_continua_funcionando(self):
        """El menú inicia y permite salir sin interrupciones."""
        with patch("builtins.input", side_effect=["5"]):
            with redirect_stdout(StringIO()) as salida:
                main.main()

        self.assertIn("Software FJ", salida.getvalue())
        self.assertIn("Gracias por usar el sistema", salida.getvalue())


if __name__ == "__main__":
    unittest.main()