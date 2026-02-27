"""
Módulo de Cámaras Frigoríficas
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from core import theme as T
from core.database import listar_camaras, listar_medias_en_camara, mover_media_a_camara

class CamarasMenu(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.GRIS_OSCURO, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._back).pack(side="left", padx=15, pady=12)
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            for name in ["logo.png", "logo.jpg", "logo.jpeg", "logo.gif", "Logo.png", "Logo.jpg", "Logo.jpeg", "Logo.gif", "LOGO.png", "LOGO.jpg", "LOGO.jpeg", "LOGO.gif"]:
                path = os.path.join(base_dir, name)
                if os.path.exists(path):
                    try:
                        self._logo_img = tk.PhotoImage(file=path)
                        tk.Label(header, image=self._logo_img, bg=T.GRIS_OSCURO).pack(side="left", padx=4, pady=8)
                    except:
                        pass
                    break
        except:
            pass
        tk.Label(header, text="❄️ MÓDULO DE CÁMARAS", font=T.FONT_SUBTITULO, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Panel izquierdo: lista de cámaras
        left_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_frame, text="CÁMARAS", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL).pack(pady=10)

        scroll_left = ttk.Scrollbar(left_frame)
        scroll_left.pack(side="right", fill="y")

        cols = ("numero", "nombre", "capacidad", "ocupacion", "disp")
        self.tree_camaras = ttk.Treeview(left_frame, columns=cols, show="headings", yscrollcommand=scroll_left.set, height=20)

        headers = [("numero", "N°", 50), ("nombre", "Nombre", 150), ("capacidad", "Cap.kg", 80), ("ocupacion", "Ocup.kg", 80), ("disp", "Disp.kg", 80)]

        for col_id, text, width in headers:
            self.tree_camaras.heading(col_id, text=text)
            self.tree_camaras.column(col_id, width=width, minwidth=50)

        scroll_left.config(command=self.tree_camaras.yview)
        self.tree_camaras.pack(fill="both", expand=True)

        self.tree_camaras.bind("<<TreeviewSelect>>", self._on_camara_select)

        # Panel derecho: contenido de cámara seleccionada
        right_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(right_frame, text="CONTENIDO", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE).pack(pady=10)

        scroll_right = ttk.Scrollbar(right_frame)
        scroll_right.pack(side="right", fill="y")

        cols2 = ("codigo", "especie", "media", "peso", "fecha")
        self.tree_contenido = ttk.Treeview(right_frame, columns=cols2, show="headings", yscrollcommand=scroll_right.set, height=20)

        headers2 = [("codigo", "Código", 100), ("especie", "Especie", 70), ("media", "Media", 70), ("peso", "Peso kg", 80), ("fecha", "Fecha", 100)]

        for col_id, text, width in headers2:
            self.tree_contenido.heading(col_id, text=text)
            self.tree_contenido.column(col_id, width=width, minwidth=50)

        scroll_right.config(command=self.tree_contenido.yview)
        self.tree_contenido.pack(fill="both", expand=True)

        move_frame = tk.Frame(right_frame, bg=T.BLANCO)
        move_frame.pack(fill="x", pady=8)
        tk.Label(move_frame, text="Mover a:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=8)
        self.combo_destino = ttk.Combobox(move_frame, values=[], width=20, state="readonly", font=T.FONT_NORMAL)
        self.combo_destino.pack(side="left", padx=5)
        tk.Button(move_frame, text="Mover seleccionadas", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._mover_seleccion).pack(side="left", padx=8)

        self._cargar_camaras()

    def _cargar_camaras(self):
        for item in self.tree_camaras.get_children():
            self.tree_camaras.delete(item)

        camaras = listar_camaras()
        for c in camaras:
            ocup = c.get('ocupacion_kg', 0)
            cap = c.get('capacidad_kg', 0)
            disp = cap - ocup
            self.tree_camaras.insert("", "end", values=(
                c.get('numero', ''),
                c.get('nombre', ''),
                f"{cap:,.0f}",
                f"{ocup:,.0f}",
                f"{disp:,.0f}",
            ))

    def _on_camara_select(self, event):
        selection = self.tree_camaras.selection()
        if not selection:
            return

        item = self.tree_camaras.item(selection[0])
        numero = item['values'][0]

        # Buscar ID de cámara
        camaras = listar_camaras()
        camara_id = None
        for c in camaras:
            if c['numero'] == numero:
                camara_id = c['id']
                break

        self._cargar_contenido(camara_id)

    def _cargar_contenido(self, camara_id):
        for item in self.tree_contenido.get_children():
            self.tree_contenido.delete(item)

        if not camara_id:
            return

        self._camara_actual = camara_id
        medias = listar_medias_en_camara(camara_id)
        self._contenido_map = {}
        for m in medias:
            iid = self.tree_contenido.insert("", "end", values=(
                m.get('codigo', ''),
                m.get('especie', ''),
                m.get('media', ''),
                f"{m.get('peso', 0):,.0f}",
                m.get('fecha_ingreso', ''),
            ))
            self._contenido_map[iid] = m
        cams = listar_camaras()
        self.combo_destino['values'] = [f"{c['numero']} - {c['nombre']}" for c in cams if c['id'] != camara_id]
        self._camaras_map = {f"{c['numero']} - {c['nombre']}": c for c in cams}

    def _back(self):
        try:
            if callable(self.on_back):
                self.on_back()
        except Exception:
            pass

    def _mover_seleccion(self):
        selection = self.tree_contenido.selection()
        if not selection:
            return
        dest_lbl = self.combo_destino.get()
        if not dest_lbl:
            messagebox.showwarning("Atención", "Seleccione cámara destino")
            return
        dest = self._camaras_map.get(dest_lbl)
        if not dest:
            return
        ok = 0
        for iid in selection:
            m = self._contenido_map.get(iid)
            if not m:
                continue
            if mover_media_a_camara(m['id'], dest['id']):
                ok += 1
        if ok:
            self._cargar_contenido(self._camara_actual)
