"""Pruebas de datos inválidos y manejo de horarios."""

import unittest
from datetime import date, timedelta

from catalogo_servicios import seleccionar_sala
from cliente import Cliente
from excepciones import DatoInvalidoError, ReservaInvalidaError
from main import validar_cruce_sala
from reserva import Reserva
from servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada


class TestValidacionesAdicionales(unittest.TestCase):
    def test_cliente_rechaza_datos_que_no_son_texto(self):
        with self.assertRaises(DatoInvalidoError):
            Cliente(None, "cc", "123")

    def test_parametros_obligatorios_faltantes(self):
        with self.assertRaises(DatoInvalidoError):
            Cliente("Omar", "cc")
        with self.assertRaises(DatoInvalidoError):
            ReservaSala("Sala")
        with self.assertRaises(ReservaInvalidaError):
            Reserva()

    def test_costo_inconsistente_genera_error_controlado(self):
        servicio = ReservaSala("Sala", 1e308, horas=2)
        with self.assertRaises(DatoInvalidoError):
            servicio.calcular_costo()

    def test_modificar_nombre_invalido_no_cambia_el_valor(self):
        cliente = Cliente("Omar", "cc", "123")
        with self.assertRaises(DatoInvalidoError):
            cliente.nombre = ""
        self.assertEqual(cliente.nombre, "Omar")

    def test_servicio_rechaza_valores_no_finitos(self):
        for valor in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(valor=valor):
                with self.assertRaises(DatoInvalidoError):
                    ReservaSala("Sala", valor)
                with self.assertRaises(DatoInvalidoError):
                    ReservaSala("Sala", 100, horas=valor)
                with self.assertRaises(DatoInvalidoError):
                    ReservaSala("Sala", 100, impuesto=valor)
                with self.assertRaises(DatoInvalidoError):
                    ReservaSala("Sala", 100, descuento=valor)

    def test_servicios_describen_su_tipo(self):
        servicios = (ReservaSala("Sala", 100), AlquilerEquipo("Equipo", 100),
                     AsesoriaEspecializada("Asesoría", 100))
        for servicio in servicios:
            self.assertIn(servicio.nombre, servicio.describir_servicio())

    def test_cruce_consecutiva_y_cancelacion(self):
        cliente = Cliente("Omar", "cc", "123")
        fecha = (date.today() + timedelta(days=2)).isoformat()
        existente = Reserva(cliente, seleccionar_sala(50, horas=2), fecha, "09:00")
        cruce = Reserva(cliente, seleccionar_sala(50), fecha, "10:00")
        consecutiva = Reserva(cliente, seleccionar_sala(50), fecha, "11:00")
        otra_sala = Reserva(cliente, seleccionar_sala(100), fecha, "10:00")
        with self.assertRaises(ReservaInvalidaError):
            validar_cruce_sala(cruce, [existente])
        validar_cruce_sala(consecutiva, [existente])
        validar_cruce_sala(otra_sala, [existente])
        existente.cancelar_reserva()
        validar_cruce_sala(cruce, [existente])


if __name__ == "__main__":
    unittest.main()
