# Software FJ - Sistema de Gestión de Clientes, Servicios y Reservas

Proyecto académico desarrollado para la Fase 4 - Prácticas simuladas del curso
Programación de la UNAD.

## Descripción del proyecto

Software FJ es una empresa dedicada a la prestación de servicios corporativos.
Este sistema permite registrar clientes, consultar un catálogo de servicios y
gestionar reservas de salas corporativas, combos de equipos y asesorías
especializadas.

La aplicación está desarrollada en Python y aplica conceptos de programación
orientada a objetos:

- Abstracción.
- Herencia.
- Encapsulamiento.
- Polimorfismo.

## Objetivo del sistema

Desarrollar una aplicación en Python para gestionar clientes, servicios y
reservas, aplicando programación orientada a objetos, validaciones, excepciones
personalizadas y registro de eventos.

## Integrantes del equipo

- Omar Daniel Gómez
- Sandra Carvajal
- [Integrante 3]
- [Integrante 4]
- [Integrante 5]

## Funcionalidades implementadas

### Gestión de clientes

- Registro de clientes.
- Validación del nombre, tipo y número de identificación.
- Validación del número de identificación para aceptar únicamente dígitos.
- Reutilización del cliente registrado durante una misma ejecución.

### Catálogo de servicios

- Tres salas corporativas:
  - Sala Pequeña: 40 personas.
  - Sala Mediana: 80 personas.
  - Sala Grande: 200 personas.
- Selección automática de la sala de menor capacidad que pueda atender la
  cantidad de asistentes.
- Validación de la cantidad de asistentes.
- Cálculo del costo de las salas según las horas reservadas.
- Tres combos cerrados de equipos:
  - Reunión empresarial.
  - Capacitación empresarial.
  - Evento corporativo.
- Componentes y cantidades definidos para cada combo.
- Tarifa fija por jornada de 8 horas para los combos.
- Tres asesorías especializadas:
  - Desarrollo de software.
  - Infraestructura tecnológica y seguridad informática.
  - Transformación digital y automatización.
- Tarifa fija por sesión para las asesorías.

### Gestión de reservas

- Creación de reservas asociadas a un cliente y un servicio.
- Validación de fecha y hora.
- Aceptación de formatos de hora AM/PM y formato de 24 horas.
- Validación de la disponibilidad general del servicio al crear y confirmar una
  reserva.
- Cálculo del costo mediante el servicio correspondiente.
- Estados de reserva: pendiente, confirmada y cancelada.
- Confirmación y cancelación de reservas.
- Posibilidad de dejar una reserva pendiente.
- Registro y consulta de varias reservas durante una misma ejecución.
- Consulta de reservas por código o número de posición.

La disponibilidad general del servicio es una condición propia del servicio.
El sistema todavía no valida la disponibilidad de un horario específico ni los
cruces entre reservas.

### Registro de eventos

- Registro de eventos y errores mediante `logging`.
- Archivo de registro `logs/eventos.log`.
- Configuración mediante `configuracion_logs.py`.

### Pruebas

- Pruebas manuales mediante `pruebas.py`.
- Pruebas automatizadas con `unittest` para servicios, reservas, catálogo y menú
  principal.
- En la revisión de esta versión se ejecutaron satisfactoriamente 109 pruebas
  automatizadas. Esta cifra corresponde a ese cierre y puede variar si se
  agregan nuevas pruebas.

## Tecnologías utilizadas

- Python.
- Programación orientada a objetos.
- Git y GitHub.
- Módulos de la biblioteca estándar:
  - `abc`.
  - `datetime`.
  - `logging`.
  - `unittest`.
  - `unittest.mock`.
  - `contextlib`.
  - `io`.
  - `math`.

No se utilizan dependencias externas ni bases de datos.

## Estructura del proyecto

```text
fase4-gestion-reservas/
├── .gitignore
├── README.md
├── main.py                         Punto de entrada y menú principal
├── cliente.py                      Clase Cliente y sus validaciones
├── servicio.py                     Clases de servicios y cálculo de costos
├── catalogo_servicios.py           Catálogo de salas, combos y asesorías
├── reserva.py                      Clase Reserva y gestión de estados
├── excepciones.py                  Excepciones personalizadas
├── configuracion_logs.py           Configuración del registro de eventos
├── pruebas.py                      Pruebas manuales del sistema
├── pruebas/
│   ├── __init__.py
│   ├── test_servicios.py           Pruebas de los servicios
│   ├── test_reserva.py             Pruebas de la clase Reserva
│   ├── test_catalogo_servicios.py  Pruebas del catálogo
│   └── test_main.py                Pruebas del menú principal
└── logs/
    ├── README.md                   Descripción de la carpeta de logs
    └── eventos.log                 Archivo generado durante la ejecución
```

El archivo `logs/eventos.log` y las carpetas `__pycache__/` se generan
automáticamente. El archivo de log está excluido en `.gitignore`.

## Requisitos previos

- Tener Python instalado.
- El proyecto se ha ejecutado y probado con Python 3.14.3.
- No se requiere instalar paquetes externos mediante `pip`.
- Ejecutar los comandos desde la carpeta raíz del proyecto, debido a las rutas
  relativas utilizadas para el registro de eventos.

Para consultar la versión instalada de Python:

```bash
python --version
```

## Ejecución del programa

Desde la carpeta raíz del proyecto:

```bash
python main.py
```

El menú principal ofrece las siguientes opciones:

1. Reservar una sala corporativa.
2. Reservar un combo de equipos.
3. Solicitar una asesoría especializada.
4. Consultar las reservas registradas.
5. Salir.

## Ejecución de las pruebas manuales

Desde la carpeta raíz del proyecto:

```bash
python pruebas.py
```

El archivo `pruebas.py` contiene comprobaciones manuales sobre la creación de
clientes, el rechazo de fechas pasadas, la creación de reservas, los estados y
la cancelación.

En la versión revisada, este script no finaliza correctamente porque intenta
crear una reserva con un servicio representado como texto, mientras que la
clase `Reserva` exige una instancia de `Servicio`. Por este motivo, se conserva
como referencia, pero la validación recomendada del sistema se realiza con las
pruebas automatizadas.

## Pruebas automatizadas individuales

Pruebas de servicios:

```bash
python -m unittest pruebas.test_servicios -v
```

Pruebas de reservas:

```bash
python -m unittest pruebas.test_reserva -v
```

Pruebas del catálogo:

```bash
python -m unittest pruebas.test_catalogo_servicios -v
```

Pruebas del menú principal:

```bash
python -m unittest pruebas.test_main -v
```

## Ejecución de todas las pruebas automatizadas

```bash
python -m unittest discover -s pruebas -v
```

## Aspectos pendientes y posibles mejoras

- **Validación de cruces de horarios:** impedir que se registren o confirmen
  reservas superpuestas para el mismo recurso, permitir reservas consecutivas y
  liberar el horario cuando una reserva se cancela. Actualmente no está
  implementada.
- **Fidelización de clientes:** estudiar la implementación de categorías
  Silver, Gold y Platinum, con beneficios o descuentos según el historial de
  reservas. Los niveles y porcentajes deben quedar sujetos a la revisión y
  aprobación del equipo. Actualmente no está implementada.
- **Identificación con NIT y dígito de verificación:** permitir formatos como
  `1098631256-6`. Actualmente la validación solo acepta dígitos.
- **Gestión de varios clientes:** permitir registrar y seleccionar diferentes
  clientes durante una misma ejecución. Actualmente se reutiliza el cliente
  registrado.
- **Persistencia de información:** incorporar almacenamiento permanente
  mediante archivos o una base de datos. Actualmente los datos de clientes y
  reservas se mantienen en memoria y se pierden al cerrar el programa.
- **Reglas comerciales de impuestos y descuentos:** definir y configurar los
  valores correspondientes. El módulo de servicios ya contempla los cálculos de
  impuestos y descuentos, pero los servicios del catálogo actualmente se crean
  con estos valores en cero.
- **Reportes y consultas:** ampliar la gestión con filtros por cliente, fecha,
  servicio y estado de reserva.
- **Actualización de las pruebas manuales:** ajustar `pruebas.py` para que use
  una instancia real de `Servicio` y pueda ejecutarse correctamente con las
  validaciones actuales.
