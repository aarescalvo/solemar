"""
Ciclo I - Menu
Submenús: Recepción, Mod./Mov. Hacienda, Pesaje Hacienda, Listado de Faena,
Palco de Junta, Movimientos de Cámara, Reportes
"""
import tkinter as tk
from tkinter import ttk
import os
from core import theme as T
from core.session import Sesion

class Ciclo1Menu(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._current = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self._back).pack(side="left", padx=15, pady=12)
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            for name in ["logo.png", "logo.jpg", "logo.jpeg", "logo.gif", "Logo.png", "Logo.jpg", "Logo.jpeg", "Logo.gif", "LOGO.png", "LOGO.jpg", "LOGO.jpeg", "LOGO.gif"]:
                path = os.path.join(base_dir, name)
                if os.path.exists(path):
                    try:
                        self._logo_img = tk.PhotoImage(file=path)
                        tk.Label(header, image=self._logo_img, bg=T.AZUL).pack(side="left", padx=4, pady=8)
                    except:
                        pass
                    break
        except:
            pass
        tk.Label(header, text="CICLO I - Recepcion, Faena y Stock", font=T.FONT_SUBTITULO, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)
        tk.Label(header, text=f"{Sesion.nombre_usuario()}", font=T.FONT_NORMAL, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="right", padx=20)

        self.container = tk.Frame(self, bg=T.FONDO)
        self.container.pack(expand=True, fill="both")
        self._show_main_menu()

    def _show_main_menu(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both", padx=50, pady=30)

        tk.Label(self._current, text="Seleccione una opción:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=25)

        cards_frame = tk.Frame(self._current, bg=T.FONDO)
        cards_frame.pack(expand=True)

        opciones = [
            ("📥 RECEPCIÓN", "Recepción de hacienda", self._show_recepcion, T.VERDE),
            ("🔧 MODIFICACIONES", "Modificación y movimientos de hacienda", self._show_mod_mov_hacienda, T.AZUL),
            ("⚖️ PESAJE HACIENDA", "Pesaje en pie", self._show_pesaje_hacienda, T.AZUL),
            ("📋 LISTADO FAENA", "Resumen de faenas", self._show_listado_faena, T.ROJO),
            ("🎯 PALCO DE JUNTA", "Control de junta", self._show_palco_junta, T.GRIS_OSCURO),
            ("❄️ MOV. CÁMARA", "Movimientos de cámara", self._show_movimientos_camara, T.VERDE),
            ("📊 REPORTES", "Reportes del ciclo", self._show_reportes, T.AZUL),
        ]

        for i, (titulo, desc, cmd, color) in enumerate(opciones):
            # 3 columnas para encajar sin scroll
            self._make_card(cards_frame, titulo, desc, cmd, color, i // 3, i % 3)

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

    def _show_recepcion(self):
        self._clear_current()
        from ui.recepcion_menu import RecepcionMenu
        RecepcionMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_faena(self):
        self._clear_current()
        from ui.faena_menu import FaenaMenu
        FaenaMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_stock(self):
        self._clear_current()
        from ui.stock_menu import StockMenu
        StockMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    # Nuevos submenús
    def _show_mod_mov_hacienda(self):
        self._clear_current()
        frame = MovimientosHacienda(self._current, self._show_main_menu)
        frame.pack(expand=True, fill="both")

    def _show_pesaje_hacienda(self):
        self._clear_current()
        # Reutiliza PesajeIndividual de Recepción
        try:
            from ui.recepcion_menu import PesajeIndividual
            PesajeIndividual(self._current, self._show_main_menu).pack(expand=True, fill="both")
        except Exception:
            tk.Label(self._current, text="No disponible: PesajeIndividual", font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.ROJO).pack(pady=40)

    def _show_listado_faena(self):
        self._clear_current()
        # Reutiliza Historial de Faena
        try:
            from ui.faena_menu import HistorialFaena
            HistorialFaena(self._current, self._show_main_menu).pack(expand=True, fill="both")
        except Exception:
            tk.Label(self._current, text="No disponible: Historial de Faena", font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.ROJO).pack(pady=40)

    def _show_palco_junta(self):
        self._clear_current()
        PalcoDeJunta(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_movimientos_camara(self):
        self._clear_current()
        try:
            from ui.camaras_menu import CamarasMenu
            CamarasMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")
        except Exception:
            tk.Label(self._current, text="No disponible: Cámaras", font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.ROJO).pack(pady=40)

    def _show_reportes(self):
        self._clear_current()
        from ui.reportes_menu import ReportesMenu
        ReportesMenu(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _back(self):
        self.master._show_menu()


class MovimientosHacienda(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="🔧 MODIFICACIONES Y MOVIMIENTOS DE HACIENDA", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        top = tk.Frame(content, bg=T.FONDO)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text="Tropa:", font=T.FONT_LABEL, bg=T.FONDO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_tropa = tk.Entry(top, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=20, relief="solid", bd=1)
        self.entry_tropa.pack(side="left", padx=5)
        tk.Button(top, text="Buscar", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._buscar_tropa).pack(side="left", padx=8)

        middle = tk.Frame(content, bg=T.FONDO)
        middle.pack(expand=True, fill="both")

        left = tk.Frame(middle, bg=T.BLANCO, relief="solid", bd=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        cols = ("codigo", "tipif", "peso", "caravana", "corral")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for cid, text, w in [("codigo", "Código", 160), ("tipif", "Tipif.", 100), ("peso", "Peso", 70), ("caravana", "Caravana", 100), ("corral", "Corral", 80)]:
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=w, minwidth=50)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)

        right = tk.Frame(middle, bg=T.BLANCO, relief="solid", bd=1)
        right.pack(side="right", fill="y")

        form = tk.Frame(right, bg=T.BLANCO)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Tipificación", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.entry_tipif = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=18, relief="solid", bd=1)
        self.entry_tipif.grid(row=0, column=1, padx=4, pady=4)
        tk.Label(form, text="Raza/Pelaje", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.entry_raza_pelaje = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=18, relief="solid", bd=1)
        self.entry_raza_pelaje.grid(row=1, column=1, padx=4, pady=4)
        tk.Label(form, text="Gordura", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=2, column=0, sticky="e", padx=4, pady=4)
        self.entry_gordura = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=18, relief="solid", bd=1)
        self.entry_gordura.grid(row=2, column=1, padx=4, pady=4)
        tk.Label(form, text="Peso vivo", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=3, column=0, sticky="e", padx=4, pady=4)
        self.entry_peso = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=18, relief="solid", bd=1)
        self.entry_peso.grid(row=3, column=1, padx=4, pady=4)
        tk.Label(form, text="Obs.", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=4, column=0, sticky="e", padx=4, pady=4)
        self.entry_obs = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=18, relief="solid", bd=1)
        self.entry_obs.grid(row=4, column=1, padx=4, pady=4)

        btns = tk.Frame(right, bg=T.BLANCO)
        btns.pack(padx=10, pady=4, fill="x")
        tk.Button(btns, text="Guardar cambios", font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._guardar_cambios).pack(fill="x", pady=4)

        move = tk.Frame(right, bg=T.BLANCO)
        move.pack(padx=10, pady=10, fill="x")
        tk.Label(move, text="Mover a corral", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w")
        self.combo_corral = ttk.Combobox(move, values=[], width=20, state="readonly", font=T.FONT_NORMAL)
        self.combo_corral.pack(fill="x", pady=4)
        tk.Button(move, text="Mover", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._mover_corral).pack(fill="x", pady=4)

        self._animales_map = {}
        self._corrales_map = {}
        self._animal_sel = None
        self._cargar_corrales()

    def _cargar_corrales(self):
        from core.database import listar_corrales
        corrales = listar_corrales("mixto")
        self._corrales_map = {c['numero']: c for c in corrales}
        self.combo_corral['values'] = list(self._corrales_map.keys())

    def _buscar_tropa(self):
        from tkinter import messagebox
        from core.database import listar_animales
        tropa = self.entry_tropa.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._animales_map = {}
        if not tropa:
            messagebox.showwarning("Atención", "Ingrese número de tropa")
            return
        animales = listar_animales({"numero_tropa": tropa})
        for a in animales:
            iid = self.tree.insert("", "end", values=(
                a['codigo'],
                a.get('tipificacion', '-'),
                f"{a.get('peso_vivo', 0):.0f}",
                a.get('caravana', '-'),
                a.get('corral_num', a.get('corral_id', ''))
            ))
            self._animales_map[iid] = a

    def _on_sel(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        a = self._animales_map.get(sel[0])
        self._animal_sel = a
        self.entry_tipif.delete(0, tk.END); self.entry_tipif.insert(0, a.get('tipificacion', '') or '')
        self.entry_raza_pelaje.delete(0, tk.END); self.entry_raza_pelaje.insert(0, a.get('raza', '') or a.get('pelaje', '') or '')
        self.entry_gordura.delete(0, tk.END); self.entry_gordura.insert(0, a.get('gordura', '') or '')
        self.entry_peso.delete(0, tk.END); self.entry_peso.insert(0, f"{a.get('peso_vivo', 0):.0f}")
        self.entry_obs.delete(0, tk.END); self.entry_obs.insert(0, a.get('observaciones', '') or '')

    def _guardar_cambios(self):
        from tkinter import messagebox
        from core.database import actualizar_animal
        if not self._animal_sel:
            return
        try:
            peso = float(self.entry_peso.get() or 0)
        except:
            messagebox.showwarning("Validación", "Peso inválido")
            return
        datos = {
            "tipificacion": self.entry_tipif.get().strip(),
            "raza": self.entry_raza_pelaje.get().strip(),
            "gordura": self.entry_gordura.get().strip(),
            "pelaje": self.entry_raza_pelaje.get().strip(),
            "peso_vivo": peso,
            "observaciones": self.entry_obs.get().strip()
        }
        actualizar_animal(self._animal_sel['id'], datos)
        self._buscar_tropa()

    def _mover_corral(self):
        from tkinter import messagebox
        from core.database import mover_animal_corral
        if not self._animal_sel:
            return
        dest_num = self.combo_corral.get()
        if not dest_num:
            messagebox.showwarning("Atención", "Seleccione corral destino")
            return
        dest = self._corrales_map.get(dest_num)
        if not dest:
            return
        mover_animal_corral(self._animal_sel['id'], dest['id'], "Movimiento manual", "")
        self._buscar_tropa()


class PalcoDeJunta(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.GRIS_OSCURO, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="🎯 PALCO DE JUNTA", font=T.FONT_SUBTITULO, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        tk.Label(content, text="Pantalla en preparación.\nControl en tiempo real de junta y validaciones.", font=T.FONT_NORMAL, bg=T.FONDO, fg=T.TEXTO, justify="left").pack(anchor="w", pady=10)
