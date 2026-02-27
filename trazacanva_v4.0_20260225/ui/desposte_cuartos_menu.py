"""
Módulo de Desposte desde Cuartos
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core import theme as T
from core.session import Sesion
from core.database import (
    listar_cuartos_en_camaras, listar_camaras, listar_lotes_cuarteo, crear_orden_desposte,
    registrar_produccion, obtener_numero_tropa_de_cuarto
)


class DesposteCuartosMenu(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._orden_id = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.ROJO, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=15, pady=12)
        tk.Label(header, text="🥩 DESPOSTE DESDE CUARTOS", font=T.FONT_SUBTITULO, bg=T.ROJO, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Panel izquierdo: cuartos disponibles
        left = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(left, text="CUARTOS EN CÁMARAS", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL).pack(pady=8)
        cols = ("codigo", "tipo", "peso", "camara", "posicion")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for cid, text, w in [("codigo", "Código", 160), ("tipo", "Tipo", 100), ("peso", "Peso", 80), ("camara", "Cámara", 100), ("posicion", "Posición", 100)]:
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=w, minwidth=50)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)

        # Panel derecho: orden y producción
        right = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        right.pack(side="right", fill="y")
        tk.Label(right, text="ORDEN Y PRODUCCIÓN", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE).pack(pady=8)

        # Crear/seleccionar orden
        top = tk.Frame(right, bg=T.BLANCO)
        top.pack(padx=10, pady=8, fill="x")
        tk.Label(top, text="Lote de cuarteo:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.combo_lote = ttk.Combobox(top, values=[f"{l['numero_lote']} (#{l['id']})" for l in listar_lotes_cuarteo("abierto")], width=24, state="readonly")
        self.combo_lote.grid(row=0, column=1, padx=4, pady=4)
        tk.Button(top, text="Crear orden de desposte", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._crear_orden).grid(row=1, column=0, columnspan=2, pady=6, sticky="ew")
        self.lbl_orden = tk.Label(right, text="Orden: -", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO)
        self.lbl_orden.pack(padx=10, pady=4, anchor="w")

        # Form producción
        form = tk.Frame(right, bg=T.BLANCO)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Producto", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.combo_prod = ttk.Combobox(form, values=[
            "Nalga", "Cuadril", "Bola de lomo", "Tapa de nalga", "Tapa de cuadril",
            "Colita de cuadril", "Palomita", "Bife angosto", "Bife ancho", "Ojo de bife",
            "Entraña", "Asado", "Vacío", "Matambre", "Falda", "Paleta", "Cogote",
            "Hueso", "Grasa"
        ], width=22, state="readonly")
        self.combo_prod.grid(row=0, column=1, padx=4, pady=4)
        tk.Label(form, text="Peso (kg)", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.entry_peso = tk.Entry(form, font=T.FONT_MONO_SMALL, bg=T.GRIS_CLARO, width=12, relief="solid", bd=1, justify="right")
        self.entry_peso.grid(row=1, column=1, padx=4, pady=4)
        tk.Label(form, text="Cajas", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=2, column=0, sticky="e", padx=4, pady=4)
        self.entry_cajas = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=12, relief="solid", bd=1, justify="right")
        self.entry_cajas.grid(row=2, column=1, padx=4, pady=4)
        tk.Label(form, text="Lote producción", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=3, column=0, sticky="e", padx=4, pady=4)
        self.entry_lote_prod = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=14, relief="solid", bd=1)
        self.entry_lote_prod.grid(row=3, column=1, padx=4, pady=4)
        self.lbl_tropa = tk.Label(form, text="Tropa: -", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO)
        self.lbl_tropa.grid(row=4, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        tk.Button(form, text="Registrar producción", font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._registrar).grid(row=5, column=0, columnspan=2, sticky="ew", pady=6)

        self._cuartos_map = {}
        self._cuarto_sel = None
        self._cargar_cuartos()

    def _cargar_cuartos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._cuartos_map = {}
        cams = {c['id']: c for c in listar_camaras()}
        for q in listar_cuartos_en_camaras():
            cam = cams.get(q.get('camara_id') or 0)
            camlbl = f"{cam['numero']} - {cam['nombre']}" if cam else "-"
            iid = self.tree.insert("", "end", values=(q.get('codigo', ''), q.get('tipo', ''), f"{q.get('peso', 0):,.0f}", camlbl, q.get('posicion', '-') or '-'))
            self._cuartos_map[iid] = q

    def _on_sel(self, e):
        sel = self.tree.selection()
        if not sel:
            return
        self._cuarto_sel = self._cuartos_map.get(sel[0])
        numero_tropa, especie = obtener_numero_tropa_de_cuarto(self._cuarto_sel['id'])
        if especie == "bovino" and numero_tropa:
            self.lbl_tropa.configure(text=f"Tropa: {numero_tropa}")
        else:
            self.lbl_tropa.configure(text=f"Tropa: (no requerido)")

    def _crear_orden(self):
        from tkinter import messagebox
        sel = self.combo_lote.get()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un lote de cuarteo (abierto)")
            return
        lote_id = int(sel.split("#")[-1].strip(")"))
        oid, numero = crear_orden_desposte(lote_id)
        self._orden_id = oid
        self.lbl_orden.configure(text=f"Orden: {numero}")
        messagebox.showinfo("OK", f"Orden creada: {numero}")

    def _registrar(self):
        from tkinter import messagebox
        if not self._orden_id:
            messagebox.showwarning("Atención", "Cree una orden primero")
            return
        if not self._cuarto_sel:
            messagebox.showwarning("Atención", "Seleccione un cuarto")
            return
        prod = self.combo_prod.get()
        if not prod:
            messagebox.showwarning("Validación", "Seleccione producto")
            return
        try:
            peso = float(self.entry_peso.get().replace(",", "."))
        except:
            messagebox.showwarning("Validación", "Peso inválido")
            return
        try:
            cajas = int(self.entry_cajas.get() or "0")
        except:
            messagebox.showwarning("Validación", "Cajas inválido")
            return
        lote_prod = self.entry_lote_prod.get().strip()
        numero_tropa, especie = obtener_numero_tropa_de_cuarto(self._cuarto_sel['id'])
        if especie == "bovino" and not numero_tropa:
            messagebox.showwarning("Validación", "No se pudo determinar la tropa (bovino)")
            return
        registrar_produccion(self._orden_id, prod, peso, cajas, lote_prod, numero_tropa if especie == "bovino" else None)
        messagebox.showinfo("OK", "Producción registrada")
        self.entry_peso.delete(0, tk.END)
        self.entry_cajas.delete(0, tk.END)
        self.entry_lote_prod.delete(0, tk.END)
