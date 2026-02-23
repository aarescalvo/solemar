"""
Base de datos SQLite - Frigorifico Solemar
Tablas para todos los modulos del sistema
Version 2.2 - Operadores del sistema (clave numerica) y Usuarios de faena separados
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frigorifico.db")

# ═══════════════════════════════════════════════════════════════
# TIPIFICACIONES POR ESPECIE
# ═══════════════════════════════════════════════════════════════

TIPIFICACIONES_BOVINO = ["Torito (MEJ)", "TORO", "vaquillona", "vaca", "novillito", "novillo"]
TIPIFICACIONES_EQUINO = ["yegua", "caballo padrillo", "potranca/potrillo", "burro", "mula"]

RAZAS_BOVINO = ["Aberdeen Angus", "Hereford", "Shorthorn", "Nelore", "Brahman", "Brangus", "Charolais", "Limousin", "Criollo", "Mestizo", "Otra"]
PELAJES_EQUINO = ["Alazan", "Bayo", "Negro", "Castanho", "Tordillo", "Rosillo", "Overo", "Picaso", "Zaino", "Otro"]
GORDURAS_EQUINO = ["G1", "G2", "G3", "G4", "G5"]

# Modulos del sistema para permisos
MODULOS_SISTEMA = [
    "pesaje", "recepcion", "faena", "camaras", 
    "desposte", "stock", "reportes", "configuracion"
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ═══════════════════════════════════════════════════════════
    # TABLAS DEL SISTEMA
    # ═══════════════════════════════════════════════════════════

    # OPERADORES DEL SISTEMA - Clave numerica, niveles de acceso
    cur.execute("""
        CREATE TABLE IF NOT EXISTS operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_operador INTEGER UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            clave TEXT NOT NULL,
            nivel TEXT DEFAULT 'usuario',
            mod_pesaje INTEGER DEFAULT 0,
            mod_recepcion INTEGER DEFAULT 0,
            mod_faena INTEGER DEFAULT 0,
            mod_camaras INTEGER DEFAULT 0,
            mod_desposte INTEGER DEFAULT 0,
            mod_stock INTEGER DEFAULT 0,
            mod_reportes INTEGER DEFAULT 0,
            mod_configuracion INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1
        )
    """)

    # USUARIOS DE FAENA - Carneadores con datos profesionales
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_faena (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_usuario TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            razon_social TEXT,
            cuit TEXT,
            matricula TEXT,
            direccion TEXT,
            telefono TEXT,
            email TEXT,
            numero_cuenta TEXT,
            observaciones TEXT,
            activo INTEGER DEFAULT 1
        )
    """)

    # TRANSPORTISTAS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transportistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_transportista TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            razon_social TEXT,
            cuit TEXT,
            telefono TEXT,
            nombre_chofer TEXT,
            dni_chofer TEXT,
            patente_chasis TEXT,
            patente_acoplado TEXT,
            num_habilitacion_senasa TEXT,
            contacto TEXT,
            observaciones TEXT,
            activo INTEGER DEFAULT 1
        )
    """)

    # PROVEEDORES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_proveedor TEXT UNIQUE NOT NULL,
            razon_social TEXT NOT NULL,
            cuit TEXT,
            provincia TEXT,
            localidad TEXT,
            direccion TEXT,
            telefono TEXT,
            email TEXT,
            contacto TEXT,
            renspa TEXT,
            activo INTEGER DEFAULT 1
        )
    """)

    # CORRALES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS corrales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL,
            especie TEXT DEFAULT 'mixto',
            capacidad INTEGER DEFAULT 50,
            ocupacion INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'activo'
        )
    """)

    # TROPAS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tropas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_tropa TEXT UNIQUE NOT NULL,
            especie TEXT NOT NULL,
            proveedor_id INTEGER,
            ticket_pesaje_id INTEGER,
            fecha_ingreso TEXT,
            cantidad_esperada INTEGER DEFAULT 0,
            cantidad_cabezas INTEGER DEFAULT 0,
            peso_total REAL DEFAULT 0,
            procedencia TEXT,
            num_guia TEXT,
            corral_id INTEGER,
            estado TEXT DEFAULT 'pendiente',
            paso_actual INTEGER DEFAULT 1,
            observaciones TEXT
        )
    """)

    # ANIMALES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS animales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            numero_tropa TEXT NOT NULL,
            numero_correlativo INTEGER NOT NULL,
            tropa_id INTEGER,
            caravana TEXT,
            especie TEXT NOT NULL,
            tipificacion TEXT,
            raza TEXT,
            gordura TEXT,
            pelaje TEXT,
            corral_id INTEGER,
            proveedor_id INTEGER,
            peso_vivo REAL,
            fecha_pesaje TEXT,
            hora_pesaje TEXT,
            fecha_ingreso TEXT,
            estado TEXT DEFAULT 'en_corral',
            etiqueta_impresa INTEGER DEFAULT 0,
            observaciones TEXT
        )
    """)

    # NUMEROS ELIMINADOS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS numeros_eliminados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_tropa TEXT NOT NULL,
            numero_correlativo INTEGER NOT NULL,
            animal_id INTEGER,
            fecha_eliminacion TEXT,
            hora_eliminacion TEXT,
            operador TEXT,
            motivo TEXT
        )
    """)

    # TROPA TIPIFICACIONES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tropa_tipificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tropa_id INTEGER NOT NULL,
            tipificacion TEXT NOT NULL,
            cantidad_esperada INTEGER DEFAULT 0,
            cantidad_registrada INTEGER DEFAULT 0
        )
    """)

    # MOVIMIENTOS DE CORRAL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_corral (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            corral_origen_id INTEGER,
            corral_destino_id INTEGER,
            fecha_movimiento TEXT,
            hora_movimiento TEXT,
            motivo TEXT,
            observaciones TEXT,
            operador TEXT
        )
    """)

    # MORTANDAD
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mortandad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            fecha_muerte TEXT,
            causa TEXT,
            observaciones TEXT,
            operador TEXT
        )
    """)

    # FAENA
    cur.execute("""
        CREATE TABLE IF NOT EXISTS faena (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_faena TEXT UNIQUE NOT NULL,
            animal_id INTEGER,
            especie TEXT,
            categoria TEXT,
            fecha_faena TEXT,
            hora_faena TEXT,
            peso_vivo REAL,
            peso_canal REAL,
            rendimiento REAL,
            tipificacion TEXT,
            destino TEXT,
            usuario_faena_id INTEGER,
            operador TEXT,
            observaciones TEXT
        )
    """)

    # MEDIAS RESES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medias_reses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            faena_id INTEGER,
            especie TEXT,
            media TEXT,
            peso REAL,
            camara_id INTEGER,
            posicion TEXT,
            fecha_ingreso TEXT,
            estado TEXT DEFAULT 'en_camara',
            observaciones TEXT
        )
    """)

    # CAMARAS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS camaras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            nombre TEXT,
            especie TEXT DEFAULT 'mixta',
            capacidad_kg INTEGER DEFAULT 10000,
            temperatura REAL DEFAULT -18,
            ocupacion_kg REAL DEFAULT 0,
            estado TEXT DEFAULT 'activa'
        )
    """)

    # STOCK CAMARAS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_camaras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camara_id INTEGER,
            producto TEXT,
            cantidad INTEGER DEFAULT 0,
            peso_kg REAL DEFAULT 0,
            fecha_entrada TEXT,
            lote TEXT,
            estado TEXT DEFAULT 'disponible'
        )
    """)

    # DESPOSTE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS desposte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_lote TEXT,
            fecha TEXT,
            media_res_id INTEGER,
            producto TEXT,
            peso_kg REAL,
            camara_destino INTEGER,
            operador TEXT,
            observaciones TEXT
        )
    """)

    # DESPACHOS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS despachos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_remito TEXT UNIQUE NOT NULL,
            fecha TEXT,
            cliente TEXT,
            cuit_cliente TEXT,
            destino TEXT,
            patente TEXT,
            transportista TEXT,
            peso_total REAL,
            operador TEXT,
            estado TEXT DEFAULT 'pendiente',
            observaciones TEXT
        )
    """)

    # TICKETS DE PESAJE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets_pesaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_ticket TEXT,
            tipo_ticket TEXT,
            tipo_operacion TEXT,
            fecha TEXT,
            hora TEXT,
            patente_chasis TEXT,
            patente_acoplado TEXT,
            transportista_id INTEGER,
            transportista TEXT,
            cuit_transportista TEXT,
            dni_chofer TEXT,
            chofer TEXT,
            operador_id INTEGER,
            usuario_faena_id INTEGER,
            proveedor_id INTEGER,
            numero_guia TEXT,
            numero_dte TEXT,
            num_habilitacion TEXT,
            precintos TEXT,
            observaciones TEXT,
            peso_kg REAL,
            peso_manual INTEGER,
            ticket_ingreso_id INTEGER,
            tropa_id INTEGER,
            peso_bruto_kg REAL,
            peso_tara_kg REAL,
            peso_neto_kg REAL,
            operador TEXT,
            estado TEXT,
            creado_en TEXT
        )
    """)

    # CONFIGURACION DE TICKETS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_tickets (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            prox_ingreso INTEGER DEFAULT 1,
            prox_egreso INTEGER DEFAULT 1
        )
    """)

    # CONFIGURACION GENERAL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            prox_tropa_bovino INTEGER DEFAULT 1,
            prox_tropa_equino INTEGER DEFAULT 1,
            prox_faena INTEGER DEFAULT 1,
            prox_media INTEGER DEFAULT 1,
            prox_despacho INTEGER DEFAULT 1,
            prox_lote_desposte INTEGER DEFAULT 1,
            prox_operador INTEGER DEFAULT 1,
            prox_transportista INTEGER DEFAULT 1,
            prox_usuario_faena INTEGER DEFAULT 1,
            prox_proveedor INTEGER DEFAULT 1
        )
    """)

    # CONFIGURACION DE EQUIPOS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS config_equipos (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            balanza_puerto TEXT DEFAULT 'COM1',
            balanza_baudrate INTEGER DEFAULT 9600,
            balanza_timeout INTEGER DEFAULT 1,
            rfid_puerto TEXT DEFAULT 'COM2',
            rfid_baudrate INTEGER DEFAULT 9600,
            rfid_timeout INTEGER DEFAULT 1,
            impresora_puerto TEXT DEFAULT 'LPT1',
            impresora_tipo TEXT DEFAULT 'datamax',
            impresora_ancho_etiqueta INTEGER DEFAULT 50,
            impresora_alto_etiqueta INTEGER DEFAULT 25
        )
    """)

    # ═══════════════════════════════════════════════════════════
    # DATOS INICIALES
    # ═══════════════════════════════════════════════════════════

    cur.execute("INSERT OR IGNORE INTO configuracion_tickets (id, prox_ingreso, prox_egreso) VALUES (1, 1, 1)")
    cur.execute("INSERT OR IGNORE INTO configuracion (id, prox_tropa_bovino, prox_tropa_equino, prox_faena, prox_media, prox_despacho, prox_lote_desposte, prox_operador, prox_transportista, prox_usuario_faena, prox_proveedor) VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)")
    cur.execute("INSERT OR IGNORE INTO config_equipos (id) VALUES (1)")
    
    # Agregar columna prox_proveedor si no existe
    try:
        cur.execute("ALTER TABLE configuracion ADD COLUMN prox_proveedor INTEGER DEFAULT 1")
    except:
        pass

    # Operadores por defecto (clave numerica)
    # Administrador: 0001, clave: 1234
    cur.execute("INSERT OR IGNORE INTO operadores (numero_operador, nombre, clave, nivel, mod_pesaje, mod_recepcion, mod_faena, mod_camaras, mod_desposte, mod_stock, mod_reportes, mod_configuracion) VALUES (?, ?, ?, ?, 1, 1, 1, 1, 1, 1, 1, 1)",
                (1, "Administrador", hash_password("1234"), "administrador"))
    # Supervisor: 0002, clave: 1234
    cur.execute("INSERT OR IGNORE INTO operadores (numero_operador, nombre, clave, nivel, mod_pesaje, mod_recepcion, mod_faena, mod_camaras, mod_desposte, mod_stock, mod_reportes, mod_configuracion) VALUES (?, ?, ?, ?, 1, 1, 1, 0, 0, 0, 1, 0)",
                (2, "Supervisor", hash_password("1234"), "supervisor"))
    # Usuario: 0003, clave: 1234
    cur.execute("INSERT OR IGNORE INTO operadores (numero_operador, nombre, clave, nivel, mod_pesaje, mod_recepcion, mod_faena, mod_camaras, mod_desposte, mod_stock, mod_reportes, mod_configuracion) VALUES (?, ?, ?, ?, 1, 1, 0, 0, 0, 0, 0, 0)",
                (3, "Operador", hash_password("1234"), "usuario"))

    # Corrales
    corrales = [
        ("B-01", "bovino", "bovino", 50), ("B-02", "bovino", "bovino", 50), ("B-03", "bovino", "bovino", 80),
        ("B-04", "bovino", "bovino", 60), ("B-05", "bovino", "bovino", 60), ("B-06", "bovino", "bovino", 70),
        ("E-01", "equino", "equino", 30), ("E-02", "equino", "equino", 30), ("E-03", "equino", "equino", 40),
        ("C-01", "cuarentena", "mixto", 20), ("C-02", "cuarentena", "mixto", 20),
        ("PF-01", "espera_faena", "mixto", 40), ("PF-02", "espera_faena", "mixto", 40),
    ]
    for numero, tipo, especie, cap in corrales:
        cur.execute("INSERT OR IGNORE INTO corrales (numero, tipo, especie, capacidad) VALUES (?, ?, ?, ?)", 
                    (numero, tipo, especie, cap))

    # Camaras
    camaras = [
        ("01", "Camara Bovinos", "bovino", 15000), ("02", "Camara Equinos", "equino", 10000),
        ("03", "Camara Desposte", "mixta", 8000), ("04", "Camara Subproductos", "mixta", 5000),
        ("05", "Congelacion", "mixta", 12000),
    ]
    for numero, nombre, especie, cap in camaras:
        cur.execute("INSERT OR IGNORE INTO camaras (numero, nombre, especie, capacidad_kg) VALUES (?, ?, ?, ?)", 
                    (numero, nombre, especie, cap))

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE OPERADORES DEL SISTEMA
# ═══════════════════════════════════════════════════════════════

def autenticar_operador(numero_operador, clave):
    """Autentica operador con numero y clave numerica"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM operadores WHERE numero_operador=? AND clave=? AND activo=1",
                (numero_operador, hash_password(clave)))
    op = cur.fetchone()
    conn.close()
    return dict(op) if op else None


def get_proximo_numero_operador():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT prox_operador FROM configuracion WHERE id=1")
    row = cur.fetchone()
    num = row['prox_operador'] if row else 1
    conn.close()
    return num


def incrementar_operador():
    conn = get_connection()
    conn.execute("UPDATE configuracion SET prox_operador = prox_operador + 1 WHERE id=1")
    conn.commit()
    conn.close()


def listar_operadores():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM operadores ORDER BY numero_operador")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_operador_by_id(op_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM operadores WHERE id=?", (op_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def existe_numero_operador(numero_operador):
    """Verifica si ya existe un numero de operador"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM operadores WHERE numero_operador=?", (numero_operador,))
    row = cur.fetchone()
    conn.close()
    return row is not None


def crear_operador(datos):
    """Crea un nuevo operador con numero personalizado"""
    conn = get_connection()
    cur = conn.cursor()
    num_op = datos.get("numero_operador")
    
    # Verificar que no exista
    cur.execute("SELECT id FROM operadores WHERE numero_operador=?", (num_op,))
    if cur.fetchone():
        conn.close()
        raise ValueError(f"El numero de operador {num_op:04d} ya existe")
    
    cur.execute("""
        INSERT INTO operadores (numero_operador, nombre, clave, nivel, 
            mod_pesaje, mod_recepcion, mod_faena, mod_camaras, 
            mod_desposte, mod_stock, mod_reportes, mod_configuracion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (num_op, datos.get("nombre"), hash_password(datos.get("clave", "1234")), datos.get("nivel", "usuario"),
          datos.get("mod_pesaje", 0), datos.get("mod_recepcion", 0), datos.get("mod_faena", 0),
          datos.get("mod_camaras", 0), datos.get("mod_desposte", 0), datos.get("mod_stock", 0),
          datos.get("mod_reportes", 0), datos.get("mod_configuracion", 0)))
    conn.commit()
    conn.close()
    return num_op


def actualizar_operador(op_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE operadores SET nombre=?, nivel=?, 
            mod_pesaje=?, mod_recepcion=?, mod_faena=?, mod_camaras=?,
            mod_desposte=?, mod_stock=?, mod_reportes=?, mod_configuracion=?
        WHERE id=?
    """, (datos.get("nombre"), datos.get("nivel"),
          datos.get("mod_pesaje", 0), datos.get("mod_recepcion", 0), datos.get("mod_faena", 0),
          datos.get("mod_camaras", 0), datos.get("mod_desposte", 0), datos.get("mod_stock", 0),
          datos.get("mod_reportes", 0), datos.get("mod_configuracion", 0), op_id))
    conn.commit()
    conn.close()


def cambiar_clave_operador(op_id, clave):
    conn = get_connection()
    conn.execute("UPDATE operadores SET clave=? WHERE id=?", (hash_password(clave), op_id))
    conn.commit()
    conn.close()


def eliminar_operador(op_id):
    conn = get_connection()
    conn.execute("UPDATE operadores SET activo=0 WHERE id=?", (op_id,))
    conn.commit()
    conn.close()


def verificar_permiso(op_id, modulo):
    """Verifica si el operador tiene permiso para un modulo"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT nivel, mod_{} FROM operadores WHERE id=? AND activo=1".format(modulo), (op_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    if row['nivel'] == 'administrador':
        return True
    return bool(row[0])


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE USUARIOS DE FAENA
# ═══════════════════════════════════════════════════════════════

def get_proximo_codigo_usuario_faena():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT prox_usuario_faena FROM configuracion WHERE id=1")
    row = cur.fetchone()
    num = row['prox_usuario_faena'] if row else 1
    conn.close()
    return f"UF-{num:04d}"


def incrementar_usuario_faena():
    conn = get_connection()
    conn.execute("UPDATE configuracion SET prox_usuario_faena = prox_usuario_faena + 1 WHERE id=1")
    conn.commit()
    conn.close()


def listar_usuarios_faena():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios_faena ORDER BY codigo_usuario")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_usuarios_faena_activos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, codigo_usuario, nombre FROM usuarios_faena WHERE activo=1 ORDER BY nombre")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_usuario_faena_by_id(uf_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios_faena WHERE id=?", (uf_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def crear_usuario_faena(datos):
    conn = get_connection()
    cur = conn.cursor()
    codigo = get_proximo_codigo_usuario_faena()
    cur.execute("""
        INSERT INTO usuarios_faena (codigo_usuario, nombre, razon_social, cuit, matricula, direccion, telefono, email, numero_cuenta, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (codigo, datos.get("nombre"), datos.get("razon_social"), datos.get("cuit"), datos.get("matricula"),
          datos.get("direccion"), datos.get("telefono"), datos.get("email"), datos.get("numero_cuenta"), datos.get("observaciones")))
    conn.commit()
    conn.close()
    incrementar_usuario_faena()
    return codigo


def actualizar_usuario_faena(uf_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE usuarios_faena SET nombre=?, razon_social=?, cuit=?, matricula=?, direccion=?, telefono=?, email=?, numero_cuenta=?, observaciones=?
        WHERE id=?
    """, (datos.get("nombre"), datos.get("razon_social"), datos.get("cuit"), datos.get("matricula"),
          datos.get("direccion"), datos.get("telefono"), datos.get("email"), datos.get("numero_cuenta"),
          datos.get("observaciones"), uf_id))
    conn.commit()
    conn.close()


def eliminar_usuario_faena(uf_id):
    conn = get_connection()
    conn.execute("UPDATE usuarios_faena SET activo=0 WHERE id=?", (uf_id,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE TRANSPORTISTAS
# ═══════════════════════════════════════════════════════════════

def get_proximo_numero_transportista():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT prox_transportista FROM configuracion WHERE id=1")
    row = cur.fetchone()
    num = row['prox_transportista'] if row else 1
    conn.close()
    return f"TR-{num:05d}"


def incrementar_transportista():
    conn = get_connection()
    conn.execute("UPDATE configuracion SET prox_transportista = prox_transportista + 1 WHERE id=1")
    conn.commit()
    conn.close()


def listar_transportistas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transportistas ORDER BY codigo_transportista")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_transportistas_activos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, codigo_transportista, nombre, razon_social, nombre_chofer, patente_chasis, patente_acoplado, cuit FROM transportistas WHERE activo=1 ORDER BY nombre")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_transportista_by_id(transportista_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transportistas WHERE id=?", (transportista_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def buscar_transportista_by_patente(patente):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transportistas WHERE activo=1 AND (patente_chasis LIKE ? OR patente_acoplado LIKE ?)",
                (f"%{patente}%", f"%{patente}%"))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def crear_transportista(datos):
    conn = get_connection()
    cur = conn.cursor()
    codigo = get_proximo_numero_transportista()
    cur.execute("""
        INSERT INTO transportistas (codigo_transportista, nombre, razon_social, cuit, telefono, nombre_chofer, dni_chofer, patente_chasis, patente_acoplado, num_habilitacion_senasa, contacto, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (codigo, datos.get("nombre"), datos.get("razon_social"), datos.get("cuit"),
          datos.get("telefono"), datos.get("nombre_chofer"), datos.get("dni_chofer"),
          datos.get("patente_chasis"), datos.get("patente_acoplado"),
          datos.get("num_habilitacion_senasa"), datos.get("contacto"), datos.get("observaciones")))
    conn.commit()
    conn.close()
    incrementar_transportista()
    return codigo


def actualizar_transportista(transportista_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE transportistas SET nombre=?, razon_social=?, cuit=?, telefono=?, nombre_chofer=?, dni_chofer=?, patente_chasis=?, patente_acoplado=?, num_habilitacion_senasa=?, contacto=?, observaciones=?
        WHERE id=?
    """, (datos.get("nombre"), datos.get("razon_social"), datos.get("cuit"), datos.get("telefono"),
          datos.get("nombre_chofer"), datos.get("dni_chofer"),
          datos.get("patente_chasis"), datos.get("patente_acoplado"), datos.get("num_habilitacion_senasa"),
          datos.get("contacto"), datos.get("observaciones"), transportista_id))
    conn.commit()
    conn.close()


def eliminar_transportista(transportista_id):
    conn = get_connection()
    conn.execute("UPDATE transportistas SET activo=0 WHERE id=?", (transportista_id,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE PESAJE - TICKETS
# ═══════════════════════════════════════════════════════════════

def get_proximo_ticket(tipo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT prox_ingreso, prox_egreso FROM configuracion_tickets WHERE id=1")
    row = cur.fetchone()
    conn.close()
    anio = datetime.now().year
    if tipo == "ingreso":
        return f"TI-{anio}-{row['prox_ingreso']:06d}"
    return f"TE-{anio}-{row['prox_egreso']:06d}"


def incrementar_ticket(tipo):
    conn = get_connection()
    if tipo == "ingreso":
        conn.execute("UPDATE configuracion_tickets SET prox_ingreso = prox_ingreso + 1 WHERE id=1")
    else:
        conn.execute("UPDATE configuracion_tickets SET prox_egreso = prox_egreso + 1 WHERE id=1")
    conn.commit()
    conn.close()


def get_config_tickets():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT prox_ingreso, prox_egreso FROM configuracion_tickets WHERE id=1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {"prox_ingreso": 1, "prox_egreso": 1}


def set_config_ticket(tipo, valor):
    conn = get_connection()
    if tipo == "ingreso":
        conn.execute("UPDATE configuracion_tickets SET prox_ingreso=? WHERE id=1", (valor,))
    else:
        conn.execute("UPDATE configuracion_tickets SET prox_egreso=? WHERE id=1", (valor,))
    conn.commit()
    conn.close()


def guardar_ticket(datos):
    conn = get_connection()
    cur = conn.cursor()
    ahora = datetime.now()
    estado_inicial = "abierto" if datos.get("tipo_ticket") == "ingreso" else "cerrado"
    
    cur.execute("""
        INSERT INTO tickets_pesaje (
            numero_ticket, tipo_ticket, tipo_operacion, fecha, hora,
            patente_chasis, patente_acoplado, transportista_id, transportista, cuit_transportista,
            dni_chofer, chofer, operador_id, usuario_faena_id, proveedor_id, numero_guia, numero_dte,
            num_habilitacion, precintos, observaciones, peso_kg, peso_manual, 
            ticket_ingreso_id, tropa_id, peso_bruto_kg, peso_tara_kg, peso_neto_kg, 
            operador, estado, creado_en
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos.get("numero_ticket", ""), datos.get("tipo_ticket", ""), datos.get("tipo_operacion", ""),
        ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S"),
        datos.get("patente_chasis", ""), datos.get("patente_acoplado", ""), datos.get("transportista_id"),
        datos.get("transportista", ""), datos.get("cuit_transportista", ""),
        datos.get("dni_chofer", ""), datos.get("chofer", ""), datos.get("operador_id"),
        datos.get("usuario_faena_id"), datos.get("proveedor_id"), datos.get("numero_guia", ""), 
        datos.get("numero_dte", ""), datos.get("num_habilitacion", ""), datos.get("precintos", ""),
        datos.get("observaciones", ""), datos.get("peso_kg", 0), datos.get("peso_manual", 0),
        datos.get("ticket_ingreso_id"), datos.get("tropa_id"),
        datos.get("peso_bruto_kg"), datos.get("peso_tara_kg"),
        datos.get("peso_neto_kg"), datos.get("operador", ""), estado_inicial, ahora.strftime("%Y-%m-%d %H:%M:%S")
    ))
    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()
    incrementar_ticket(datos.get("tipo_ticket", "ingreso"))
    return ticket_id


def listar_tickets(filtros=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM tickets_pesaje WHERE 1=1"
    params = []
    if filtros:
        if filtros.get("estado"):
            query += " AND estado=?"
            params.append(filtros["estado"])
        if filtros.get("tipo"):
            query += " AND tipo_ticket=?"
            params.append(filtros["tipo"])
        if filtros.get("fecha_desde"):
            query += " AND fecha >= ?"
            params.append(filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            query += " AND fecha <= ?"
            params.append(filtros["fecha_hasta"])
        if filtros.get("patente"):
            query += " AND (patente_chasis LIKE ? OR patente_acoplado LIKE ?)"
            p = f"%{filtros['patente']}%"
            params.extend([p, p])
    query += " ORDER BY id DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def buscar_ticket_ingreso(patente):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM tickets_pesaje
        WHERE tipo_ticket='ingreso' AND estado='abierto'
        AND (patente_chasis LIKE ? OR patente_acoplado LIKE ?)
        ORDER BY id DESC
    """, (f"%{patente}%", f"%{patente}%"))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_ticket_by_id(ticket_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets_pesaje WHERE id=?", (ticket_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_ticket_by_numero(numero_ticket):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets_pesaje WHERE numero_ticket=?", (numero_ticket,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_tickets_ingreso_abiertos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.*, p.razon_social as proveedor_nombre 
        FROM tickets_pesaje t
        LEFT JOIN proveedores p ON t.proveedor_id=p.id
        WHERE t.tipo_ticket='ingreso' AND t.estado='abierto'
        ORDER BY t.fecha DESC, t.hora DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def cerrar_ticket(ticket_id):
    conn = get_connection()
    conn.execute("UPDATE tickets_pesaje SET estado='cerrado' WHERE id=?", (ticket_id,))
    conn.commit()
    conn.close()


def guardar_ticket_egreso(datos):
    conn = get_connection()
    cur = conn.cursor()
    ahora = datetime.now()
    
    cur.execute("""
        INSERT INTO tickets_pesaje (
            numero_ticket, tipo_ticket, tipo_operacion, fecha, hora,
            patente_chasis, patente_acoplado, transportista_id, transportista, cuit_transportista,
            dni_chofer, chofer, operador_id, num_habilitacion, precintos,
            observaciones, peso_kg, peso_manual, ticket_ingreso_id, tropa_id,
            peso_bruto_kg, peso_tara_kg, peso_neto_kg, operador, estado, creado_en
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos.get("numero_ticket", ""), "egreso", datos.get("tipo_operacion", ""),
        ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S"),
        datos.get("patente_chasis", ""), datos.get("patente_acoplado", ""), datos.get("transportista_id"),
        datos.get("transportista", ""), datos.get("cuit_transportista", ""),
        datos.get("dni_chofer", ""), datos.get("chofer", ""), datos.get("operador_id"),
        datos.get("num_habilitacion", ""), datos.get("precintos", ""),
        datos.get("observaciones", ""), datos.get("peso_kg", 0), datos.get("peso_manual", 0),
        datos.get("ticket_ingreso_id"), datos.get("tropa_id"),
        datos.get("peso_bruto_kg"), datos.get("peso_tara_kg"),
        datos.get("peso_neto_kg"), datos.get("operador", ""), "cerrado", ahora.strftime("%Y-%m-%d %H:%M:%S")
    ))
    ticket_egreso_id = cur.lastrowid
    
    ticket_ingreso_id = datos.get("ticket_ingreso_id")
    if ticket_ingreso_id:
        cur.execute("UPDATE tickets_pesaje SET estado='cerrado' WHERE id=?", (ticket_ingreso_id,))
    
    conn.commit()
    conn.close()
    incrementar_ticket("egreso")
    return ticket_egreso_id


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE PROVEEDORES
# ═══════════════════════════════════════════════════════════════

def get_proximo_codigo_proveedor():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT prox_proveedor FROM configuracion WHERE id=1")
    row = cur.fetchone()
    num = row['prox_proveedor'] if row else 1
    conn.close()
    return f"PR-{num:05d}"


def incrementar_proveedor():
    conn = get_connection()
    conn.execute("UPDATE configuracion SET prox_proveedor = prox_proveedor + 1 WHERE id=1")
    conn.commit()
    conn.close()


def listar_proveedores():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM proveedores WHERE activo=1 ORDER BY codigo_proveedor")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_proveedor_by_id(proveedor_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM proveedores WHERE id=?", (proveedor_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def guardar_proveedor(datos):
    conn = get_connection()
    cur = conn.cursor()
    codigo = get_proximo_codigo_proveedor()
    cur.execute("""
        INSERT INTO proveedores (codigo_proveedor, razon_social, cuit, provincia, localidad, direccion, telefono, email, contacto, renspa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (codigo, datos.get("razon_social"), datos.get("cuit"), datos.get("provincia"), datos.get("localidad"),
          datos.get("direccion"), datos.get("telefono"), datos.get("email"), datos.get("contacto"), datos.get("renspa")))
    conn.commit()
    conn.close()
    incrementar_proveedor()
    return codigo


def actualizar_proveedor(proveedor_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE proveedores SET razon_social=?, cuit=?, provincia=?, localidad=?, direccion=?, telefono=?, email=?, contacto=?, renspa=?
        WHERE id=?
    """, (datos.get("razon_social"), datos.get("cuit"), datos.get("provincia"), datos.get("localidad"),
          datos.get("direccion"), datos.get("telefono"), datos.get("email"), datos.get("contacto"),
          datos.get("renspa"), proveedor_id))
    conn.commit()
    conn.close()


def eliminar_proveedor(proveedor_id):
    conn = get_connection()
    conn.execute("UPDATE proveedores SET activo=0 WHERE id=?", (proveedor_id,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE CORRALES
# ═══════════════════════════════════════════════════════════════

def listar_corrales(especie=None):
    conn = get_connection()
    cur = conn.cursor()
    if especie:
        cur.execute("SELECT * FROM corrales WHERE estado='activo' AND (especie=? OR especie='mixto') ORDER BY numero", (especie,))
    else:
        cur.execute("SELECT * FROM corrales WHERE estado='activo' ORDER BY numero")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def actualizar_ocupacion_corral(corral_id, delta):
    conn = get_connection()
    conn.execute("UPDATE corrales SET ocupacion = ocupacion + ? WHERE id=?", (delta, corral_id))
    conn.commit()
    conn.close()


def get_corral_by_id(corral_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM corrales WHERE id=?", (corral_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE TROPAS
# ═══════════════════════════════════════════════════════════════

def get_proxima_tropa(especie):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT prox_tropa_bovino, prox_tropa_equino FROM configuracion WHERE id=1")
    row = cur.fetchone()
    conn.close()
    anio = datetime.now().year
    if especie == "bovino":
        return f"B-{anio}-{row['prox_tropa_bovino']:05d}"
    else:
        return f"E-{anio}-{row['prox_tropa_equino']:05d}"


def incrementar_tropa(especie):
    conn = get_connection()
    if especie == "bovino":
        conn.execute("UPDATE configuracion SET prox_tropa_bovino = prox_tropa_bovino + 1 WHERE id=1")
    else:
        conn.execute("UPDATE configuracion SET prox_tropa_equino = prox_tropa_equino + 1 WHERE id=1")
    conn.commit()
    conn.close()


def crear_tropa_paso1(datos):
    conn = get_connection()
    cur = conn.cursor()
    ahora = datetime.now()
    especie = datos.get("especie", "bovino")
    
    cur.execute("""
        INSERT INTO tropas (numero_tropa, especie, proveedor_id, ticket_pesaje_id, fecha_ingreso,
                          procedencia, num_guia, corral_id, estado, paso_actual, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'activo', 2, ?)
    """, (datos.get("numero_tropa"), especie, datos.get("proveedor_id"), datos.get("ticket_pesaje_id"),
          ahora.strftime("%Y-%m-%d"), datos.get("procedencia"), datos.get("num_guia"), 
          datos.get("corral_id"), datos.get("observaciones", "")))
    tropa_id = cur.lastrowid
    
    if datos.get("ticket_pesaje_id"):
        cur.execute("UPDATE tickets_pesaje SET tropa_id=? WHERE id=?", (tropa_id, datos.get("ticket_pesaje_id")))
    
    conn.commit()
    conn.close()
    incrementar_tropa(especie)
    return tropa_id


def actualizar_tropa_cantidad_esperada(tropa_id, cantidad_total):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tropas SET cantidad_esperada=?, paso_actual=3 WHERE id=?", 
                (cantidad_total, tropa_id))
    conn.commit()
    conn.close()


def guardar_tipificaciones_tropa(tropa_id, tipificaciones):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tropa_tipificaciones WHERE tropa_id=?", (tropa_id,))
    
    for tipif, cantidad in tipificaciones.items():
        if cantidad > 0:
            cur.execute("""
                INSERT INTO tropa_tipificaciones (tropa_id, tipificacion, cantidad_esperada, cantidad_registrada)
                VALUES (?, ?, ?, 0)
            """, (tropa_id, tipif, cantidad))
    
    conn.commit()
    conn.close()


def get_tipificaciones_tropa(tropa_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tropa_tipificaciones WHERE tropa_id=?", (tropa_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_tropas(filtros=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT t.*, p.razon_social as proveedor, c.numero as corral_num FROM tropas t LEFT JOIN proveedores p ON t.proveedor_id=p.id LEFT JOIN corrales c ON t.corral_id=c.id WHERE 1=1"
    params = []
    if filtros:
        if filtros.get("especie"):
            query += " AND t.especie=?"
            params.append(filtros["especie"])
        if filtros.get("estado"):
            query += " AND t.estado=?"
            params.append(filtros["estado"])
    query += " ORDER BY t.id DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def listar_tropas_activas(especie=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT t.*, p.razon_social as proveedor, c.numero as corral_num FROM tropas t LEFT JOIN proveedores p ON t.proveedor_id=p.id LEFT JOIN corrales c ON t.corral_id=c.id WHERE t.paso_actual=3"
    params = []
    if especie:
        query += " AND t.especie=?"
        params.append(especie)
    query += " ORDER BY t.id DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_tropa_by_id(tropa_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT t.*, p.razon_social as proveedor, c.numero as corral_num FROM tropas t LEFT JOIN proveedores p ON t.proveedor_id=p.id LEFT JOIN corrales c ON t.corral_id=c.id WHERE t.id=?", (tropa_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_tropa_by_numero(numero_tropa):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tropas WHERE numero_tropa=?", (numero_tropa,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def finalizar_tropa(tropa_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM animales WHERE tropa_id=? AND estado='en_corral'", (tropa_id,))
    row = cur.fetchone()
    cantidad = row['total'] if row else 0
    cur.execute("SELECT SUM(peso_vivo) as total FROM animales WHERE tropa_id=? AND estado='en_corral'", (tropa_id,))
    row = cur.fetchone()
    peso_total = row['total'] if row and row['total'] else 0
    cur.execute("UPDATE tropas SET estado='en_corral', paso_actual=4, cantidad_cabezas=?, peso_total=? WHERE id=?", 
                (cantidad, peso_total, tropa_id))
    conn.commit()
    conn.close()
    return cantidad


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE ANIMALES
# ═══════════════════════════════════════════════════════════════

def get_proximo_numero_animal(numero_tropa):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(numero_correlativo) as max_num FROM animales WHERE numero_tropa=?", (numero_tropa,))
    row = cur.fetchone()
    max_num = row['max_num'] or 0
    conn.close()
    return max_num + 1


def guardar_animal(datos):
    conn = get_connection()
    cur = conn.cursor()
    ahora = datetime.now()
    numero_tropa = datos.get("numero_tropa")
    num_corr = datos.get("numero_correlativo", 1)
    codigo = f"{numero_tropa}-{num_corr:03d}"
    
    cur.execute("""
        INSERT INTO animales (codigo, numero_tropa, numero_correlativo, tropa_id, caravana, especie,
                            tipificacion, raza, gordura, pelaje, corral_id, proveedor_id,
                            peso_vivo, fecha_pesaje, hora_pesaje, fecha_ingreso, estado, etiqueta_impresa, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'en_corral', 0, ?)
    """, (codigo, numero_tropa, num_corr, datos.get("tropa_id"), datos.get("caravana"), datos.get("especie"),
          datos.get("tipificacion"), datos.get("raza"), datos.get("gordura"), datos.get("pelaje"),
          datos.get("corral_id"), datos.get("proveedor_id"), datos.get("peso_vivo"),
          datos.get("fecha_pesaje"), ahora.strftime("%H:%M:%S"), ahora.strftime("%Y-%m-%d"),
          datos.get("observaciones", "")))
    animal_id = cur.lastrowid
    
    if datos.get("tipificacion") and datos.get("tropa_id"):
        cur.execute("""
            UPDATE tropa_tipificaciones 
            SET cantidad_registrada = cantidad_registrada + 1
            WHERE tropa_id=? AND tipificacion=?
        """, (datos.get("tropa_id"), datos.get("tipificacion")))
    
    if datos.get("corral_id"):
        cur.execute("UPDATE corrales SET ocupacion = ocupacion + 1 WHERE id=?", (datos.get("corral_id"),))
    
    conn.commit()
    conn.close()
    return animal_id, codigo


def marcar_etiqueta_impresa(animal_id):
    conn = get_connection()
    conn.execute("UPDATE animales SET etiqueta_impresa=1 WHERE id=?", (animal_id,))
    conn.commit()
    conn.close()


def listar_animales(filtros=None):
    conn = get_connection()
    cur = conn.cursor()
    query = """SELECT a.*, c.numero as corral_num, p.razon_social as proveedor 
               FROM animales a 
               LEFT JOIN corrales c ON a.corral_id=c.id 
               LEFT JOIN proveedores p ON a.proveedor_id=p.id 
               WHERE 1=1"""
    params = []
    if filtros:
        if filtros.get("tropa_id"):
            query += " AND a.tropa_id=?"
            params.append(filtros["tropa_id"])
        if filtros.get("numero_tropa"):
            query += " AND a.numero_tropa=?"
            params.append(filtros["numero_tropa"])
        if filtros.get("especie"):
            query += " AND a.especie=?"
            params.append(filtros["especie"])
        if filtros.get("estado"):
            query += " AND a.estado=?"
            params.append(filtros["estado"])
    query += " ORDER BY a.numero_correlativo"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_animal_by_id(animal_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT a.*, c.numero as corral_num FROM animales a LEFT JOIN corrales c ON a.corral_id=c.id WHERE a.id=?", (animal_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_animal_by_codigo(codigo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM animales WHERE codigo=?", (codigo,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def actualizar_animal(animal_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE animales SET tipificacion=?, raza=?, gordura=?, pelaje=?, peso_vivo=?, observaciones=?
        WHERE id=?
    """, (datos.get("tipificacion"), datos.get("raza"), datos.get("gordura"),
          datos.get("pelaje"), datos.get("peso_vivo"), datos.get("observaciones"), animal_id))
    conn.commit()
    conn.close()


def eliminar_animal(animal_id, operador="", motivo=""):
    conn = get_connection()
    cur = conn.cursor()
    ahora = datetime.now()
    cur.execute("SELECT * FROM animales WHERE id=?", (animal_id,))
    animal = cur.fetchone()
    if not animal:
        conn.close()
        return False
    
    cur.execute("""
        INSERT INTO numeros_eliminados (numero_tropa, numero_correlativo, animal_id, fecha_eliminacion, hora_eliminacion, operador, motivo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (animal['numero_tropa'], animal['numero_correlativo'], animal_id,
          ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S"), operador, motivo))
    
    if animal['tipificacion'] and animal['tropa_id']:
        cur.execute("""
            UPDATE tropa_tipificaciones 
            SET cantidad_registrada = cantidad_registrada - 1
            WHERE tropa_id=? AND tipificacion=?
        """, (animal['tropa_id'], animal['tipificacion']))
    
    if animal['corral_id']:
        cur.execute("UPDATE corrales SET ocupacion = ocupacion - 1 WHERE id=?", (animal['corral_id'],))
    
    cur.execute("UPDATE animales SET estado='eliminado' WHERE id=?", (animal_id,))
    conn.commit()
    conn.close()
    return True


def contar_animales_tropa(tropa_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM animales WHERE tropa_id=? AND estado='en_corral'", (tropa_id,))
    row = cur.fetchone()
    conn.close()
    return row['total'] if row else 0


def contar_animales_tropa_todos(tropa_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM animales WHERE tropa_id=?", (tropa_id,))
    row = cur.fetchone()
    conn.close()
    return row['total'] if row else 0
