"""
Modulo de Configuracion - Administracion de Operadores y Usuarios de Faena
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from core import theme as T
from core.session import Sesion
from core.database import (
    # Operadores del sistema
    listar_operadores, get_operador_by_id, crear_operador, 
    actualizar_operador, cambiar_clave_operador, eliminar_operador,
    MODULOS_SISTEMA,
    # Usuarios de faena
    listar_usuarios_faena, listar_usuarios_faena_activos, get_usuario_faena_by_id,
    crear_usuario_faena, actualizar_usuario_faena, eliminar_usuario_faena,
    # Transportistas
    listar_transportistas, listar_transportistas_activos, get_transportista_by_id,
    crear_transportista, actualizar_transportista, eliminar_transportista,
    # Proveedores
    listar_proveedores, get_proveedor_by_id, guardar_proveedor, 
    actualizar_proveedor, eliminar_proveedor,
    # Numeracion tickets
    get_config_tickets, set_config_ticket, autenticar_operador,
)


class ConfigMenu(tk.Frame):
    def __init__(self, master, on_back, hide_items=None, start_view=None):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._current = None
        self.hide_items = set(hide_items) if hide_items else set()
        self.start_view = start_view
        self._build()
        if self.start_view == "tickets":
            self._show_ticket_numbers()

    def _build(self):
        header = tk.Frame(self, bg=T.GRIS_OSCURO, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=15, pady=12)
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
        tk.Label(header, text="CONFIGURACION GENERAL", font=T.FONT_SUBTITULO, 
                 bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)

        self.container = tk.Frame(self, bg=T.FONDO)
        self.container.pack(expand=True, fill="both")
        self._show_main_menu()

    def _show_main_menu(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both", padx=50, pady=30)

        tk.Label(self._current, text="Seleccione una opcion:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=20)

        cards_frame = tk.Frame(self._current, bg=T.FONDO)
        cards_frame.pack(expand=True)

        opciones_all = [
            ("NUMERACION TICKETS", "Próximos números ingreso/egreso", self._show_ticket_numbers, T.AZUL, "tickets"),
            ("ESTABLECIMIENTO", "Datos generales del establecimiento", self._show_establecimiento, T.GRIS_OSCURO, "establecimiento"),
            ("OPERADORES", "Operadores del sistema de trazabilidad", self._show_operadores, T.AZUL, "operadores"),
            ("USUARIOS FAENA", "Usuarios de faena (carneadores)", self._show_usuarios_faena, T.VERDE, "usuarios_faena"),
            ("TRANSPORTISTAS", "Transportistas y patentes", self._show_transportistas, T.AZUL, "transportistas"),
            ("PROVEEDORES", "Proveedores de hacienda", self._show_proveedores, T.GRIS_OSCURO, "proveedores"),
            ("CAMARAS", "Camaras frigorificas", self._show_camaras, T.VERDE, "camaras"),
            ("EQUIPOS", "Configuracion de equipos", self._show_equipos, T.AZUL, "equipos"),
        ]
        opciones = [(t, d, c, col) for (t, d, c, col, key) in opciones_all if key not in self.hide_items]

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

    def _clear_current(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both")

    def _show_operadores(self):
        self._clear_current()
        AdminOperadores(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_establecimiento(self):
        self._clear_current()
        ConfigEstablecimiento(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_usuarios_faena(self):
        self._clear_current()
        AdminUsuariosFaena(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_transportistas(self):
        self._clear_current()
        AdminTransportistas(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_proveedores(self):
        self._clear_current()
        AdminProveedores(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_camaras(self):
        self._clear_current()
        AdminCamaras(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_equipos(self):
        self._clear_current()
        ConfigEquipos(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_ticket_numbers(self):
        from datetime import datetime
        self._clear_current()
        top = tk.Frame(self._current, bg=T.FONDO)
        top.pack(fill="x")
        tk.Button(top, text="Volver", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._show_main_menu).pack(side="left", padx=5, pady=8)
        tk.Label(self._current, text="Numeracion de Tickets", font=T.FONT_TITULO, bg=T.FONDO, fg=T.TEXTO).pack(pady=10)

        config_frame = tk.Frame(self._current, bg=T.BLANCO, relief="solid", bd=1)
        config_frame.pack(pady=5, padx=10, fill="x")

        cfg = get_config_tickets()

        row1 = tk.Frame(config_frame, bg=T.BLANCO)
        row1.pack(fill="x", padx=20, pady=15)
        tk.Label(row1, text="Proximo N Ticket INGRESO:", font=T.FONT_BOTON, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=10)
        self.entry_ingreso = tk.Entry(row1, font=T.FONT_MONO, bg=T.GRIS_CLARO, fg=T.TEXTO, width=10, justify="right", relief="solid", bd=1)
        self.entry_ingreso.pack(side="left", padx=10)
        self.entry_ingreso.insert(0, str(cfg['prox_ingreso']))
        self.entry_ingreso.configure(state="disabled")
        tk.Button(row1, text="Modificar", font=T.FONT_BOTON, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=lambda: self._modificar_ticket("ingreso")).pack(side="left", padx=15)

        row2 = tk.Frame(config_frame, bg=T.BLANCO)
        row2.pack(fill="x", padx=20, pady=15)
        tk.Label(row2, text="Proximo N Ticket EGRESO:", font=T.FONT_BOTON, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=10)
        self.entry_egreso = tk.Entry(row2, font=T.FONT_MONO, bg=T.GRIS_CLARO, fg=T.TEXTO, width=10, justify="right", relief="solid", bd=1)
        self.entry_egreso.pack(side="left", padx=10)
        self.entry_egreso.insert(0, str(cfg['prox_egreso']))
        self.entry_egreso.configure(state="disabled")
        tk.Button(row2, text="Modificar", font=T.FONT_BOTON, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=lambda: self._modificar_ticket("egreso")).pack(side="left", padx=15)

        tk.Label(config_frame, text="Para modificar se requiere clave de supervisor",
                 font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=15)

        preview = tk.Frame(self._current, bg=T.AZUL)
        preview.pack(pady=15, padx=10, fill="x")
        tk.Label(preview, text="Vista Previa de Proximos Tickets", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(pady=10)
        anio = datetime.now().year
        self.lbl_preview_in = tk.Label(preview, text=f"Ingreso: TI-{anio}-{cfg['prox_ingreso']:06d}", font=T.FONT_MONO, bg=T.AZUL, fg=T.TEXTO_CLARO)
        self.lbl_preview_in.pack(pady=5)
        self.lbl_preview_out = tk.Label(preview, text=f"Egreso: TE-{anio}-{cfg['prox_egreso']:06d}", font=T.FONT_MONO, bg=T.AZUL, fg=T.TEXTO_CLARO)
        self.lbl_preview_out.pack(pady=5)

    def _modificar_ticket(self, tipo):
        dlg = tk.Toplevel(self)
        dlg.title("Autorizacion Requerida")
        dlg.geometry("380x250")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.configure(bg=T.FONDO)
        dlg.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + 400
        y = self.winfo_toplevel().winfo_y() + 200
        dlg.geometry(f"+{x}+{y}")

        tk.Label(dlg, text="AUTORIZACION DE SUPERVISOR", font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.ROJO).pack(pady=20)
        frame = tk.Frame(dlg, bg=T.BLANCO, relief="solid", bd=1)
        frame.pack(pady=10, padx=30, fill="x")
        tk.Label(frame, text="N Operador:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=0, padx=10, pady=8, sticky="e")
        entry_num = tk.Entry(frame, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, relief="solid", bd=1, width=15)
        entry_num.grid(row=0, column=1, padx=10, pady=8)
        tk.Label(frame, text="Clave:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=1, column=0, padx=10, pady=8, sticky="e")
        entry_pass = tk.Entry(frame, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, relief="solid", bd=1, width=15, show="*")
        entry_pass.grid(row=1, column=1, padx=10, pady=8)
        btns = tk.Frame(dlg, bg=T.FONDO)
        btns.pack(pady=15)

        def autorizar():
            num_op = entry_num.get().strip()
            clave = entry_pass.get()
            if not num_op or not clave:
                messagebox.showwarning("Error", "Complete todos los campos", parent=dlg)
                return
            if not num_op.isdigit():
                messagebox.showerror("Error", "N Operador debe ser numerico", parent=dlg)
                return
            auth = autenticar_operador(int(num_op), clave)
            if not auth:
                messagebox.showerror("Error", "Credenciales incorrectas", parent=dlg)
                return
            if auth['nivel'] not in ('supervisor', 'administrador'):
                messagebox.showerror("Error", "Se requiere rol de supervisor", parent=dlg)
                return
            dlg.destroy()
            self._editar_ticket(tipo)

        tk.Button(btns, text="Autorizar", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=autorizar).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_BOTON, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=dlg.destroy).pack(side="left", padx=10)
        entry_num.focus()
        entry_num.bind("<Return>", lambda e: entry_pass.focus())
        entry_pass.bind("<Return>", lambda e: autorizar())

    def _editar_ticket(self, tipo):
        dlg = tk.Toplevel(self)
        dlg.title(f"Modificar Ticket de {tipo.title()}")
        dlg.geometry("350x150")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.configure(bg=T.FONDO)
        dlg.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + 400
        y = self.winfo_toplevel().winfo_y() + 250
        dlg.geometry(f"+{x}+{y}")

        tk.Label(dlg, text=f"Nuevo valor para {tipo.upper()}:", font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.TEXTO).pack(pady=20)
        frame = tk.Frame(dlg, bg=T.BLANCO, relief="solid", bd=1)
        frame.pack(padx=30, fill="x")
        entry = tk.Entry(frame, font=T.FONT_MONO, bg=T.GRIS_CLARO, fg=T.TEXTO, width=15, justify="right")
        entry.pack(pady=15)
        if tipo == "ingreso":
            entry.insert(0, self.entry_ingreso.get())
        else:
            entry.insert(0, self.entry_egreso.get())
        btns = tk.Frame(dlg, bg=T.FONDO)
        btns.pack(pady=15)

        def guardar():
            try:
                valor = int(entry.get().strip())
                if valor < 1:
                    raise ValueError("Debe ser mayor a 0")
                set_config_ticket(tipo, valor)
                if tipo == "ingreso":
                    self.entry_ingreso.configure(state="normal")
                    self.entry_ingreso.delete(0, tk.END)
                    self.entry_ingreso.insert(0, str(valor))
                    self.entry_ingreso.configure(state="disabled")
                else:
                    self.entry_egreso.configure(state="normal")
                    self.entry_egreso.delete(0, tk.END)
                    self.entry_egreso.insert(0, str(valor))
                    self.entry_egreso.configure(state="disabled")
                from datetime import datetime
                anio = datetime.now().year
                try:
                    ing = int(self.entry_ingreso.get())
                    eg = int(self.entry_egreso.get())
                    self.lbl_preview_in.configure(text=f"Ingreso: TI-{anio}-{ing:06d}")
                    self.lbl_preview_out.configure(text=f"Egreso: TE-{anio}-{eg:06d}")
                except:
                    pass
                dlg.destroy()
                messagebox.showinfo("Exito", f"Ticket de {tipo} actualizado")
            except ValueError as e:
                messagebox.showerror("Error", f"Valor invalido: {e}", parent=dlg)

        tk.Button(btns, text="Guardar", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=guardar).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_BOTON, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=dlg.destroy).pack(side="left", padx=10)

# ═══════════════════════════════════════════════════════════════
# ADMINISTRACION DE OPERADORES DEL SISTEMA
# ═══════════════════════════════════════════════════════════════

class AdminOperadores(tk.Frame):
    """Administracion de operadores del sistema de trazabilidad"""
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self.operador_sel = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="OPERADORES DEL SISTEMA", font=T.FONT_SUBTITULO, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Panel izquierdo: Lista
        left_frame = tk.LabelFrame(content, text=" OPERADORES REGISTRADOS ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("num_op", "nombre", "nivel", "estado")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=12)

        self.tree.heading("num_op", text="N Operador")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("nivel", text="Nivel")
        self.tree.heading("estado", text="Estado")

        self.tree.column("num_op", width=100)
        self.tree.column("nombre", width=180)
        self.tree.column("nivel", width=120)
        self.tree.column("estado", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._seleccionar_operador)

        btns_left = tk.Frame(left_frame, bg=T.BLANCO)
        btns_left.pack(fill="x", padx=10, pady=10)

        tk.Button(btns_left, text="Nuevo", font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._nuevo_operador).pack(side="left", padx=5)
        tk.Button(btns_left, text="Editar", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._editar_operador).pack(side="left", padx=5)
        tk.Button(btns_left, text="Eliminar", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._eliminar_operador).pack(side="left", padx=5)
        tk.Button(btns_left, text="Actualizar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._cargar_operadores).pack(side="left", padx=5)

        # Panel derecho: Formulario
        right_frame = tk.LabelFrame(content, text=" DATOS DEL OPERADOR ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.form_frame = tk.Frame(right_frame, bg=T.BLANCO)
        self.form_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self._cargar_operadores()
        self._mostrar_form_vacio()

    def _cargar_operadores(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        operadores = listar_operadores()
        self.ops_map = {}
        
        for op in operadores:
            estado = "Activo" if op['activo'] else "Inactivo"
            nivel_text = {"administrador": "Administrador General", "supervisor": "Supervisor", "usuario": "Usuario"}.get(op['nivel'], op['nivel'])
            item_id = self.tree.insert("", "end", values=(
                f"{op['numero_operador']:04d}",
                op['nombre'],
                nivel_text,
                estado
            ))
            self.ops_map[item_id] = op

    def _seleccionar_operador(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        if item_id not in self.ops_map:
            return
        self.operador_sel = self.ops_map[item_id]
        self._mostrar_datos_operador()

    def _mostrar_form_vacio(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        tk.Label(self.form_frame, text="Seleccione un operador para ver los datos",
                 font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=50)

    def _mostrar_datos_operador(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        if not self.operador_sel:
            return
        
        op = self.operador_sel
        nivel_text = {"administrador": "Administrador General", "supervisor": "Supervisor", "usuario": "Usuario"}.get(op['nivel'], op['nivel'])
        
        campos = [
            ("N Operador:", f"{op['numero_operador']:04d}"),
            ("Nombre:", op['nombre']),
            ("Nivel:", nivel_text),
        ]
        
        for label, valor in campos:
            row = tk.Frame(self.form_frame, bg=T.BLANCO)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=18, anchor="e").pack(side="left", padx=5)
            tk.Label(row, text=valor, font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=5)
        
        # Mostrar permisos
        tk.Label(self.form_frame, text="Permisos de modulos:", font=T.FONT_LABEL, 
                 bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w", padx=5, pady=(15, 5))
        
        modulos_nombres = {
            "pesaje": "Pesaje", "recepcion": "Recepcion", "faena": "Faena",
            "camaras": "Camaras", "desposte": "Desposte", "stock": "Stock",
            "reportes": "Reportes", "configuracion": "Configuracion"
        }
        
        perm_frame = tk.Frame(self.form_frame, bg=T.BLANCO)
        perm_frame.pack(fill="x", padx=5)
        
        for i, mod in enumerate(MODULOS_SISTEMA):
            tiene = op.get(f'mod_{mod}', 0) or op['nivel'] == 'administrador'
            texto = f"[X] {modulos_nombres.get(mod, mod)}" if tiene else f"[ ] {modulos_nombres.get(mod, mod)}"
            color = T.VERDE if tiene else T.GRIS_OSCURO
            tk.Label(perm_frame, text=texto, font=T.FONT_NORMAL, bg=T.BLANCO, fg=color).grid(row=i//2, column=i%2, sticky="w", padx=10, pady=2)

    def _nuevo_operador(self):
        self.operador_sel = None
        self._mostrar_form_editar(nuevo=True)

    def _editar_operador(self):
        if not self.operador_sel:
            messagebox.showwarning("Atencion", "Seleccione un operador para editar")
            return
        self._mostrar_form_editar(nuevo=False)

    def _mostrar_form_editar(self, nuevo=True):
        for w in self.form_frame.winfo_children():
            w.destroy()
        
        self.entries = {}
        
        # N Operador (solo al crear nuevo)
        if nuevo:
            row = tk.Frame(self.form_frame, bg=T.BLANCO)
            row.pack(fill="x", pady=5)
            tk.Label(row, text="N Operador *:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO, width=18, anchor="e").pack(side="left", padx=5)
            entry = tk.Entry(row, font=T.FONT_MONO_SMALL, bg=T.GRIS_CLARO, width=10, justify="center")
            entry.pack(side="left", padx=5)
            entry.bind("<Key>", self._validar_numero)
            self.entries['numero_operador'] = entry
            tk.Label(row, text="(solo numeros, ej: 0001)", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="left", padx=5)
        
        # Nombre
        row = tk.Frame(self.form_frame, bg=T.BLANCO)
        row.pack(fill="x", pady=5)
        tk.Label(row, text="Nombre *:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO, width=18, anchor="e").pack(side="left", padx=5)
        entry = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=25)
        entry.pack(side="left", padx=5)
        if not nuevo:
            entry.insert(0, self.operador_sel['nombre'])
        self.entries['nombre'] = entry
        
        # Clave
        row = tk.Frame(self.form_frame, bg=T.BLANCO)
        row.pack(fill="x", pady=5)
        texto = "Clave *:" if nuevo else "Nueva clave:"
        tk.Label(row, text=texto, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO if nuevo else T.TEXTO, width=18, anchor="e").pack(side="left", padx=5)
        entry = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=15, show="*")
        entry.pack(side="left", padx=5)
        entry.bind("<Key>", self._validar_numero)
        self.entries['clave'] = entry
        tk.Label(row, text="(solo numeros)", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="left", padx=5)
        
        # Nivel
        row = tk.Frame(self.form_frame, bg=T.BLANCO)
        row.pack(fill="x", pady=5)
        tk.Label(row, text="Nivel *:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO, width=18, anchor="e").pack(side="left", padx=5)
        self.combo_nivel = ttk.Combobox(row, values=["administrador", "supervisor", "usuario"], width=22, state="readonly")
        self.combo_nivel.pack(side="left", padx=5)
        if not nuevo:
            self.combo_nivel.set(self.operador_sel['nivel'])
        else:
            self.combo_nivel.set("usuario")
        
        # Permisos (solo para nivel usuario)
        tk.Label(self.form_frame, text="Permisos de modulos (solo usuarios):", font=T.FONT_LABEL, 
                 bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w", padx=5, pady=(15, 5))
        
        self.checks = {}
        modulos_nombres = {
            "pesaje": "Pesaje", "recepcion": "Recepcion", "faena": "Faena",
            "camaras": "Camaras", "desposte": "Desposte", "stock": "Stock",
            "reportes": "Reportes", "configuracion": "Configuracion"
        }
        
        check_frame = tk.Frame(self.form_frame, bg=T.BLANCO)
        check_frame.pack(fill="x", padx=5)
        
        for i, mod in enumerate(MODULOS_SISTEMA):
            var = tk.IntVar()
            if not nuevo:
                var.set(self.operador_sel.get(f'mod_{mod}', 0))
            cb = tk.Checkbutton(check_frame, text=modulos_nombres.get(mod, mod), variable=var,
                               font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.TEXTO, selectcolor=T.GRIS_CLARO)
            cb.grid(row=i//2, column=i%2, sticky="w", padx=10, pady=2)
            self.checks[mod] = var
        
        # Botones
        btns = tk.Frame(self.form_frame, bg=T.BLANCO)
        btns.pack(fill="x", pady=20)
        
        texto_btn = "GUARDAR NUEVO" if nuevo else "GUARDAR CAMBIOS"
        tk.Button(btns, text=texto_btn, font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=20, pady=8,
                  command=lambda: self._guardar_operador(nuevo)).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=15, pady=8,
                  command=self._mostrar_form_vacio).pack(side="left", padx=10)

    def _validar_numero(self, event):
        """Solo permite ingresar numeros"""
        if event.keysym in ("BackSpace", "Delete", "Tab", "Return", "Left", "Right"):
            return
        if event.char and not event.char.isdigit():
            return "break"

    def _guardar_operador(self, nuevo):
        datos = {
            "nombre": self.entries['nombre'].get().strip(),
            "clave": self.entries['clave'].get().strip(),
            "nivel": self.combo_nivel.get(),
        }
        
        # Numero de operador solo al crear
        if nuevo:
            num_op_str = self.entries['numero_operador'].get().strip()
            if not num_op_str:
                messagebox.showwarning("Validacion", "El numero de operador es obligatorio")
                return
            if not num_op_str.isdigit():
                messagebox.showwarning("Validacion", "El numero de operador debe ser solo numeros")
                return
            datos["numero_operador"] = int(num_op_str)
        
        # Obtener permisos de checks
        for mod in MODULOS_SISTEMA:
            datos[f'mod_{mod}'] = self.checks[mod].get()
        
        if not datos["nombre"]:
            messagebox.showwarning("Validacion", "El nombre es obligatorio")
            return
        if nuevo and not datos["clave"]:
            messagebox.showwarning("Validacion", "La clave es obligatoria")
            return
        if datos["clave"] and not datos["clave"].isdigit():
            messagebox.showwarning("Validacion", "La clave debe ser solo numeros")
            return
        
        try:
            if nuevo:
                num = crear_operador(datos)
                messagebox.showinfo("Exito", f"Operador creado\nN Operador: {num:04d}")
            else:
                actualizar_operador(self.operador_sel['id'], datos)
                if datos["clave"]:
                    cambiar_clave_operador(self.operador_sel['id'], datos["clave"])
                messagebox.showinfo("Exito", "Operador actualizado correctamente")
            
            self._cargar_operadores()
            self._mostrar_form_vacio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _eliminar_operador(self):
        if not self.operador_sel:
            messagebox.showwarning("Atencion", "Seleccione un operador")
            return
        if messagebox.askyesno("Confirmar", f"Eliminar operador {self.operador_sel['nombre']}?"):
            try:
                eliminar_operador(self.operador_sel['id'])
                messagebox.showinfo("Exito", "Operador eliminado")
                self._cargar_operadores()
                self._mostrar_form_vacio()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")


# ═══════════════════════════════════════════════════════════════
# ADMINISTRACION DE USUARIOS DE FAENA
# ═══════════════════════════════════════════════════════════════

class AdminUsuariosFaena(tk.Frame):
    """Administracion de usuarios de faena (carneadores)"""
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self.usuario_sel = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="USUARIOS DE FAENA", font=T.FONT_SUBTITULO, 
                 bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Panel izquierdo: Lista
        left_frame = tk.LabelFrame(content, text=" USUARIOS REGISTRADOS ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("codigo", "nombre", "cuit", "matricula", "estado")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=12)

        self.tree.heading("codigo", text="Codigo")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("cuit", text="CUIT")
        self.tree.heading("matricula", text="Matricula")
        self.tree.heading("estado", text="Estado")

        self.tree.column("codigo", width=80)
        self.tree.column("nombre", width=150)
        self.tree.column("cuit", width=100)
        self.tree.column("matricula", width=100)
        self.tree.column("estado", width=70)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._seleccionar_usuario)

        btns_left = tk.Frame(left_frame, bg=T.BLANCO)
        btns_left.pack(fill="x", padx=10, pady=10)

        tk.Button(btns_left, text="Nuevo", font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._nuevo_usuario).pack(side="left", padx=5)
        tk.Button(btns_left, text="Editar", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._editar_usuario).pack(side="left", padx=5)
        tk.Button(btns_left, text="Eliminar", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._eliminar_usuario).pack(side="left", padx=5)
        tk.Button(btns_left, text="Actualizar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._cargar_usuarios).pack(side="left", padx=5)

        # Panel derecho: Formulario
        right_frame = tk.LabelFrame(content, text=" DATOS DEL USUARIO ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.form_frame = tk.Frame(right_frame, bg=T.BLANCO)
        self.form_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self._cargar_usuarios()
        self._mostrar_form_vacio()

    def _cargar_usuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        usuarios = listar_usuarios_faena()
        self.users_map = {}
        
        for u in usuarios:
            estado = "Activo" if u['activo'] else "Inactivo"
            item_id = self.tree.insert("", "end", values=(
                u['codigo_usuario'],
                u['nombre'],
                u.get('cuit', '-') or '-',
                u.get('matricula', '-') or '-',
                estado
            ))
            self.users_map[item_id] = u

    def _seleccionar_usuario(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        if item_id not in self.users_map:
            return
        self.usuario_sel = self.users_map[item_id]
        self._mostrar_datos_usuario()

    def _mostrar_form_vacio(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        tk.Label(self.form_frame, text="Seleccione un usuario para ver los datos",
                 font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=50)

    def _mostrar_datos_usuario(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        if not self.usuario_sel:
            return
        
        u = self.usuario_sel
        campos = [
            ("Codigo Usuario:", u['codigo_usuario']),
            ("Nombre:", u['nombre']),
            ("Razon Social:", u.get('razon_social', '-') or '-'),
            ("CUIT:", u.get('cuit', '-') or '-'),
            ("N Matricula:", u.get('matricula', '-') or '-'),
            ("Direccion:", u.get('direccion', '-') or '-'),
            ("Telefono:", u.get('telefono', '-') or '-'),
            ("Email:", u.get('email', '-') or '-'),
            ("N Cuenta:", u.get('numero_cuenta', '-') or '-'),
            ("Observaciones:", u.get('observaciones', '-') or '-'),
        ]
        
        for label, valor in campos:
            row = tk.Frame(self.form_frame, bg=T.BLANCO)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=18, anchor="e").pack(side="left", padx=5)
            tk.Label(row, text=valor, font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=5)

    def _nuevo_usuario(self):
        self.usuario_sel = None
        self._mostrar_form_editar(nuevo=True)

    def _editar_usuario(self):
        if not self.usuario_sel:
            messagebox.showwarning("Atencion", "Seleccione un usuario")
            return
        self._mostrar_form_editar(nuevo=False)

    def _mostrar_form_editar(self, nuevo=True):
        for w in self.form_frame.winfo_children():
            w.destroy()
        
        self.entries = {}
        campos = [
            ("nombre", "Nombre *:", True),
            ("razon_social", "Razon Social:", False),
            ("cuit", "CUIT:", False),
            ("matricula", "N Matricula:", False),
            ("direccion", "Direccion:", False),
            ("telefono", "Telefono:", False),
            ("email", "Email:", False),
            ("numero_cuenta", "N Cuenta:", False),
            ("observaciones", "Observaciones:", False),
        ]
        
        for key, label, required in campos:
            row = tk.Frame(self.form_frame, bg=T.BLANCO)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO if required else T.TEXTO, width=18, anchor="e").pack(side="left", padx=5)
            entry = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=30)
            entry.pack(side="left", padx=5)
            if not nuevo:
                entry.insert(0, self.usuario_sel.get(key, '') or '')
            self.entries[key] = entry
        
        btns = tk.Frame(self.form_frame, bg=T.BLANCO)
        btns.pack(fill="x", pady=20)
        
        texto_btn = "GUARDAR NUEVO" if nuevo else "GUARDAR CAMBIOS"
        tk.Button(btns, text=texto_btn, font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=20, pady=8,
                  command=lambda: self._guardar_usuario(nuevo)).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=15, pady=8,
                  command=self._mostrar_form_vacio).pack(side="left", padx=10)

    def _guardar_usuario(self, nuevo):
        datos = {key: self.entries[key].get().strip() for key in self.entries}
        
        if not datos["nombre"]:
            messagebox.showwarning("Validacion", "El nombre es obligatorio")
            return
        
        try:
            if nuevo:
                codigo = crear_usuario_faena(datos)
                messagebox.showinfo("Exito", f"Usuario creado\nCodigo: {codigo}")
            else:
                actualizar_usuario_faena(self.usuario_sel['id'], datos)
                messagebox.showinfo("Exito", "Usuario actualizado")
            
            self._cargar_usuarios()
            self._mostrar_form_vacio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _eliminar_usuario(self):
        if not self.usuario_sel:
            messagebox.showwarning("Atencion", "Seleccione un usuario")
            return
        if messagebox.askyesno("Confirmar", f"Eliminar usuario {self.usuario_sel['nombre']}?"):
            try:
                eliminar_usuario_faena(self.usuario_sel['id'])
                messagebox.showinfo("Exito", "Usuario eliminado")
                self._cargar_usuarios()
                self._mostrar_form_vacio()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")


# ═══════════════════════════════════════════════════════════════
# ADMINISTRACION DE TRANSPORTISTAS
# ═══════════════════════════════════════════════════════════════

class AdminTransportistas(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self.transportista_sel = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="TRANSPORTISTAS", font=T.FONT_SUBTITULO, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        left_frame = tk.LabelFrame(content, text=" TRANSPORTISTAS REGISTRADOS ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("num_reg", "nombre", "pat_chasis", "pat_acoplado", "estado")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=12)

        self.tree.heading("num_reg", text="N Registro")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("pat_chasis", text="Pat. Chasis")
        self.tree.heading("pat_acoplado", text="Pat. Acoplado")
        self.tree.heading("estado", text="Estado")

        self.tree.column("num_reg", width=90)
        self.tree.column("nombre", width=180)
        self.tree.column("pat_chasis", width=90)
        self.tree.column("pat_acoplado", width=90)
        self.tree.column("estado", width=70)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._seleccionar_transportista)

        btns_left = tk.Frame(left_frame, bg=T.BLANCO)
        btns_left.pack(fill="x", padx=10, pady=10)

        tk.Button(btns_left, text="Nuevo", font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._nuevo_transportista).pack(side="left", padx=5)
        tk.Button(btns_left, text="Editar", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._editar_transportista).pack(side="left", padx=5)
        tk.Button(btns_left, text="Eliminar", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._eliminar_transportista).pack(side="left", padx=5)
        tk.Button(btns_left, text="Actualizar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._cargar_transportistas).pack(side="left", padx=5)

        right_frame = tk.LabelFrame(content, text=" DATOS DEL TRANSPORTISTA ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.form_frame = tk.Frame(right_frame, bg=T.BLANCO)
        self.form_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self._cargar_transportistas()
        self._mostrar_form_vacio()

    def _cargar_transportistas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        transportistas = listar_transportistas()
        self.transp_map = {}
        for t in transportistas:
            estado = "Activo" if t['activo'] else "Inactivo"
            item_id = self.tree.insert("", "end", values=(
                t.get('codigo_transportista', '-'), t['nombre'],
                t.get('patente_chasis', '-') or '-',
                t.get('patente_acoplado', '-') or '-', estado
            ))
            self.transp_map[item_id] = t

    def _seleccionar_transportista(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        if item_id not in self.transp_map:
            return
        self.transportista_sel = self.transp_map[item_id]
        self._mostrar_datos()

    def _mostrar_form_vacio(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        tk.Label(self.form_frame, text="Seleccione un transportista",
                 font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=50)

    def _mostrar_datos(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        if not self.transportista_sel:
            return
        t = self.transportista_sel
        campos = [
            ("Codigo:", t.get('codigo_transportista', '-') or '-'),
            ("Nombre:", t['nombre']),
            ("Razon Social:", t.get('razon_social', '-') or '-'),
            ("CUIT:", t.get('cuit', '-') or '-'),
            ("Telefono:", t.get('telefono', '-') or '-'),
            ("Nombre Chofer:", t.get('nombre_chofer', '-') or '-'),
            ("DNI Chofer:", t.get('dni_chofer', '-') or '-'),
            ("Patente Chasis:", t.get('patente_chasis', '-') or '-'),
            ("Patente Acoplado:", t.get('patente_acoplado', '-') or '-'),
            ("Habilitacion SENASA:", t.get('num_habilitacion_senasa', '-') or '-'),
        ]
        for label, valor in campos:
            row = tk.Frame(self.form_frame, bg=T.BLANCO)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=18, anchor="e").pack(side="left", padx=5)
            tk.Label(row, text=valor, font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=5)

    def _nuevo_transportista(self):
        self.transportista_sel = None
        self._mostrar_form_editar(nuevo=True)

    def _editar_transportista(self):
        if not self.transportista_sel:
            messagebox.showwarning("Atencion", "Seleccione un transportista")
            return
        self._mostrar_form_editar(nuevo=False)

    def _mostrar_form_editar(self, nuevo=True):
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.entries = {}
        campos = [
            ("nombre", "Nombre *:", True),
            ("razon_social", "Razon Social:", False),
            ("cuit", "CUIT:", False),
            ("telefono", "Telefono:", False),
            ("nombre_chofer", "Nombre Chofer:", False),
            ("dni_chofer", "DNI Chofer:", False),
            ("patente_chasis", "Patente Chasis:", False),
            ("patente_acoplado", "Patente Acoplado:", False),
            ("num_habilitacion_senasa", "Habilitacion SENASA:", False),
        ]
        for key, label, required in campos:
            row = tk.Frame(self.form_frame, bg=T.BLANCO)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO if required else T.TEXTO, width=18, anchor="e").pack(side="left", padx=5)
            entry = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=25)
            entry.pack(side="left", padx=5)
            if not nuevo:
                entry.insert(0, self.transportista_sel.get(key, '') or '')
            self.entries[key] = entry
        
        btns = tk.Frame(self.form_frame, bg=T.BLANCO)
        btns.pack(fill="x", pady=20)
        tk.Button(btns, text="GUARDAR", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=20, pady=8,
                  command=lambda: self._guardar(nuevo)).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=15, pady=8,
                  command=self._mostrar_form_vacio).pack(side="left", padx=10)

    def _guardar(self, nuevo):
        datos = {key: self.entries[key].get().strip() for key in self.entries}
        datos['patente_chasis'] = datos['patente_chasis'].upper()
        datos['patente_acoplado'] = datos['patente_acoplado'].upper()
        
        if not datos["nombre"]:
            messagebox.showwarning("Validacion", "El nombre es obligatorio")
            return
        
        try:
            if nuevo:
                num = crear_transportista(datos)
                messagebox.showinfo("Exito", f"Transportista creado\nN Registro: {num}")
            else:
                actualizar_transportista(self.transportista_sel['id'], datos)
                messagebox.showinfo("Exito", "Transportista actualizado")
            self._cargar_transportistas()
            self._mostrar_form_vacio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _eliminar_transportista(self):
        if not self.transportista_sel:
            messagebox.showwarning("Atencion", "Seleccione un transportista")
            return
        if messagebox.askyesno("Confirmar", f"Eliminar {self.transportista_sel['nombre']}?"):
            try:
                eliminar_transportista(self.transportista_sel['id'])
                messagebox.showinfo("Exito", "Transportista eliminado")
                self._cargar_transportistas()
                self._mostrar_form_vacio()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")



# ═══════════════════════════════════════════════════════════════
# ADMINISTRACION DE PROVEEDORES
# ═══════════════════════════════════════════════════════════════

class AdminProveedores(tk.Frame):
    """Administracion de proveedores de hacienda"""
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self.proveedor_sel = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.GRIS_OSCURO, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="PROVEEDORES", font=T.FONT_SUBTITULO, 
                 bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Panel izquierdo: Lista
        left_frame = tk.LabelFrame(content, text=" PROVEEDORES REGISTRADOS ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("codigo", "razon", "cuit", "localidad", "estado")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=12)

        self.tree.heading("codigo", text="Codigo")
        self.tree.heading("razon", text="Razon Social")
        self.tree.heading("cuit", text="CUIT")
        self.tree.heading("localidad", text="Localidad")
        self.tree.heading("estado", text="Estado")

        self.tree.column("codigo", width=80)
        self.tree.column("razon", width=180)
        self.tree.column("cuit", width=100)
        self.tree.column("localidad", width=120)
        self.tree.column("estado", width=70)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._seleccionar_proveedor)

        btns_left = tk.Frame(left_frame, bg=T.BLANCO)
        btns_left.pack(fill="x", padx=10, pady=10)

        tk.Button(btns_left, text="Nuevo", font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._nuevo_proveedor).pack(side="left", padx=5)
        tk.Button(btns_left, text="Editar", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._editar_proveedor).pack(side="left", padx=5)
        tk.Button(btns_left, text="Eliminar", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._eliminar_proveedor).pack(side="left", padx=5)
        tk.Button(btns_left, text="Actualizar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._cargar_proveedores).pack(side="left", padx=5)

        # Panel derecho: Formulario
        right_frame = tk.LabelFrame(content, text=" DATOS DEL PROVEEDOR ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.form_frame = tk.Frame(right_frame, bg=T.BLANCO)
        self.form_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self._cargar_proveedores()
        self._mostrar_form_vacio()

    def _cargar_proveedores(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        proveedores = listar_proveedores()
        self.prov_map = {}
        
        for p in proveedores:
            estado = "Activo" if p.get('activo', 1) else "Inactivo"
            item_id = self.tree.insert("", "end", values=(
                p.get('codigo_proveedor', '-'),
                p['razon_social'],
                p.get('cuit', '-') or '-',
                p.get('localidad', '-') or '-',
                estado
            ))
            self.prov_map[item_id] = p

    def _seleccionar_proveedor(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        if item_id not in self.prov_map:
            return
        self.proveedor_sel = self.prov_map[item_id]
        self._mostrar_datos_proveedor()

    def _mostrar_form_vacio(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        tk.Label(self.form_frame, text="Seleccione un proveedor para ver los datos",
                 font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=50)

    def _mostrar_datos_proveedor(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        if not self.proveedor_sel:
            return
        
        p = self.proveedor_sel
        campos = [
            ("Codigo:", p.get('codigo_proveedor', '-') or '-'),
            ("Razon Social:", p['razon_social']),
            ("CUIT:", p.get('cuit', '-') or '-'),
            ("Provincia:", p.get('provincia', '-') or '-'),
            ("Localidad:", p.get('localidad', '-') or '-'),
            ("Direccion:", p.get('direccion', '-') or '-'),
            ("Telefono:", p.get('telefono', '-') or '-'),
            ("Email:", p.get('email', '-') or '-'),
            ("Contacto:", p.get('contacto', '-') or '-'),
            ("RENSPA:", p.get('renspa', '-') or '-'),
        ]
        
        for label, valor in campos:
            row = tk.Frame(self.form_frame, bg=T.BLANCO)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=18, anchor="e").pack(side="left", padx=5)
            tk.Label(row, text=valor, font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=5)

    def _nuevo_proveedor(self):
        self.proveedor_sel = None
        self._mostrar_form_editar(nuevo=True)

    def _editar_proveedor(self):
        if not self.proveedor_sel:
            messagebox.showwarning("Atencion", "Seleccione un proveedor")
            return
        self._mostrar_form_editar(nuevo=False)

    def _mostrar_form_editar(self, nuevo=True):
        for w in self.form_frame.winfo_children():
            w.destroy()
        
        self.entries = {}
        campos = [
            ("razon_social", "Razon Social *:", True),
            ("cuit", "CUIT:", False),
            ("provincia", "Provincia:", False),
            ("localidad", "Localidad:", False),
            ("direccion", "Direccion:", False),
            ("telefono", "Telefono:", False),
            ("email", "Email:", False),
            ("contacto", "Contacto:", False),
            ("renspa", "RENSPA:", False),
        ]
        
        for key, label, required in campos:
            row = tk.Frame(self.form_frame, bg=T.BLANCO)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO if required else T.TEXTO, width=18, anchor="e").pack(side="left", padx=5)
            entry = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=30)
            entry.pack(side="left", padx=5)
            if not nuevo:
                entry.insert(0, self.proveedor_sel.get(key, '') or '')
            self.entries[key] = entry
        
        btns = tk.Frame(self.form_frame, bg=T.BLANCO)
        btns.pack(fill="x", pady=20)
        
        texto_btn = "GUARDAR NUEVO" if nuevo else "GUARDAR CAMBIOS"
        tk.Button(btns, text=texto_btn, font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=20, pady=8,
                  command=lambda: self._guardar_proveedor(nuevo)).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=15, pady=8,
                  command=self._mostrar_form_vacio).pack(side="left", padx=10)

    def _guardar_proveedor(self, nuevo):
        datos = {key: self.entries[key].get().strip() for key in self.entries}
        
        if not datos["razon_social"]:
            messagebox.showwarning("Validacion", "La razon social es obligatoria")
            return
        
        try:
            if nuevo:
                codigo = guardar_proveedor(datos)
                messagebox.showinfo("Exito", f"Proveedor creado\nCodigo: {codigo}")
            else:
                actualizar_proveedor(self.proveedor_sel['id'], datos)
                messagebox.showinfo("Exito", "Proveedor actualizado")
            
            self._cargar_proveedores()
            self._mostrar_form_vacio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _eliminar_proveedor(self):
        if not self.proveedor_sel:
            messagebox.showwarning("Atencion", "Seleccione un proveedor")
            return
        if messagebox.askyesno("Confirmar", f"Eliminar proveedor {self.proveedor_sel['razon_social']}?"):
            try:
                eliminar_proveedor(self.proveedor_sel['id'])
                messagebox.showinfo("Exito", "Proveedor eliminado")
                self._cargar_proveedores()
                self._mostrar_form_vacio()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")


# ═══════════════════════════════════════════════════════════════
# ADMINISTRACION DE CAMARAS
# ═══════════════════════════════════════════════════════════════

class AdminCamaras(tk.Frame):
    """Administracion de camaras frigorificas"""
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="CAMARAS FRIGORIFICAS", font=T.FONT_SUBTITULO, 
                 bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Panel izquierdo: lista de camaras
        left_frame = tk.LabelFrame(content, text=" CAMARAS ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("numero", "nombre", "capacidad", "ocupacion", "disp")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=12)

        self.tree.heading("numero", text="N")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("capacidad", text="Cap.kg")
        self.tree.heading("ocupacion", text="Ocup.kg")
        self.tree.heading("disp", text="Disp.kg")

        self.tree.column("numero", width=50)
        self.tree.column("nombre", width=150)
        self.tree.column("capacidad", width=80)
        self.tree.column("ocupacion", width=80)
        self.tree.column("disp", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btns_left = tk.Frame(left_frame, bg=T.BLANCO)
        btns_left.pack(fill="x", padx=10, pady=10)

        tk.Button(btns_left, text="Actualizar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._cargar_camaras).pack(side="left", padx=5)

        # Panel derecho: contenido
        right_frame = tk.LabelFrame(content, text=" CONTENIDO DE CAMARA ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.content_frame = tk.Frame(right_frame, bg=T.BLANCO)
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self._cargar_camaras()
        self._mostrar_vacio()

    def _cargar_camaras(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        from core.database import listar_camaras
        camaras = listar_camaras()
        self.camaras_map = {}
        
        for c in camaras:
            ocup = c.get('ocupacion_kg', 0) or 0
            cap = c.get('capacidad_kg', 0) or 0
            disp = cap - ocup
            item_id = self.tree.insert("", "end", values=(
                c.get('numero', ''),
                c.get('nombre', ''),
                f"{cap:,.0f}",
                f"{ocup:,.0f}",
                f"{disp:,.0f}",
            ))
            self.camaras_map[item_id] = c
        
        self.tree.bind("<<TreeviewSelect>>", self._seleccionar_camara)

    def _seleccionar_camara(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        if item_id not in self.camaras_map:
            return
        self.camara_sel = self.camaras_map[item_id]
        self._mostrar_contenido()

    def _mostrar_vacio(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        tk.Label(self.content_frame, text="Seleccione una camara para ver su contenido",
                 font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=50)

    def _mostrar_contenido(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        
        from core.database import listar_medias_en_camara
        camara_id = self.camara_sel.get('id')
        medias = listar_medias_en_camara(camara_id) if camara_id else []
        
        cols = ("codigo", "especie", "media", "peso", "fecha")
        tree = ttk.Treeview(self.content_frame, columns=cols, show="headings", height=10)
        
        tree.heading("codigo", text="Codigo")
        tree.heading("especie", text="Especie")
        tree.heading("media", text="Media")
        tree.heading("peso", text="Peso kg")
        tree.heading("fecha", text="Fecha")
        
        tree.column("codigo", width=100)
        tree.column("especie", width=80)
        tree.column("media", width=60)
        tree.column("peso", width=80)
        tree.column("fecha", width=100)
        
        tree.pack(fill="both", expand=True)
        
        for m in medias:
            tree.insert("", "end", values=(
                m.get('codigo', ''),
                m.get('especie', ''),
                m.get('media', ''),
                f"{m.get('peso', 0):,.0f}",
                m.get('fecha_ingreso', ''),
            ))


# ═══════════════════════════════════════════════════════════════
# CONFIGURACION DE EQUIPOS
# ═══════════════════════════════════════════════════════════════

class ConfigEquipos(tk.Frame):
    """Configuracion de equipos (balanza, RFID, impresora)"""
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="CONFIGURACION DE EQUIPOS", font=T.FONT_SUBTITULO, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=50, pady=30)

        # Balanza
        balanza_frame = tk.LabelFrame(content, text=" BALANZA (RS232) ", 
                                      font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        balanza_frame.pack(fill="x", pady=10)

        from core.database import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM config_equipos WHERE id=1")
        cfg = dict(cur.fetchone() or {})
        conn.close()

        row1 = tk.Frame(balanza_frame, bg=T.BLANCO)
        row1.pack(fill="x", padx=15, pady=8)
        
        tk.Label(row1, text="Puerto:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=15, anchor="e").pack(side="left", padx=5)
        self.entry_balanza_puerto = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=10)
        self.entry_balanza_puerto.insert(0, cfg.get('balanza_puerto', 'COM1'))
        self.entry_balanza_puerto.pack(side="left", padx=5)
        
        tk.Label(row1, text="Baudrate:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=10, anchor="e").pack(side="left", padx=5)
        self.entry_balanza_baud = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=8)
        self.entry_balanza_baud.insert(0, str(cfg.get('balanza_baudrate', 9600)))
        self.entry_balanza_baud.pack(side="left", padx=5)

        # RFID
        rfid_frame = tk.LabelFrame(content, text=" BASTON RFID (RS232) ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE, relief="solid", bd=1)
        rfid_frame.pack(fill="x", pady=10)

        row2 = tk.Frame(rfid_frame, bg=T.BLANCO)
        row2.pack(fill="x", padx=15, pady=8)
        
        tk.Label(row2, text="Puerto:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=15, anchor="e").pack(side="left", padx=5)
        self.entry_rfid_puerto = tk.Entry(row2, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=10)
        self.entry_rfid_puerto.insert(0, cfg.get('rfid_puerto', 'COM2'))
        self.entry_rfid_puerto.pack(side="left", padx=5)
        
        tk.Label(row2, text="Baudrate:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=10, anchor="e").pack(side="left", padx=5)
        self.entry_rfid_baud = tk.Entry(row2, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=8)
        self.entry_rfid_baud.insert(0, str(cfg.get('rfid_baudrate', 9600)))
        self.entry_rfid_baud.pack(side="left", padx=5)

        # Impresora
        imp_frame = tk.LabelFrame(content, text=" IMPRESORA DE ETIQUETAS ", 
                                  font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.GRIS_OSCURO, relief="solid", bd=1)
        imp_frame.pack(fill="x", pady=10)

        row3 = tk.Frame(imp_frame, bg=T.BLANCO)
        row3.pack(fill="x", padx=15, pady=8)
        
        tk.Label(row3, text="Puerto:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=15, anchor="e").pack(side="left", padx=5)
        self.entry_imp_puerto = tk.Entry(row3, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=10)
        self.entry_imp_puerto.insert(0, cfg.get('impresora_puerto', 'LPT1'))
        self.entry_imp_puerto.pack(side="left", padx=5)
        
        tk.Label(row3, text="Tipo:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=10, anchor="e").pack(side="left", padx=5)
        self.entry_imp_tipo = tk.Entry(row3, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=10)
        self.entry_imp_tipo.insert(0, cfg.get('impresora_tipo', 'datamax'))
        self.entry_imp_tipo.pack(side="left", padx=5)

        # Botones
        btns = tk.Frame(content, bg=T.FONDO)
        btns.pack(pady=20)
        
        tk.Button(btns, text="GUARDAR CONFIGURACION", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=20, pady=8, command=self._guardar).pack(side="left", padx=10)
        tk.Button(btns, text="Probar Balanza", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=15, pady=8, command=self._probar_balanza).pack(side="left", padx=10)

    def _guardar(self):
        conn = get_connection()
        conn.execute("""
            UPDATE config_equipos SET 
                balanza_puerto=?, balanza_baudrate=?,
                rfid_puerto=?, rfid_baudrate=?,
                impresora_puerto=?, impresora_tipo=?
            WHERE id=1
        """, (
            self.entry_balanza_puerto.get().strip(),
            int(self.entry_balanza_baud.get().strip() or 9600),
            self.entry_rfid_puerto.get().strip(),
            int(self.entry_rfid_baud.get().strip() or 9600),
            self.entry_imp_puerto.get().strip(),
            self.entry_imp_tipo.get().strip()
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Exito", "Configuracion guardada correctamente")

    def _probar_balanza(self):
        try:
            from core.equipos import capturar_peso_balanza
            peso = capturar_peso_balanza()
            if peso is not None:
                messagebox.showinfo("Balanza", f"Peso capturado: {peso} kg")
            else:
                messagebox.showwarning("Balanza", "No se pudo capturar peso. Verifique la conexion.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con la balanza:\n{e}")


# ═══════════════════════════════════════════════════════════════
# CONFIGURACION DE DATOS DEL ESTABLECIMIENTO
# ═══════════════════════════════════════════════════════════════

class ConfigEstablecimiento(tk.Frame):
    """Datos generales del establecimiento (nombre, CUIT, direccion, matricula, N° establecimiento)"""
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="DATOS DEL ESTABLECIMIENTO", font=T.FONT_SUBTITULO, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=50, pady=30)

        frame = tk.LabelFrame(content, text=" DATOS GENERALES ", 
                              font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        frame.pack(fill="x", pady=10)

        inner = tk.Frame(frame, bg=T.BLANCO)
        inner.pack(fill="x", padx=20, pady=15)

        # Leer configuracion actual
        from core.database import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM config_establecimiento WHERE id=1")
        cfg_row = cur.fetchone()
        cfg = dict(cfg_row) if cfg_row else {}
        conn.close()

        # Campos
        self.entry_nombre = self._make_row(inner, 0, "Nombre:", cfg.get("nombre", ""), required=True)
        self.entry_cuit = self._make_row(inner, 1, "CUIT:", cfg.get("cuit", ""))
        self.entry_direccion = self._make_row(inner, 2, "Direccion:", cfg.get("direccion", ""))
        self.entry_matricula = self._make_row(inner, 3, "Matricula:", cfg.get("matricula", ""))
        self.entry_nro_est = self._make_row(inner, 4, "N° Establecimiento:", cfg.get("numero_establecimiento", ""))

        # Botones
        btns = tk.Frame(content, bg=T.FONDO)
        btns.pack(pady=20)

        tk.Button(btns, text="GUARDAR DATOS", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=25, pady=8,
                  command=self._guardar).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", padx=15, pady=8,
                  command=self.on_back).pack(side="left", padx=10)

    def _make_row(self, parent, row_idx, label, valor, required=False):
        row = tk.Frame(parent, bg=T.BLANCO)
        row.grid(row=row_idx, column=0, sticky="w", pady=5)
        texto = f"{label}" if not required else f"{label} *"
        color = T.ROJO if required else T.TEXTO
        tk.Label(row, text=texto, font=T.FONT_LABEL, bg=T.BLANCO, fg=color, width=20, anchor="e").pack(side="left", padx=5)
        entry = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=40, relief="solid", bd=1)
        entry.insert(0, valor or "")
        entry.pack(side="left", padx=5)
        return entry

    def _guardar(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Validacion", "El nombre del establecimiento es obligatorio")
            return

        datos = {
            "nombre": nombre,
            "cuit": self.entry_cuit.get().strip(),
            "direccion": self.entry_direccion.get().strip(),
            "matricula": self.entry_matricula.get().strip(),
            "numero_establecimiento": self.entry_nro_est.get().strip(),
        }

        from core.database import get_connection
        conn = get_connection()
        conn.execute("""
            UPDATE config_establecimiento SET 
                nombre=?, cuit=?, direccion=?, matricula=?, numero_establecimiento=?
            WHERE id=1
        """, (
            datos["nombre"], datos["cuit"], datos["direccion"],
            datos["matricula"], datos["numero_establecimiento"]
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Exito", "Datos del establecimiento guardados correctamente")
