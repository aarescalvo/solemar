"""
Módulo de Desposte
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core import theme as T
from core.session import Sesion
from core.database import get_proximo_lote_desposte, guardar_desposte, listar_medias_en_camara, listar_camaras

class DesposteMenu(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._back).pack(side="left", padx=15, pady=12)
        tk.Label(header, text="🥩 MÓDULO DE DESPOSTE", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Info lote
        lote_num = get_proximo_lote_desposte()
        self.lote_num = lote_num

        info_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=10)

        tk.Label(info_frame, text=f"Lote: {lote_num}", font=T.FONT_BOTON, bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=15, pady=10)
        tk.Label(info_frame, text=f"Fecha: {__import__('datetime').datetime.now().strftime('%d/%m/%Y')}", font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="right", padx=15, pady=10)

        # Panel izquierdo: medias disponibles
        left_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_frame, text="MEDIAS DISPONIBLES", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE).pack(pady=10)

        scroll_left = ttk.Scrollbar(left_frame)
        scroll_left.pack(side="right", fill="y")

        cols = ("codigo", "especie", "media", "peso", "camara")
        self.tree_medias = ttk.Treeview(left_frame, columns=cols, show="headings", yscrollcommand=scroll_left.set, height=15)

        headers = [("codigo", "Código", 100), ("especie", "Especie", 70), ("media", "Media", 60), ("peso", "Peso kg", 80), ("camara", "Cámara", 60)]

        for col_id, text, width in headers:
            self.tree_medias.heading(col_id, text=text)
            self.tree_medias.column(col_id, width=width, minwidth=50)

        scroll_left.config(command=self.tree_medias.yview)
        self.tree_medias.pack(fill="both", expand=True)

        # Panel derecho: formulario de desposte
        right_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(right_frame, text="REGISTRAR DESPOSTE", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL).pack(pady=10)

        form = tk.Frame(right_frame, bg=T.BLANCO)
        form.pack(fill="x", padx=15, pady=10)

        tk.Label(form, text="Producto:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w")
        self.combo_producto = ttk.Combobox(form, values=[
            "Nalga", "Cuadril", "Bola de lomo", "Tapa de nalga", "Tapa de cuadril",
            "Colita de cuadril", "Palomita", "Bife angosto", "Bife ancho", "Ojo de bife",
            "Entraña", "Asado", "Vacío", "Matambre", "Falda", "Paleta", "Cogote",
            "Hueso", "Grasa", "Vísceras"
        ], width=30, font=T.FONT_NORMAL)
        self.combo_producto.pack(fill="x", pady=5)

        tk.Label(form, text="Peso (kg):", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w", pady=(10, 0))
        self.entry_peso = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, relief="solid", bd=1, width=15)
        self.entry_peso.pack(fill="x", pady=5)

        tk.Label(form, text="Cámara destino:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w", pady=(10, 0))
        camaras = listar_camaras()
        self.combo_camara = ttk.Combobox(form, values=[f"{c['numero']} - {c['nombre']}" for c in camaras], width=30, font=T.FONT_NORMAL)
        self.combo_camara.pack(fill="x", pady=5)
        self.camaras = {f"{c['numero']} - {c['nombre']}": c['id'] for c in camaras}

        tk.Label(form, text="Observaciones:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w", pady=(10, 0))
        self.text_obs = tk.Text(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, height=3, relief="solid", bd=1)
        self.text_obs.pack(fill="x", pady=5)

        btn_frame = tk.Frame(right_frame, bg=T.BLANCO)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="✅ AGREGAR", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=8, command=self._agregar).pack(side="left", padx=10)

        self._cargar_medias()

    def _cargar_medias(self):
        for item in self.tree_medias.get_children():
            self.tree_medias.delete(item)

        medias = listar_medias_en_camara()
        for m in medias:
            self.tree_medias.insert("", "end", values=(
                m.get('codigo', ''),
                m.get('especie', ''),
                m.get('media', ''),
                f"{m.get('peso', 0):,.0f}",
                m.get('camara_num', ''),
            ))

    def _agregar(self):
        selection = self.tree_medias.selection()
        if not selection:
            messagebox.showwarning("Atención", "Seleccione una media res")
            return

        producto = self.combo_producto.get()
        peso = self.entry_peso.get().strip()

        if not producto:
            messagebox.showwarning("Validación", "Seleccione un producto")
            return

        if not peso:
            messagebox.showwarning("Validación", "Ingrese el peso")
            return

        try:
            peso = float(peso)
        except:
            messagebox.showwarning("Validación", "Peso inválido")
            return

        item = self.tree_medias.item(selection[0])
        codigo_media = item['values'][0]

        datos = {
            "numero_lote": self.lote_num,
            "producto": producto,
            "peso_kg": peso,
            "camara_destino": self.camaras.get(self.combo_camara.get()),
            "operador": Sesion.nombre_usuario(),
            "observaciones": self.text_obs.get("1.0", tk.END).strip(),
        }

        try:
            guardar_desposte(datos)
            messagebox.showinfo("Éxito", f"Producto '{producto}' agregado al lote {self.lote_num}")
            self.entry_peso.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _back(self):
        self.master._show_menu()
