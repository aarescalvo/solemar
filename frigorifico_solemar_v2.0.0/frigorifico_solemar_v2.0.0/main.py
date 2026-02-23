"""
Main - Frigorifico Solemar v2.0.0
Sistema de Trazabilidad para Frigorificos

Estructura de modulos:
- Pesaje (modulo individual)
- Ciclo I: Recepcion, Faena, Stock, Configuracion
- Ciclo II: Desposte, Stock, Configuracion, Reportes
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import theme as T
from core.database import init_db
from core.session import Sesion


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Frigorifico Solemar - v2.0.0")
        self.geometry("1280x800")
        self.configure(bg=T.FONDO)

        try:
            init_db()
        except Exception as e:
            messagebox.showerror("Error", f"Error BD: {e}")
            return

        self._show_login()

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _show_login(self):
        self._clear()
        from ui.login import LoginScreen
        LoginScreen(self, self._show_menu).pack(fill="both", expand=True)

    def _show_menu(self):
        self._clear()
        from ui.menu import MenuScreen
        MenuScreen(self, self._show_login).pack(fill="both", expand=True)

    def _go_modulo(self, modulo):
        self._clear()

        if modulo == "pesaje":
            from ui.pesaje_menu import PesajeMenu
            PesajeMenu(self, self._show_menu).pack(fill="both", expand=True)
        elif modulo == "ciclo1":
            from ui.ciclo1_menu import Ciclo1Menu
            Ciclo1Menu(self, self._show_menu).pack(fill="both", expand=True)
        elif modulo == "ciclo2":
            from ui.ciclo2_menu import Ciclo2Menu
            Ciclo2Menu(self, self._show_menu).pack(fill="both", expand=True)
        # Modulos directos (para compatibilidad)
        elif modulo == "recepcion":
            from ui.recepcion_menu import RecepcionMenu
            RecepcionMenu(self, self._show_menu).pack(fill="both", expand=True)
        elif modulo == "faena":
            from ui.faena_menu import FaenaMenu
            FaenaMenu(self, self._show_menu).pack(fill="both", expand=True)
        elif modulo == "camaras":
            from ui.camaras_menu import CamarasMenu
            CamarasMenu(self, self._show_menu).pack(fill="both", expand=True)
        elif modulo == "desposte":
            from ui.desposte_menu import DesposteMenu
            DesposteMenu(self, self._show_menu).pack(fill="both", expand=True)
        elif modulo == "stock":
            from ui.stock_menu import StockMenu
            StockMenu(self, self._show_menu).pack(fill="both", expand=True)
        elif modulo == "reportes":
            from ui.reportes_menu import ReportesMenu
            ReportesMenu(self, self._show_menu).pack(fill="both", expand=True)
        elif modulo == "config":
            from ui.config_menu import ConfigMenu
            ConfigMenu(self, self._show_menu).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
