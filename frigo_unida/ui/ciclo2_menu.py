"""
Ciclo II - Menu
Modulos: Desposte, Stock Ciclo II, Configuracion Ciclo II, Reportes Ciclo II
"""
import tkinter as tk
import os
from core import theme as T
from core.session import Sesion

class Ciclo2Menu(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._current = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.ROJO, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self._back).pack(side="left", padx=15, pady=12)
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            for name in ["logo.png", "logo.jpg", "logo.jpeg", "logo.gif", "Logo.png", "Logo.jpg", "Logo.jpeg", "Logo.gif", "LOGO.png", "LOGO.jpg", "LOGO.jpeg", "LOGO.gif"]:
                path = os.path.join(base_dir, name)
                if os.path.exists(path):
                    try:
                        self._logo_img = tk.PhotoImage(file=path)
                        tk.Label(header, image=self._logo_img, bg=T.ROJO).pack(side="left", padx=4, pady=8)
                    except:
                        pass
                    break
        except:
            pass
        tk.Label(header, text="CICLO II - Desposte y Productos", font=T.FONT_SUBTITULO, 
                 bg=T.ROJO, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)
        tk.Label(header, text=f"{Sesion.nombre_usuario()}", font=T.FONT_NORMAL, 
                 bg=T.ROJO, fg=T.TEXTO_CLARO).pack(side="right", padx=20)

        self.container = tk.Frame(self, bg=T.FONDO)
        self.container.pack(expand=True, fill="both")
        self._show_main_menu()

    def _show_main_menu(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both", padx=50, pady=30)

        tk.Label(self._current, text="Seleccione una opcion:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=25)

        cards_frame = tk.Frame(self._current, bg=T.FONDO)
        cards_frame.pack(expand=True)

        opciones = [
            ("CUARTEO", "Lotes y cuartos", self._show_cuarteo, T.AZUL),
            ("DESPOSTE (MEDIAS)", "Corte desde medias", self._show_desposte, T.ROJO),
            ("DESPOSTE (CUARTOS)", "Órdenes y producción", self._show_desposte_cuartos, T.VERDE),
            ("STOCK CICLO II", "Stock de productos", self._show_stock, T.VERDE),
            ("REPORTES", "Reportes Ciclo II", self._show_reportes, T.GRIS_OSCURO),
        ]

        for i, (titulo, desc, cmd, color) in enumerate(opciones):
            self._make_card(cards_frame, titulo, desc, cmd, color, i // 2, i % 2)

    def _make_card(self, parent, titulo, desc, cmd, color, row, col):
        outer = tk.Frame(parent, bg=T.FONDO, width=240, height=120)
        outer.grid(row=row, column=col, padx=12, pady=12)
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

    def _show_desposte(self):
        self._clear_current()
        from ui.desposte_menu import DesposteMenu
        DesposteMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_cuarteo(self):
        self._clear_current()
        CuarteoMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_desposte_cuartos(self):
        self._clear_current()
        from ui.desposte_cuartos_menu import DesposteCuartosMenu
        DesposteCuartosMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_stock(self):
        self._clear_current()
        from ui.stock_menu import StockMenu
        StockMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_config(self):
        self._clear_current()
        from ui.config_menu import ConfigMenu
        ConfigMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_reportes(self):
        self._clear_current()
        from ui.reportes_menu import ReportesMenu
        ReportesMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _back(self):
        self.master._show_menu()


class CuarteoMenu(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="CUARTEO", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        left = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(left, text="MEDIAS PARA CUARTEAR", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL).pack(pady=8)
        cols = ("codigo", "especie", "media", "peso", "camara")
        self.tree_medias = tk.Treeview(left, columns=cols, show="headings", height=18)
        for cid, text, w in [("codigo", "Código", 140), ("especie", "Especie", 80), ("media", "Media", 80), ("peso", "Peso", 80), ("camara", "Cámara", 100)]:
            self.tree_medias.heading(cid, text=text)
            self.tree_medias.column(cid, width=w, minwidth=50)
        self.tree_medias.pack(fill="both", expand=True, padx=8, pady=8)

        right = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        right.pack(side="right", fill="y")
        tk.Label(right, text="Lote y Cuartos", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE).pack(pady=8)
        top = tk.Frame(right, bg=T.BLANCO)
        top.pack(padx=10, pady=6, fill="x")
        tk.Button(top, text="Crear lote de cuarteo", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._crear_lote).pack(fill="x")
        self.lbl_lote = tk.Label(right, text="Lote: -", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO)
        self.lbl_lote.pack(padx=10, pady=4, anchor="w")

        form = tk.Frame(right, bg=T.BLANCO)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Tipo", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.combo_tipo = tk.StringVar()
        tipos = ["delantero", "trasero", "asado"]
        self.entry_tipo = tk.OptionMenu(form, self.combo_tipo, *tipos)
        self.entry_tipo.configure(bg=T.BLANCO)
        self.entry_tipo.grid(row=0, column=1, padx=4, pady=4)
        tk.Label(form, text="Peso (kg)", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.entry_peso = tk.Entry(form, font=T.FONT_MONO_SMALL, bg=T.GRIS_CLARO, width=12, relief="solid", bd=1, justify="right")
        self.entry_peso.grid(row=1, column=1, padx=4, pady=4)
        tk.Button(form, text="Guardar cuarto", font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._guardar_cuarto).grid(row=2, column=0, columnspan=2, sticky="ew", pady=6)

        self._medias_map = {}
        self._lote_id = None
        self._cargar_medias()

    def _cargar_medias(self):
        from core.database import listar_medias_para_cuartear, listar_camaras
        for item in self.tree_medias.get_children():
            self.tree_medias.delete(item)
        self._medias_map = {}
        cams = {c['id']: c for c in listar_camaras()}
        for m in listar_medias_para_cuartear():
            camara = cams.get(m.get('camara_id') or 0)
            label = f"{camara['numero']} - {camara['nombre']}" if camara else "-"
            iid = self.tree_medias.insert("", "end", values=(m.get('codigo', ''), m.get('especie', ''), m.get('media', ''), f"{m.get('peso', 0):,.0f}", label))
            self._medias_map[iid] = m

    def _crear_lote(self):
        from core.database import crear_lote_cuarteo
        lote_id, numero = crear_lote_cuarteo()
        self._lote_id = lote_id
        self.lbl_lote.configure(text=f"Lote: {numero}")

    def _guardar_cuarto(self):
        from tkinter import messagebox
        from core.database import agregar_media_a_lote_cuarteo, guardar_cuarto
        if not self._lote_id:
            messagebox.showwarning("Atención", "Cree un lote primero")
            return
        sel = self.tree_medias.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una media")
            return
        m = self._medias_map.get(sel[0])
        t = self.combo_tipo.get()
        if not t:
            messagebox.showwarning("Validación", "Seleccione tipo de cuarto")
            return
        try:
            p = float(self.entry_peso.get().replace(",", "."))
        except:
            messagebox.showwarning("Validación", "Peso inválido")
            return
        agregar_media_a_lote_cuarteo(self._lote_id, m['id'])
        guardar_cuarto(m['id'], t, p, m.get('camara_id'), "")
        self._cargar_medias()
        messagebox.showinfo("OK", "Cuarto guardado")
