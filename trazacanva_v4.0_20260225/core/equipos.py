"""
Módulo de Equipos - Frigorífico Solemar
Manejo de conexiones con:
- Balanza (RS232)
- Bastón electrónico RFID
"""

import threading
import queue
import time
import re

# Intentar importar serial, si no está disponible usar simulación
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("⚠️ pyserial no instalado. Usando modo simulación.")


class BalanzaRS232:
    """
    Clase para manejar conexión con balanza vía RS232.
    Soporta lectura continua y captura bajo demanda.
    """
    
    def __init__(self, puerto='COM1', baudrate=9600, timeout=1):
        self.puerto = puerto
        self.baudrate = baudrate
        self.timeout = timeout
        self.conexion = None
        self._lectura_continua = False
        self._thread = None
        self._cola_lecturas = queue.Queue()
        self._ultimo_peso = 0
        self._connected = False
        
    def conectar(self):
        """Establece conexión con la balanza"""
        if not SERIAL_AVAILABLE:
            print(f"📡 Balanza: Modo simulación activado ({self.puerto})")
            self._connected = True
            return True
            
        try:
            self.conexion = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self._connected = True
            print(f"✅ Balanza conectada en {self.puerto}")
            return True
        except Exception as e:
            print(f"❌ Error conectando balanza: {e}")
            self._connected = False
            return False
    
    def desconectar(self):
        """Cierra la conexión con la balanza"""
        self._lectura_continua = False
        if self._thread:
            self._thread.join(timeout=2)
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
        self._connected = False
        print("🔌 Balanza desconectada")
    
    def _leer_linea(self):
        """Lee una línea de la balanza"""
        if not SERIAL_AVAILABLE:
            # Simulación: retorna peso aleatorio
            import random
            return f"{random.randint(300, 600)}"
            
        if not self.conexion or not self.conexion.is_open:
            return None
            
        try:
            linea = self.conexion.readline().decode('ascii').strip()
            return linea
        except Exception as e:
            print(f"Error lectura balanza: {e}")
            return None
    
    def _parsear_peso(self, linea):
        """
        Parsea el peso desde la línea leída.
        Soporta varios formatos comunes de balanzas.
        """
        if not linea:
            return None
            
        # Remover caracteres no numéricos excepto punto y signo
        # Formato común: "   456.8 kg" o "ST,GS,+000456.8kg" o "456.8"
        
        # Intentar extraer número
        match = re.search(r'[\+\-]?(\d+\.?\d*)', linea.replace(',', '.'))
        if match:
            try:
                peso = float(match.group(1))
                return peso
            except ValueError:
                return None
        return None
    
    def capturar_peso(self):
        """
        Captura un peso de la balanza.
        Retorna el peso en kg o None si hay error.
        """
        if not self._connected:
            return None
            
        # Si está en lectura continua, obtener de la cola
        if self._lectura_continua:
            try:
                peso = self._cola_lecturas.get(timeout=2)
                return peso
            except queue.Empty:
                return self._ultimo_peso
        
        # Lectura única
        linea = self._leer_linea()
        peso = self._parsear_peso(linea)
        if peso is not None:
            self._ultimo_peso = peso
        return peso
    
    def iniciar_lectura_continua(self, callback=None):
        """
        Inicia lectura continua de la balanza.
        callback: función que recibe el peso cada vez que se lee
        """
        if self._lectura_continua:
            return
            
        self._lectura_continua = True
        
        def _thread_lectura():
            while self._lectura_continua:
                peso = self.capturar_peso()
                if peso is not None:
                    self._ultimo_peso = peso
                    try:
                        self._cola_lecturas.put(peso, timeout=0.1)
                    except queue.Full:
                        pass
                    if callback:
                        callback(peso)
                time.sleep(0.1)
        
        self._thread = threading.Thread(target=_thread_lectura, daemon=True)
        self._thread.start()
        print("📊 Lectura continua de balanza iniciada")
    
    def detener_lectura_continua(self):
        """Detiene la lectura continua"""
        self._lectura_continua = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
        print("⏹️ Lectura continua detenida")
    
    def get_ultimo_peso(self):
        """Retorna el último peso leído"""
        return self._ultimo_peso
    
    def esta_conectado(self):
        """Verifica si la balanza está conectada"""
        if SERIAL_AVAILABLE:
            return self.conexion and self.conexion.is_open
        return self._connected


class BastonRFID:
    """
    Clase para manejar conexión con bastón electrónico RFID.
    Para lectura de caravanas electrónicas.
    """
    
    def __init__(self, puerto='COM2', baudrate=9600, timeout=1):
        self.puerto = puerto
        self.baudrate = baudrate
        self.timeout = timeout
        self.conexion = None
        self._connected = False
        self._ultima_lectura = ""
        self._callback_lectura = None
        self._thread_lectura = None
        self._leyendo = False
        
    def conectar(self):
        """Establece conexión con el bastón RFID"""
        if not SERIAL_AVAILABLE:
            print(f"📡 RFID: Modo simulación activado ({self.puerto})")
            self._connected = True
            return True
            
        try:
            self.conexion = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self._connected = True
            print(f"✅ Bastón RFID conectado en {self.puerto}")
            return True
        except Exception as e:
            print(f"❌ Error conectando RFID: {e}")
            self._connected = False
            return False
    
    def desconectar(self):
        """Cierra la conexión con el bastón"""
        self._leyendo = False
        if self._thread_lectura:
            self._thread_lectura.join(timeout=2)
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
        self._connected = False
        print("🔌 Bastón RFID desconectado")
    
    def _leer_tag(self):
        """Lee un tag RFID"""
        if not SERIAL_AVAILABLE:
            # Simulación: retorna un número de caravana aleatorio
            import random
            return f"CAR{random.randint(100000, 999999)}"
            
        if not self.conexion or not self.conexion.is_open:
            return None
            
        try:
            linea = self.conexion.readline().decode('ascii').strip()
            return linea
        except Exception as e:
            print(f"Error lectura RFID: {e}")
            return None
    
    def capturar_caravana(self, timeout=5):
        """
        Espera a que se lea una caravana.
        timeout: tiempo máximo de espera en segundos
        """
        if not self._connected:
            return None
            
        inicio = time.time()
        while time.time() - inicio < timeout:
            tag = self._leer_tag()
            if tag:
                self._ultima_lectura = tag
                return tag
            time.sleep(0.1)
        return None
    
    def iniciar_lectura_continua(self, callback):
        """
        Inicia lectura continua del bastón.
        callback: función que recibe la caravana cada vez que se lee
        """
        if self._leyendo:
            return
            
        self._leyendo = True
        self._callback_lectura = callback
        
        def _thread_lectura():
            while self._leyendo:
                tag = self._leer_tag()
                if tag and self._callback_lectura:
                    self._ultima_lectura = tag
                    self._callback_lectura(tag)
                time.sleep(0.1)
        
        self._thread_lectura = threading.Thread(target=_thread_lectura, daemon=True)
        self._thread_lectura.start()
        print("📡 Lectura continua RFID iniciada")
    
    def detener_lectura(self):
        """Detiene la lectura continua"""
        self._leyendo = False
        if self._thread_lectura:
            self._thread_lectura.join(timeout=2)
            self._thread_lectura = None
        print("⏹️ Lectura RFID detenida")
    
    def get_ultima_lectura(self):
        """Retorna la última caravana leída"""
        return self._ultima_lectura
    
    def esta_conectado(self):
        """Verifica si el bastón está conectado"""
        if SERIAL_AVAILABLE:
            return self.conexion and self.conexion.is_open
        return self._connected


class GestorEquipos:
    """
    Gestor centralizado de equipos.
    Mantiene instancias singleton de balanza y RFID.
    """
    
    _instance = None
    _balanza = None
    _rfid = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_balanza(cls, config=None):
        """Obtiene o crea instancia de balanza"""
        if cls._balanza is None:
            if config is None:
                config = {
                    'puerto': 'COM1',
                    'baudrate': 9600,
                    'timeout': 1
                }
            cls._balanza = BalanzaRS232(
                puerto=config.get('puerto', 'COM1'),
                baudrate=config.get('baudrate', 9600),
                timeout=config.get('timeout', 1)
            )
        return cls._balanza
    
    @classmethod
    def get_rfid(cls, config=None):
        """Obtiene o crea instancia de RFID"""
        if cls._rfid is None:
            if config is None:
                config = {
                    'puerto': 'COM2',
                    'baudrate': 9600,
                    'timeout': 1
                }
            cls._rfid = BastonRFID(
                puerto=config.get('puerto', 'COM2'),
                baudrate=config.get('baudrate', 9600),
                timeout=config.get('timeout', 1)
            )
        return cls._rfid
    
    @classmethod
    def conectar_todos(cls, config_balanza=None, config_rfid=None):
        """Conecta todos los equipos"""
        balanza = cls.get_balanza(config_balanza)
        rfid = cls.get_rfid(config_rfid)
        
        balanza_ok = balanza.conectar()
        rfid_ok = rfid.conectar()
        
        return {
            'balanza': balanza_ok,
            'rfid': rfid_ok
        }
    
    @classmethod
    def desconectar_todos(cls):
        """Desconecta todos los equipos"""
        if cls._balanza:
            cls._balanza.desconectar()
            cls._balanza = None
        if cls._rfid:
            cls._rfid.desconectar()
            cls._rfid = None
    
    @classmethod
    def estado_equipos(cls):
        """Retorna el estado de todos los equipos"""
        return {
            'balanza': cls._balanza.esta_conectado() if cls._balanza else False,
            'rfid': cls._rfid.esta_conectado() if cls._rfid else False
        }


# Funciones de conveniencia
def capturar_peso_balanza(timeout=3):
    """
    Función simple para capturar un peso.
    Conecta automáticamente si es necesario.
    """
    gestor = GestorEquipos()
    balanza = gestor.get_balanza()
    
    if not balanza.esta_conectado():
        balanza.conectar()
    
    return balanza.capturar_peso()


def capturar_caravana_rfid(timeout=5):
    """
    Función simple para capturar una caravana.
    Conecta automáticamente si es necesario.
    """
    gestor = GestorEquipos()
    rfid = gestor.get_rfid()
    
    if not rfid.esta_conectado():
        rfid.conectar()
    
    return rfid.capturar_caravana(timeout)
