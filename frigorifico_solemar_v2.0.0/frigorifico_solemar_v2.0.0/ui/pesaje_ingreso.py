"""
Pesaje - Ingreso v1.9.9
Layout optimizado sin scrolls - usa 2 columnas para mejor aprovechamiento del espacio
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core import theme as T
from core.session import Sesion
from core.database import (
    get_proximo_ticket, guardar_ticket, 
    listar_proveedores, listar_transportistas_activos, listar_usuarios_faena_activos,
    buscar_transportista_by_patente
)


class PesajeIngreso(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self.tipo_op = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        btn_volver = tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                               relief="flat", cursor="hand2", command=self._volver)
        btn_volver.pack(side="left", padx=10, pady=8)
        
        tk.Label(header, text="INGRESO - Pesaje de Entrada", font=T.FONT_SUBTITULO, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        self.content = tk.Frame(self, bg=T.FONDO)
        self.content.pack(expand=True, fill="both", padx=15, pady=10)
        self._show_tipo_selector()

    def _volver(self):
        self.on_back()

    def _clear_content(self):
        for widget in self.content.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

    def _show_tipo_selector(self):
        self._clear_content()
        
        tk.Label(self.content, text="Seleccione tipo de ingreso:", 
                 font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.TEXTO).pack(pady=30)

        frame = tk.Frame(self.content, bg=T.FONDO)
        frame.pack()

        tipos = [("INGRESO HACIENDA", "Camion con animales", "hacienda"),
                 ("PESAJE NORMAL", "Mercaderia general", "normal"),
                 ("CAMION VACIO", "Registro de tara", "vacio")]

        for titulo, desc, tipo in tipos:
            self._make_tipo_btn(frame, titulo, desc, tipo)

    def _make_tipo_btn(self, parent, titulo, desc, tipo):
        btn = tk.Frame(parent, bg=T.BLANCO, relief="solid", bd=1, cursor="hand2")
        btn.pack(fill="x", pady=6, padx=20)

        tk.Label(btn, text=titulo, font=T.FONT_BOTON, bg=T.BLANCO, fg=T.AZUL).pack(pady=(10, 0))
        tk.Label(btn, text=desc, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=(0, 10))

        def on_click(e):
            self.tipo_op = tipo
            self._show_form()

        def on_enter(e):
            btn.configure(bg=T.GRIS_CLARO)
            for w in btn.winfo_children():
                try:
                    w.configure(bg=T.GRIS_CLARO)
                except:
                    pass

        def on_leave(e):
            btn.configure(bg=T.BLANCO)
            for w in btn.winfo_children():
                try:
                    w.configure(bg=T.BLANCO)
                except:
                    pass

        btn.bind("<Button-1>", on_click)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        for c in btn.winfo_children():
            c.bind("<Button-1>", on_click)

    def _show_form(self):
        self._clear_content()

        ticket = get_proximo_ticket("ingreso")
        self.ticket_num = ticket

        # Info superior compacta
        info_frame = tk.Frame(self.content, bg=T.BLANCO, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=(0, 8))

        tk.Label(info_frame, text=f"Ticket: {ticket}", font=T.FONT_BOTON, 
                 bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=15, pady=8)
        tk.Label(info_frame, text=f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                 font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="right", padx=15, pady=8)

        # Contenedor principal - 2 columnas
        main_frame = tk.Frame(self.content, bg=T.FONDO)
        main_frame.pack(fill="both", expand=True)

        # Cargar listas
        proveedores = listar_proveedores()
        transportistas = listar_transportistas_activos()
        usuarios_faena = listar_usuarios_faena_activos()
        
        self.proveedores_map = {p['razon_social']: p for p in proveedores}
        self.transportistas_map = {t['nombre']: t for t in transportistas}
        self.usuarios_faena_map = {u['nombre']: u for u in usuarios_faena}
        self.transportista_sel_id = None
        self.usuario_faena_id = None
        self.proveedor_sel_id = None

        # ═══════════════════════════════════════════════════════════
        # COLUMNA IZQUIERDA - Datos del Ingreso
        # ═══════════════════════════════════════════════════════════
        left_frame = tk.LabelFrame(main_frame, text=" DATOS DEL INGRESO ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                   relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        form_left = tk.Frame(left_frame, bg=T.BLANCO)
        form_left.pack(fill="both", expand=True, padx=10, pady=8)

        # Fila 1: Proveedor
        row = tk.Frame(form_left, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Proveedor:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.prov_nombre = tk.StringVar()
        prov_entry = tk.Entry(row, textvariable=self.prov_nombre, font=T.FONT_NORMAL, 
                              bg=T.GRIS_CLARO, width=22, relief="solid", bd=1)
        prov_entry.pack(side="left", padx=3)
        tk.Button(row, text="...", font=T.FONT_NORMAL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  width=2, command=lambda: self._seleccionar_proveedor(proveedores)).pack(side="left", padx=2)

        # Fila 2: N Guia y N DTE
        row = tk.Frame(form_left, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="N Guia:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_guia = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                   width=12, relief="solid", bd=1)
        self.entry_guia.pack(side="left", padx=3)
        tk.Label(row, text="DTE:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=6, anchor="e").pack(side="left", padx=3)
        self.entry_dte = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                  width=12, relief="solid", bd=1)
        self.entry_dte.pack(side="left", padx=3)

        # Fila 3: Habilitacion SENASA
        row = tk.Frame(form_left, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Habilitacion SENASA:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_habilitacion = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                           width=18, relief="solid", bd=1)
        self.entry_habilitacion.pack(side="left", padx=3)

        # Separador
        tk.Frame(form_left, bg=T.GRIS_CLARO, height=1).pack(fill="x", pady=8)

        # Fila 4: Patentes
        row = tk.Frame(form_left, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Pat. Chasis *:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.ROJO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_pat_chasis = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                         width=10, relief="solid", bd=1)
        self.entry_pat_chasis.pack(side="left", padx=3)
        self.entry_pat_chasis.bind("<KeyRelease>", self._buscar_transportista)
        
        tk.Label(row, text="Acoplado:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=8, anchor="e").pack(side="left", padx=3)
        self.entry_pat_acoplado = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                           width=10, relief="solid", bd=1)
        self.entry_pat_acoplado.pack(side="left", padx=3)

        # Fila 5: Transportista
        row = tk.Frame(form_left, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Transportista *:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.ROJO, width=14, anchor="e").pack(side="left", padx=3)
        self.transp_nombre = tk.StringVar()
        self.entry_transportista = tk.Entry(row, textvariable=self.transp_nombre, 
                                            font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                            width=22, relief="solid", bd=1)
        self.entry_transportista.pack(side="left", padx=3)
        tk.Button(row, text="...", font=T.FONT_NORMAL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  width=2, command=lambda: self._seleccionar_transportista(transportistas)).pack(side="left", padx=2)

        # Fila 6: CUIT Transportista
        row = tk.Frame(form_left, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="CUIT Transp.:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_cuit_transp = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                          width=15, relief="solid", bd=1)
        self.entry_cuit_transp.pack(side="left", padx=3)

        # Fila 7: Chofer
        row = tk.Frame(form_left, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Chofer *:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.ROJO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_chofer = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                     width=22, relief="solid", bd=1)
        self.entry_chofer.pack(side="left", padx=3)

        # Fila 8: DNI Chofer
        row = tk.Frame(form_left, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="DNI Chofer:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_dni_chofer = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                         width=12, relief="solid", bd=1)
        self.entry_dni_chofer.pack(side="left", padx=3)

        # ═══════════════════════════════════════════════════════════
        # COLUMNA DERECHA - Usuario y Pesaje
        # ═══════════════════════════════════════════════════════════
        right_frame = tk.Frame(main_frame, bg=T.FONDO)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Usuario Faena
        user_frame = tk.LabelFrame(right_frame, text=" USUARIO DESTINO ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                   relief="solid", bd=1)
        user_frame.pack(fill="x", pady=(0, 8))

        form_user = tk.Frame(user_frame, bg=T.BLANCO)
        form_user.pack(fill="x", padx=10, pady=8)

        row = tk.Frame(form_user, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Usuario Faena:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.usuario_destino = tk.StringVar()
        self.entry_usuario_destino = tk.Entry(row, textvariable=self.usuario_destino,
                                               font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                               width=20, relief="solid", bd=1)
        self.entry_usuario_destino.pack(side="left", padx=3)
        tk.Button(row, text="...", font=T.FONT_NORMAL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  width=2, command=lambda: self._seleccionar_usuario_faena(usuarios_faena)).pack(side="left", padx=2)

        row = tk.Frame(form_user, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Operador:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_operador = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                            width=25, relief="solid", bd=1)
        self.entry_operador.insert(0, f"{Sesion.numero_operador()} - {Sesion.nombre_operador()}")
        self.entry_operador.configure(state="readonly")
        self.entry_operador.pack(side="left", padx=3)

        # Precintos
        row = tk.Frame(form_user, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Precintos:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_precintos = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                        width=30, relief="solid", bd=1)
        self.entry_precintos.pack(side="left", padx=3)

        # Observaciones
        row = tk.Frame(form_user, bg=T.BLANCO)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Observaciones:", font=T.FONT_LABEL, 
                 bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w", padx=3)
        self.entry_obs = tk.Text(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                 fg=T.TEXTO, height=2, width=35, relief="solid", bd=1)
        self.entry_obs.pack(fill="x", padx=3, pady=3)

        # ═══════════════════════════════════════════════════════════
        # PESAJE - Seccion completa y visible
        # ═══════════════════════════════════════════════════════════
        peso_frame = tk.LabelFrame(right_frame, text=" PESAJE ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                   relief="solid", bd=1)
        peso_frame.pack(fill="both", expand=True)

        peso_inner = tk.Frame(peso_frame, bg=T.BLANCO)
        peso_inner.pack(expand=True, fill="both", padx=10, pady=10)

        # Display del peso GRANDE
        self.lbl_peso = tk.Label(peso_inner, text="0 kg", font=T.FONT_MONO, 
                                 bg=T.GRIS_CLARO, fg=T.VERDE, width=12, height=2, 
                                 relief="solid", bd=2)
        self.lbl_peso.pack(pady=10)

        # Botones de captura
        peso_btns = tk.Frame(peso_inner, bg=T.BLANCO)
        peso_btns.pack(pady=8)

        tk.Button(peso_btns, text="Capturar Balanza", font=T.FONT_BOTON, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=12, pady=5,
                  command=self._capturar_peso).pack(side="left", padx=8)
        
        tk.Label(peso_btns, text="o manual:", font=T.FONT_NORMAL, 
                 bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="left", padx=5)

        self.entry_peso = tk.Entry(peso_btns, font=T.FONT_MONO_SMALL, bg=T.GRIS_CLARO, 
                                   fg=T.TEXTO, width=10, justify="right", relief="solid", bd=1)
        self.entry_peso.pack(side="left", padx=3)
        self.entry_peso.insert(0, "0")
        
        tk.Label(peso_btns, text="kg", font=T.FONT_NORMAL, 
                 bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=3)

        # Botones de accion
        btn_frame = tk.Frame(peso_inner, bg=T.BLANCO)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="GUARDAR TICKET", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=8, 
                  command=self._guardar).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancelar", font=T.FONT_BOTON, bg=T.ROJO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=15, pady=8, 
                  command=self._show_tipo_selector).pack(side="left", padx=10)

    def _seleccionar_proveedor(self, proveedores):
        win = tk.Toplevel(self)
        win.title("Seleccionar Proveedor")
        win.geometry("450x350")
        win.configure(bg=T.FONDO)
        win.transient(self)
        win.grab_set()
        
        tk.Label(win, text="Seleccione un proveedor:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=10)
        
        frame = tk.Frame(win, bg=T.FONDO)
        frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame, font=T.FONT_NORMAL, bg=T.BLANCO, 
                             yscrollcommand=scrollbar.set, height=12)
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        for p in proveedores:
            listbox.insert("end", p['razon_social'])
        
        def on_select():
            sel = listbox.curselection()
            if sel:
                nombre = listbox.get(sel[0])
                self.prov_nombre.set(nombre)
                if nombre in self.proveedores_map:
                    self.proveedor_sel_id = self.proveedores_map[nombre]['id']
            win.destroy()
        
        tk.Button(win, text="Seleccionar", font=T.FONT_BOTON, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", command=on_select).pack(pady=10)
        
        listbox.bind("<Double-Button-1>", lambda e: on_select())

    def _seleccionar_transportista(self, transportistas):
        win = tk.Toplevel(self)
        win.title("Seleccionar Transportista")
        win.geometry("550x350")
        win.configure(bg=T.FONDO)
        win.transient(self)
        win.grab_set()
        
        tk.Label(win, text="Seleccione un transportista:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=10)
        
        frame = tk.Frame(win, bg=T.FONDO)
        frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        cols = ("nombre", "pat_chasis", "pat_acoplado")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        
        tree.heading("nombre", text="Nombre")
        tree.heading("pat_chasis", text="Pat. Chasis")
        tree.heading("pat_acoplado", text="Pat. Acoplado")
        
        tree.column("nombre", width=220)
        tree.column("pat_chasis", width=90)
        tree.column("pat_acoplado", width=90)
        
        tree.pack(fill="both", expand=True)
        
        self.temp_transp_map = {}
        for t in transportistas:
            item_id = tree.insert("", "end", values=(
                t['nombre'],
                t.get('patente_chasis', '-') or '-',
                t.get('patente_acoplado', '-') or '-'
            ))
            self.temp_transp_map[item_id] = t
        
        def on_select():
            sel = tree.selection()
            if sel:
                t = self.temp_transp_map[sel[0]]
                self.transp_nombre.set(t['nombre'])
                self.transportista_sel_id = t['id']
                if t.get('patente_chasis'):
                    self.entry_pat_chasis.delete(0, tk.END)
                    self.entry_pat_chasis.insert(0, t['patente_chasis'])
                if t.get('patente_acoplado'):
                    self.entry_pat_acoplado.delete(0, tk.END)
                    self.entry_pat_acoplado.insert(0, t['patente_acoplado'])
                if t.get('cuit'):
                    self.entry_cuit_transp.delete(0, tk.END)
                    self.entry_cuit_transp.insert(0, t['cuit'])
            win.destroy()
        
        tk.Button(win, text="Seleccionar", font=T.FONT_BOTON, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", command=on_select).pack(pady=10)
        
        tree.bind("<Double-Button-1>", lambda e: on_select())

    def _seleccionar_usuario_faena(self, usuarios_faena):
        win = tk.Toplevel(self)
        win.title("Seleccionar Usuario de Faena")
        win.geometry("400x300")
        win.configure(bg=T.FONDO)
        win.transient(self)
        win.grab_set()
        
        tk.Label(win, text="Seleccione un usuario de faena:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=10)
        
        frame = tk.Frame(win, bg=T.FONDO)
        frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame, font=T.FONT_NORMAL, bg=T.BLANCO, 
                             yscrollcommand=scrollbar.set, height=10)
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        self.temp_uf_map = {}
        for u in usuarios_faena:
            display = f"{u['nombre']} ({u.get('codigo_usuario', '-')})"
            listbox.insert("end", display)
            self.temp_uf_map[display] = u
        
        def on_select():
            sel = listbox.curselection()
            if sel:
                display = listbox.get(sel[0])
                u = self.temp_uf_map[display]
                self.usuario_destino.set(u['nombre'])
                self.usuario_faena_id = u['id']
            win.destroy()
        
        tk.Button(win, text="Seleccionar", font=T.FONT_BOTON, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", command=on_select).pack(pady=10)
        
        listbox.bind("<Double-Button-1>", lambda e: on_select())

    def _buscar_transportista(self, event):
        patente = self.entry_pat_chasis.get().strip().upper()
        if len(patente) >= 3:
            transp = buscar_transportista_by_patente(patente)
            if transp:
                self.transp_nombre.set(transp['nombre'])
                self.transportista_sel_id = transp['id']
                if transp.get('patente_acoplado'):
                    self.entry_pat_acoplado.delete(0, tk.END)
                    self.entry_pat_acoplado.insert(0, transp['patente_acoplado'])
                if transp.get('cuit'):
                    self.entry_cuit_transp.delete(0, tk.END)
                    self.entry_cuit_transp.insert(0, transp['cuit'])

    def _capturar_peso(self):
        try:
            from core.equipos import capturar_peso_balanza
            peso = capturar_peso_balanza()
            if peso is not None:
                self.lbl_peso.configure(text=f"{peso:,.0f} kg")
                self.entry_peso.delete(0, tk.END)
                self.entry_peso.insert(0, str(int(peso)))
                return
        except Exception as e:
            print(f"Error capturando peso: {e}")
        
        # Simulacion si no hay conexion
        import random
        peso = random.randint(5000, 25000)
        self.lbl_peso.configure(text=f"{peso:,.0f} kg")
        self.entry_peso.delete(0, tk.END)
        self.entry_peso.insert(0, str(peso))
        messagebox.showinfo("Balanza", f"Peso capturado (simulado): {peso} kg\n\nConfigure la balanza en Configuracion > Equipos")

    def _guardar(self):
        try:
            patente = self.entry_pat_chasis.get().strip()
            transportista = self.entry_transportista.get().strip()
            chofer = self.entry_chofer.get().strip()
        except tk.TclError:
            messagebox.showerror("Error", "Error al leer los datos. Intente nuevamente.")
            return

        if not patente:
            messagebox.showwarning("Validacion", "Patente Chasis es obligatoria")
            return
        if not transportista:
            messagebox.showwarning("Validacion", "Transportista es obligatorio")
            return
        if not chofer:
            messagebox.showwarning("Validacion", "Chofer es obligatorio")
            return

        try:
            peso = float(self.entry_peso.get().strip().replace(",", "."))
        except:
            messagebox.showwarning("Validacion", "Peso invalido")
            return

        if peso <= 0:
            messagebox.showwarning("Validacion", "El peso debe ser mayor a 0")
            return

        datos = {
            "numero_ticket": self.ticket_num,
            "tipo_ticket": "ingreso",
            "tipo_operacion": self.tipo_op,
            "patente_chasis": patente.upper(),
            "patente_acoplado": self.entry_pat_acoplado.get().upper(),
            "transportista_id": self.transportista_sel_id,
            "transportista": transportista,
            "cuit_transportista": self.entry_cuit_transp.get().strip(),
            "dni_chofer": self.entry_dni_chofer.get().strip(),
            "chofer": chofer,
            "operador_id": Sesion.operador_id(),
            "usuario_faena_id": self.usuario_faena_id,
            "proveedor_id": self.proveedor_sel_id,
            "numero_guia": self.entry_guia.get().strip(),
            "numero_dte": self.entry_dte.get().strip(),
            "num_habilitacion": self.entry_habilitacion.get().strip(),
            "precintos": self.entry_precintos.get().strip(),
            "observaciones": self.entry_obs.get("1.0", tk.END).strip(),
            "peso_kg": peso,
            "peso_manual": 1,
            "operador": Sesion.nombre_operador(),
        }

        try:
            guardar_ticket(datos)
            self._show_success(datos)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _show_success(self, datos):
        self._clear_content()

        frame = tk.Frame(self.content, bg=T.BLANCO, relief="solid", bd=2)
        frame.pack(expand=True, pady=40, padx=80)

        tk.Label(frame, text="TICKET GUARDADO", font=T.FONT_TITULO, 
                 bg=T.BLANCO, fg=T.VERDE).pack(pady=25)

        resumen = f"Ticket: {datos['numero_ticket']}\n"
        resumen += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        resumen += f"Proveedor: {self.prov_nombre.get() or '-'}\n"
        resumen += f"N Guia: {datos.get('numero_guia', '-') or '-'}\n"
        resumen += f"N DTE: {datos.get('numero_dte', '-') or '-'}\n\n"
        resumen += f"Patente: {datos['patente_chasis']} - {datos['patente_acoplado']}\n"
        resumen += f"Transportista: {datos['transportista']}\n"
        resumen += f"Chofer: {datos['chofer']}\n"
        resumen += f"Usuario Faena: {self.usuario_destino.get() or '-'}\n\n"
        resumen += f"Peso: {datos['peso_kg']:,.0f} kg\n\n"
        resumen += f"Operador: {Sesion.numero_operador()} - {datos['operador']}"

        tk.Label(frame, text=resumen, font=T.FONT_NORMAL, bg=T.BLANCO, 
                 fg=T.TEXTO, justify="left").pack(padx=25, pady=15)

        btns = tk.Frame(frame, bg=T.BLANCO)
        btns.pack(pady=15)

        tk.Button(btns, text="Nuevo Ingreso", font=T.FONT_BOTON, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=15, pady=8, 
                  command=self._show_tipo_selector).pack(side="left", padx=10)
        tk.Button(btns, text="Volver", font=T.FONT_BOTON, bg=T.GRIS_OSCURO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=15, pady=8, 
                  command=self._volver).pack(side="left", padx=10)
