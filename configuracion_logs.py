# Configuramos el archivo donde se guardarán los eventos y errores del sistema. acompañado de un formato que incluya la fecha, la hora, el nivel de severidad y el mensaje del evento o error.
import logging 
import os

# Calculamos la carpeta del proyecto a partir de la ubicación de este archivo.
# Así la ruta de los logs no depende del directorio desde el que se ejecute el programa.
DIRECTORIO_PROYECTO = os.path.dirname(os.path.abspath(__file__))
DIRECTORIO_LOGS = os.path.join(DIRECTORIO_PROYECTO, "logs")
ARCHIVO_EVENTOS = os.path.join(DIRECTORIO_LOGS, "eventos.log")

os.makedirs(DIRECTORIO_LOGS, exist_ok=True)

logging.basicConfig(
    filename=ARCHIVO_EVENTOS,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO)