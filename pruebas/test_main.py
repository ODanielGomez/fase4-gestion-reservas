"""Pruebas automatizadas para el menú principal de Software FJ."""

import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch

import main
from catalogo_servicios import obtener_salas
from excepciones import DatoInvalidoError, ReservaInvalidaError
from reserva import Reserva
from servicio import ComboEquipos, SalaCorporativa


def fecha_futura(dias=10):
    """Devuelve una fecha futura para que las pruebas no caduquen."""
    return (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")


def crear_cliente():
    """Crea un cliente válido sin pasar por el menú."""
    datos = ["Ana Pérez", "CC", "1234567890"]
    with patch("builtins.input", side_effect=datos):
        return main.registrar_cliente()


def crear_reservas_de_prueba():
    """Crea dos reservas con códigos RES-001 y RES-002."""
    cliente = crear_cliente()
    sala = obtener_salas()[0]
    contador_original = Reserva.contador

    Reserva.contador = 0
    try:
        primera = Reserva(cliente, sala, fecha_futura(), "10:00")
        segunda = Reserva(cliente, sala, fecha_futura(), "11:00")
    finally:
        Reserva.contador = contador_original

    return [primera, segunda]


class TestFuncionesAuxiliares(unittest.TestCase):
    """Comprueba la conversión de horas y el formato de precios."""

    def test_conversion_de_horas_am_y_pm(self):
        """Las horas AM y PM se convierten al formato de 24 horas."""
        casos = {
            "8:00 PM": "20:00",
            "8:00 AM": "08:00",
            "8:00PM": "20:00",
            "20:00": "20:00",
            "08:00": "08:00",
        }

        for entrada, esperada in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(main.convertir_hora_a_24_horas(entrada), esperada)

    def test_acepta_horas_sin_minutos_y_en_minusculas(self):
        """También se aceptan horas como 5 pm u 8 am."""
        casos = {
            "5 pm": "17:00",
            "8 am": "08:00",
            "  5 pm  ": "17:00",
            "5:30 pm": "17:30",
            "8:30 am": "08:30",
        }

        for entrada, esperada in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(main.convertir_hora_a_24_horas(entrada), esperada)

    def test_rechaza_horas_invalidas(self):
        """Se informa cuando la hora no tiene un formato válido."""
        casos = (
            "",
            "25:00",
            "12:70",
            "5:70 pm",
            "ocho de la noche",
            None,
        )

        for hora in casos:
            with self.subTest(hora=hora):
                with self.assertRaises(ReservaInvalidaError):
                    main.convertir_hora_a_24_horas(hora)

    def test_formato_de_pesos_colombiano(self):
        """Los valores monetarios se muestran con separadores de miles."""
        self.assertEqual(main.formatear_pesos(100000), "$100.000")
        self.assertEqual(main.formatear_pesos(300000.0), "$300.000")
        self.assertEqual(main.formatear_pesos(150000.5), "$150.000,50")

    def test_solicitar_entero_reintenta_hasta_recibir_un_numero(self):
        """Una entrada no numérica no cierra el programa."""
        with patch("builtins.input", side_effect=["texto", "7"]):
            with redirect_stdout(StringIO()):
                self.assertEqual(main.solicitar_entero("Opción: "), 7)

    def test_solicitar_horas_reintenta_hasta_recibir_un_valor_positivo(self):
        """Solo se aceptan horas numéricas mayores que cero."""
        with patch("builtins.input", side_effect=["texto", "0", "2.5"]):
            with redirect_stdout(StringIO()):
                self.assertEqual(main.solicitar_horas("Horas: "), 2.5)


class TestRegistroCliente(unittest.TestCase):
    """Comprueba el registro del cliente desde el menú."""

    def test_registrar_cliente_valido(self):
        """El cliente se crea con los datos ingresados."""
        datos = ["Ana Pérez", "CC", "1234567890"]

        with patch("builtins.input", side_effect=datos):
            cliente = main.registrar_cliente()

        self.assertEqual(cliente.nombre, "Ana Pérez")
        self.assertEqual(cliente.tipo_identificacion, "CC")
        self.assertEqual(cliente.obtener_numero_identificacion(), "1234567890")

    def test_registrar_cliente_invalido(self):
        """Las validaciones de Cliente se conservan."""
        datos = ["", "CC", "1234567890"]

        with patch("builtins.input", side_effect=datos):
            with self.assertRaises(DatoInvalidoError):
                main.registrar_cliente()


class TestFlujosDeReserva(unittest.TestCase):
    """Comprueba la creación y gestión de reservas desde las opciones del menú."""

    def test_reservar_sala_selecciona_segun_asistentes(self):
        """La sala se elige automáticamente y el costo se calcula por horas."""
        cliente = crear_cliente()
        reservas = []
        entradas = ["10", "2", fecha_futura(), "8:00 PM", "3"]

        with patch("builtins.input", side_effect=entradas):
            with redirect_stdout(StringIO()):
                main.reservar_sala(cliente, reservas)

        reserva = reservas[0]
        self.assertIsInstance(reserva.servicio, SalaCorporativa)
        self.assertEqual(reserva.servicio.nombre, "Sala Pequeña")
        self.assertEqual(reserva.servicio.capacidad, 40)
        self.assertEqual(reserva.duracion, 2)
        self.assertEqual(reserva.hora, "20:00")
        self.assertEqual(reserva.estado, Reserva.ESTADO_PENDIENTE)
        self.assertAlmostEqual(reserva.calcular_costo(), 200000)

    def test_reservar_combo_mantiene_el_precio_fijo(self):
        """El combo conserva su tarifa fija y su jornada de ocho horas."""
        cliente = crear_cliente()
        reservas = []
        entradas = ["1", fecha_futura(), "20:00", "1"]

        with patch("builtins.input", side_effect=entradas):
            with redirect_stdout(StringIO()):
                main.reservar_combo(cliente, reservas)

        reserva = reservas[0]
        self.assertIsInstance(reserva.servicio, ComboEquipos)
        self.assertEqual(reserva.servicio.nombre, "Reunión empresarial")
        self.assertEqual(reserva.duracion, 8)
        self.assertEqual(reserva.estado, Reserva.ESTADO_CONFIRMADA)
        self.assertAlmostEqual(reserva.calcular_costo(), 160000)

    def test_reservar_asesoria_cobra_una_sesion(self):
        """La asesoría cobra una tarifa fija por sesión."""
        cliente = crear_cliente()
        reservas = []
        entradas = ["2", fecha_futura(), "08:00", "2"]

        with patch("builtins.input", side_effect=entradas):
            with redirect_stdout(StringIO()):
                main.reservar_asesoria(cliente, reservas)

        reserva = reservas[0]
        self.assertEqual(reserva.servicio.nombre, "Infraestructura tecnológica y seguridad informática")
        self.assertIsNone(reserva.duracion)
        self.assertEqual(reserva.estado, Reserva.ESTADO_CANCELADA)
        self.assertAlmostEqual(reserva.calcular_costo(), 180000)

    def test_consultar_reservas_permite_cancelar_una_existente(self):
        """Las reservas registradas se pueden gestionar posteriormente."""
        cliente = crear_cliente()
        sala = obtener_salas()[0]
        reserva = Reserva(cliente, sala, fecha_futura(), "10:00")
        reservas = [reserva]

        with patch("builtins.input", side_effect=["1", "2"]):
            with redirect_stdout(StringIO()):
                main.consultar_reservas(reservas)

        self.assertEqual(reserva.estado, Reserva.ESTADO_CANCELADA)

    def test_gestionar_reserva_por_codigo(self):
        """Una reserva se puede buscar y gestionar usando su código."""
        reservas = crear_reservas_de_prueba()
        self.assertEqual(reservas[1].codigo_reserva, "RES-002")

        with patch("builtins.input", side_effect=["RES-002", "2"]):
            with redirect_stdout(StringIO()):
                main.consultar_reservas(reservas)

        self.assertEqual(reservas[0].estado, Reserva.ESTADO_PENDIENTE)
        self.assertEqual(reservas[1].estado, Reserva.ESTADO_CANCELADA)

    def test_gestionar_reserva_por_posicion(self):
        """Una reserva se puede buscar y gestionar usando su posición."""
        reservas = crear_reservas_de_prueba()

        with patch("builtins.input", side_effect=["2", "2"]):
            with redirect_stdout(StringIO()):
                main.consultar_reservas(reservas)

        self.assertEqual(reservas[0].estado, Reserva.ESTADO_PENDIENTE)
        self.assertEqual(reservas[1].estado, Reserva.ESTADO_CANCELADA)

    def test_codigo_de_reserva_inexistente(self):
        """Se informa cuando el código o la posición no existen."""
        reservas = crear_reservas_de_prueba()

        with patch("builtins.input", side_effect=["RES-999"]):
            with redirect_stdout(StringIO()) as salida:
                main.consultar_reservas(reservas)

        self.assertIn("No existe una reserva", salida.getvalue())
        self.assertEqual(reservas[0].estado, Reserva.ESTADO_PENDIENTE)
        self.assertEqual(reservas[1].estado, Reserva.ESTADO_PENDIENTE)

    def test_enter_regresa_al_menu_sin_errores(self):
        """Presionar Enter regresa al menú sin modificar las reservas."""
        reservas = crear_reservas_de_prueba()

        with patch("builtins.input", side_effect=[""]):
            with redirect_stdout(StringIO()) as salida:
                main.consultar_reservas(reservas)

        self.assertNotIn("No existe una reserva", salida.getvalue())
        self.assertEqual(reservas[0].estado, Reserva.ESTADO_PENDIENTE)
        self.assertEqual(reservas[1].estado, Reserva.ESTADO_PENDIENTE)

    def test_rechaza_fecha_invalida_y_permite_reintentar(self):
        """Una fecha inválida no cierra el programa y se puede corregir."""
        cliente = crear_cliente()
        reservas = []
        entradas = [
            "10",
            "1",
            "fecha incorrecta",
            "8:00 AM",
            fecha_futura(),
            "8:00 AM",
            "3",
        ]

        with patch("builtins.input", side_effect=entradas):
            with redirect_stdout(StringIO()):
                main.reservar_sala(cliente, reservas)

        self.assertEqual(len(reservas), 1)
        self.assertEqual(reservas[0].estado, Reserva.ESTADO_PENDIENTE)


class TestInicioPrograma(unittest.TestCase):
    """Comprueba que el programa pueda iniciar y salir correctamente."""

    def test_main_muestra_el_menu_y_termina(self):
        """La opción Salir cierra el menú sin errores."""
        with patch("builtins.input", side_effect=["5"]):
            with redirect_stdout(StringIO()) as salida:
                main.main()

        self.assertIn("Software FJ", salida.getvalue())
        self.assertIn("Gracias por usar el sistema", salida.getvalue())

    def test_opcion_invalida_no_cierra_el_programa(self):
        """Una opción incorrecta permite volver a intentarlo."""
        with patch("builtins.input", side_effect=["9", "5"]):
            with redirect_stdout(StringIO()) as salida:
                main.main()

        self.assertIn("Opción no válida", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
