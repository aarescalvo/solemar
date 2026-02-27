# Frigo Unida v1.0.0

## Sistema ERP Unificado para Frigorificos

**Frigo Unida** es un sistema ERP completo para la gestion de frigorificos, unificado a partir de las mejores versiones de Frigorifico Solemar y Trazacanva.

---

## Estructura del Proyecto

```
frigo_unida/
├── __init__.py              # Inicializacion del paquete
├── main.py                  # Punto de entrada principal
├── requirements.txt         # Dependencias Python
├── README.md               # Este archivo
│
├── core/                   # Nucleo del sistema
│   ├── __init__.py
│   ├── config.py          # Configuracion global
│   ├── database.py        # Acceso a base de datos SQLite
│   ├── session.py         # Gestion de sesiones de usuario
│   ├── theme.py           # Temas visuales
│   ├── equipos.py         # Conexion con hardware (Balanza, RFID)
│   └── impresion.py       # Impresion de etiquetas
│
├── ui/                     # Interfaces de usuario
│   ├── __init__.py
│   ├── login.py           # Pantalla de login
│   ├── menu.py            # Menu principal
│   ├── camaras_menu.py    # Gestion de camaras frigorificas
│   ├── ciclo1_menu.py     # Ciclo 1 de produccion
│   ├── ciclo2_menu.py     # Ciclo 2 de produccion
│   ├── config_menu.py     # Configuracion del sistema
│   ├── desposte_menu.py   # Modulo de desposte
│   ├── desposte_cuartos_menu.py  # Desposte de cuartos
│   ├── faena_menu.py      # Gestion de faena
│   ├── pesaje_*.py        # Modulos de pesaje (4 archivos)
│   ├── recepcion_menu.py  # Recepcion de animales
│   ├── reportes_menu.py   # Generacion de reportes
│   └── stock_menu.py      # Control de stock
│
├── utils/                  # Utilidades
│   ├── __init__.py
│   └── reportes_impresion.py  # Generacion de PDFs
│
├── reportes/               # Reportes generados (PDF)
│
└── etiquetas/              # Etiquetas de impresion
```

---

## Modulos del Sistema

### 1. PESAJE (Pesaje de Camiones)
- Tickets: TP-YYYY-NNNNN
- Ingreso y egreso de camiones
- Pesaje bruto, tara y neto
- Impresion de tickets PDF

### 2. RECEPCION (Recepcion de Animales)
- Tropas de bovinos: B-YYYY-NNN
- Tropas de porcinos: Q-YYYY-NNN
- Registro de datos del productor
- Control sanitario

### 3. FAENA (Procesamiento)
- Ordenes de faena: OF-B-YYYY-NNN
- Registro de medias reses: MR-YYYY-NNNNNN-I/D
- Clasificacion de categorias
- Trazabilidad completa

### 4. CAMARAS (Almacenamiento)
- Cuartos frigoricos: CU-YYYY-NNNNNN-D/T/A
- Control de temperatura
- Ingreso y egreso de productos

### 5. DESPOSTE (Corte y Empaque)
- Desposte de medias reses
- Productos y subproductos
- Rendimiento y mermas

### 6. DESPACHOS (Salida de Productos)
- Facturacion
- Remitos
- Control de salida

### 7. CONFIGURACION
- Usuarios y permisos
- Parametros del sistema
- Conexion con hardware

---

## Credenciales por Defecto

| Usuario  | Contrasena | Rol           |
|----------|------------|---------------|
| admin    | admin1234  | Administrador |
| 0001     | 1234       | Operador      |

---

## Instalacion

### Requisitos
- Python 3.11+
- Windows / Linux

### Pasos

```bash
# 1. Clonar o descargar el proyecto
cd frigo_unida

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicacion
python main.py
```

---

## Hardware Soportado

### Balanza RS232
- Conexion: Puerto serial (COM1-COM9)
- Baudrate: 9600 (configurable)
- Modo simulacion disponible

### Baston RFID
- Lectura de caravanas electronicas
- Conexion serial
- Modo simulacion disponible

### Impresora Datamax
- Etiquetas de 50x25mm
- Codigo ZPL/DPL
- Puerto LPT1 o USB

---

## Base de Datos

El sistema utiliza **SQLite** con las siguientes tablas principales:

- `usuarios` - Usuarios del sistema
- `tropas` - Grupos de animales recibidos
- `animales` - Registro individual de animales
- `faena` - Registros de procesamiento
- `camaras` - Inventario de camaras
- `stock` - Control de inventario
- `tickets_pesaje` - Tickets de camiones
- `despachos` - Registro de salidas

---

## Caracteristicas Principales

- 100% Offline - No requiere internet
- Interfaz en espanol
- Multi-usuario con permisos
- Trazabilidad completa
- Reportes PDF automaticos
- Impresion de etiquetas
- Conexion con hardware de balanza
- Compatible con Windows y Linux

---

## Historial de Versiones

| Version | Fecha | Descripcion |
|---------|-------|-------------|
| 1.0.0 | 2025-01 | Version unificada de Frigorifico Solemar + Trazacanva |

---

## Licencia

Proyecto privado para uso interno de Frigorifico Solemar.

---

## Soporte

Para soporte tecnico, contactar al equipo de desarrollo.
