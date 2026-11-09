# Configuramos el archivo donde se guardarán los eventos y errores del sistema. acompañado de un formato que incluya la fecha, la hora, el nivel de severidad y el mensaje del evento o error.
import logging 
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/eventos.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO)