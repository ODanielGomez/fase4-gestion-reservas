"""Pruebas automatizadas para el catálogo de servicios de Software FJ."""

import unittest
from datetime import datetime, timedelta

from catalogo_servicios import (
    CAPACIDAD_MAXIMA_SALAS,
    obtener_asesoria,
    obtener_asesorias,
    obtener_combo,
    obtener_combos,
    obtener_salas,
    obtener_todos_los_servicios,
    seleccionar_sala,
)
from cliente import Cliente
from excepciones import DatoInvalidoError, ServicioNoDisponibleError
from reserva import Reserva
from servicio import (
    AsesoriaEspecializada,
    ComboEquipos,
    SalaCorporativa,
    Servicio,
)


def fecha_futura(dias=10):
    """Devuelve una fecha futura para que las pruebas no caduquen."""
    return (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")


def crear_cliente():
    """Crea un cliente válido para las pruebas de integración."""
    return Cliente("Ana Pérez", "CC", "1234567890")


class TestCatalogoSalas(unittest.TestCase):
    """Comprueba las salas, su selección automática y sus costos."""

    def test_existen_las_tres_salas_del_catalogo(self):
        """El catálogo conserva nombre, capacidad, descripción y tarifa."""
        salas = {sala.nombre: sala for sala in obtener_salas()}

        self.assertEqual(len(salas), 3)
        self.assertEqual(salas["Sala Pequeña"].capacidad, 40)
        self.assertEqual(salas["Sala Pequeña"].tarifa_base, 100000)
        self.assertIn("reuniones", salas["Sala Pequeña"].descripcion.lower())

        self.assertEqual(salas["Sala Mediana"].capacidad, 80)
        self.assertEqual(salas["Sala Mediana"].tarifa_base, 160000)
        self.assertIn("capacitaciones", salas["Sala Mediana"].descripcion.lower())

        self.assertEqual(salas["Sala Grande"].capacidad, 200)
        self.assertEqual(salas["Sala Grande"].tarifa_base, 200000)
        self.assertIn("eventos", salas["Sala Grande"].descripcion.lower())

    def test_seleccion_en_los_limites_de_capacidad(self):
        """La sala más pequeña se elige según los límites acordados."""
        casos = (
            (1, "Sala Pequeña", 40),
            (40, "Sala Pequeña", 40),
            (41, "Sala Mediana", 80),
            (80, "Sala Mediana", 80),
            (81, "Sala Grande", 200),
            (200, "Sala Grande", 200),
        )

        for asistentes, nombre, capacidad in casos:
            with self.subTest(asistentes=asistentes):
                sala = seleccionar_sala(asistentes)
                self.assertIsInstance(sala, SalaCorporativa)
                self.assertEqual(sala.nombre, nombre)
                self.assertEqual(sala.capacidad, capacidad)

    def test_rechaza_asistentes_invalidos(self):
        """No se aceptan cero, negativos ni valores que no sean enteros."""
        casos = ("40", None, True, 0, -1, 40.5)

        for asistentes in casos:
            with self.subTest(asistentes=asistentes):
                with self.assertRaises(DatoInvalidoError):
                    seleccionar_sala(asistentes)

    def test_rechaza_mas_de_doscientos_asistentes(self):
        """La capacidad máxima del catálogo es de 200 personas."""
        with self.assertRaises(DatoInvalidoError) as contexto:
            seleccionar_sala(CAPACIDAD_MAXIMA_SALAS + 1)

        self.assertEqual(
            str(contexto.exception),
            "No hay salas disponibles para más de 200 asistentes.",
        )

    def test_costo_de_sala_segun_las_horas(self):
        """El costo de la sala conserva el cálculo por horas."""
        casos = (
            (10, 3, 300000),
            (50, 2, 320000),
            (100, 1, 200000),
        )

        for asistentes, horas, costo_esperado in casos:
            with self.subTest(asistentes=asistentes, horas=horas):
                sala = seleccionar_sala(asistentes, horas=horas)
                self.assertAlmostEqual(sala.calcular_costo(), costo_esperado)

    def test_salas_del_catalogo_no_tienen_impuesto_ni_descuento(self):
        """En esta versión los servicios se crean sin impuesto ni descuento."""
        for sala in obtener_salas():
            with self.subTest(sala=sala.nombre):
                self.assertEqual(sala.impuesto, 0)
                self.assertEqual(sala.descuento, 0)

    def test_sala_no_disponible_es_rechazada_por_la_reserva(self):
        """La disponibilidad del catálogo sigue funcionando con Reserva."""
        sala = seleccionar_sala(10, disponible=False)

        with self.assertRaises(ServicioNoDisponibleError):
            Reserva(crear_cliente(), sala, fecha_futura(), "10:30")


class TestCatalogoCombos(unittest.TestCase):
    """Comprueba los combos cerrados de equipos y su tarifa fija."""

    def test_existen_los_tres_combos(self):
        """El catálogo contiene los combos acordados."""
        nombres = {combo.nombre for combo in obtener_combos()}

        self.assertEqual(
            nombres,
            {
                "Reunión empresarial",
                "Capacitación empresarial",
                "Evento corporativo",
            },
        )

    def test_componentes_y_cantidades_de_cada_combo(self):
        """Cada combo registra claramente sus equipos y cantidades."""
        combos = {combo.nombre: combo for combo in obtener_combos()}

        self.assertEqual(
            combos["Reunión empresarial"].componentes,
            {
                "Computador portátil": 1,
                "Equipo de videoconferencia": 1,
            },
        )
        self.assertEqual(
            combos["Capacitación empresarial"].componentes,
            {
                "Computador portátil": 1,
                "Video beam": 1,
                "Sistema de sonido": 1,
            },
        )
        self.assertEqual(
            combos["Evento corporativo"].componentes,
            {
                "Computador portátil": 2,
                "Video beam": 1,
                "Sistema de sonido": 1,
                "Equipo de videoconferencia": 1,
            },
        )

    def test_precio_total_de_cada_combo(self):
        """La tarifa del combo es un precio total por jornada."""
        costos_esperados = {
            "Reunión empresarial": 160000,
            "Capacitación empresarial": 300000,
            "Evento corporativo": 450000,
        }

        for combo in obtener_combos():
            with self.subTest(combo=combo.nombre):
                self.assertAlmostEqual(
                    combo.calcular_costo(), costos_esperados[combo.nombre]
                )

    def test_la_tarifa_no_se_multiplica_por_los_equipos(self):
        """El precio del combo no se multiplica por la cantidad de equipos."""
        for combo in obtener_combos():
            with self.subTest(combo=combo.nombre):
                total_equipos = sum(combo.componentes.values())
                self.assertGreater(total_equipos, 1)
                self.assertNotEqual(
                    combo.calcular_costo(), combo.tarifa_base * total_equipos
                )

    def test_jornada_de_ocho_horas(self):
        """Todos los combos corresponden a una jornada de ocho horas."""
        for combo in obtener_combos():
            with self.subTest(combo=combo.nombre):
                self.assertEqual(combo.jornada_horas, 8)
                self.assertEqual(combo.horas, 8)

    def test_los_combos_son_servicios_del_catalogo(self):
        """Los combos son objetos compatibles con Servicio."""
        for combo in obtener_combos():
            with self.subTest(combo=combo.nombre):
                self.assertIsInstance(combo, Servicio)
                self.assertIsInstance(combo, ComboEquipos)
                self.assertEqual(combo.impuesto, 0)
                self.assertEqual(combo.descuento, 0)

    def test_los_componentes_no_se_pueden_modificar_desde_afuera(self):
        """La propiedad componentes devuelve una copia de los datos."""
        combo = obtener_combo("Reunión empresarial")
        componentes = combo.componentes
        componentes["Equipo adicional"] = 1

        self.assertNotIn("Equipo adicional", combo.componentes)

    def test_buscar_un_combo_inexistente(self):
        """Se informa cuando el combo solicitado no existe."""
        with self.assertRaises(DatoInvalidoError):
            obtener_combo("Combo inexistente")

    def test_combo_no_disponible_es_rechazado_por_la_reserva(self):
        """La disponibilidad del combo se valida al crear la reserva."""
        combo = obtener_combo("Reunión empresarial", disponible=False)

        with self.assertRaises(ServicioNoDisponibleError):
            Reserva(crear_cliente(), combo, fecha_futura(), "10:30")


class TestCatalogoAsesorias(unittest.TestCase):
    """Comprueba las asesorías, sus tarifas y su uso con Reserva."""

    def test_existen_las_tres_asesorias(self):
        """El catálogo contiene las asesorías acordadas."""
        asesorias = {asesoria.nombre: asesoria for asesoria in obtener_asesorias()}

        self.assertEqual(len(asesorias), 3)
        self.assertEqual(
            asesorias["Desarrollo de software"].tarifa_base, 150000
        )
        self.assertEqual(
            asesorias[
                "Infraestructura tecnológica y seguridad informática"
            ].tarifa_base,
            180000,
        )
        self.assertEqual(
            asesorias[
                "Transformación digital y automatización"
            ].tarifa_base,
            160000,
        )

    def test_costo_de_cada_asesoria(self):
        """Cada asesoría cobra una tarifa fija por sesión."""
        costos_esperados = {
            "Desarrollo de software": 150000,
            "Infraestructura tecnológica y seguridad informática": 180000,
            "Transformación digital y automatización": 160000,
        }

        for asesoria in obtener_asesorias():
            with self.subTest(asesoria=asesoria.nombre):
                self.assertIsInstance(asesoria, AsesoriaEspecializada)
                self.assertAlmostEqual(
                    asesoria.calcular_costo(), costos_esperados[asesoria.nombre]
                )

    def test_buscar_una_asesoria_inexistente(self):
        """Se informa cuando la asesoría solicitada no existe."""
        with self.assertRaises(DatoInvalidoError):
            obtener_asesoria("Asesoría inexistente")


class TestIntegracionCatalogo(unittest.TestCase):
    """Comprueba que todo el catálogo sea compatible con Reserva."""

    def test_todos_los_servicios_heredan_de_servicio(self):
        """Salas, combos y asesorías son compatibles con la clase abstracta."""
        servicios = obtener_todos_los_servicios()

        self.assertEqual(len(servicios), 9)
        for servicio in servicios:
            with self.subTest(servicio=servicio.nombre):
                self.assertIsInstance(servicio, Servicio)

    def test_una_sala_del_catalogo_puede_reservarse(self):
        """Una sala seleccionada automáticamente se usa en una reserva."""
        sala = seleccionar_sala(75, horas=2)
        reserva = Reserva(crear_cliente(), sala, fecha_futura(), "10:30")

        self.assertAlmostEqual(reserva.calcular_costo(), 320000)
        self.assertEqual(reserva.duracion, 2)

    def test_un_combo_del_catalogo_puede_reservarse(self):
        """Un combo conserva su precio fijo al integrarse con Reserva."""
        combo = obtener_combo("Evento corporativo")
        reserva = Reserva(crear_cliente(), combo, fecha_futura(), "10:30")

        self.assertAlmostEqual(reserva.calcular_costo(), 450000)
        self.assertEqual(reserva.duracion, 8)

    def test_una_asesoria_del_catalogo_puede_reservarse(self):
        """Una asesoría conserva su tarifa al integrarse con Reserva."""
        asesoria = obtener_asesoria("Desarrollo de software")
        reserva = Reserva(crear_cliente(), asesoria, fecha_futura(), "10:30")

        self.assertAlmostEqual(reserva.calcular_costo(), 150000)


if __name__ == "__main__":
    unittest.main()
