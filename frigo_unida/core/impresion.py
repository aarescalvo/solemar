"""
Módulo de Impresión - Frigorífico Solemar
Impresión de etiquetas para animales con impresora Datamax
Etiqueta de 4 datos: N° Tropa, N° Animal, Año, Kilogramos
"""

import os
import time
from datetime import datetime

# Intentar importar winsound para beep (Windows)
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


class ImpresoraDatamax:
    """
    Clase para manejar impresión de etiquetas con impresora Datamax.
    Soporta impresión directa por puerto paralelo/LPT o USB.
    """
    
    def __init__(self, puerto='LPT1', tipo='datamax', ancho=50, alto=25):
        self.puerto = puerto
        self.tipo = tipo.lower()
        self.ancho = ancho  # mm
        self.alto = alto    # mm
        self._connected = False
        self._archivo_temp = None
        
    def conectar(self):
        """Verifica que la impresora esté disponible"""
        try:
            # Intentar abrir el puerto para escritura
            if self.puerto.startswith('LPT') or self.puerto.startswith('COM'):
                # Puerto paralelo/serial - verificar si existe
                if os.name == 'nt':  # Windows
                    # En Windows, intentamos escribir para verificar
                    try:
                        with open(self.puerto, 'wb') as f:
                            pass
                        self._connected = True
                        print(f"✅ Impresora Datamax conectada en {self.puerto}")
                        return True
                    except:
                        # Si no puede escribir directo, usar spooler
                        print(f"⚠️ Usando spooler de Windows para {self.puerto}")
                        self._connected = True
                        return True
                else:  # Linux
                    ruta = f"/dev/{self.puerto.lower()}"
                    if os.path.exists(ruta):
                        self._connected = True
                        print(f"✅ Impresora conectada en {ruta}")
                        return True
            else:
                # Ruta de archivo o impresora de red
                self._connected = True
                print(f"✅ Impresora configurada: {self.puerto}")
                return True
                
        except Exception as e:
            print(f"❌ Error conectando impresora: {e}")
            # Modo simulación
            self._connected = True
            print("⚠️ Impresora en modo simulación")
            return True
    
    def desconectar(self):
        """Desconecta la impresora"""
        self._connected = False
        print("🔌 Impresora desconectada")
    
    def generar_zpl_etiqueta(self, tropa, numero_animal, año, kilogramos):
        """
        Genera código ZPL para etiqueta de 4 datos.
        Formato de etiqueta pequeña (50x25mm)
        """
        # Formatear datos
        tropa_str = str(tropa)
        num_str = str(numero_animal).zfill(3)
        año_str = str(año)
        kg_str = f"{kilogramos:.0f}"
        
        # Código ZPL para Datamax (compatible con ZPL)
        zpl = f"""
^XA
^FX Etiqueta Animal - Frigorifico Solemar
^PW400
^LL200

^FO30,20^A0N,28,28^FDTROPA:^FS
^FO120,20^A0N,28,28^FD{tropa_str}^FS

^FO30,60^A0N,28,28^FDANIMAL:^FS
^FO130,60^A0N,28,28^FD{num_str}^FS

^FO30,100^A0N,28,28^FDAÑO:^FS
^FO100,100^A0N,28,28^FD{año_str}^FS

^FO30,140^A0N,28,28^FDKG:^FS
^FO90,140^A0N,28,28^FD{kg_str}^FS

^XZ
"""
        return zpl.strip()
    
    def generar_dpl_etiqueta(self, tropa, numero_animal, año, kilogramos):
        """
        Genera código DPL (Datamax Programming Language) para etiqueta.
        Alternativa a ZPL para impresoras Datamax nativas.
        """
        tropa_str = str(tropa)
        num_str = str(numero_animal).zfill(3)
        año_str = str(año)
        kg_str = f"{kilogramos:.0f}"
        
        # Código DPL para Datamax
        dpl = f"""
<STX>D<s1>ES<ETX>
<STX>L<CR>
<STX>11<CR>
<STX>H08<CR>
<STX>Pc<CR>
<STX>121100001060010TROPA: {tropa_str}<CR>
<STX>121100001080010ANIMAL: {num_str}<CR>
<STX>121100001100010AÑO: {año_str}<CR>
<STX>121100001120010KG: {kg_str}<CR>
<STX>E<CR>
"""
        return dpl.strip()
    
    def generar_etiqueta_simple(self, tropa, numero_animal, año, kilogramos):
        """
        Genera una etiqueta en formato texto simple.
        Útil para pruebas o impresoras térmicas básicas.
        """
        num_str = str(numero_animal).zfill(3)
        
        etiqueta = f"""
╔══════════════════════════╗
║    FRIGORIFICO SOLEMAR   ║
╠══════════════════════════╣
║ TROPA:    {tropa:>14} ║
║ ANIMAL:   {num_str:>14} ║
║ AÑO:      {año:>14} ║
║ KG:       {kilogramos:>14.0f} ║
╚══════════════════════════╝
"""
        return etiqueta
    
    def imprimir(self, tropa, numero_animal, año, kilogramos, formato='zpl'):
        """
        Imprime una etiqueta con los 4 datos básicos.
        
        Args:
            tropa: Número de tropa (ej: B-2026-00001)
            numero_animal: Número correlativo del animal (1, 2, 3...)
            año: Año de ingreso
            kilogramos: Peso vivo en kg
            formato: 'zpl', 'dpl' o 'simple'
            
        Returns:
            bool: True si se imprimió correctamente
        """
        if not self._connected:
            print("❌ Impresora no conectada")
            return False
        
        # Generar código según formato
        if formato == 'zpl':
            codigo = self.generar_zpl_etiqueta(tropa, numero_animal, año, kilogramos)
        elif formato == 'dpl':
            codigo = self.generar_dpl_etiqueta(tropa, numero_animal, año, kilogramos)
        else:
            codigo = self.generar_etiqueta_simple(tropa, numero_animal, año, kilogramos)
        
        try:
            # Intentar imprimir directamente al puerto
            if self.puerto.startswith('LPT') or self.puerto.startswith('COM'):
                try:
                    # Windows - escritura directa al puerto
                    with open(self.puerto, 'wb') as f:
                        f.write(codigo.encode('ascii', errors='replace'))
                    print(f"✅ Etiqueta enviada a {self.puerto}")
                    self._beep_ok()
                    return True
                except PermissionError:
                    # Si falla, usar método alternativo con spooler
                    return self._imprimir_spooler(codigo)
                except Exception as e:
                    print(f"⚠️ Error escritura directa: {e}")
                    return self._imprimir_archivo_temp(codigo)
            else:
                # Imprimir a archivo o ruta de red
                return self._imprimir_archivo_temp(codigo)
                
        except Exception as e:
            print(f"❌ Error imprimiendo: {e}")
            return False
    
    def _imprimir_spooler(self, codigo):
        """Imprime usando el spooler de Windows"""
        try:
            import subprocess
            import tempfile
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.prn', delete=False) as f:
                f.write(codigo)
                temp_path = f.name
            
            # Enviar a impresora con copy
            if os.name == 'nt':
                cmd = f'copy /b "{temp_path}" {self.puerto}'
                subprocess.run(cmd, shell=True, check=True)
            
            # Eliminar archivo temporal
            os.unlink(temp_path)
            
            print("✅ Etiqueta enviada al spooler")
            self._beep_ok()
            return True
            
        except Exception as e:
            print(f"❌ Error spooler: {e}")
            return False
    
    def _imprimir_archivo_temp(self, codigo):
        """Guarda en archivo temporal para impresión manual o simulación"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"etiqueta_{timestamp}.prn"
            
            # Crear directorio si no existe
            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'etiquetas')
            os.makedirs(temp_dir, exist_ok=True)
            
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w', encoding='ascii', errors='replace') as f:
                f.write(codigo)
            
            print(f"📄 Etiqueta guardada en: {filepath}")
            print(f"   Contenido: Tropa={codigo.split('TROPA')[1][:20] if 'TROPA' in codigo else 'N/A'}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando archivo: {e}")
            return False
    
    def _beep_ok(self):
        """Emite un beep de confirmación"""
        if WINSOUND_AVAILABLE:
            try:
                winsound.Beep(1000, 200)  # 1000Hz por 200ms
            except:
                pass
    
    def reimprimir(self, codigo_animal, tropa, numero_animal, año, kilogramos):
        """
        Reimprime una etiqueta existente.
        Mismo que imprimir pero con logging diferente.
        """
        print(f"🔄 Reimprimiendo etiqueta para animal {codigo_animal}")
        return self.imprimir(tropa, numero_animal, año, kilogramos)
    
    def imprimir_test(self):
        """Imprime una etiqueta de prueba"""
        print("🧪 Imprimiendo etiqueta de prueba...")
        return self.imprimir(
            tropa="B-2026-00001",
            numero_animal=999,
            año=2026,
            kilogramos=500,
            formato='zpl'
        )
    
    def esta_conectado(self):
        """Verifica si la impresora está lista"""
        return self._connected


class GestorImpresion:
    """
    Gestor centralizado de impresión.
    Mantiene instancia singleton de la impresora.
    """
    
    _instance = None
    _impresora = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_impresora(cls, config=None):
        """Obtiene o crea instancia de impresora"""
        if cls._impresora is None:
            if config is None:
                config = {
                    'puerto': 'LPT1',
                    'tipo': 'datamax',
                    'ancho': 50,
                    'alto': 25
                }
            cls._impresora = ImpresoraDatamax(
                puerto=config.get('puerto', 'LPT1'),
                tipo=config.get('tipo', 'datamax'),
                ancho=config.get('ancho', 50),
                alto=config.get('alto', 25)
            )
        return cls._impresora
    
    @classmethod
    def conectar(cls, config=None):
        """Conecta la impresora"""
        impresora = cls.get_impresora(config)
        return impresora.conectar()
    
    @classmethod
    def imprimir_etiqueta(cls, tropa, numero_animal, año, kilogramos):
        """Imprime una etiqueta"""
        impresora = cls.get_impresora()
        if not impresora.esta_conectado():
            impresora.conectar()
        return impresora.imprimir(tropa, numero_animal, año, kilogramos)
    
    @classmethod
    def reimprimir_etiqueta(cls, codigo_animal, tropa, numero_animal, año, kilogramos):
        """Reimprime una etiqueta"""
        impresora = cls.get_impresora()
        if not impresora.esta_conectado():
            impresora.conectar()
        return impresora.reimprimir(codigo_animal, tropa, numero_animal, año, kilogramos)


# Funciones de conveniencia
def imprimir_etiqueta_animal(tropa, numero_animal, año, kilogramos):
    """
    Función simple para imprimir etiqueta de animal.
    Conecta automáticamente si es necesario.
    """
    return GestorImpresion.imprimir_etiqueta(tropa, numero_animal, año, kilogramos)


def generar_vista_previa_etiqueta(tropa, numero_animal, año, kilogramos):
    """
    Genera una vista previa en texto de la etiqueta.
    Útil para mostrar en pantalla antes de imprimir.
    """
    num_str = str(numero_animal).zfill(3)
    
    preview = f"""
    ┌─────────────────────────────────┐
    │      FRIGORIFICO SOLEMAR        │
    ├─────────────────────────────────┤
    │  TROPA:     {tropa:>18}   │
    │  ANIMAL:    {num_str:>18}   │
    │  AÑO:       {año:>18}   │
    │  KG:        {kilogramos:>18.0f}   │
    └─────────────────────────────────┘
    """
    return preview
