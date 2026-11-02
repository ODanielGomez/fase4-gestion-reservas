"""Pruebas automatizadas para los servicios de Software FJ."""

import unittest

from excepciones import DatoInvalidoError, ServicioNoDisponibleError
from servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala, Servicio


class BasePruebas(unittest.TestCase):
    """Agrupa ayudas que usan varias pruebas."""

    def comprobar_error(self, tipo_error, mensaje, funcion):
        """Ejecuta una acción y comprueba el tipo y el mensaje del error."""
        with self.assertRaises(tipo_error) as contexto:
            funcion()
        self.assertEqual(str(contexto.exception), mensaje)


class TestServicioAbstracto(BasePruebas):
    """Comprueba la abstracción y la herencia de los servicios."""

    def test_no_se_puede_instanciar_servicio(self):
        """La clase Servicio es abstracta y no permite crear objetos."""
        with self.assertRaises(TypeError):
            Servicio("Servicio genérico", 100)

    def test_las_subclases_heredan_de_servicio(self):
        """Los tres servicios especializados heredan de Servicio."""
        clases = (ReservaSala, AlquilerEquipo, AsesoriaEspecializada)
        for clase in clases:
            with self.subTest(clase=clase.__name__):
                self.assertTrue(issubclass(clase, Servicio))


class TestCreacionServicios(unittest.TestCase):
    """Comprueba que los servicios se creen con los datos correctos."""

    def test_crear_reserva_sala_con_datos_validos(self):
        """Una sala guarda su nombre, tarifa, horas, impuesto y descuento."""
        sala = ReservaSala("Sala A", 100, horas=2, impuesto=19, descuento=10)
        self.assertEqual(sala.nombre, "Sala A")
        self.assertEqual(sala.tarifa_base, 100)
        self.assertEqual(sala.horas, 2)
        self.assertEqual(sala.impuesto, 19)
        self.assertEqual(sala.descuento, 10)
        self.assertTrue(sala.disponible)

    def test_crear_alquiler_equipo_con_datos_validos(self):
        """Un alquiler guarda su nombre, tarifa y cantidad de equipos."""
        equipo = AlquilerEquipo("Portátil", 50, cantidad=3, impuesto=10, descuento=5)
        self.assertEqual(equipo.nombre, "Portátil")
        self.assertEqual(equipo.tarifa_base, 50)
        self.assertEqual(equipo.cantidad, 3)
        self.assertEqual(equipo.impuesto, 10)
        self.assertEqual(equipo.descuento, 5)
        self.assertTrue(equipo.disponible)

    def test_crear_asesoria_con_datos_validos(self):
        """Una asesoría guarda su nombre y tarifa base."""
        asesoria = AsesoriaEspecializada("Asesoría en redes", 200)
        self.assertEqual(asesoria.nombre, "Asesoría en redes")
        self.assertEqual(asesoria.tarifa_base, 200)
        self.assertTrue(asesoria.disponible)

    def test_valores_por_defecto(self):
        """Sin datos opcionales, el impuesto y el descuento son cero."""
        asesoria = AsesoriaEspecializada("Asesoría", 200)
        self.assertEqual(asesoria.impuesto, 0)
        self.assertEqual(asesoria.descuento, 0)
        self.assertTrue(asesoria.disponible)

    def test_nombre_se_guarda_sin_espacios_extremos(self):
        """El nombre se limpia para evitar espacios al inicio y al final."""
        sala = ReservaSala("  Sala A  ", 100)
        self.assertEqual(sala.nombre, "Sala A")

    def test_propiedades_son_solo_lectura(self):
        """Los datos principales no se pueden cambiar directamente."""
        sala = ReservaSala("Sala A", 100, horas=2)
        equipo = AlquilerEquipo("Portátil", 50, cantidad=1)

        propiedades = (
            (sala, "nombre"),
            (sala, "tarifa_base"),
            (sala, "impuesto"),
            (sala, "descuento"),
            (sala, "disponible"),
            (sala, "horas"),
            (equipo, "cantidad"),
        )

        for servicio, propiedad in propiedades:
            with self.subTest(propiedad=propiedad):
                with self.assertRaises(AttributeError):
                    setattr(servicio, propiedad, "otro valor")


class TestValidaciones(BasePruebas):
    """Comprueba los datos inválidos y sus mensajes."""

    def test_nombre_invalido(self):
        """El nombre no puede estar vacío ni faltar."""
        casos = (
            ("vacío", ""),
            ("solo espacios", "   "),
            ("nulo", None),
            ("número", 123),
        )

        for descripcion, nombre in casos:
            with self.subTest(caso=descripcion):
                self.comprobar_error(
                    DatoInvalidoError,
                    "El nombre del servicio no puede estar vacío.",
                    lambda nombre=nombre: AsesoriaEspecializada(nombre, 100),
                )

    def test_tarifa_base_invalida(self):
        """La tarifa debe ser un número y no puede ser negativa."""
        casos = (
            (
                "texto",
                lambda: AsesoriaEspecializada("Asesoría", "100"),
                "La tarifa base debe ser un número.",
            ),
            (
                "booleano",
                lambda: AsesoriaEspecializada("Asesoría", True),
                "La tarifa base debe ser un número.",
            ),
            (
                "negativa",
                lambda: AsesoriaEspecializada("Asesoría", -1),
                "La tarifa base no puede ser negativa.",
            ),
        )

        for descripcion, funcion, mensaje in casos:
            with self.subTest(caso=descripcion):
                self.comprobar_error(DatoInvalidoError, mensaje, funcion)

    def test_impuesto_invalido(self):
        """El impuesto debe ser un número entre 0 y 100."""
        casos = (
            (
                "texto",
                lambda: AsesoriaEspecializada("Asesoría", 100, impuesto="19"),
                "El impuesto debe ser un número.",
            ),
            (
                "negativo",
                lambda: AsesoriaEspecializada("Asesoría", 100, impuesto=-1),
                "El impuesto debe estar entre 0 y 100.",
            ),
            (
                "mayor a 100",
                lambda: AsesoriaEspecializada("Asesoría", 100, impuesto=101),
                "El impuesto debe estar entre 0 y 100.",
            ),
        )

        for descripcion, funcion, mensaje in casos:
            with self.subTest(caso=descripcion):
                self.comprobar_error(DatoInvalidoError, mensaje, funcion)

    def test_descuento_invalido(self):
        """El descuento debe ser un número entre 0 y 100."""
        casos = (
            (
                "texto",
                lambda: AsesoriaEspecializada("Asesoría", 100, descuento="10"),
                "El descuento debe ser un número.",
            ),
            (
                "negativo",
                lambda: AsesoriaEspecializada("Asesoría", 100, descuento=-1),
                "El descuento debe estar entre 0 y 100.",
            ),
            (
                "mayor a 100",
                lambda: AsesoriaEspecializada("Asesoría", 100, descuento=101),
                "El descuento debe estar entre 0 y 100.",
            ),
        )

        for descripcion, funcion, mensaje in casos:
            with self.subTest(caso=descripcion):
                self.comprobar_error(DatoInvalidoError, mensaje, funcion)

    def test_horas_invalidas(self):
        """Las horas de la sala deben ser un número mayor que cero."""
        casos = (
            (
                "texto",
                lambda: ReservaSala("Sala A", 100, horas="2"),
                "Las horas de la sala deben ser un número.",
            ),
            (
                "booleano",
                lambda: ReservaSala("Sala A", 100, horas=True),
                "Las horas de la sala deben ser un número.",
            ),
            (
                "cero",
                lambda: ReservaSala("Sala A", 100, horas=0),
                "Las horas de la sala deben ser mayores que cero.",
            ),
            (
                "negativo",
                lambda: ReservaSala("Sala A", 100, horas=-1),
                "Las horas de la sala deben ser mayores que cero.",
            ),
        )

        for descripcion, funcion, mensaje in casos:
            with self.subTest(caso=descripcion):
                self.comprobar_error(DatoInvalidoError, mensaje, funcion)

    def test_cantidad_invalida(self):
        """La cantidad de equipos debe ser un entero mayor que cero."""
        casos = (
            (
                "decimal",
                lambda: AlquilerEquipo("Portátil", 50, cantidad=1.5),
                "La cantidad de equipos debe ser un número entero.",
            ),
            (
                "texto",
                lambda: AlquilerEquipo("Portátil", 50, cantidad="3"),
                "La cantidad de equipos debe ser un número entero.",
            ),
            (
                "booleano",
                lambda: AlquilerEquipo("Portátil", 50, cantidad=True),
                "La cantidad de equipos debe ser un número entero.",
            ),
            (
                "cero",
                lambda: AlquilerEquipo("Portátil", 50, cantidad=0),
                "La cantidad de equipos debe ser mayor que cero.",
            ),
            (
                "negativa",
                lambda: AlquilerEquipo("Portátil", 50, cantidad=-1),
                "La cantidad de equipos debe ser mayor que cero.",
            ),
        )

        for descripcion, funcion, mensaje in casos:
            with self.subTest(caso=descripcion):
                self.comprobar_error(DatoInvalidoError, mensaje, funcion)

    def test_disponibilidad_invalida(self):
        """La disponibilidad solo acepta verdadero o falso."""
        casos = ("sí", 1, None)

        for valor in casos:
            with self.subTest(valor=valor):
                self.comprobar_error(
                    DatoInvalidoError,
                    "La disponibilidad debe ser verdadera o falsa.",
                    lambda valor=valor: AsesoriaEspecializada(
                        "Asesoría", 100, disponible=valor
                    ),
                )


class TestCalculosCosto(unittest.TestCase):
    """Comprueba el costo base de cada tipo de servicio."""

    def test_costo_base_reserva_sala(self):
        """La sala cobra la tarifa base multiplicada por las horas."""
        sala = ReservaSala("Sala A", 100, horas=2)
        self.assertEqual(sala.calcular_costo_base(), 200)

    def test_costo_base_reserva_sala_con_horas_fraccionarias(self):
        """La sala permite horas con decimales."""
        sala = ReservaSala("Sala A", 100, horas=1.5)
        self.assertEqual(sala.calcular_costo_base(), 150)

    def test_costo_base_alquiler_equipo(self):
        """El equipo cobra la tarifa base multiplicada por la cantidad."""
        equipo = AlquilerEquipo("Portátil", 50, cantidad=3)
        self.assertEqual(equipo.calcular_costo_base(), 150)

    def test_costo_base_asesoria(self):
        """La asesoría cobra un valor fijo por sesión."""
        asesoria = AsesoriaEspecializada("Asesoría", 200)
        self.assertEqual(asesoria.calcular_costo_base(), 200)

    def test_costo_con_tarifa_cero(self):
        """Una tarifa de cero produce un costo de cero."""
        asesoria = AsesoriaEspecializada("Asesoría gratuita", 0)
        self.assertEqual(asesoria.calcular_costo(), 0)


class TestImpuestosYDescuentos(unittest.TestCase):
    """Comprueba la fórmula actual: impuesto y descuento sobre el costo base."""

    def test_descuento_sala(self):
        """El descuento se calcula sobre el costo base."""
        sala = ReservaSala("Sala A", 100, horas=2, descuento=10)
        self.assertAlmostEqual(sala.calcular_descuento(), 20)

    def test_impuesto_sala_sobre_la_base(self):
        """El impuesto se calcula sobre el costo base, no sobre el descuento."""
        sala = ReservaSala("Sala A", 100, horas=2, impuesto=19, descuento=10)
        self.assertAlmostEqual(sala.calcular_impuesto(), 38)

    def test_costo_total_sala_con_impuesto_y_descuento_sobre_la_base(self):
        """La sala suma el impuesto y resta el descuento sobre el costo base."""
        sala = ReservaSala("Sala A", 100, horas=2, impuesto=19, descuento=10)
        self.assertAlmostEqual(sala.calcular_costo(), 218)

    def test_costo_total_equipo_con_impuesto_y_descuento_sobre_la_base(self):
        """El equipo suma el impuesto y resta el descuento sobre el costo base."""
        equipo = AlquilerEquipo("Portátil", 50, cantidad=3, impuesto=10, descuento=5)
        self.assertAlmostEqual(equipo.calcular_costo(), 157.50)

    def test_costo_asesoria_con_impuesto(self):
        """La asesoría aplica el impuesto sobre su valor fijo."""
        asesoria = AsesoriaEspecializada("Asesoría", 200, impuesto=19)
        self.assertAlmostEqual(asesoria.calcular_costo(), 238)

    def test_costo_sin_impuesto_ni_descuento(self):
        """Sin impuesto ni descuento, el total es igual al costo base."""
        asesoria = AsesoriaEspecializada("Asesoría", 200)
        self.assertAlmostEqual(asesoria.calcular_costo(), 200)

    def test_costo_con_impuesto_al_cien(self):
        """Un impuesto del 100 % duplica el costo base."""
        asesoria = AsesoriaEspecializada("Asesoría", 200, impuesto=100)
        self.assertAlmostEqual(asesoria.calcular_costo(), 400)

    def test_costo_con_impuesto_y_descuento_al_cien(self):
        """Con impuesto y descuento del 100 % el total vuelve al costo base."""
        asesoria = AsesoriaEspecializada(
            "Asesoría", 200, impuesto=100, descuento=100
        )
        self.assertAlmostEqual(asesoria.calcular_costo(), 200)

    def test_redondeo_a_dos_decimales(self):
        """El total se redondea a dos decimales."""
        asesoria = AsesoriaEspecializada(
            "Asesoría", 100.005, impuesto=19, descuento=10
        )
        self.assertAlmostEqual(asesoria.calcular_costo(), 109.01)


class TestValoresLimite(unittest.TestCase):
    """Comprueba los valores permitidos en los extremos."""

    def test_tarifa_cero_permitida(self):
        """La tarifa cero es válida."""
        servicio = AsesoriaEspecializada("Asesoría", 0)
        self.assertEqual(servicio.tarifa_base, 0)

    def test_horas_minimas_positivas(self):
        """Una fracción positiva de hora es válida."""
        sala = ReservaSala("Sala A", 100, horas=0.5)
        self.assertEqual(sala.calcular_costo_base(), 50)

    def test_cantidad_minima(self):
        """Una unidad es la cantidad mínima permitida."""
        equipo = AlquilerEquipo("Portátil", 50, cantidad=1)
        self.assertEqual(equipo.calcular_costo_base(), 50)

    def test_impuesto_cero_y_cien_permitidos(self):
        """El impuesto acepta los valores 0 y 100."""
        sin_impuesto = AsesoriaEspecializada("Asesoría", 100, impuesto=0)
        con_impuesto = AsesoriaEspecializada("Asesoría", 100, impuesto=100)
        self.assertEqual(sin_impuesto.impuesto, 0)
        self.assertEqual(con_impuesto.impuesto, 100)

    def test_descuento_cero_y_cien_permitidos(self):
        """El descuento acepta los valores 0 y 100."""
        sin_descuento = AsesoriaEspecializada("Asesoría", 100, descuento=0)
        con_descuento = AsesoriaEspecializada("Asesoría", 100, descuento=100)
        self.assertEqual(sin_descuento.descuento, 0)
        self.assertEqual(con_descuento.descuento, 100)


class TestDisponibilidad(BasePruebas):
    """Comprueba si un servicio se puede usar o no."""

    def test_servicio_disponible_por_defecto(self):
        """Todo servicio nuevo está disponible."""
        sala = ReservaSala("Sala A", 100)
        self.assertTrue(sala.disponible)

    def test_validar_servicio_disponible_no_lanza_error(self):
        """Un servicio disponible se puede usar sin problemas."""
        sala = ReservaSala("Sala A", 100)
        sala.validar_disponibilidad()

    def test_desactivar_servicio(self):
        """El servicio se puede marcar como no disponible."""
        sala = ReservaSala("Sala A", 100)
        sala.establecer_disponibilidad(False)
        self.assertFalse(sala.disponible)

    def test_servicio_no_disponible_lanza_error(self):
        """Un servicio no disponible no se puede usar."""
        sala = ReservaSala("Sala A", 100)
        sala.establecer_disponibilidad(False)
        self.comprobar_error(
            ServicioNoDisponibleError,
            "El servicio 'Sala A' no está disponible en este momento.",
            sala.validar_disponibilidad,
        )

    def test_reactivar_servicio(self):
        """Un servicio desactivado se puede volver a activar."""
        sala = ReservaSala("Sala A", 100)
        sala.establecer_disponibilidad(False)
        sala.establecer_disponibilidad(True)
        self.assertTrue(sala.disponible)
        sala.validar_disponibilidad()

    def test_disponibilidad_independiente_entre_instancias(self):
        """Cambiar un servicio no afecta a los demás."""
        sala_uno = ReservaSala("Sala A", 100)
        sala_dos = ReservaSala("Sala B", 100)
        sala_uno.establecer_disponibilidad(False)
        self.assertFalse(sala_uno.disponible)
        self.assertTrue(sala_dos.disponible)


class TestExcepcionesPersonalizadas(BasePruebas):
    """Comprueba que se usen las excepciones del proyecto."""

    def test_dato_invalido_usa_excepcion_personalizada(self):
        """Los datos incorrectos usan DatoInvalidoError, no un error genérico."""
        with self.assertRaises(DatoInvalidoError):
            AsesoriaEspecializada("", 100)

    def test_servicio_no_disponible_usa_excepcion_personalizada(self):
        """La falta de disponibilidad usa ServicioNoDisponibleError."""
        sala = ReservaSala("Sala A", 100)
        sala.establecer_disponibilidad(False)
        with self.assertRaises(ServicioNoDisponibleError) as contexto:
            sala.validar_disponibilidad()
        self.assertEqual(
            str(contexto.exception),
            "El servicio 'Sala A' no está disponible en este momento.",
        )


if __name__ == "__main__":
    unittest.main()
