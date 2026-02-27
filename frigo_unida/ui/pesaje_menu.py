"""
Módulo de Pesaje - Menú
"""
import tkinter as tk
from core import theme as T
from core.session import Sesion

class PesajeMenu(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._current = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.VERDE, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._back).pack(side="left", padx=15, pady=12)
        tk.Label(header, text="⚖️ MÓDULO DE PESAJE", font=T.FONT_SUBTITULO, bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)
        tk.Label(header, text=f"👤 {Sesion.nombre_usuario()}", font=T.FONT_NORMAL, bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="right", padx=20)

        self.container = tk.Frame(self, bg=T.FONDO)
        self.container.pack(expand=True, fill="both")
        self._show_main_menu()

    def _show_main_menu(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both", padx=50, pady=30)

        tk.Label(self._current, text="Seleccione una opción:", font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.TEXTO).pack(pady=30)

        cards_frame = tk.Frame(self._current, bg=T.FONDO)
        cards_frame.pack(expand=True)

        opciones = [
            ("📥 INGRESO", "Pesajes de entrada", self._show_ingreso, T.AZUL),
            ("📤 EGRESO", "Pesajes de salida", self._show_egreso, T.VERDE),
            ("📊 REPORTES", "Consultar tickets", self._show_reportes, T.ROJO),
        ]

        for i, (titulo, desc, cmd, color) in enumerate(opciones):
            self._make_card(cards_frame, titulo, desc, cmd, color, i // 2, i % 2)

    def _make_card(self, parent, titulo, desc, cmd, color, row, col):
        outer = tk.Frame(parent, bg=T.FONDO, width=240, height=120)
        outer.grid(row=row, column=col, padx=15, pady=15)
        outer.grid_propagate(False)

        card = tk.Frame(outer, bg=T.BLANCO, relief="solid", bd=1, cursor="hand2")
        card.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(card, text=titulo, font=T.FONT_BOTON, bg=T.BLANCO, fg=color).pack(pady=(16, 4))
        tk.Label(card, text=desc, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=4)

        bottom = tk.Frame(card, bg=color, height=4)
        bottom.pack(fill="x", side="bottom")

        def on_click(e):
            if cmd:
                cmd()

        def on_enter(e):
            card.configure(bg=T.GRIS_CLARO)

        def on_leave(e):
            card.configure(bg=T.BLANCO)

        card.bind("<Button-1>", on_click)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        for child in card.winfo_children():
            child.bind("<Button-1>", on_click)

        parent.columnconfigure(col, weight=1)
        parent.rowconfigure(row, weight=1)

    def _clear_current(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both")

    def _show_ingreso(self):
        self._clear_current()
        from ui.pesaje_ingreso import PesajeIngreso
        PesajeIngreso(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_egreso(self):
        self._clear_current()
        from ui.pesaje_egreso import PesajeEgreso
        PesajeEgreso(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_reportes(self):
        self._clear_current()
        from ui.pesaje_reportes import PesajeReportes
        PesajeReportes(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_config(self):
        self._clear_current()
        from ui.config_menu import ConfigMenu
        ConfigMenu(self._current, self._show_main_menu, start_view="tickets").pack(expand=True, fill="both")

    def _back(self):
        self.master._show_menu()
