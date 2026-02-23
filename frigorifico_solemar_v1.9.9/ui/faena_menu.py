"""
Módulo de Faena
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core import theme as T
from core.session import Sesion
from core.database import get_proxima_faena, get_proxima_media, incrementar_media, guardar_faena, guardar_media_res, listar_faenas, listar_camaras

class FaenaMenu(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._current = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.ROJO, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._back).pack(side="left", padx=15, pady=12)
        tk.Label(header, text="🏥 MÓDULO DE FAENA", font=T.FONT_SUBTITULO, bg=T.ROJO, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)

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
            ("🪓 NUEVA FAENA", "Registrar faena", self._show_nueva_faena, T.ROJO),
            ("📋 HISTORIAL", "Ver faenas realizadas", self._show_historial, T.AZUL),
        ]

        for i, (titulo, desc, cmd, color) in enumerate(opciones):
            self._make_card(cards_frame, titulo, desc, cmd, color, 0, i)

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

    def _show_nueva_faena(self):
        self._clear_current()
        NuevaFaena(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_historial(self):
        self._clear_current()
        HistorialFaena(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _back(self):
        self.master._show_menu()


class NuevaFaena(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.ROJO, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="🪓 NUEVA FAENA", font=T.FONT_SUBTITULO, bg=T.ROJO, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Número de faena
        faena_num = get_proxima_faena()
        self.faena_num = faena_num

        info_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=10)

        tk.Label(info_frame, text=f"Faena: {faena_num}", font=T.FONT_BOTON, bg=T.BLANCO, fg=T.ROJO).pack(side="left", padx=15, pady=10)
        tk.Label(info_frame, text=f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="right", padx=15, pady=10)

        # Formulario
        form = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        form.pack(fill="x", pady=10)

        row1 = tk.Frame(form, bg=T.BLANCO)
        row1.pack(fill="x", padx=15, pady=10)

        tk.Label(row1, text="Especie:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.combo_especie = ttk.Combobox(row1, values=["bovino", "equino"], state="readonly", width=12, font=T.FONT_NORMAL)
        self.combo_especie.pack(side="left", padx=5)
        self.combo_especie.set("bovino")

        tk.Label(row1, text="Categoría:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=(20, 5))
        self.combo_cat = ttk.Combobox(row1, values=["novillo", "vaca", "vaquillona", "ternero", "toro"], state="readonly", width=12, font=T.FONT_NORMAL)
        self.combo_cat.pack(side="left", padx=5)

        row2 = tk.Frame(form, bg=T.BLANCO)
        row2.pack(fill="x", padx=15, pady=10)

        tk.Label(row2, text="Peso Vivo (kg):", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_peso_vivo = tk.Entry(row2, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=10, relief="solid", bd=1)
        self.entry_peso_vivo.pack(side="left", padx=5)

        tk.Label(row2, text="Peso Canal (kg):", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=(20, 5))
        self.entry_peso_canal = tk.Entry(row2, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=10, relief="solid", bd=1)
        self.entry_peso_canal.pack(side="left", padx=5)

        row3 = tk.Frame(form, bg=T.BLANCO)
        row3.pack(fill="x", padx=15, pady=10)

        tk.Label(row3, text="Tipificación:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_tipif = tk.Entry(row3, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=15, relief="solid", bd=1)
        self.entry_tipif.pack(side="left", padx=5)

        tk.Label(row3, text="Destino:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=(20, 5))
        self.combo_destino = ttk.Combobox(row3, values=["cámara", "desposte", "venta_directa"], state="readonly", width=12, font=T.FONT_NORMAL)
        self.combo_destino.pack(side="left", padx=5)
        self.combo_destino.set("cámara")

        # Cámara destino
        row4 = tk.Frame(form, bg=T.BLANCO)
        row4.pack(fill="x", padx=15, pady=10)

        tk.Label(row4, text="Cámara:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        camaras = listar_camaras()
        self.combo_camara = ttk.Combobox(row4, values=[f"{c['numero']} - {c['nombre']}" for c in camaras], width=25, font=T.FONT_NORMAL)
        self.combo_camara.pack(side="left", padx=5)
        self.camaras = {f"{c['numero']} - {c['nombre']}": c['id'] for c in camaras}

        # Botones
        btn_frame = tk.Frame(content, bg=T.FONDO)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="✅ GUARDAR FAENA", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=30, pady=10, command=self._guardar).pack(side="left", padx=15)
        tk.Button(btn_frame, text="❌ Cancelar", font=T.FONT_BOTON, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=10, command=self.on_back).pack(side="left", padx=15)

    def _guardar(self):
        peso_vivo = self.entry_peso_vivo.get().strip()
        peso_canal = self.entry_peso_canal.get().strip()

        if not peso_vivo or not peso_canal:
            messagebox.showwarning("Validación", "Complete peso vivo y peso canal")
            return

        try:
            peso_vivo = float(peso_vivo)
            peso_canal = float(peso_canal)
        except:
            messagebox.showwarning("Validación", "Los pesos deben ser números")
            return

        rendimiento = (peso_canal / peso_vivo * 100) if peso_vivo > 0 else 0

        datos_faena = {
            "numero_faena": self.faena_num,
            "especie": self.combo_especie.get(),
            "categoria": self.combo_cat.get(),
            "peso_vivo": peso_vivo,
            "peso_canal": peso_canal,
            "rendimiento": rendimiento,
            "tipificacion": self.entry_tipif.get().strip(),
            "destino": self.combo_destino.get(),
            "operador": Sesion.nombre_usuario(),
        }

        try:
            faena_id = guardar_faena(datos_faena)

            # Crear las dos medias reses
            n1, n2 = get_proxima_media()
            camara_id = self.camaras.get(self.combo_camara.get())
            especie = self.combo_especie.get()
            peso_media = peso_canal / 2

            guardar_media_res({"codigo": f"MR-{n1:06d}", "faena_id": faena_id, "especie": especie, "media": "izquierda", "peso": peso_media, "camara_id": camara_id})
            guardar_media_res({"codigo": f"MR-{n2:06d}", "faena_id": faena_id, "especie": especie, "media": "derecha", "peso": peso_media, "camara_id": camara_id})

            incrementar_media()

            messagebox.showinfo("Éxito", f"Faena {self.faena_num} registrada\nMedias: MR-{n1:06d} y MR-{n2:06d}")
            self.on_back()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")


class HistorialFaena(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📋 HISTORIAL DE FAENA", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        tabla_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        tabla_frame.pack(expand=True, fill="both")

        scroll = ttk.Scrollbar(tabla_frame)
        scroll.pack(side="right", fill="y")

        cols = ("faena", "fecha", "especie", "peso_vivo", "peso_canal", "rendimiento", "tipif", "operador")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", yscrollcommand=scroll.set, height=20)

        headers = [("faena", "Faena", 100), ("fecha", "Fecha", 100), ("especie", "Especie", 70),
                   ("peso_vivo", "P.Vivo", 80), ("peso_canal", "P.Canal", 80), ("rendimiento", "Rend.%", 60),
                   ("tipif", "Tipif.", 80), ("operador", "Operador", 100)]

        for col_id, text, width in headers:
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, minwidth=50)

        scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        self._cargar()

    def _cargar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        faenas = listar_faenas()
        for f in faenas:
            self.tree.insert("", "end", values=(
                f.get('numero_faena', ''),
                f.get('fecha_faena', ''),
                f.get('especie', ''),
                f"{f.get('peso_vivo', 0):,.0f}",
                f"{f.get('peso_canal', 0):,.0f}",
                f"{f.get('rendimiento', 0):.1f}%",
                f.get('tipificacion', ''),
                f.get('operador', ''),
            ))
