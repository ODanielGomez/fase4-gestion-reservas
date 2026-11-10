"""Pruebas de la ubicación y creación automática del archivo de logs."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import configuracion_logs


class TestRutaDeLogs(unittest.TestCase):
    """Comprueba que los logs no dependan del directorio de ejecución."""

    def test_ruta_de_logs_es_absoluta_y_esta_en_el_proyecto(self):
        """La carpeta y el archivo de logs se calculan desde el módulo."""
        self.assertTrue(os.path.isabs(configuracion_logs.DIRECTORIO_LOGS))
        self.assertTrue(os.path.isabs(configuracion_logs.ARCHIVO_EVENTOS))
        self.assertEqual(
            configuracion_logs.DIRECTORIO_LOGS,
            os.path.join(
                os.path.dirname(os.path.abspath(configuracion_logs.__file__)),
                "logs",
            ),
        )
        self.assertEqual(
            configuracion_logs.ARCHIVO_EVENTOS,
            os.path.join(configuracion_logs.DIRECTORIO_LOGS, "eventos.log"),
        )

    def test_crea_logs_junto_al_modulo_aunque_se_ejecute_desde_otro_directorio(self):
        """Una instalación nueva crea la carpeta y escribe sin depender del CWD."""
        with tempfile.TemporaryDirectory() as temporal:
            proyecto_nuevo = os.path.join(temporal, "proyecto_nuevo")
            otro_directorio = os.path.join(temporal, "otro_directorio")
            os.makedirs(proyecto_nuevo)
            os.makedirs(otro_directorio)

            shutil.copy(
                os.path.join(
                    os.path.dirname(os.path.abspath(configuracion_logs.__file__)),
                    "configuracion_logs.py",
                ),
                os.path.join(proyecto_nuevo, "configuracion_logs.py"),
            )

            mensaje = "evento generado desde otro directorio"
            codigo = (
                "import sys; "
                f"sys.path.insert(0, {proyecto_nuevo!r}); "
                "import configuracion_logs, logging; "
                f"logging.info({mensaje!r})"
            )

            resultado = subprocess.run(
                [sys.executable, "-c", codigo],
                cwd=otro_directorio,
                capture_output=True,
                text=True,
            )

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertFalse(
                os.path.exists(os.path.join(otro_directorio, "logs")),
                "Los logs no deben crearse en el directorio de ejecución.",
            )

            archivo = os.path.join(proyecto_nuevo, "logs", "eventos.log")
            self.assertTrue(os.path.exists(archivo))
            with open(archivo, encoding="utf-8") as registro:
                self.assertIn(mensaje, registro.read())


if __name__ == "__main__":
    unittest.main()
