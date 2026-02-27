#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicio - Frigo Unida
Ejecuta el sistema ERP para Frigorificos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_dependencias():
    """Verifica que las dependencias necesarias esten instaladas"""
    dependencias = {
        'tkinter': 'tkinter (built-in)',
        'reportlab': 'reportlab',
        'PIL': 'pillow',
        'serial': 'pyserial',
    }
    
    faltantes = []
    
    for modulo, paquete in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(paquete)
    
    if faltantes:
        print("=" * 50)
        print("DEPENDENCIAS FALTANTES")
        print("=" * 50)
        print("Faltan los siguientes paquetes:")
        for p in faltantes:
            print(f"  - {p}")
        print("\nEjecute: pip install -r requirements.txt")
        print("=" * 50)
        return False
    
    return True


def main():
    """Funcion principal de inicio"""
    print("=" * 50)
    print("  FRIGO UNIDA v1.0.0")
    print("  Sistema ERP para Frigorificos")
    print("=" * 50)
    print()
    
    # Verificar dependencias
    if not verificar_dependencias():
        input("\nPresione Enter para salir...")
        sys.exit(1)
    
    # Importar y ejecutar la aplicacion
    try:
        # Importar modulos del sistema
        from core import database, session
        from ui import login
        
        print("Iniciando sistema...")
        print()
        
        # Iniciar la aplicacion
        app = login.LoginWindow()
        app.run()
        
    except Exception as e:
        print(f"\nError al iniciar: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresione Enter para salir...")
        sys.exit(1)


if __name__ == "__main__":
    main()
