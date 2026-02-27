"""
Módulo de Faena
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
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
            ("📝 LISTADO DE FAENA", "Armar orden por fecha", self._show_listado_plan, T.VERDE),
            ("⚖️ INGRESO A FAENA", "Peso previo en línea", self._show_ingreso_linea, T.VERDE),
            ("🏷️ TIPIFICACIÓN MEDIAS", "Pesaje y tipificación", self._show_tipificacion_medias, T.AZUL),
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

    def _show_listado_plan(self):
        self._clear_current()
        ListadoFaenaPlan(self._current, self._show_main_menu).pack(expand=True, fill="both")
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

    def _show_ingreso_linea(self):
        self._clear_current()
        IngresoFaena(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_tipificacion_medias(self):
        self._clear_current()
        TipificacionMedias(self._current, self._show_main_menu).pack(expand=True, fill="both")

class ListadoFaenaPlan(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📝 LISTADO DE FAENA (PLAN)", font=T.FONT_SUBTITULO, bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Fecha del plan
        top = tk.Frame(content, bg=T.FONDO)
        top.pack(fill="x")
        tk.Label(top, text="Fecha:", font=T.FONT_LABEL, bg=T.FONDO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_fecha = tk.Entry(top, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=12, relief="solid", bd=1)
        self.entry_fecha.pack(side="left", padx=5)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        tk.Button(top, text="Guardar listado", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._guardar_listado).pack(side="left", padx=10)

        # Panel izquierdo: tropas en stock (en corral)
        left = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        tk.Label(left, text="TROPAS EN CORRAL", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL).pack(pady=8)

        cols = ("tropa", "especie", "proveedor", "corral", "esperados", "registrados")
        self.tree_tropas = ttk.Treeview(left, columns=cols, show="headings", height=18)
        headers = [("tropa", "Tropa", 120), ("especie", "Especie", 70), ("proveedor", "Proveedor", 150),
                   ("corral", "Corral", 80), ("esperados", "Esp.", 60), ("registrados", "Reg.", 60)]
        for cid, text, w in headers:
            self.tree_tropas.heading(cid, text=text)
            self.tree_tropas.column(cid, width=w, minwidth=50)
        self.tree_tropas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        add_frame = tk.Frame(left, bg=T.BLANCO)
        add_frame.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(add_frame, text="Cantidad:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_cant = tk.Entry(add_frame, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=8, relief="solid", bd=1)
        self.entry_cant.pack(side="left", padx=5)
        tk.Label(add_frame, text="Orden:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=(15,5))
        self.entry_orden = tk.Entry(add_frame, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=6, relief="solid", bd=1)
        self.entry_orden.pack(side="left", padx=5)
        tk.Button(add_frame, text="Agregar al listado →", font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._agregar_item).pack(side="left", padx=10)

        # Panel derecho: listado armado
        right = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        right.pack(side="right", fill="both", expand=True, pady=10)
        tk.Label(right, text="LISTADO ARMADO", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE).pack(pady=8)

        cols2 = ("orden", "tropa", "especie", "cantidad")
        self.tree_listado = ttk.Treeview(right, columns=cols2, show="headings", height=18)
        for cid, text, w in [("orden", "Orden", 60), ("tropa", "Tropa", 120), ("especie", "Especie", 80), ("cantidad", "Cant.", 60)]:
            self.tree_listado.heading(cid, text=text)
            self.tree_listado.column(cid, width=w, minwidth=50)
        self.tree_listado.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._tropas_map = {}
        self._items = []
        self._cargar_tropas()

    def _cargar_tropas(self):
        from core.database import listar_tropas, contar_animales_tropa
        for item in self.tree_tropas.get_children():
            self.tree_tropas.delete(item)
        tropas = listar_tropas({"estado": "en_corral"})
        self._tropas_map = {}
        for t in tropas:
            esperados = t.get('cantidad_esperada', 0)
            registrados = contar_animales_tropa(t['id'])
            iid = self.tree_tropas.insert("", "end", values=(
                t['numero_tropa'],
                t['especie'].upper(),
                t.get('proveedor', '-') or '-',
                t.get('corral_num', '-') or '-',
                esperados,
                registrados
            ))
            self._tropas_map[iid] = t

    def _agregar_item(self):
        from tkinter import messagebox
        sel = self.tree_tropas.selection()
        if not sel:
            return
        t = self._tropas_map.get(sel[0])
        if not t:
            return
        try:
            cant = int(self.entry_cant.get() or "0")
            orden = int(self.entry_orden.get() or "0")
        except:
            messagebox.showwarning("Validación", "Cantidad y orden deben ser números")
            return
        if cant <= 0:
            messagebox.showwarning("Validación", "Ingrese una cantidad mayor a 0")
            return
        self._items.append({"orden": orden, "tropa_id": t['id'], "numero_tropa": t['numero_tropa'], "especie": t['especie'], "cantidad": cant})
        self._refrescar_listado()

    def _refrescar_listado(self):
        for item in self.tree_listado.get_children():
            self.tree_listado.delete(item)
        for it in sorted(self._items, key=lambda x: (x["orden"], x["numero_tropa"])):
            self.tree_listado.insert("", "end", values=(it["orden"], it["numero_tropa"], it["especie"].upper(), it["cantidad"]))

    def _guardar_listado(self):
        from tkinter import messagebox
        from core.database import crear_listado_faena, agregar_item_listado
        fecha = self.entry_fecha.get().strip()
        if not fecha:
            messagebox.showwarning("Validación", "Ingrese la fecha")
            return
        if not self._items:
            messagebox.showwarning("Atención", "No hay ítems en el listado")
            return
        try:
            listado_id = crear_listado_faena(fecha, Sesion.nombre_usuario())
            for it in self._items:
                agregar_item_listado(listado_id, it["tropa_id"], it["numero_tropa"], it["especie"], it["cantidad"], it["orden"])
            messagebox.showinfo("Éxito", f"Listado de faena guardado para {fecha}")
            self.on_back()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")


class IngresoFaena(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="⚖️ INGRESO A FAENA (PRE-INSENSIBILIZACIÓN)", font=T.FONT_SUBTITULO, bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Selección de listado
        top = tk.Frame(content, bg=T.FONDO)
        top.pack(fill="x")
        tk.Label(top, text="Listado (fecha):", font=T.FONT_LABEL, bg=T.FONDO, fg=T.TEXTO).pack(side="left", padx=5)
        from core.database import listar_listados_faena, listar_items_listado, contar_ingresos_item, obtener_proximo_animal_para_item, registrar_ingreso_faena
        self.listados = listar_listados_faena()
        self.combo_listado = ttk.Combobox(top, values=[f"{l['fecha']} (#{l['id']})" for l in self.listados], width=22, state="readonly")
        self.combo_listado.pack(side="left", padx=5)
        self.combo_listado.bind("<<ComboboxSelected>>", self._on_listado_sel)

        # Izquierda: items del listado (tropas)
        left = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        tk.Label(left, text="ORDEN DE FAENA (POR TROPA)", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL).pack(pady=8)
        cols = ("orden", "tropa", "especie", "plan", "ingresados", "restantes")
        self.tree_items = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for cid, text, w in [("orden", "Orden", 60), ("tropa", "Tropa", 120), ("especie", "Especie", 80), ("plan", "Plan", 60), ("ingresados", "Ing.", 60), ("restantes", "Rest.", 60)]:
            self.tree_items.heading(cid, text=text)
            self.tree_items.column(cid, width=w, minwidth=50)
        self.tree_items.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree_items.bind("<<TreeviewSelect>>", self._on_item_sel)

        # Derecha: captura de peso
        right = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        right.pack(side="right", fill="y", pady=10)
        tk.Label(right, text="CAPTURA DE PESO PREVIO", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE).pack(pady=10)
        form = tk.Frame(right, bg=T.BLANCO)
        form.pack(padx=12, pady=12)
        tk.Label(form, text="Peso (kg):", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.entry_peso_pre = tk.Entry(form, font=T.FONT_MONO_SMALL, bg=T.GRIS_CLARO, width=12, relief="solid", bd=1, justify="right")
        self.entry_peso_pre.grid(row=0, column=1, padx=4, pady=4)
        tk.Button(form, text="Registrar ingreso", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._registrar).grid(row=1, column=0, columnspan=2, pady=8, sticky="ew")
        self.lbl_estado = tk.Label(right, text="Seleccione un item", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO, justify="left")
        self.lbl_estado.pack(pady=(6, 12))

        self._listado_sel = None
        self._items_map = {}
        self._item_sel = None

    def _on_listado_sel(self, e):
        from core.database import listar_items_listado, contar_ingresos_item
        sel = self.combo_listado.get()
        if not sel:
            return
        listado_id = int(sel.split("#")[-1].strip(")"))
        self._listado_sel = listado_id
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
        self._items_map = {}
        items = listar_items_listado(listado_id)
        for it in items:
            ingresados = contar_ingresos_item(it['id'])
            restantes = max(0, (it.get('cantidad', 0) or 0) - ingresados)
            iid = self.tree_items.insert("", "end", values=(it.get('orden', 0), it.get('numero_tropa', ''), it.get('especie', '').upper(), it.get('cantidad', 0), ingresados, restantes))
            self._items_map[iid] = it

    def _on_item_sel(self, e):
        sel = self.tree_items.selection()
        if not sel:
            return
        self._item_sel = self._items_map.get(sel[0])
        self.lbl_estado.configure(text=f"Item seleccionado: Tropa {self._item_sel['numero_tropa']} (Plan: {self._item_sel['cantidad']})")

    def _registrar(self):
        from tkinter import messagebox
        from core.database import contar_ingresos_item, obtener_proximo_animal_para_item, registrar_ingreso_faena
        if not self._listado_sel or not self._item_sel:
            messagebox.showwarning("Atención", "Seleccione listado e item")
            return
        try:
            peso = float(self.entry_peso_pre.get().replace(",", "."))
        except:
            messagebox.showwarning("Validación", "Ingrese un peso válido")
            return
        plan = int(self._item_sel.get("cantidad", 0) or 0)
        ingresados = contar_ingresos_item(self._item_sel['id'])
        if ingresados >= plan:
            messagebox.showinfo("Completado", "Este item ya alcanzó la cantidad planificada")
            return
        prox = obtener_proximo_animal_para_item(self._item_sel['id'], self._item_sel['tropa_id'])
        if not prox:
            messagebox.showwarning("Sin animales", "No hay más animales disponibles en corral para esta tropa")
            return
        registrar_ingreso_faena(self._listado_sel, self._item_sel['id'], prox['id'], peso)
        self.entry_peso_pre.delete(0, tk.END)
        self.entry_peso_pre.insert(0, "")
        self._on_listado_sel(None)
        messagebox.showinfo("Registrado", f"Ingreso registrado: Animal {prox['codigo']} - {peso:,.0f} kg")


class TipificacionMedias(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="🏷️ PESAJE Y TIPIFICACIÓN DE MEDIAS", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        left = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(left, text="ANIMALES EN LÍNEA", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL).pack(pady=8)
        cols = ("codigo", "tropa", "especie", "peso_pre")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for cid, text, w in [("codigo", "Código", 140), ("tropa", "Tropa", 120), ("especie", "Especie", 80), ("peso_pre", "Peso pre", 80)]:
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=w, minwidth=50)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)

        right = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        right.pack(side="right", fill="y")
        tk.Label(right, text="MEDIDA", font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE).pack(pady=8)
        form = tk.Frame(right, bg=T.BLANCO)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Media", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.combo_media = ttk.Combobox(form, values=["izquierda", "derecha"], state="readonly", width=14)
        self.combo_media.grid(row=0, column=1, padx=4, pady=4)
        tk.Label(form, text="Peso canal", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.entry_peso = tk.Entry(form, font=T.FONT_MONO_SMALL, bg=T.GRIS_CLARO, width=12, relief="solid", bd=1, justify="right")
        self.entry_peso.grid(row=1, column=1, padx=4, pady=4)
        tk.Label(form, text="Engrasamiento", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=2, column=0, sticky="e", padx=4, pady=4)
        self.entry_eng = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=14, relief="solid", bd=1)
        self.entry_eng.grid(row=2, column=1, padx=4, pady=4)
        tk.Label(form, text="Conformación", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=3, column=0, sticky="e", padx=4, pady=4)
        self.entry_conf = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=14, relief="solid", bd=1)
        self.entry_conf.grid(row=3, column=1, padx=4, pady=4)
        tk.Label(form, text="Categoría", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=4, column=0, sticky="e", padx=4, pady=4)
        self.entry_cat = tk.Entry(form, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=14, relief="solid", bd=1)
        self.entry_cat.grid(row=4, column=1, padx=4, pady=4)
        tk.Button(form, text="Guardar media", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._guardar).grid(row=5, column=0, columnspan=2, sticky="ew", pady=6)
        self.lbl_info = tk.Label(right, text="Seleccione un animal", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO, justify="left")
        self.lbl_info.pack(pady=(6, 12))

        self._animales_map = {}
        self._animal_sel = None
        self._cargar()

    def _cargar(self):
        from core.database import listar_animales_en_linea
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._animales_map = {}
        for a in listar_animales_en_linea():
            iid = self.tree.insert("", "end", values=(a.get('codigo', ''), a.get('numero_tropa', ''), a.get('especie', '').upper(), f"{a.get('peso_pre_faena', 0):,.0f}"))
            self._animales_map[iid] = a

    def _on_sel(self, e):
        sel = self.tree.selection()
        if not sel:
            return
        self._animal_sel = self._animales_map.get(sel[0])
        self.lbl_info.configure(text=f"Animal {self._animal_sel.get('codigo', '')}")

    def _guardar(self):
        from tkinter import messagebox
        from core.database import get_proxima_faena, guardar_faena, get_proxima_media, guardar_media_res
        if not self._animal_sel:
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        media = self.combo_media.get()
        if not media:
            messagebox.showwarning("Validación", "Seleccione media")
            return
        try:
            peso = float(self.entry_peso.get().replace(",", "."))
        except:
            messagebox.showwarning("Validación", "Peso inválido")
            return
        num_faena = get_proxima_faena()
        faena_id = guardar_faena({
            "numero_faena": num_faena,
            "animal_id": self._animal_sel['id'],
            "especie": self._animal_sel.get("especie", ""),
            "categoria": self.entry_cat.get().strip(),
            "peso_vivo": self._animal_sel.get("peso_pre_faena", 0),
            "peso_canal": peso
        })
        codigo_media = get_proxima_media()
        guardar_media_res({
            "codigo": codigo_media,
            "faena_id": faena_id,
            "especie": self._animal_sel.get("especie", ""),
            "media": media,
            "peso": peso,
            "camara_id": None,
            "posicion": "",
            "observaciones": f"E:{self.entry_eng.get().strip()} C:{self.entry_conf.get().strip()} K:{self.entry_cat.get().strip()}"
        })
        messagebox.showinfo("OK", f"Media {media} guardada\nFaena {num_faena} - {codigo_media}")
        self.entry_peso.delete(0, tk.END)
        self.entry_eng.delete(0, tk.END)
        self.entry_conf.delete(0, tk.END)
        self.entry_cat.delete(0, tk.END)

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
