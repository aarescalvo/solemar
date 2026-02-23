"""
Módulo de Recepción - Frigorífico Solemar
Estructura en 4 pasos:
1. Selección de especie, tropa y vinculación con ticket de ingreso (muestra observaciones)
2. Cantidad de animales por tipificación
3. Captura individual de datos (KG, caravana, raza, tipificación) + impresión etiqueta
4. Reimpresión de etiquetas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core import theme as T
from core.session import Sesion
from core.database import (
    # Tropas
    get_proxima_tropa, crear_tropa_paso1, get_tropa_by_id, get_tropa_by_numero,
    listar_tropas, listar_tropas_activas, actualizar_tropa_cantidad_esperada,
    guardar_tipificaciones_tropa, get_tipificaciones_tropa, finalizar_tropa,
    # Animales
    get_proximo_numero_animal, guardar_animal, listar_animales,
    get_animal_by_id, get_animal_by_codigo, actualizar_animal, eliminar_animal,
    listar_eliminados_tropa, contar_animales_tropa, contar_animales_tropa_todos,
    marcar_etiqueta_impresa,
    # Corrales
    listar_corrales, get_corral_by_id,
    # Proveedores
    listar_proveedores, get_proveedor_by_id,
    # Tickets
    listar_tickets_ingreso_abiertos, get_ticket_by_id,
    # Tipificaciones
    TIPIFICACIONES_BOVINO, TIPIFICACIONES_EQUINO, RAZAS_BOVINO, PELAJES_EQUINO, GORDURAS_EQUINO
)
from core.equipos import GestorEquipos, BalanzaRS232, BastonRFID
from core.impresion import GestorImpresion, generar_vista_previa_etiqueta


class RecepcionMenu(tk.Frame):
    """Menú principal del módulo de recepción"""
    
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._current = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self._back).pack(side="left", padx=15, pady=12)
        tk.Label(header, text="🐄 MÓDULO DE RECEPCIÓN", font=T.FONT_SUBTITULO, bg=T.AZUL, 
                 fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)

        self.container = tk.Frame(self, bg=T.FONDO)
        self.container.pack(expand=True, fill="both")
        self._show_main_menu()

    def _show_main_menu(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both", padx=50, pady=30)

        tk.Label(self._current, text="Seleccione una opción:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=20)

        cards_frame = tk.Frame(self._current, bg=T.FONDO)
        cards_frame.pack(expand=True)

        opciones = [
            ("📥 NUEVA TROPA", "Iniciar proceso de recepción", self._show_paso1, T.VERDE),
            ("⚖️ PESAJE HACIENDA EN PIE", "Pesaje individual de animales", self._show_pesaje_individual, T.AZUL),
            ("📋 LISTAR TROPAS", "Ver tropas registradas", self._show_listar_tropas, T.AZUL),
            ("🔄 REIMPRIMIR ETIQUETAS", "Reimprimir etiquetas de animales", self._show_reimpresion, T.AZUL),
        ]

        for i, (titulo, desc, cmd, color) in enumerate(opciones):
            self._make_card(cards_frame, titulo, desc, cmd, color, 0, i)

    def _make_card(self, parent, titulo, desc, cmd, color, row, col):
        outer = tk.Frame(parent, bg=T.FONDO, width=250, height=130)
        outer.grid(row=row, column=col, padx=12, pady=12)
        outer.grid_propagate(False)

        card = tk.Frame(outer, bg=T.BLANCO, relief="solid", bd=1, cursor="hand2")
        card.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(card, text=titulo, font=T.FONT_BOTON, bg=T.BLANCO, fg=color).pack(pady=(20, 5))
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

    def _show_paso1(self):
        """Paso 1: Selección de especie, tropa y vinculación con ticket"""
        self._clear_current()
        Paso1NuevaTropa(self._current, self._show_main_menu, self._ir_paso2).pack(expand=True, fill="both")

    def _show_pesaje_individual(self):
        """Pesaje individual de hacienda en pie"""
        self._clear_current()
        PesajeIndividual(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _ir_paso2(self, tropa_id):
        """Navega al paso 2 con el ID de tropa creado"""
        self._clear_current()
        Paso2Tipificaciones(self._current, tropa_id, self._show_paso1, self._ir_paso3).pack(expand=True, fill="both")

    def _ir_paso3(self, tropa_id):
        """Navega al paso 3 para captura individual"""
        self._clear_current()
        Paso3CapturaIndividual(self._current, tropa_id, self._show_main_menu).pack(expand=True, fill="both")

    def _show_listar_tropas(self):
        self._clear_current()
        ListarTropas(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_reimpresion(self):
        self._clear_current()
        ReimpresionEtiquetas(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _back(self):
        self.master._show_menu()


# ═══════════════════════════════════════════════════════════════
# PASO 1: Selección de especie, tropa y vinculación con ticket
# ═══════════════════════════════════════════════════════════════

class Paso1NuevaTropa(tk.Frame):
    """
    Paso 1: 
    - Seleccionar especie (bovino/equino)
    - Obtener número de tropa automático
    - Vincular con ticket de pesaje de ingreso (muestra observaciones del ticket)
    - El proveedor y guía ya vienen del ticket de ingreso
    """
    
    def __init__(self, master, on_back, on_next):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self.on_next = on_next
        self.especie_sel = None
        self.ticket_sel = None
        self._build()
    
    def _build(self):
        # Header
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📥 PASO 1: Nueva Tropa", font=T.FONT_SUBTITULO, bg=T.VERDE, 
                 fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)
        
        # Indicador de pasos
        pasos_frame = tk.Frame(header, bg=T.VERDE)
        pasos_frame.pack(side="right", padx=20)
        
        pasos = [("1", T.AZUL), ("2", T.GRIS_OSCURO), ("3", T.GRIS_OSCURO), ("4", T.GRIS_OSCURO)]
        for num, color in pasos:
            lbl = tk.Label(pasos_frame, text=num, font=T.FONT_BOTON, bg=color, fg=T.TEXTO_CLARO,
                          width=3, relief="solid", bd=1)
            lbl.pack(side="left", padx=3)
        
        # Contenido
        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Panel de especie
        especie_frame = tk.LabelFrame(content, text=" SELECCIONAR ESPECIE ", 
                                      font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.ROJO, 
                                      relief="solid", bd=1)
        especie_frame.pack(fill="x", pady=10)
        
        btn_frame = tk.Frame(especie_frame, bg=T.BLANCO)
        btn_frame.pack(pady=15)
        
        self.btn_bovino = tk.Button(btn_frame, text="🐄 BOVINO", font=T.FONT_BOTON, bg=T.GRIS_CLARO,
                                    fg=T.TEXTO, relief="solid", bd=2, width=15, height=2,
                                    command=lambda: self._seleccionar_especie("bovino"))
        self.btn_bovino.pack(side="left", padx=20)
        
        self.btn_equino = tk.Button(btn_frame, text="🐴 EQUINO", font=T.FONT_BOTON, bg=T.GRIS_CLARO,
                                    fg=T.TEXTO, relief="solid", bd=2, width=15, height=2,
                                    command=lambda: self._seleccionar_especie("equino"))
        self.btn_equino.pack(side="left", padx=20)
        
        # Número de tropa
        tropa_frame = tk.Frame(especie_frame, bg=T.BLANCO)
        tropa_frame.pack(pady=10)
        
        tk.Label(tropa_frame, text="Número de Tropa:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.lbl_tropa = tk.Label(tropa_frame, text="- Seleccione especie -", font=T.FONT_BOTON, 
                                   bg=T.BLANCO, fg=T.AZUL, width=20)
        self.lbl_tropa.pack(side="left", padx=10)
        
        # Panel de ticket de ingreso
        ticket_frame = tk.LabelFrame(content, text=" VINCULAR TICKET DE INGRESO DE HACIENDA ", 
                                     font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                     relief="solid", bd=1)
        ticket_frame.pack(fill="x", pady=10)
        
        # Tabla de tickets disponibles CON OBSERVACIONES
        tabla_frame = tk.Frame(ticket_frame, bg=T.BLANCO)
        tabla_frame.pack(fill="x", padx=10, pady=10)
        
        cols = ("ticket", "fecha", "patente", "proveedor", "guia", "dte", "peso", "observaciones")
        self.tree_tickets = ttk.Treeview(tabla_frame, columns=cols, show="headings", height=6)
        
        self.tree_tickets.heading("ticket", text="Ticket")
        self.tree_tickets.heading("fecha", text="Fecha/Hora")
        self.tree_tickets.heading("patente", text="Patente")
        self.tree_tickets.heading("proveedor", text="Proveedor")
        self.tree_tickets.heading("guia", text="N° Guía")
        self.tree_tickets.heading("dte", text="N° DTE")
        self.tree_tickets.heading("peso", text="Peso (kg)")
        self.tree_tickets.heading("observaciones", text="Observaciones")
        
        self.tree_tickets.column("ticket", width=100)
        self.tree_tickets.column("fecha", width=110)
        self.tree_tickets.column("patente", width=90)
        self.tree_tickets.column("proveedor", width=140)
        self.tree_tickets.column("guia", width=80)
        self.tree_tickets.column("dte", width=80)
        self.tree_tickets.column("peso", width=70)
        self.tree_tickets.column("observaciones", width=150)
        
        self.tree_tickets.pack(fill="x")
        self.tree_tickets.bind("<<TreeviewSelect>>", self._seleccionar_ticket)
        
        tk.Button(ticket_frame, text="🔄 Actualizar tickets", font=T.FONT_LABEL, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2",
                  command=self._cargar_tickets).pack(pady=5)
        
        self.lbl_ticket_sel = tk.Label(ticket_frame, text="Ningún ticket seleccionado", 
                                        font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO)
        self.lbl_ticket_sel.pack(pady=5)
        
        # Panel de datos del ticket seleccionado
        self.info_ticket_frame = tk.LabelFrame(content, text=" DATOS DEL TICKET SELECCIONADO ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.VERDE, 
                                    relief="solid", bd=1)
        self.info_ticket_frame.pack(fill="x", pady=10)
        
        self.lbl_info_ticket = tk.Label(self.info_ticket_frame, text="Seleccione un ticket para ver los datos", 
                                        font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO, justify="left")
        self.lbl_info_ticket.pack(padx=15, pady=10, anchor="w")
        
        # Panel de datos adicionales (solo corral y procedencia)
        datos_frame = tk.LabelFrame(content, text=" DATOS ADICIONALES ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                    relief="solid", bd=1)
        datos_frame.pack(fill="x", pady=10)
        
        row1 = tk.Frame(datos_frame, bg=T.BLANCO)
        row1.pack(fill="x", padx=10, pady=8)
        
        tk.Label(row1, text="Procedencia:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_procedencia = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=25, relief="solid", bd=1)
        self.entry_procedencia.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(row1, text="Corral Destino *:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO).grid(row=0, column=2, padx=15, pady=5, sticky="e")
        self.combo_corral = ttk.Combobox(row1, values=[], width=20, font=T.FONT_NORMAL, state="readonly")
        self.combo_corral.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(row1, text="Observaciones:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).grid(row=0, column=4, padx=15, pady=5, sticky="e")
        self.entry_obs = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=30, relief="solid", bd=1)
        self.entry_obs.grid(row=0, column=5, padx=5, pady=5)
        
        # Botones
        btn_frame = tk.Frame(content, bg=T.FONDO)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="➡️ SIGUIENTE PASO", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=30, pady=10,
                  command=self._siguiente_paso).pack(side="left", padx=15)
        tk.Button(btn_frame, text="❌ Cancelar", font=T.FONT_BOTON, bg=T.ROJO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=10,
                  command=self.on_back).pack(side="left", padx=15)
        
        # Cargar tickets
        self._cargar_tickets()
    
    def _seleccionar_especie(self, especie):
        self.especie_sel = especie
        
        if especie == "bovino":
            self.btn_bovino.configure(bg=T.AZUL, fg=T.TEXTO_CLARO)
            self.btn_equino.configure(bg=T.GRIS_CLARO, fg=T.TEXTO)
        else:
            self.btn_equino.configure(bg=T.AZUL, fg=T.TEXTO_CLARO)
            self.btn_bovino.configure(bg=T.GRIS_CLARO, fg=T.TEXTO)
        
        # Obtener número de tropa
        tropa_num = get_proxima_tropa(especie)
        self.lbl_tropa.configure(text=tropa_num, fg=T.VERDE)
        
        # Actualizar corrales según especie
        corrales = listar_corrales(especie)
        self.combo_corral['values'] = [f"{c['numero']} (Disp: {c['capacidad'] - c['ocupacion']})" for c in corrales]
        self.corrales_map = {f"{c['numero']} (Disp: {c['capacidad'] - c['ocupacion']})": c for c in corrales}
    
    def _cargar_tickets(self):
        for item in self.tree_tickets.get_children():
            self.tree_tickets.delete(item)
        
        tickets = listar_tickets_ingreso_abiertos()
        self.tickets_map = {}
        
        for t in tickets:
            patente = f"{t.get('patente_chasis', '')} / {t.get('patente_acoplado', '')}"
            item_id = self.tree_tickets.insert("", "end", values=(
                t.get('numero_ticket', ''),
                f"{t.get('fecha', '')} {t.get('hora', '')}",
                patente,
                t.get('proveedor_nombre', '-') or '-',
                t.get('numero_guia', '-') or '-',
                t.get('numero_dte', '-') or '-',
                f"{t.get('peso_kg', 0):,.0f}",
                t.get('observaciones', '-') or '-'
            ))
            self.tickets_map[item_id] = t
        
        if not tickets:
            self.tree_tickets.insert("", "end", values=("No hay tickets de ingreso disponibles", "", "", "", "", "", "", ""))
    
    def _seleccionar_ticket(self, event):
        selection = self.tree_tickets.selection()
        if not selection:
            return
        
        item_id = selection[0]
        if item_id not in self.tickets_map:
            return
        
        self.ticket_sel = self.tickets_map[item_id]
        
        # Mostrar información detallada del ticket
        info = f"Ticket: {self.ticket_sel['numero_ticket']}\n"
        info += f"Proveedor: {self.ticket_sel.get('proveedor_nombre', '-') or '-'}\n"
        info += f"N° Guía: {self.ticket_sel.get('numero_guia', '-') or '-'}\n"
        info += f"N° DTE: {self.ticket_sel.get('numero_dte', '-') or '-'}\n"
        info += f"Transportista: {self.ticket_sel.get('transportista', '-') or '-'}\n"
        info += f"Chofer: {self.ticket_sel.get('chofer', '-') or '-'}\n"
        info += f"Peso: {self.ticket_sel.get('peso_kg', 0):,.0f} kg\n"
        info += f"Observaciones: {self.ticket_sel.get('observaciones', '-') or '-'}"
        
        self.lbl_info_ticket.configure(text=info, fg=T.TEXTO)
        self.lbl_ticket_sel.configure(
            text=f"✓ Ticket seleccionado: {self.ticket_sel['numero_ticket']}", 
            fg=T.VERDE
        )
    
    def _siguiente_paso(self):
        if not self.especie_sel:
            messagebox.showwarning("Validación", "Seleccione la especie")
            return
        
        if not self.ticket_sel:
            messagebox.showwarning("Validación", "Seleccione un ticket de ingreso de hacienda")
            return
        
        corral_sel = self.combo_corral.get()
        if not corral_sel:
            messagebox.showwarning("Validación", "Seleccione un corral destino")
            return
        
        corral = self.corrales_map.get(corral_sel)
        
        # Crear la tropa - El proveedor y guía vienen del ticket
        tropa_num = self.lbl_tropa.cget("text")
        datos_tropa = {
            "numero_tropa": tropa_num,
            "especie": self.especie_sel,
            "proveedor_id": self.ticket_sel.get('proveedor_id'),
            "ticket_pesaje_id": self.ticket_sel['id'],
            "num_guia": self.ticket_sel.get('numero_guia', ''),
            "procedencia": self.entry_procedencia.get().strip(),
            "corral_id": corral['id'],
            "observaciones": self.entry_obs.get().strip()
        }
        
        try:
            tropa_id = crear_tropa_paso1(datos_tropa)
            messagebox.showinfo("Éxito", f"Tropa {tropa_num} creada\n\nProceda al Paso 2 para indicar las cantidades por tipificación.")
            self.on_next(tropa_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tropa:\n{e}")


# ═══════════════════════════════════════════════════════════════
# PESAJE INDIVIDUAL DE HACIENDA EN PIE
# ═══════════════════════════════════════════════════════════════

class PesajeIndividual(tk.Frame):
    """
    Pesaje individual de hacienda en pie
    - Seleccionar tropa que no ha sido pesada individualmente
    - Capturar peso individual
    """
    
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self.tropa_sel = None
        self._build()
    
    def _build(self):
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="⚖️ PESAJE DE HACIENDA EN PIE", font=T.FONT_SUBTITULO, bg=T.VERDE, 
                 fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)
        
        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Panel de selección de tropa
        tropa_frame = tk.LabelFrame(content, text=" SELECCIONAR TROPA A PESAR ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                    relief="solid", bd=1)
        tropa_frame.pack(fill="x", pady=10)
        
        tk.Label(tropa_frame, text="Tropas pendientes de pesaje individual:", 
                 font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(padx=15, pady=10, anchor="w")
        
        cols = ("tropa", "especie", "proveedor", "cant_esperada", "cant_pesada", "estado")
        self.tree_tropas = ttk.Treeview(tropa_frame, columns=cols, show="headings", height=8)
        
        self.tree_tropas.heading("tropa", text="N° Tropa")
        self.tree_tropas.heading("especie", text="Especie")
        self.tree_tropas.heading("proveedor", text="Proveedor")
        self.tree_tropas.heading("cant_esperada", text="Esperados")
        self.tree_tropas.heading("cant_pesada", text="Pesados")
        self.tree_tropas.heading("estado", text="Estado")
        
        self.tree_tropas.column("tropa", width=120)
        self.tree_tropas.column("especie", width=80)
        self.tree_tropas.column("proveedor", width=180)
        self.tree_tropas.column("cant_esperada", width=80)
        self.tree_tropas.column("cant_pesada", width=80)
        self.tree_tropas.column("estado", width=100)
        
        self.tree_tropas.pack(fill="x", padx=10, pady=5)
        self.tree_tropas.bind("<<TreeviewSelect>>", self._seleccionar_tropa)
        
        self._cargar_tropas()
        
        # Info de tropa seleccionada
        self.lbl_tropa_sel = tk.Label(tropa_frame, text="Seleccione una tropa", 
                                      font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO)
        self.lbl_tropa_sel.pack(pady=10)
        
        # Botón para ir a captura
        btn_frame = tk.Frame(content, bg=T.FONDO)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="⚖️ IR A CAPTURA INDIVIDUAL", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=30, pady=10,
                  command=self._ir_captura).pack(side="left", padx=15)
        tk.Button(btn_frame, text="❌ Cancelar", font=T.FONT_BOTON, bg=T.ROJO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=10,
                  command=self.on_back).pack(side="left", padx=15)
    
    def _cargar_tropas(self):
        for item in self.tree_tropas.get_children():
            self.tree_tropas.delete(item)
        
        # Listar tropas que están en paso 3 (captura individual)
        tropas = listar_tropas_activas()
        self.tropas_map = {}
        
        for t in tropas:
            esperados = t.get('cantidad_esperada', 0)
            pesados = contar_animales_tropa(t['id'])
            estado = "Completo" if pesados >= esperados else "Pendiente"
            
            item_id = self.tree_tropas.insert("", "end", values=(
                t['numero_tropa'],
                t['especie'].upper(),
                t.get('proveedor', '-') or '-',
                esperados,
                pesados,
                estado
            ))
            self.tropas_map[item_id] = t
    
    def _seleccionar_tropa(self, event):
        selection = self.tree_tropas.selection()
        if not selection:
            return
        
        item_id = selection[0]
        if item_id not in self.tropas_map:
            return
        
        self.tropa_sel = self.tropas_map[item_id]
        self.lbl_tropa_sel.configure(
            text=f"✓ Tropa seleccionada: {self.tropa_sel['numero_tropa']} - {self.tropa_sel['especie'].upper()}",
            fg=T.VERDE
        )
    
    def _ir_captura(self):
        if not self.tropa_sel:
            messagebox.showwarning("Validación", "Seleccione una tropa")
            return
        
        # Navegar al paso 3 con la tropa seleccionada
        self.master.master._ir_paso3(self.tropa_sel['id'])


# ═══════════════════════════════════════════════════════════════
# PASO 2: Cantidad de animales por tipificación
# ═══════════════════════════════════════════════════════════════

class Paso2Tipificaciones(tk.Frame):
    """
    Paso 2:
    - Indicar cantidad de animales por tipificación
    - Para bovinos: tipificación + raza
    - Para equinos: tipificación + gordura + pelaje
    """
    
    def __init__(self, master, tropa_id, on_back, on_next):
        super().__init__(master, bg=T.FONDO)
        self.tropa_id = tropa_id
        self.on_back = on_back
        self.on_next = on_next
        self.tropa = get_tropa_by_id(tropa_id)
        self._build()
    
    def _build(self):
        # Header
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📋 PASO 2: Cantidad por Tipificación", font=T.FONT_SUBTITULO, bg=T.AZUL, 
                 fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)
        
        # Indicador de pasos
        pasos_frame = tk.Frame(header, bg=T.AZUL)
        pasos_frame.pack(side="right", padx=20)
        
        pasos = [("1", T.VERDE), ("2", T.AZUL), ("3", T.GRIS_OSCURO), ("4", T.GRIS_OSCURO)]
        for num, color in pasos:
            lbl = tk.Label(pasos_frame, text=num, font=T.FONT_BOTON, bg=color, fg=T.TEXTO_CLARO,
                          width=3, relief="solid", bd=1)
            lbl.pack(side="left", padx=3)
        
        # Info de tropa
        info_frame = tk.Frame(self, bg=T.VERDE)
        info_frame.pack(fill="x")
        
        info_text = f"Tropa: {self.tropa['numero_tropa']} | Especie: {self.tropa['especie'].upper()}"
        tk.Label(info_frame, text=info_text, font=T.FONT_BOTON, bg=T.VERDE, 
                 fg=T.TEXTO_CLARO).pack(pady=8)
        
        # Contenido
        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Panel de tipificaciones
        tipif_frame = tk.LabelFrame(content, text=" INGRESE CANTIDAD POR TIPIFICACIÓN ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                    relief="solid", bd=1)
        tipif_frame.pack(fill="both", expand=True, pady=10)
        
        # Determinar tipificaciones según especie
        if self.tropa['especie'] == 'bovino':
            tipificaciones = TIPIFICACIONES_BOVINO
        else:
            tipificaciones = TIPIFICACIONES_EQUINO
        
        # Crear entradas para cada tipificación
        self.entries = {}
        self.total_label = None
        
        scroll_frame = tk.Frame(tipif_frame, bg=T.BLANCO)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(scroll_frame, text="Tipificación", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=25).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(scroll_frame, text="Cantidad", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        for i, tipif in enumerate(tipificaciones, 1):
            tk.Label(scroll_frame, text=tipif, font=T.FONT_NORMAL, bg=T.BLANCO, 
                     fg=T.TEXTO).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            entry = tk.Entry(scroll_frame, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                            width=10, relief="solid", bd=1, justify="center")
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, "0")
            entry.bind("<KeyRelease>", self._actualizar_total)
            self.entries[tipif] = entry
        
        # Total
        total_frame = tk.Frame(scroll_frame, bg=T.GRIS_CLARO)
        total_frame.grid(row=len(tipificaciones)+1, column=0, columnspan=2, pady=15, sticky="ew")
        
        tk.Label(total_frame, text="TOTAL ANIMALES:", font=T.FONT_BOTON, bg=T.GRIS_CLARO, 
                 fg=T.TEXTO).pack(side="left", padx=20, pady=10)
        self.total_label = tk.Label(total_frame, text="0", font=T.FONT_BOTON, bg=T.GRIS_CLARO, 
                                     fg=T.VERDE)
        self.total_label.pack(side="left", padx=10, pady=10)
        
        # Botones
        btn_frame = tk.Frame(content, bg=T.FONDO)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="➡️ SIGUIENTE PASO", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=30, pady=10,
                  command=self._siguiente_paso).pack(side="left", padx=15)
        tk.Button(btn_frame, text="❌ Cancelar", font=T.FONT_BOTON, bg=T.ROJO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=10,
                  command=self.on_back).pack(side="left", padx=15)
    
    def _actualizar_total(self, event=None):
        total = 0
        for tipif, entry in self.entries.items():
            try:
                cantidad = int(entry.get() or 0)
                total += cantidad
            except:
                pass
        self.total_label.configure(text=str(total))
    
    def _siguiente_paso(self):
        total = 0
        tipificaciones = {}
        
        for tipif, entry in self.entries.items():
            try:
                cantidad = int(entry.get() or 0)
                if cantidad > 0:
                    tipificaciones[tipif] = cantidad
                    total += cantidad
            except:
                pass
        
        if total == 0:
            messagebox.showwarning("Validación", "Ingrese al menos un animal")
            return
        
        # Guardar tipificaciones esperadas
        guardar_tipificaciones_tropa(self.tropa_id, tipificaciones)
        actualizar_tropa_cantidad_esperada(self.tropa_id, total)
        
        messagebox.showinfo("Éxito", f"Cantidades guardadas\nTotal: {total} animales\n\nProceda al Paso 3 para capturar los datos individuales.")
        self.on_next(self.tropa_id)


# ═══════════════════════════════════════════════════════════════
# PASO 3: Captura individual de datos
# ═══════════════════════════════════════════════════════════════

class Paso3CapturaIndividual(tk.Frame):
    """
    Paso 3:
    - Captura individual de datos por animal
    - Kilogramos (balanza RS232 o manual)
    - Caravana (RFID o manual)
    - Tipificación, Raza/Pelaje (dropdown)
    - Impresión de etiqueta al aceptar
    - Numeración correlativa con tracking de eliminados
    """
    
    def __init__(self, master, tropa_id, on_finish):
        super().__init__(master, bg=T.FONDO)
        self.tropa_id = tropa_id
        self.on_finish = on_finish
        self.tropa = get_tropa_by_id(tropa_id)
        self.tipificaciones_tropa = get_tipificaciones_tropa(tropa_id)
        self.balanza = None
        self.rfid = None
        self._build()
        self._init_equipos()
    
    def _init_equipos(self):
        """Inicializa conexión con equipos"""
        try:
            self.balanza = GestorEquipos.get_balanza()
            self.balanza.conectar()
        except:
            self.balanza = None
        
        try:
            self.rfid = GestorEquipos.get_rfid()
            self.rfid.conectar()
        except:
            self.rfid = None
    
    def _build(self):
        # Header
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(header, text="✓ Finalizar", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self._finalizar).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="⚖️ PASO 3: Captura Individual", font=T.FONT_SUBTITULO, bg=T.VERDE, 
                 fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)
        
        # Indicador de pasos
        pasos_frame = tk.Frame(header, bg=T.VERDE)
        pasos_frame.pack(side="right", padx=20)
        
        pasos = [("1", T.VERDE), ("2", T.VERDE), ("3", T.AZUL), ("4", T.GRIS_OSCURO)]
        for num, color in pasos:
            lbl = tk.Label(pasos_frame, text=num, font=T.FONT_BOTON, bg=color, fg=T.TEXTO_CLARO,
                          width=3, relief="solid", bd=1)
            lbl.pack(side="left", padx=3)
        
        # Info de tropa
        info_frame = tk.Frame(self, bg=T.AZUL)
        info_frame.pack(fill="x")
        
        self.lbl_info_tropa = tk.Label(info_frame, text=self._get_info_text(), font=T.FONT_BOTON, 
                                        bg=T.AZUL, fg=T.TEXTO_CLARO)
        self.lbl_info_tropa.pack(pady=8)
        
        # Contenido principal
        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Panel izquierdo: Captura de datos
        left_frame = tk.LabelFrame(content, text=" CAPTURA DE DATOS ", 
                                   font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                   relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Número de animal
        num_frame = tk.Frame(left_frame, bg=T.BLANCO)
        num_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(num_frame, text="N° Animal:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.lbl_num_animal = tk.Label(num_frame, text="-", font=T.FONT_MONO, bg=T.BLANCO, 
                                        fg=T.VERDE, width=6, relief="solid", bd=1)
        self.lbl_num_animal.pack(side="left", padx=10)
        self._actualizar_numero_animal()
        
        # Peso
        peso_frame = tk.Frame(left_frame, bg=T.BLANCO)
        peso_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(peso_frame, text="Peso (kg):", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO).pack(side="left", padx=5)
        
        self.lbl_peso = tk.Label(peso_frame, text="0", font=T.FONT_MONO_LARGE, bg=T.FONDO, 
                                  fg=T.VERDE, width=10, relief="solid", bd=2)
        self.lbl_peso.pack(side="left", padx=10)
        
        tk.Button(peso_frame, text="⚖️ Balanza", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._capturar_balanza).pack(side="left", padx=5)
        
        self.entry_peso = tk.Entry(peso_frame, font=T.FONT_MONO, bg=T.GRIS_CLARO, 
                                   width=8, relief="solid", bd=1, justify="right")
        self.entry_peso.pack(side="left", padx=5)
        self.entry_peso.insert(0, "0")
        
        # Caravana
        caravana_frame = tk.Frame(left_frame, bg=T.BLANCO)
        caravana_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(caravana_frame, text="Caravana:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        
        self.entry_caravana = tk.Entry(caravana_frame, font=T.FONT_MONO, bg=T.GRIS_CLARO, 
                                        width=20, relief="solid", bd=1)
        self.entry_caravana.pack(side="left", padx=10)
        
        tk.Button(caravana_frame, text="📡 RFID", font=T.FONT_LABEL, bg=T.AZUL, fg=T.TEXTO_CLARO,
                  relief="flat", cursor="hand2", command=self._capturar_rfid).pack(side="left", padx=5)
        
        # Tipificación
        tipif_frame = tk.Frame(left_frame, bg=T.BLANCO)
        tipif_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(tipif_frame, text="Tipificación:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.ROJO).pack(side="left", padx=5)
        
        # Filtrar tipificaciones que tienen cantidad esperada > 0
        tipifs_disponibles = [t['tipificacion'] for t in self.tipificaciones_tropa if t['cantidad_esperada'] > t['cantidad_registrada']]
        if not tipifs_disponibles:
            tipifs_disponibles = TIPIFICACIONES_BOVINO if self.tropa['especie'] == 'bovino' else TIPIFICACIONES_EQUINO
        
        self.combo_tipif = ttk.Combobox(tipif_frame, values=tipifs_disponibles, width=20, 
                                         font=T.FONT_NORMAL, state="readonly")
        self.combo_tipif.pack(side="left", padx=10)
        if tipifs_disponibles:
            self.combo_tipif.set(tipifs_disponibles[0])
        
        # Raza/Pelaje
        raza_frame = tk.Frame(left_frame, bg=T.BLANCO)
        raza_frame.pack(fill="x", padx=15, pady=10)
        
        if self.tropa['especie'] == 'bovino':
            tk.Label(raza_frame, text="Raza:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
            valores = RAZAS_BOVINO
        else:
            tk.Label(raza_frame, text="Pelaje:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
            valores = PELAJES_EQUINO
        
        self.combo_raza_pelaje = ttk.Combobox(raza_frame, values=valores, width=20, 
                                               font=T.FONT_NORMAL, state="readonly")
        self.combo_raza_pelaje.pack(side="left", padx=10)
        
        # Gordura (solo equinos)
        if self.tropa['especie'] == 'equino':
            gordura_frame = tk.Frame(left_frame, bg=T.BLANCO)
            gordura_frame.pack(fill="x", padx=15, pady=10)
            
            tk.Label(gordura_frame, text="Gordura:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
            self.combo_gordura = ttk.Combobox(gordura_frame, values=GORDURAS_EQUINO, width=8, 
                                               font=T.FONT_NORMAL, state="readonly")
            self.combo_gordura.pack(side="left", padx=10)
        
        # Vista previa de etiqueta
        preview_frame = tk.Frame(left_frame, bg=T.GRIS_CLARO, relief="solid", bd=1)
        preview_frame.pack(fill="x", padx=15, pady=15)
        
        self.lbl_preview = tk.Label(preview_frame, text="Complete los datos para ver vista previa", 
                                     font=T.FONT_MONO, bg=T.GRIS_CLARO, fg=T.GRIS_OSCURO, justify="left")
        self.lbl_preview.pack(pady=10)
        
        # Botones de acción
        btn_frame = tk.Frame(left_frame, bg=T.BLANCO)
        btn_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Button(btn_frame, text="✅ GUARDAR E IMPRIMIR", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=15, pady=8,
                  command=self._guardar_e_imprimir).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="💾 Guardar sin imprimir", font=T.FONT_LABEL, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=10, pady=8,
                  command=lambda: self._guardar(imprimir=False)).pack(side="left", padx=5)
        
        # Panel derecho: Lista de animales
        right_frame = tk.LabelFrame(content, text=" ANIMALES REGISTRADOS ", 
                                    font=T.FONT_SUBTITULO, bg=T.BLANCO, fg=T.AZUL, 
                                    relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Tabla
        cols = ("num", "tipif", "peso", "caravana", "acciones")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=15)
        
        self.tree.heading("num", text="N°")
        self.tree.heading("tipif", text="Tipificación")
        self.tree.heading("peso", text="KG")
        self.tree.heading("caravana", text="Caravana")
        self.tree.heading("acciones", text="Acciones")
        
        self.tree.column("num", width=50)
        self.tree.column("tipif", width=120)
        self.tree.column("peso", width=70)
        self.tree.column("caravana", width=100)
        self.tree.column("acciones", width=80)
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botón eliminar
        tk.Button(right_frame, text="🗑️ Eliminar seleccionado", font=T.FONT_LABEL, bg=T.ROJO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2",
                  command=self._eliminar_animal).pack(pady=5)
        
        # Cargar animales existentes
        self._cargar_animales()
        
        # Bindings para actualizar vista previa
        self.entry_peso.bind("<KeyRelease>", self._actualizar_preview)
        self.entry_caravana.bind("<KeyRelease>", self._actualizar_preview)
        self.combo_tipif.bind("<<ComboboxSelected>>", self._actualizar_preview)
    
    def _get_info_text(self):
        """Genera texto de info de la tropa"""
        esperados = self.tropa.get('cantidad_esperada', 0)
        registrados = contar_animales_tropa(self.tropa_id)
        
        tipifs_pendientes = []
        for t in self.tipificaciones_tropa:
            pendientes = t['cantidad_esperada'] - t['cantidad_registrada']
            if pendientes > 0:
                tipifs_pendientes.append(f"{t['tipificacion']}: {pendientes}")
        
        texto = f"Tropa: {self.tropa['numero_tropa']} | Registrados: {registrados}/{esperados}"
        if tipifs_pendientes:
            texto += f" | Pendientes: {', '.join(tipifs_pendientes[:3])}"
            if len(tipifs_pendientes) > 3:
                texto += "..."
        
        return texto
    
    def _actualizar_numero_animal(self):
        """Actualiza el número correlativo del próximo animal"""
        num = get_proximo_numero_animal(self.tropa['numero_tropa'])
        self.lbl_num_animal.configure(text=str(num))
    
    def _capturar_balanza(self):
        """Captura peso de la balanza"""
        if self.balanza:
            peso = self.balanza.capturar_peso()
            if peso is not None:
                self.lbl_peso.configure(text=f"{peso:.0f}")
                self.entry_peso.delete(0, tk.END)
                self.entry_peso.insert(0, f"{peso:.0f}")
                self._actualizar_preview()
                return
        
        # Simulación si no hay balanza
        import random
        peso = random.randint(350, 550)
        self.lbl_peso.configure(text=f"{peso}")
        self.entry_peso.delete(0, tk.END)
        self.entry_peso.insert(0, str(peso))
        self._actualizar_preview()
        messagebox.showinfo("Balanza", f"Peso capturado: {peso} kg")
    
    def _capturar_rfid(self):
        """Captura caravana del bastón RFID"""
        if self.rfid:
            caravana = self.rfid.capturar_caravana(timeout=3)
            if caravana:
                self.entry_caravana.delete(0, tk.END)
                self.entry_caravana.insert(0, caravana)
                self._actualizar_preview()
                return
        
        # Simulación si no hay RFID
        import random
        caravana = f"CAR{random.randint(100000, 999999)}"
        self.entry_caravana.delete(0, tk.END)
        self.entry_caravana.insert(0, caravana)
        self._actualizar_preview()
        messagebox.showinfo("RFID", f"Caravana leída: {caravana}")
    
    def _actualizar_preview(self, event=None):
        """Actualiza la vista previa de la etiqueta"""
        try:
            peso = float(self.entry_peso.get() or 0)
        except:
            peso = 0
        
        num_animal = self.lbl_num_animal.cget("text")
        año = datetime.now().year
        
        preview = generar_vista_previa_etiqueta(
            self.tropa['numero_tropa'],
            num_animal,
            año,
            peso
        )
        
        self.lbl_preview.configure(text=preview, fg=T.TEXTO)
    
    def _guardar_e_imprimir(self):
        """Guarda el animal e imprime la etiqueta"""
        self._guardar(imprimir=True)
    
    def _guardar(self, imprimir=True):
        """Guarda los datos del animal"""
        # Validar datos
        try:
            peso = float(self.entry_peso.get() or 0)
        except:
            messagebox.showwarning("Validación", "Peso inválido")
            return
        
        if peso <= 0:
            messagebox.showwarning("Validación", "Ingrese el peso del animal")
            return
        
        tipif = self.combo_tipif.get()
        if not tipif:
            messagebox.showwarning("Validación", "Seleccione la tipificación")
            return
        
        # Obtener próximo número
        num_correlativo = int(self.lbl_num_animal.cget("text"))
        
        # Preparar datos
        datos = {
            "numero_tropa": self.tropa['numero_tropa'],
            "numero_correlativo": num_correlativo,
            "tropa_id": self.tropa_id,
            "especie": self.tropa['especie'],
            "tipificacion": tipif,
            "raza": self.combo_raza_pelaje.get() if self.tropa['especie'] == 'bovino' else "",
            "pelaje": self.combo_raza_pelaje.get() if self.tropa['especie'] == 'equino' else "",
            "gordura": self.combo_gordura.get() if self.tropa['especie'] == 'equino' else "",
            "caravana": self.entry_caravana.get().strip(),
            "peso_vivo": peso,
            "corral_id": self.tropa.get('corral_id'),
            "proveedor_id": self.tropa.get('proveedor_id')
        }
        
        try:
            animal_id, codigo = guardar_animal(datos)
            
            # Imprimir etiqueta
            if imprimir:
                año = datetime.now().year
                GestorImpresion.imprimir_etiqueta(
                    self.tropa['numero_tropa'],
                    num_correlativo,
                    año,
                    peso
                )
                marcar_etiqueta_impresa(animal_id)
            
            # Actualizar interfaz
            self._cargar_animales()
            self._actualizar_numero_animal()
            self.lbl_info_tropa.configure(text=self._get_info_text())
            
            # Limpiar campos
            self.entry_peso.delete(0, tk.END)
            self.entry_peso.insert(0, "0")
            self.entry_caravana.delete(0, tk.END)
            self.lbl_peso.configure(text="0")
            self.lbl_preview.configure(text="Complete los datos para ver vista previa", fg=T.GRIS_OSCURO)
            
            # Actualizar tipificaciones disponibles
            self.tipificaciones_tropa = get_tipificaciones_tropa(self.tropa_id)
            tipifs_disponibles = [t['tipificacion'] for t in self.tipificaciones_tropa 
                                  if t['cantidad_esperada'] > t['cantidad_registrada']]
            self.combo_tipif['values'] = tipifs_disponibles
            if tipifs_disponibles:
                self.combo_tipif.set(tipifs_disponibles[0])
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
    
    def _cargar_animales(self):
        """Carga la lista de animales en la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        animales = listar_animales({"tropa_id": self.tropa_id})
        for a in animales:
            self.tree.insert("", "end", values=(
                a['numero_correlativo'],
                a.get('tipificacion', '-'),
                f"{a.get('peso_vivo', 0):.0f}",
                a.get('caravana', '-'),
                "Eliminar"
            ))
    
    def _eliminar_animal(self):
        """Elimina un animal (marcado como eliminado, no reutiliza número)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        num_corr = values[0]
        
        if not messagebox.askyesno("Confirmar", f"¿Eliminar animal N° {num_corr}?\n\nEl número NO será reutilizado."):
            return
        
        try:
            eliminar_animal(self.tropa_id, int(num_corr))
            self._cargar_animales()
            self._actualizar_numero_animal()
            self.tipificaciones_tropa = get_tipificaciones_tropa(self.tropa_id)
            self.lbl_info_tropa.configure(text=self._get_info_text())
            messagebox.showinfo("Éxito", "Animal eliminado")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")
    
    def _finalizar(self):
        """Finaliza la carga de la tropa"""
        esperados = self.tropa.get('cantidad_esperada', 0)
        registrados = contar_animales_tropa(self.tropa_id)
        
        if registrados < esperados:
            if not messagebox.askyesno("Confirmar", 
                f"Faltan {esperados - registrados} animales por registrar.\n\n¿Finalizar de todos modos?"):
                return
        
        finalizar_tropa(self.tropa_id)
        messagebox.showinfo("Éxito", f"Tropa completada\nTotal: {registrados} animales")
        self.on_finish()


# ═══════════════════════════════════════════════════════════════
# LISTAR TROPAS
# ═══════════════════════════════════════════════════════════════

class ListarTropas(tk.Frame):
    """Lista todas las tropas"""
    
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()
    
    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📋 LISTADO DE TROPAS", font=T.FONT_SUBTITULO, bg=T.AZUL, 
                 fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)
        
        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Filtros
        filtros_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        filtros_frame.pack(fill="x", pady=10)
        
        tk.Label(filtros_frame, text="Especie:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=10)
        self.combo_especie = ttk.Combobox(filtros_frame, values=["", "bovino", "equino"], width=12, state="readonly")
        self.combo_especie.pack(side="left", padx=5)
        self.combo_especie.set("")
        
        tk.Button(filtros_frame, text="🔍 Buscar", font=T.FONT_LABEL, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self._cargar).pack(side="left", padx=15)
        
        # Tabla
        tabla_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        tabla_frame.pack(expand=True, fill="both", pady=10)
        
        cols = ("tropa", "especie", "proveedor", "fecha", "esperados", "registrados", "estado")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", height=20)
        
        self.tree.heading("tropa", text="N° Tropa")
        self.tree.heading("especie", text="Especie")
        self.tree.heading("proveedor", text="Proveedor")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("esperados", text="Esperados")
        self.tree.heading("registrados", text="Registrados")
        self.tree.heading("estado", text="Estado")
        
        self.tree.column("tropa", width=120)
        self.tree.column("especie", width=80)
        self.tree.column("proveedor", width=180)
        self.tree.column("fecha", width=100)
        self.tree.column("esperados", width=80)
        self.tree.column("registrados", width=80)
        self.tree.column("estado", width=100)
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._cargar()
    
    def _cargar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtros = {}
        especie = self.combo_especie.get()
        if especie:
            filtros["especie"] = especie
        
        tropas = listar_tropas(filtros)
        for t in tropas:
            registrados = contar_animales_tropa(t['id'])
            self.tree.insert("", "end", values=(
                t['numero_tropa'],
                t['especie'].upper(),
                t.get('proveedor', '-') or '-',
                t.get('fecha_ingreso', '-'),
                t.get('cantidad_esperada', 0),
                registrados,
                t.get('estado', '-')
            ))


# ═══════════════════════════════════════════════════════════════
# REIMPRESIÓN DE ETIQUETAS
# ═══════════════════════════════════════════════════════════════

class ReimpresionEtiquetas(tk.Frame):
    """Reimpresión de etiquetas de animales"""
    
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()
    
    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="🔄 REIMPRESIÓN DE ETIQUETAS", font=T.FONT_SUBTITULO, bg=T.AZUL, 
                 fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)
        
        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Búsqueda
        search_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        search_frame.pack(fill="x", pady=10)
        
        tk.Label(search_frame, text="N° Tropa:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=10)
        self.entry_tropa = tk.Entry(search_frame, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=15)
        self.entry_tropa.pack(side="left", padx=5)
        
        tk.Button(search_frame, text="🔍 Buscar", font=T.FONT_LABEL, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self._buscar).pack(side="left", padx=15)
        
        # Tabla
        tabla_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        tabla_frame.pack(expand=True, fill="both", pady=10)
        
        cols = ("codigo", "tipif", "peso", "caravana", "impresa")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", height=15)
        
        self.tree.heading("codigo", text="Código")
        self.tree.heading("tipif", text="Tipificación")
        self.tree.heading("peso", text="KG")
        self.tree.heading("caravana", text="Caravana")
        self.tree.heading("impresa", text="Impresa")
        
        self.tree.column("codigo", width=150)
        self.tree.column("tipif", width=120)
        self.tree.column("peso", width=80)
        self.tree.column("caravana", width=120)
        self.tree.column("impresa", width=80)
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botón reimprimir
        tk.Button(content, text="🖨️ REIMPRIMIR SELECCIONADO", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=10,
                  command=self._reimprimir).pack(pady=10)
    
    def _buscar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        tropa = self.entry_tropa.get().strip()
        if not tropa:
            messagebox.showwarning("Atención", "Ingrese número de tropa")
            return
        
        animales = listar_animales({"numero_tropa": tropa})
        self.animales_map = {}
        
        for a in animales:
            item_id = self.tree.insert("", "end", values=(
                a['codigo'],
                a.get('tipificacion', '-'),
                f"{a.get('peso_vivo', 0):.0f}",
                a.get('caravana', '-'),
                "Sí" if a.get('etiqueta_impresa') else "No"
            ))
            self.animales_map[item_id] = a
    
    def _reimprimir(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        
        item = selection[0]
        animal = self.animales_map.get(item)
        if not animal:
            return
        
        try:
            año = datetime.now().year
            peso = animal.get('peso_vivo', 0)
            num_corr = animal.get('numero_correlativo', 1)
            
            GestorImpresion.imprimir_etiqueta(
                animal['numero_tropa'],
                num_corr,
                año,
                peso
            )
            marcar_etiqueta_impresa(animal['id'])
            messagebox.showinfo("Éxito", "Etiqueta reimpresa")
            self._buscar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reimprimir:\n{e}")
