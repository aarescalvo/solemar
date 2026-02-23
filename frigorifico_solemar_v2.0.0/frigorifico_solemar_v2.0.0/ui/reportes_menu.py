"""
Módulo de Reportes Generales
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from core import theme as T
from core.database import listar_tickets, listar_tropas, listar_faenas, listar_despachos

class ReportesMenu(tk.Frame):
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
        tk.Label(header, text="📊 REPORTES GENERALES", font=T.FONT_SUBTITULO, bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)

        self.container = tk.Frame(self, bg=T.FONDO)
        self.container.pack(expand=True, fill="both")
        self._show_main_menu()

    def _show_main_menu(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both", padx=50, pady=30)

        tk.Label(self._current, text="Seleccione tipo de reporte:", font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.TEXTO).pack(pady=30)

        cards_frame = tk.Frame(self._current, bg=T.FONDO)
        cards_frame.pack(expand=True)

        opciones = [
            ("⚖️ PESAJES", "Reportes de tickets de pesaje", self._show_pesajes, T.AZUL),
            ("🐄 TROPAS", "Reportes de tropas recibidas", self._show_tropas, T.VERDE),
            ("🏥 FAENA", "Reportes de faena", self._show_faena, T.ROJO),
            ("📦 DESPACHOS", "Reportes de despachos", self._show_despachos, T.GRIS_OSCURO),
        ]

        for i, (titulo, desc, cmd, color) in enumerate(opciones):
            self._make_card(cards_frame, titulo, desc, cmd, color, i // 2, i % 2)

    def _make_card(self, parent, titulo, desc, cmd, color, row, col):
        outer = tk.Frame(parent, bg=T.FONDO, width=250, height=140)
        outer.grid(row=row, column=col, padx=15, pady=15)
        outer.grid_propagate(False)

        card = tk.Frame(outer, bg=T.BLANCO, relief="solid", bd=1, cursor="hand2")
        card.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(card, text=titulo, font=T.FONT_BOTON, bg=T.BLANCO, fg=color).pack(pady=(25, 5))
        tk.Label(card, text=desc, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=5)

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

    def _clear_current(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both")

    def _show_pesajes(self):
        self._clear_current()
        self._show_tabla("PESAJES", listar_tickets, ["ticket", "fecha", "tipo", "patente", "transportista", "peso"],
                         {"ticket": ("Ticket", 120), "fecha": ("Fecha", 120), "tipo": ("Tipo", 60),
                          "patente": ("Patente", 100), "transportista": ("Transportista", 150), "peso": ("Peso kg", 80)})

    def _show_tropas(self):
        self._clear_current()
        self._show_tabla("TROPAS", listar_tropas, ["tropa", "fecha", "especie", "cantidad", "proveedor"],
                         {"tropa": ("Tropa", 120), "fecha": ("Fecha", 100), "especie": ("Especie", 80),
                          "cantidad": ("Cant.", 60), "proveedor": ("Proveedor", 200)})

    def _show_faena(self):
        self._clear_current()
        self._show_tabla("FAENA", listar_faenas, ["faena", "fecha", "especie", "peso_vivo", "peso_canal", "rendimiento"],
                         {"faena": ("Faena", 100), "fecha": ("Fecha", 100), "especie": ("Especie", 70),
                          "peso_vivo": ("P.Vivo", 80), "peso_canal": ("P.Canal", 80), "rendimiento": ("Rend.%", 60)})

    def _show_despachos(self):
        self._clear_current()
        self._show_tabla("DESPACHOS", listar_despachos, ["remito", "fecha", "cliente", "patente", "peso"],
                         {"remito": ("Remito", 120), "fecha": ("Fecha", 100), "cliente": ("Cliente", 150),
                          "patente": ("Patente", 80), "peso": ("Peso kg", 80)})

    def _show_tabla(self, titulo, funcion_datos, campos, headers_config):
        header = tk.Frame(self._current, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._show_main_menu).pack(side="left", padx=10, pady=8)
        tk.Label(header, text=f"📋 {titulo}", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        tabla_frame = tk.Frame(self._current, bg=T.BLANCO, relief="solid", bd=1)
        tabla_frame.pack(expand=True, fill="both", padx=20, pady=15)

        scroll = ttk.Scrollbar(tabla_frame)
        scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(tabla_frame, columns=campos, show="headings", yscrollcommand=scroll.set, height=25)

        for col_id, (text, width) in headers_config.items():
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, minwidth=50)

        scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        # Cargar datos
        datos = funcion_datos()
        for d in datos:
            valores = []
            for campo in campos:
                val = d.get(campo, '')
                if isinstance(val, float):
                    val = f"{val:,.0f}"
                valores.append(val)
            self.tree.insert("", "end", values=valores)

        tk.Label(self._current, text=f"{len(datos)} registros", font=T.FONT_LABEL, bg=T.FONDO, fg=T.GRIS_OSCURO).pack(anchor="w", padx=20, pady=5)

    def _back(self):
        self.master._show_menu()
