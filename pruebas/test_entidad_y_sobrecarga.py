"""Pruebas de la entidad abstracta y de los métodos de costo sobrecargados."""

import unittest
from datetime import datetime, timedelta

from cliente import Cliente
from entidad import Entidad
from excepciones import DatoInvalidoError
from reserva import Reserva
from servicio import (
    AsesoriaEspecializada,
    ComboEquipos,
    ReservaSala,
    SalaCorporativa,
)


def fecha_futura(dias=10):
    """Devuelve una fecha futura para que las pruebas no caduquen."""
    return (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")


def crear_cliente():
    """Crea un cliente válido para las pruebas."""
    return Cliente("Ana Pérez", "CC", "1234567890")


class TestEntidadAbstracta(unittest.TestCase):
    """Comprueba la clase abstracta general del sistema."""

    def test_entidad_no_se_puede_instanciar(self):
        """Entidad es abstracta y exige implementar describir."""
        with self.assertRaises(TypeError):
            Entidad()

    def test_clientes_servicios_y_reservas_son_entidades(self):
        """Las entidades principales heredan de la clase abstracta general."""
        cliente = crear_cliente()
        sala = ReservaSala("Sala", 100)
        reserva = Reserva(cliente, sala, fecha_futura(), "10:30")

        for entidad in (cliente, sala, reserva):
            with self.subTest(tipo=type(entidad).__name__):
                self.assertIsInstance(entidad, Entidad)
                self.assertIsInstance(entidad.describir(), str)

    def test_descripciones_de_entidades(self):
        """Cada entidad describe sus datos principales."""
        cliente = crear_cliente()
        sala = ReservaSala("Sala A", 100, horas=2)
        reserva = Reserva(cliente, sala, fecha_futura(), "10:30")
        combo = ComboEquipos(
            "Combo básico",
            500,
            {"Computador": 1, "Video beam": 1},
        )
        asesoria = AsesoriaEspecializada("Asesoría", 200)

        self.assertIn("Ana Pérez", cliente.describir())
        self.assertIn("Sala A", sala.describir())
        self.assertIn("Computador", combo.describir())
        self.assertIn("Asesoría", asesoria.describir())
        self.assertIn(reserva.codigo_reserva, reserva.describir())
        self.assertIn("Sala A", reserva.describir())


class TestCalculoCostoSobrecargado(unittest.TestCase):
    """Comprueba las variantes del cálculo de costo con parámetros opcionales."""

    def test_costo_sin_parametros_usa_la_configuracion_del_servicio(self):
        """Sin argumentos se mantiene el comportamiento anterior."""
        sala = ReservaSala("Sala", 100, horas=2)

        self.assertAlmostEqual(sala.calcular_costo(), 200)

    def test_costo_con_impuesto_opcional(self):
        """Se puede calcular una variante con impuesto sin modificarlo."""
        sala = ReservaSala("Sala", 100, horas=2)

        self.assertAlmostEqual(sala.calcular_costo(impuesto=19), 238)
        self.assertEqual(sala.impuesto, 0)

    def test_costo_con_descuento_opcional(self):
        """Se puede calcular una variante con descuento sin modificarlo."""
        sala = ReservaSala("Sala", 100, horas=2)

        self.assertAlmostEqual(sala.calcular_costo(descuento=10), 180)
        self.assertEqual(sala.descuento, 0)

    def test_costo_con_impuesto_y_descuento(self):
        """Ambos parámetros opcionales se aplican sobre el costo base."""
        sala = ReservaSala("Sala", 100, horas=2)

        self.assertAlmostEqual(
            sala.calcular_costo(impuesto=19, descuento=10),
            218,
        )

    def test_parametros_opcionales_invalidos(self):
        """Las variantes también validan los porcentajes recibidos."""
        sala = ReservaSala("Sala", 100, horas=2)

        for valor in (-1, 101, "19", None, True):
            with self.subTest(valor=valor):
                if valor is None:
                    continue
                with self.assertRaises(DatoInvalidoError):
                    if valor in (-1, 101):
                        sala.calcular_costo(impuesto=valor)
                    else:
                        sala.calcular_costo(descuento=valor)


class TestDescribirServicioPolimorfico(unittest.TestCase):
    """Comprueba que todos los servicios implementen describir_servicio."""

    def test_todos_los_servicios_se_describen(self):
        """Cada servicio concreto responde a describir_servicio."""
        servicios = (
            ReservaSala("Sala", 100),
            SalaCorporativa("Sala Grande", 200, "Eventos", 200000),
            ComboEquipos("Combo", 500, {"Computador": 1}),
            AsesoriaEspecializada("Asesoría", 200),
        )

        for servicio in servicios:
            with self.subTest(servicio=type(servicio).__name__):
                self.assertIn(servicio.nombre, servicio.describir_servicio())


if __name__ == "__main__":
    unittest.main()
