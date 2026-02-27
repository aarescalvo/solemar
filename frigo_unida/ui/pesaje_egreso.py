"""
Pesaje - Egreso v1.9.9
Layout optimizado sin scrolls
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core import theme as T
from core.session import Sesion
from core.database import (
    get_proximo_ticket, 
    guardar_ticket_egreso,
    listar_tickets_ingreso_abiertos,
    get_ticket_by_id
)


class PesajeEgreso(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self.tipo_op = None
        self.ticket_ingreso = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="EGRESO - Pesaje de Salida", font=T.FONT_SUBTITULO, 
                 bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        self.content = tk.Frame(self, bg=T.FONDO)
        self.content.pack(expand=True, fill="both", padx=15, pady=10)
        
        self._show_tickets_disponibles()

    def _show_tickets_disponibles(self):
        for w in self.content.winfo_children():
            w.destroy()

        # Panel superior compacto
        info_frame = tk.Frame(self.content, bg=T.BLANCO, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=(0, 8))

        tk.Label(info_frame, text="TICKETS DE INGRESO DISPONIBLES", 
                 font=T.FONT_BOTON, bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=15, pady=8)
        tk.Label(info_frame, text="Seleccione un ticket para registrar el egreso", 
                 font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="right", padx=15, pady=8)

        # Filtros
        filtros_frame = tk.Frame(self.content, bg=T.BLANCO, relief="solid", bd=1)
        filtros_frame.pack(fill="x", pady=(0, 8))

        row = tk.Frame(filtros_frame, bg=T.BLANCO)
        row.pack(fill="x", padx=10, pady=6)

        tk.Label(row, text="Buscar patente:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_buscar = tk.Entry(row, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=12, relief="solid", bd=1)
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind("<KeyRelease>", self._filtrar)

        tk.Button(row, text="Actualizar", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self._cargar_tickets).pack(side="left", padx=10)

        # Tabla de tickets
        tabla_frame = tk.Frame(self.content, bg=T.BLANCO, relief="solid", bd=1)
        tabla_frame.pack(expand=True, fill="both")

        scroll = ttk.Scrollbar(tabla_frame)
        scroll.pack(side="right", fill="y")

        cols = ("ticket", "fecha", "patente_chasis", "patente_acoplado", "transportista", "peso", "estado")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", 
                                  yscrollcommand=scroll.set, height=12)

        headers = [
            ("ticket", "Ticket", 120),
            ("fecha", "Fecha/Hora", 120),
            ("patente_chasis", "Pat. Chasis", 85),
            ("patente_acoplado", "Pat. Acoplado", 85),
            ("transportista", "Transportista", 160),
            ("peso", "Peso (kg)", 90),
            ("estado", "Estado", 70)
        ]

        for col_id, text, width in headers:
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, minwidth=50)

        scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree.bind("<Double-1>", self._seleccionar_ticket)
        self.tree.bind("<Return>", self._seleccionar_ticket)

        # Botones
        btn_frame = tk.Frame(self.content, bg=T.FONDO)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="SELECCIONAR TICKET", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=15, pady=6,
                  command=self._seleccionar_ticket_click).pack(side="left", padx=10)

        tk.Label(btn_frame, text="Doble click en un ticket para seleccionarlo", 
                 font=T.FONT_LABEL, bg=T.FONDO, fg=T.GRIS_OSCURO).pack(side="left", padx=15)

        self._cargar_tickets()

    def _cargar_tickets(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        tickets = listar_tickets_ingreso_abiertos()
        self.tickets_map = {}

        for t in tickets:
            item_id = self.tree.insert("", "end", values=(
                t.get('numero_ticket', ''),
                f"{t.get('fecha', '')} {t.get('hora', '')}",
                t.get('patente_chasis', ''),
                t.get('patente_acoplado', ''),
                t.get('transportista', '') or '-',
                f"{t.get('peso_kg', 0):,.0f}",
                t.get('estado', 'abierto').upper()
            ))
            self.tickets_map[item_id] = t

        if not tickets:
            self.tree.insert("", "end", values=("- No hay tickets de ingreso disponibles -", "", "", "", "", "", ""))

    def _filtrar(self, event=None):
        buscar = self.entry_buscar.get().strip().upper()
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        tickets = listar_tickets_ingreso_abiertos()
        self.tickets_map = {}

        for t in tickets:
            patente_chasis = (t.get('patente_chasis', '') or '').upper()
            patente_acoplado = (t.get('patente_acoplado', '') or '').upper()
            
            if buscar and buscar not in patente_chasis and buscar not in patente_acoplado:
                continue

            item_id = self.tree.insert("", "end", values=(
                t.get('numero_ticket', ''),
                f"{t.get('fecha', '')} {t.get('hora', '')}",
                t.get('patente_chasis', ''),
                t.get('patente_acoplado', ''),
                t.get('transportista', '') or '-',
                f"{t.get('peso_kg', 0):,.0f}",
                t.get('estado', 'abierto').upper()
            ))
            self.tickets_map[item_id] = t

    def _seleccionar_ticket_click(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atencion", "Seleccione un ticket de ingreso")
            return
        
        item_id = selection[0]
        if item_id not in self.tickets_map:
            messagebox.showwarning("Atencion", "Seleccione un ticket valido")
            return

        self.ticket_ingreso = self.tickets_map[item_id]
        self._show_tipo_selector()

    def _seleccionar_ticket(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        if item_id not in self.tickets_map:
            return

        self.ticket_ingreso = self.tickets_map[item_id]
        self._show_tipo_selector()

    def _show_tipo_selector(self):
        for w in self.content.winfo_children():
            w.destroy()

        # Info del ticket seleccionado - compacto
        info_frame = tk.Frame(self.content, bg=T.BLANCO, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=8)

        tk.Label(info_frame, text="TICKET DE INGRESO SELECCIONADO", 
                 font=T.FONT_BOTON, bg=T.BLANCO, fg=T.AZUL).pack(anchor="w", padx=15, pady=(8, 3))

        info = f"N: {self.ticket_ingreso['numero_ticket']} | Fecha: {self.ticket_ingreso['fecha']} {self.ticket_ingreso['hora']}\n"
        info += f"Patente: {self.ticket_ingreso.get('patente_chasis', '-')} / {self.ticket_ingreso.get('patente_acoplado', '-')} | "
        info += f"Transportista: {self.ticket_ingreso.get('transportista', '-')} | Peso: {self.ticket_ingreso.get('peso_kg', 0):,.0f} kg"

        tk.Label(info_frame, text=info, font=T.FONT_NORMAL, bg=T.BLANCO, 
                 fg=T.TEXTO, justify="left").pack(anchor="w", padx=15, pady=(0, 8))

        # Selector de tipo
        tk.Label(self.content, text="Seleccione tipo de egreso:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=20)

        frame = tk.Frame(self.content, bg=T.FONDO)
        frame.pack()

        tipos = [
            ("CAMION VACIO", "Pesaje de tara - El camion regresa vacio", "vacio"),
            ("CAMION CON MERCANCIA", "Pesaje bruto de salida - El camion lleva carga", "mercancia")
        ]

        for titulo, desc, tipo in tipos:
            self._make_tipo_btn(frame, titulo, desc, tipo)

        # Boton volver
        tk.Button(self.content, text="Volver a lista", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self._show_tickets_disponibles).pack(pady=15)

    def _make_tipo_btn(self, parent, titulo, desc, tipo):
        btn = tk.Frame(parent, bg=T.BLANCO, relief="solid", bd=1, cursor="hand2")
        btn.pack(fill="x", pady=6, padx=20)

        tk.Label(btn, text=titulo, font=T.FONT_BOTON, bg=T.BLANCO, fg=T.VERDE).pack(pady=(10, 0))
        tk.Label(btn, text=desc, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=(0, 10))

        def on_click(e):
            self.tipo_op = tipo
            self._show_form()

        def on_enter(e):
            btn.configure(bg=T.GRIS_CLARO)
            for w in btn.winfo_children():
                w.configure(bg=T.GRIS_CLARO)

        def on_leave(e):
            btn.configure(bg=T.BLANCO)
            for w in btn.winfo_children():
                w.configure(bg=T.BLANCO)

        btn.bind("<Button-1>", on_click)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        for c in btn.winfo_children():
            c.bind("<Button-1>", on_click)

    def _show_form(self):
        for w in self.content.winfo_children():
            w.destroy()

        # Layout de 2 columnas
        main_frame = tk.Frame(self.content, bg=T.FONDO)
        main_frame.pack(fill="both", expand=True)

        # COLUMNA IZQUIERDA - Info del ingreso y datos adicionales
        left_frame = tk.Frame(main_frame, bg=T.FONDO)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Info del ticket de ingreso
        info_in = tk.LabelFrame(left_frame, text=" TICKET DE INGRESO ", 
                                font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.ROJO, relief="solid", bd=1)
        info_in.pack(fill="x", pady=8)

        info_inner = tk.Frame(info_in, bg=T.BLANCO)
        info_inner.pack(fill="x", padx=10, pady=8)

        campos = [
            ("N Ticket:", self.ticket_ingreso['numero_ticket']),
            ("Fecha:", f"{self.ticket_ingreso['fecha']} {self.ticket_ingreso['hora']}"),
            ("Patente:", f"{self.ticket_ingreso.get('patente_chasis', '-')} / {self.ticket_ingreso.get('patente_acoplado', '-')}"),
            ("Transportista:", self.ticket_ingreso.get('transportista', '-')),
            ("Peso registrado:", f"{self.ticket_ingreso.get('peso_kg', 0):,.0f} kg"),
        ]

        for label, valor in campos:
            row = tk.Frame(info_inner, bg=T.BLANCO)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
            tk.Label(row, text=valor, font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=3)

        # Datos adicionales (precintos + observaciones)
        extra_frame = tk.LabelFrame(left_frame, text=" DATOS DE PRECINTOS Y OBSERVACIONES ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        extra_frame.pack(fill="both", expand=True, pady=8)

        extra_inner = tk.Frame(extra_frame, bg=T.BLANCO)
        extra_inner.pack(fill="x", padx=10, pady=8)

        row_prec = tk.Frame(extra_inner, bg=T.BLANCO)
        row_prec.pack(fill="x", pady=4)
        tk.Label(row_prec, text="Precintos:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO, width=14, anchor="e").pack(side="left", padx=3)
        self.entry_precintos = tk.Entry(row_prec, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                        width=30, relief="solid", bd=1)
        # Precargar con los precintos del ingreso si existieran
        self.entry_precintos.insert(0, self.ticket_ingreso.get('precintos', '') or '')
        self.entry_precintos.pack(side="left", padx=3, fill="x", expand=True)

        tk.Label(extra_inner, text="Observaciones:", font=T.FONT_LABEL, 
                 bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w", padx=3, pady=(8, 0))
        self.text_obs = tk.Text(extra_inner, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                 fg=T.TEXTO, height=4, width=40, relief="solid", bd=1)
        self.text_obs.pack(fill="both", expand=True, padx=3, pady=(2, 4))

        # COLUMNA DERECHA - Pesaje y botones
        right_frame = tk.Frame(main_frame, bg=T.FONDO)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Nuevo ticket de egreso
        ticket = get_proximo_ticket("egreso")
        self.ticket_egreso = ticket

        ticket_frame = tk.Frame(right_frame, bg=T.VERDE)
        ticket_frame.pack(fill="x", pady=8)

        tk.Label(ticket_frame, text=f"Nuevo Ticket Egreso: {ticket}", font=T.FONT_BOTON, 
                 bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=8)
        tk.Label(ticket_frame, text=f"Tipo: {'VACIO' if self.tipo_op == 'vacio' else 'CON MERCANCIA'}", 
                 font=T.FONT_LABEL, bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=8)
        tk.Label(ticket_frame, text=f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                 font=T.FONT_NORMAL, bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="right", padx=15, pady=8)

        # Pesaje
        peso_frame = tk.LabelFrame(right_frame, text=" PESAJE DE EGRESO ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, relief="solid", bd=1)
        peso_frame.pack(fill="both", expand=True)

        peso_inner = tk.Frame(peso_frame, bg=T.BLANCO)
        peso_inner.pack(expand=True, fill="both", padx=15, pady=15)

        # Display del peso
        self.lbl_peso = tk.Label(peso_inner, text="0 kg", font=T.FONT_MONO, 
                                  bg=T.GRIS_CLARO, fg=T.VERDE, width=12, height=2, 
                                  relief="solid", bd=2)
        self.lbl_peso.pack(pady=10)

        # Botones de captura
        peso_btns = tk.Frame(peso_inner, bg=T.BLANCO)
        peso_btns.pack(pady=8)

        tk.Button(peso_btns, text="Capturar Balanza", font=T.FONT_BOTON, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=10, pady=5,
                  command=self._capturar_peso).pack(side="left", padx=8)
        tk.Label(peso_btns, text="o manual:", font=T.FONT_NORMAL, 
                 bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="left", padx=5)

        self.entry_peso = tk.Entry(peso_btns, font=T.FONT_MONO_SMALL, bg=T.GRIS_CLARO, 
                                    fg=T.TEXTO, width=10, justify="right", relief="solid", bd=1)
        self.entry_peso.pack(side="left", padx=3)
        self.entry_peso.insert(0, "0")
        tk.Label(peso_btns, text="kg", font=T.FONT_NORMAL, 
                 bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=3)

        # Calculo
        calc_frame = tk.Frame(peso_inner, bg=T.BLANCO)
        calc_frame.pack(pady=12)

        tk.Button(calc_frame, text="CALCULAR PESOS", font=T.FONT_BOTON, bg=T.ROJO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self._calcular).pack(pady=5)

        self.lbl_bruto = tk.Label(calc_frame, text="Peso Bruto: ---", 
                                   font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.TEXTO)
        self.lbl_bruto.pack()

        self.lbl_tara = tk.Label(calc_frame, text="Tara: ---", 
                                  font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.TEXTO)
        self.lbl_tara.pack()

        self.lbl_neto = tk.Label(calc_frame, text="Peso Neto: ---", 
                                  font=T.FONT_MONO, bg=T.BLANCO, fg=T.VERDE)
        self.lbl_neto.pack(pady=5)

        # Botones de accion
        btn_frame = tk.Frame(peso_inner, bg=T.BLANCO)
        btn_frame.pack(pady=12)

        tk.Button(btn_frame, text="GUARDAR Y CERRAR", font=T.FONT_BOTON, 
                  bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  padx=15, pady=6, command=self._guardar).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancelar", font=T.FONT_BOTON, bg=T.ROJO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=15, pady=6, 
                  command=self._show_tickets_disponibles).pack(side="left", padx=10)

    def _capturar_peso(self):
        import random
        peso = random.randint(5000, 25000)
        self.lbl_peso.configure(text=f"{peso:,} kg")
        self.entry_peso.delete(0, tk.END)
        self.entry_peso.insert(0, str(peso))
        messagebox.showinfo("Balanza", f"Peso capturado: {peso:,} kg")

    def _calcular(self):
        try:
            peso_egreso = float(self.entry_peso.get().strip().replace(",", "."))
        except:
            messagebox.showwarning("Error", "Peso invalido")
            return

        peso_ingreso = self.ticket_ingreso.get('peso_kg', 0)

        if self.tipo_op == "vacio":
            peso_bruto = peso_ingreso
            peso_tara = peso_egreso
        else:
            peso_bruto = peso_egreso
            peso_tara = peso_ingreso

        peso_neto = peso_bruto - peso_tara

        self.lbl_bruto.configure(text=f"Peso Bruto: {peso_bruto:,.0f} kg")
        self.lbl_tara.configure(text=f"Tara: {peso_tara:,.0f} kg")
        self.lbl_neto.configure(text=f"Peso Neto: {peso_neto:,.0f} kg")

        self.peso_bruto = peso_bruto
        self.peso_tara = peso_tara
        self.peso_neto = peso_neto

    def _guardar(self):
        if not hasattr(self, 'peso_neto'):
            messagebox.showwarning("Error", "Primero calcule los pesos")
            return

        try:
            peso_egreso = float(self.entry_peso.get().strip().replace(",", "."))
        except:
            messagebox.showwarning("Error", "Peso invalido")
            return

        if not messagebox.askyesno("Confirmar", 
            f"¿Confirmar egreso?\n\n"
            f"Ticket ingreso: {self.ticket_ingreso['numero_ticket']} (se cerrara)\n"
            f"Ticket egreso: {self.ticket_egreso}\n"
            f"Peso neto: {self.peso_neto:,.0f} kg"):
            return

        datos = {
            "numero_ticket": self.ticket_egreso,
            "tipo_ticket": "egreso",
            "tipo_operacion": self.tipo_op,
            "patente_chasis": self.ticket_ingreso.get('patente_chasis', ''),
            "patente_acoplado": self.ticket_ingreso.get('patente_acoplado', ''),
            "transportista": self.ticket_ingreso.get('transportista', ''),
            "cuit_transportista": self.ticket_ingreso.get('cuit_transportista', ''),
            "dni_chofer": self.ticket_ingreso.get('dni_chofer', ''),
            "chofer": self.ticket_ingreso.get('chofer', ''),
            "usuario_carga": self.ticket_ingreso.get('usuario_carga', ''),
            "num_habilitacion": self.ticket_ingreso.get('num_habilitacion', ''),
            # Permitir actualizar/definir precintos al egreso
            "precintos": self.entry_precintos.get().strip() or self.ticket_ingreso.get('precintos', ''),
            "observaciones": self.text_obs.get("1.0", tk.END).strip(),
            "peso_kg": peso_egreso,
            "peso_manual": 1,
            "ticket_ingreso_id": self.ticket_ingreso['id'],
            "peso_bruto_kg": self.peso_bruto,
            "peso_tara_kg": self.peso_tara,
            "peso_neto_kg": self.peso_neto,
            "operador": Sesion.nombre_usuario(),
        }

        try:
            guardar_ticket_egreso(datos)
            self._show_success(datos)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _show_success(self, datos):
        for w in self.content.winfo_children():
            w.destroy()

        frame = tk.Frame(self.content, bg=T.BLANCO, relief="solid", bd=2)
        frame.pack(expand=True, pady=40, padx=80)

        tk.Label(frame, text="TICKETS CERRADOS CORRECTAMENTE", 
                 font=T.FONT_TITULO, bg=T.BLANCO, fg=T.VERDE).pack(pady=25)

        resumen = f"Ticket Egreso: {datos['numero_ticket']} - CERRADO\n"
        resumen += f"Ticket Ingreso: {self.ticket_ingreso['numero_ticket']} - CERRADO\n"
        resumen += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        resumen += f"Patente: {datos['patente_chasis']} / {datos['patente_acoplado']}\n\n"
        resumen += f"Peso Bruto: {datos['peso_bruto_kg']:,.0f} kg\n"
        resumen += f"Tara: {datos['peso_tara_kg']:,.0f} kg\n"
        resumen += f"PESO NETO: {datos['peso_neto_kg']:,.0f} kg"

        tk.Label(frame, text=resumen, font=T.FONT_NORMAL, bg=T.BLANCO, 
                 fg=T.TEXTO, justify="left").pack(padx=25, pady=15)

        btns = tk.Frame(frame, bg=T.BLANCO)
        btns.pack(pady=15)

        tk.Button(btns, text="Nuevo Egreso", font=T.FONT_BOTON, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=15, pady=8, 
                  command=self._show_tickets_disponibles).pack(side="left", padx=10)
        tk.Button(btns, text="Volver al menu", font=T.FONT_BOTON, bg=T.GRIS_OSCURO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=15, pady=8, 
                  command=self.on_back).pack(side="left", padx=10)
