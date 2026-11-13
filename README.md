# Software FJ - Sistema de Gestión de Clientes, Servicios y Reservas

Software FJ es una empresa dedicada a la prestación de servicios corporativos. Este proyecto consiste en una aplicación desarrollada en Python que permite registrar clientes, consultar un catálogo de servicios y gestionar reservas de salas corporativas, combos de equipos y asesorías especializadas.

El sistema aplica conceptos de programación orientada a objetos, validaciones, excepciones personalizadas y registro de eventos.

## Objetivo del sistema

Desarrollar una aplicación en Python para gestionar clientes, servicios y reservas, aplicando principios de programación orientada a objetos y buenas prácticas de organización, validación y manejo de errores.

## Integrantes del equipo

- Omar Daniel Gómez Garza.
- Sandra Milena Carvajal Gutiérrez.

## Funcionalidades implementadas

### Entidad abstracta general

- Clase abstracta `Entidad` con el método `describir()`.
- Las clases `Cliente`, `Servicio` y `Reserva` heredan de `Entidad` e implementan su descripción.

### Gestión de clientes

- Registro de clientes.
- Validación del nombre, tipo y número de identificación.
- Validación del número de identificación para aceptar únicamente dígitos.
- Reutilización del cliente registrado durante una misma ejecución.

### Catálogo de servicios

- Tres salas corporativas:
  - Sala Pequeña: capacidad para 40 personas.
  - Sala Mediana: capacidad para 80 personas.
  - Sala Grande: capacidad para 200 personas.
- Selección automática de la sala de menor capacidad que pueda atender la cantidad de asistentes.
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

### Validación polimórfica de servicios

- Método abstracto `validar_parametros()` en la clase `Servicio`.
- Sobrescritura del método en los cinco servicios concretos.
- Reutilización de las validaciones comunes mediante `super().validar_parametros()`.
- Validaciones específicas para las horas, cantidades, capacidades, descripciones y componentes, según el tipo de servicio.

### Cálculo de costos

- Método `calcular_costo()` con implementación especializada mediante `calcular_costo_base()` en cada servicio.
- Sobrecarga simulada mediante parámetros opcionales para aplicar impuestos y descuentos.
- Posibilidad de calcular costos con valores alternativos sin modificar los valores configurados en el servicio.

### Gestión de reservas

- Creación de reservas asociadas a un cliente y un servicio.
- Validación de fecha y hora.
- Aceptación de formatos de hora AM/PM y formato de 24 horas.
- Validación de la disponibilidad general del servicio al crear y confirmar una reserva.
- Almacenamiento y validación de la duración de la reserva, obtenida del servicio correspondiente.
- Cálculo de la fecha y hora de finalización según la duración almacenada.
- Las salas utilizan las horas reservadas y los combos tienen una duración fija de 8 horas. Los servicios que no definen duración conservan el valor `None`.
- Estados de reserva: pendiente, confirmada y cancelada.
- Confirmación y cancelación de reservas.
- Procesamiento de confirmaciones mediante `Reserva.procesar_reserva()`, con manejo de excepciones y registro de eventos.
- Posibilidad de dejar una reserva pendiente.
- Registro y consulta de varias reservas durante una misma ejecución.
- Consulta de reservas por código o número de posición.

La disponibilidad general pertenece al servicio. Para salas corporativas, el sistema también rechaza cruces con reservas pendientes o confirmadas durante la misma ejecución. Una reserva cancelada libera el horario. La sala se identifica por nombre; los cruces de combos y asesorías no están implementados.

### Registro de eventos

- Registro de eventos y errores mediante el módulo `logging`.
- Archivo de registro `logs/eventos.log`.
- Configuración mediante `configuracion_logs.py`.
- Registro de operaciones exitosas, errores y finalización del procesamiento de reservas.
- Creación automática de la carpeta de logs cuando no existe.

## Tecnologías utilizadas

- Python 3.14.3.
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

No se utilizan dependencias externas ni bases de datos. La información de clientes y reservas se mantiene en memoria durante la ejecución del programa.

## Estructura del proyecto

```text
fase4-gestion-reservas/
├── .gitignore
├── README.md
├── main.py                          Punto de entrada y menú principal
├── entidad.py                       Clase abstracta general del sistema
├── cliente.py                       Clase Cliente y sus validaciones
├── servicio.py                      Servicios, validaciones y costos
├── catalogo_servicios.py            Catálogo de salas, combos y asesorías
├── reserva.py                       Clase Reserva y gestión de estados
├── excepciones.py                   Excepciones personalizadas
├── configuracion_logs.py            Configuración de registros
├── simulacion_operaciones.py        Simulación de operaciones
├── pruebas.py                       Pruebas manuales del sistema
├── pruebas/
│   ├── __init__.py
│   ├── test_servicios.py            Pruebas de los servicios
│   ├── test_reserva.py              Pruebas de la clase Reserva
│   ├── test_catalogo_servicios.py   Pruebas del catálogo
│   ├── test_main.py                 Pruebas del menú principal
│   ├── test_configuracion_logs.py   Pruebas de configuración de logs
│   ├── test_entidad_y_sobrecarga.py Pruebas de Entidad y sobrecarga
│   ├── test_validaciones_adicionales.py Pruebas de validaciones adicionales
│   └── test_requisitos_completados.py Pruebas de requisitos completados
└── logs/
    └── README.md                    Descripción de la carpeta de logs
```

El archivo `logs/eventos.log` y las carpetas `__pycache__/` se generan automáticamente durante la ejecución. El archivo de registro está excluido de Git mediante `.gitignore`.

## Requisitos previos

- Tener Python instalado.
- El proyecto se ha ejecutado y probado con Python 3.14.3.
- No se requiere instalar paquetes externos mediante `pip`.
- La ruta del archivo `logs/eventos.log` se calcula a partir de la ubicación del proyecto.

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

El archivo `pruebas.py` contiene comprobaciones sobre la creación de clientes, validación de datos, rechazo de fechas pasadas, creación de reservas, cambios de estado y cancelación.

## Ejecución de la simulación

Para ejecutar la simulación de operaciones del sistema:

```bash
python simulacion_operaciones.py
```

Este módulo realiza operaciones de prueba y permite observar el comportamiento del sistema frente a operaciones válidas y situaciones de error controladas.

## Ejecución de las pruebas automatizadas

Para ejecutar todas las pruebas:

```bash
python -m unittest discover -s pruebas -v
```

También es posible ejecutar los módulos de prueba individualmente:

**Pruebas de servicios:**

```bash
python -m unittest pruebas.test_servicios -v
```

**Pruebas de reservas:**

```bash
python -m unittest pruebas.test_reserva -v
```

**Pruebas del catálogo:**

```bash
python -m unittest pruebas.test_catalogo_servicios -v
```

**Pruebas del menú principal:**

```bash
python -m unittest pruebas.test_main -v
```

En la última ejecución se completaron satisfactoriamente 145 pruebas automatizadas. Esta cantidad puede cambiar cuando se incorporen nuevas pruebas o se modifique el proyecto.

## Aspectos pendientes y posibles mejoras

Los siguientes puntos corresponden a mejoras opcionales que pueden evaluarse en futuras versiones. No todos forman parte de los requerimientos obligatorios de la actividad.

- **Validación de cruces de horarios:** ampliar la validación de salas a otros recursos y definir identificadores estables para controlar la disponibilidad de combos y asesorías.
- **Fidelización de clientes:** implementar categorías Silver, Gold y Platinum, con beneficios o descuentos según el historial de reservas. Los niveles y porcentajes deben quedar sujetos a la revisión y aprobación del equipo. Actualmente no está implementada.
- **Identificación con NIT y dígito de verificación:** permitir formatos como `1098631256-6`. Actualmente la validación solo acepta dígitos.
- **Gestión de varios clientes:** permitir registrar y seleccionar diferentes clientes durante una misma ejecución. Actualmente se reutiliza el cliente registrado.
- **Persistencia de información:** incorporar almacenamiento permanente mediante archivos o una base de datos. Actualmente los datos de clientes y reservas se mantienen en memoria y se pierden al cerrar el programa.
- **Reglas comerciales de impuestos y descuentos:** definir y configurar los valores correspondientes. El módulo de servicios contempla los cálculos de impuestos y descuentos, pero los servicios del catálogo actualmente se crean con estos valores en cero.
- **Reportes y consultas:** ampliar la gestión con filtros por cliente, fecha, servicio y estado de reserva.
