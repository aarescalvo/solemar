"""
Pesaje - Reportes con funcionalidad de impresión
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from core import theme as T
from core.database import listar_tickets, get_ticket_by_id
from core.session import Sesion

# Importar módulo de impresión
try:
    from utils.reportes_impresion import (
        generar_ticket_pesaje_pdf, 
        generar_reporte_pesajes_pdf, 
        imprimir_archivo,
        obtener_ruta_reportes,
        REPORTLAB_DISPONIBLE
    )
    IMPRESION_DISPONIBLE = True
except ImportError:
    IMPRESION_DISPONIBLE = False
    REPORTLAB_DISPONIBLE = False


class PesajeReportes(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.ROJO, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📊 REPORTES DE PESAJE", font=T.FONT_SUBTITULO, 
                 bg=T.ROJO, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Filtros
        filtros = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        filtros.pack(fill="x", pady=(0, 10))

        row1 = tk.Frame(filtros, bg=T.BLANCO)
        row1.pack(fill="x", padx=10, pady=8)

        hoy = datetime.now()
        hace7 = hoy - timedelta(days=7)

        tk.Label(row1, text="Desde:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_desde = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                     width=12, relief="solid", bd=1)
        self.entry_desde.pack(side="left", padx=5)
        self.entry_desde.insert(0, hace7.strftime("%Y-%m-%d"))

        tk.Label(row1, text="Hasta:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO).pack(side="left", padx=(15, 5))
        self.entry_hasta = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                     width=12, relief="solid", bd=1)
        self.entry_hasta.pack(side="left", padx=5)
        self.entry_hasta.insert(0, hoy.strftime("%Y-%m-%d"))

        # Filtro tipo
        tk.Label(row1, text="Tipo:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO).pack(side="left", padx=(15, 5))
        self.combo_tipo = ttk.Combobox(row1, values=["Todos", "ingreso", "egreso"], 
                                        width=10, state="readonly")
        self.combo_tipo.pack(side="left", padx=5)
        self.combo_tipo.set("Todos")

        # Filtro estado
        tk.Label(row1, text="Estado:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO).pack(side="left", padx=(15, 5))
        self.combo_estado = ttk.Combobox(row1, values=["Todos", "abierto", "cerrado"], 
                                          width=10, state="readonly")
        self.combo_estado.pack(side="left", padx=5)
        self.combo_estado.set("Todos")

        # Filtro patente
        tk.Label(row1, text="Patente:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO).pack(side="left", padx=(15, 5))
        self.entry_patente = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                                       width=10, relief="solid", bd=1)
        self.entry_patente.pack(side="left", padx=5)

        row2 = tk.Frame(filtros, bg=T.BLANCO)
        row2.pack(fill="x", padx=10, pady=8)

        tk.Button(row2, text="🔍 Buscar", font=T.FONT_BOTON, bg=T.AZUL, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self._buscar).pack(side="left", padx=10)
        tk.Button(row2, text="📋 Ver Todos", font=T.FONT_BOTON, bg=T.GRIS_OSCURO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self._todos).pack(side="left", padx=5)
        
        # Botón imprimir reporte
        tk.Button(row2, text="🖨️ Imprimir Listado", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self._imprimir_listado).pack(side="left", padx=20)

        # Info de impresión
        if IMPRESION_DISPONIBLE:
            formato = "PDF" if REPORTLAB_DISPONIBLE else "TXT"
            tk.Label(row2, text=f"(Formato: {formato})", font=T.FONT_LABEL, 
                     bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="left", padx=10)

        # Tabla
        tabla_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        tabla_frame.pack(expand=True, fill="both")

        scroll = ttk.Scrollbar(tabla_frame)
        scroll.pack(side="right", fill="y")

        cols = ("ticket", "fecha", "tipo", "patente", "transportista", "bruto", "tara", "neto", "estado", "operador")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", 
                                  yscrollcommand=scroll.set, height=18)

        headers = [
            ("ticket", "Ticket", 130),
            ("fecha", "Fecha", 130),
            ("tipo", "Tipo", 60),
            ("patente", "Patente", 100),
            ("transportista", "Transportista", 150),
            ("bruto", "Bruto", 80),
            ("tara", "Tara", 80),
            ("neto", "Neto", 80),
            ("estado", "Estado", 70),
            ("operador", "Operador", 100)
        ]

        for col_id, text, width in headers:
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, minwidth=50)

        scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        # Doble click para ver/imprimir ticket
        self.tree.bind("<Double-1>", self._ver_ticket)

        self.lbl_count = tk.Label(content, text="0 registros", 
                                   font=T.FONT_LABEL, bg=T.FONDO, fg=T.GRIS_OSCURO)
        self.lbl_count.pack(anchor="w", pady=5)

        # Botones de acción
        btn_frame = tk.Frame(content, bg=T.FONDO)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="👁️ Ver/Imprimir Ticket", font=T.FONT_BOTON, 
                  bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  padx=15, pady=5, command=self._ver_ticket_click).pack(side="left", padx=10)

        tk.Button(btn_frame, text="📂 Abrir carpeta reportes", font=T.FONT_LABEL, 
                  bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", 
                  command=self._abrir_carpeta).pack(side="left", padx=10)

        self._buscar()

    def _buscar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtros = {}
        if self.entry_desde.get().strip():
            filtros["fecha_desde"] = self.entry_desde.get().strip()
        if self.entry_hasta.get().strip():
            filtros["fecha_hasta"] = self.entry_hasta.get().strip()
        if self.entry_patente.get().strip():
            filtros["patente"] = self.entry_patente.get().strip()
        if self.combo_tipo.get() != "Todos":
            filtros["tipo"] = self.combo_tipo.get()
        if self.combo_estado.get() != "Todos":
            filtros["estado"] = self.combo_estado.get()

        tickets = listar_tickets(filtros)
        self.tickets_data = {}

        for t in tickets:
            pat = f"{t.get('patente_chasis', '')} {t.get('patente_acoplado', '')}".strip()
            bruto = t.get('peso_bruto_kg') or t.get('peso_kg', 0)
            tara = t.get('peso_tara_kg') or 0
            neto = t.get('peso_neto_kg') or bruto
            estado = t.get('estado', '-').upper()
            
            # Colorear estado
            item_id = self.tree.insert("", "end", values=(
                t.get('numero_ticket', ''),
                f"{t.get('fecha', '')} {t.get('hora', '')}",
                t.get('tipo_ticket', '').upper(),
                pat,
                t.get('transportista', ''),
                f"{bruto:,.0f}" if bruto else "-",
                f"{tara:,.0f}" if tara else "-",
                f"{neto:,.0f}" if neto else "-",
                estado,
                t.get('operador', ''),
            ))
            self.tickets_data[item_id] = t

        self.lbl_count.configure(text=f"{len(tickets)} registros")

    def _todos(self):
        self.entry_desde.delete(0, tk.END)
        self.entry_hasta.delete(0, tk.END)
        self.entry_patente.delete(0, tk.END)
        self.combo_tipo.set("Todos")
        self.combo_estado.set("Todos")
        self._buscar()

    def _ver_ticket_click(self):
        """Ver/imprimir ticket seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atención", "Seleccione un ticket")
            return
        
        item_id = selection[0]
        ticket = self.tickets_data.get(item_id)
        if ticket:
            self._mostrar_ticket(ticket)

    def _ver_ticket(self, event=None):
        """Ver/imprimir ticket con doble click"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        ticket = self.tickets_data.get(item_id)
        if ticket:
            self._mostrar_ticket(ticket)

    def _mostrar_ticket(self, ticket):
        """Muestra diálogo con detalles del ticket y opciones de impresión"""
        dlg = tk.Toplevel(self)
        dlg.title(f"Ticket {ticket.get('numero_ticket', '')}")
        dlg.geometry("500x550")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.configure(bg=T.FONDO)

        # Header
        tipo = ticket.get('tipo_ticket', 'ingreso').upper()
        estado = ticket.get('estado', '-').upper()
        color_estado = T.VERDE if estado == "ABIERTO" else T.ROJO

        header_frame = tk.Frame(dlg, bg=T.AZUL if tipo == "INGRESO" else T.VERDE)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text=f"Ticket de {tipo}", font=T.FONT_TITULO, 
                 bg=T.AZUL if tipo == "INGRESO" else T.VERDE, fg=T.TEXTO_CLARO).pack(pady=10)
        tk.Label(header_frame, text=f"N° {ticket.get('numero_ticket', '')}", 
                 font=T.FONT_SUBTITULO, bg=T.AZUL if tipo == "INGRESO" else T.VERDE, 
                 fg=T.TEXTO_CLARO).pack(pady=(0, 10))

        # Contenido
        content = tk.Frame(dlg, bg=T.BLANCO, relief="solid", bd=1)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # Info general
        info_text = f"""
Fecha: {ticket.get('fecha', '')} {ticket.get('hora', '')}
Estado: {estado}
Operador: {ticket.get('operador', '-')}

━━━ DATOS DEL TRANSPORTE ━━━
Patente Chasis: {ticket.get('patente_chasis', '-')}
Patente Acoplado: {ticket.get('patente_acoplado', '-')}
Transportista: {ticket.get('transportista', '-')}
CUIT: {ticket.get('cuit_transportista', '-')}
Chofer: {ticket.get('chofer', '-')}
DNI: {ticket.get('dni_chofer', '-')}

━━━ DATOS DE PESAJE ━━━
Peso Bruto: {ticket.get('peso_bruto_kg') or ticket.get('peso_kg', 0):,.0f} kg
Peso Tara: {ticket.get('peso_tara_kg', 0):,.0f} kg
PESO NETO: {ticket.get('peso_neto_kg') or ticket.get('peso_kg', 0):,.0f} kg

━━━ OTROS ━━━
N° Habilitación: {ticket.get('num_habilitacion', '-')}
Precintos: {ticket.get('precintos', '-')}
Observaciones: {ticket.get('observaciones', '-') or '-'}
"""
        tk.Label(content, text=info_text, font=T.FONT_NORMAL, bg=T.BLANCO, 
                 fg=T.TEXTO, justify="left").pack(padx=15, pady=10)

        # Botones
        btn_frame = tk.Frame(dlg, bg=T.FONDO)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="🖨️ IMPRIMIR", font=T.FONT_BOTON, bg=T.VERDE, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=8,
                  command=lambda: self._imprimir_ticket(ticket, dlg)).pack(side="left", padx=10)

        tk.Button(btn_frame, text="❌ Cerrar", font=T.FONT_BOTON, bg=T.ROJO, 
                  fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=8,
                  command=dlg.destroy).pack(side="left", padx=10)

    def _imprimir_ticket(self, ticket, parent_dlg=None):
        """Genera e imprime el ticket"""
        if not IMPRESION_DISPONIBLE:
            messagebox.showwarning("Impresión", 
                "Módulo de impresión no disponible.\n"
                "Instale reportlab: pip install reportlab", 
                parent=parent_dlg)
            return

        try:
            filepath = generar_ticket_pesaje_pdf(ticket, mostrar=True)
            messagebox.showinfo("Impresión", 
                f"Ticket generado:\n{filepath}\n\n"
                "El archivo se ha abierto para impresión.", 
                parent=parent_dlg)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el ticket:\n{e}", parent=parent_dlg)

    def _imprimir_listado(self):
        """Genera reporte PDF de todos los tickets filtrados"""
        if not IMPRESION_DISPONIBLE:
            messagebox.showwarning("Impresión", 
                "Módulo de impresión no disponible.\n"
                "Instale reportlab: pip install reportlab")
            return

        # Obtener filtros actuales
        filtros = {}
        if self.entry_desde.get().strip():
            filtros["fecha_desde"] = self.entry_desde.get().strip()
        if self.entry_hasta.get().strip():
            filtros["fecha_hasta"] = self.entry_hasta.get().strip()
        if self.entry_patente.get().strip():
            filtros["patente"] = self.entry_patente.get().strip()

        tickets = listar_tickets(filtros)

        if not tickets:
            messagebox.showwarning("Sin datos", "No hay tickets para imprimir")
            return

        try:
            filepath = generar_reporte_pesajes_pdf(tickets, filtros)
            messagebox.showinfo("Reporte Generado", 
                f"Reporte generado:\n{filepath}\n\n"
                f"Total: {len(tickets)} tickets\n\n"
                "El archivo se ha abierto.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{e}")

    def _abrir_carpeta(self):
        """Abre la carpeta de reportes"""
        if IMPRESION_DISPONIBLE:
            ruta = obtener_ruta_reportes()
            try:
                import os
                import subprocess
                if os.name == 'nt':
                    os.startfile(ruta)
                else:
                    subprocess.run(['xdg-open', ruta])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}")
        else:
            messagebox.showinfo("Carpeta", 
                "Los reportes se guardan en:\n"
                "<directorio_instalacion>/reportes/")
