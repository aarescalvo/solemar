"""
Pesaje - Configuracion v3.2.0
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from core import theme as T
from core.database import get_config_tickets, set_config_ticket, autenticar_operador
from ui.config_menu import AdminOperadores, AdminUsuariosFaena, AdminTransportistas, AdminProveedores

class PesajeConfig(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._current = None
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.GRIS_OSCURO, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="CONFIGURACION DE PESAJE", font=T.FONT_SUBTITULO, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        self.container = tk.Frame(self, bg=T.FONDO)
        self.container.pack(expand=True, fill="both", padx=30, pady=20)
        self._show_submenu()

    def _clear_current(self):
        if self._current:
            self._current.destroy()
        self._current = tk.Frame(self.container, bg=T.FONDO)
        self._current.pack(expand=True, fill="both")

    def _show_submenu(self):
        self._clear_current()
        tk.Label(self._current, text="Seleccione una opcion de configuracion:", font=T.FONT_SUBTITULO, bg=T.FONDO, fg=T.TEXTO).pack(pady=15)
        grid = tk.Frame(self._current, bg=T.FONDO)
        grid.pack(expand=True)

        opciones = [
            ("NÚMEROS DE TICKET", "Configurar numeración", self._show_ticket_numbers, T.AZUL),
            ("TRANSPORTISTAS", "Altas y modificaciones", self._embed_transportistas, T.AZUL),
            ("USUARIOS DE FAENA", "Altas y modificaciones", self._embed_usuarios_faena, T.VERDE),
            ("PROVEEDORES", "Altas y modificaciones", self._embed_proveedores, T.GRIS_OSCURO),
        ]
        for i, (titulo, desc, cmd, color) in enumerate(opciones):
            outer = tk.Frame(grid, bg=T.FONDO, width=260, height=130)
            outer.grid(row=i // 2, column=i % 2, padx=12, pady=12)
            outer.grid_propagate(False)
            card = tk.Frame(outer, bg=T.BLANCO, relief="solid", bd=1, cursor="hand2")
            card.place(x=0, y=0, relwidth=1, relheight=1)
            tk.Label(card, text=titulo, font=T.FONT_BOTON, bg=T.BLANCO, fg=color).pack(pady=(22, 5))
            tk.Label(card, text=desc, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=5)
            bottom = tk.Frame(card, bg=color, height=4)
            bottom.pack(fill="x", side="bottom")
            def on_click(e, fn=cmd):
                fn()
            card.bind("<Button-1>", on_click)
            card.bind("<Enter>", lambda e, c=card: c.configure(bg=T.GRIS_CLARO))
            card.bind("<Leave>", lambda e, c=card: c.configure(bg=T.BLANCO))
            for child in card.winfo_children():
                child.bind("<Button-1>", on_click)

    def _show_ticket_numbers(self):
        self._clear_current()
        tk.Button(self._current, text="← Volver", font=T.FONT_LABEL, bg=T.GRIS_OSCURO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self._show_submenu).pack(anchor="w", pady=(0,10))
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
        tk.Button(row1, text="Modificar", font=T.FONT_BOTON, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=lambda: self._modificar("ingreso")).pack(side="left", padx=15)

        row2 = tk.Frame(config_frame, bg=T.BLANCO)
        row2.pack(fill="x", padx=20, pady=15)
        tk.Label(row2, text="Proximo N Ticket EGRESO:", font=T.FONT_BOTON, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=10)
        self.entry_egreso = tk.Entry(row2, font=T.FONT_MONO, bg=T.GRIS_CLARO, fg=T.TEXTO, width=10, justify="right", relief="solid", bd=1)
        self.entry_egreso.pack(side="left", padx=10)
        self.entry_egreso.insert(0, str(cfg['prox_egreso']))
        self.entry_egreso.configure(state="disabled")
        tk.Button(row2, text="Modificar", font=T.FONT_BOTON, bg=T.AZUL, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=lambda: self._modificar("egreso")).pack(side="left", padx=15)

        tk.Label(config_frame, text="Para modificar se requiere clave de supervisor", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=15)

        preview = tk.Frame(self._current, bg=T.AZUL)
        preview.pack(pady=15, padx=10, fill="x")
        tk.Label(preview, text="Vista Previa de Proximos Tickets", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(pady=10)
        anio = datetime.now().year
        self.lbl_preview_in = tk.Label(preview, text=f"Ingreso: TI-{anio}-{cfg['prox_ingreso']:06d}", font=T.FONT_MONO, bg=T.AZUL, fg=T.TEXTO_CLARO)
        self.lbl_preview_in.pack(pady=5)
        self.lbl_preview_out = tk.Label(preview, text=f"Egreso: TE-{anio}-{cfg['prox_egreso']:06d}", font=T.FONT_MONO, bg=T.AZUL, fg=T.TEXTO_CLARO)
        self.lbl_preview_out.pack(pady=5)

    def _embed_transportistas(self):
        self._clear_current()
        AdminTransportistas(self._current, self._show_submenu).pack(expand=True, fill="both")

    def _embed_usuarios_faena(self):
        self._clear_current()
        AdminUsuariosFaena(self._current, self._show_submenu).pack(expand=True, fill="both")

    def _embed_proveedores(self):
        self._clear_current()
        AdminProveedores(self._current, self._show_submenu).pack(expand=True, fill="both")

    def _modificar(self, tipo):
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

        tk.Label(dlg, text="AUTORIZACION DE SUPERVISOR", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.ROJO).pack(pady=20)

        frame = tk.Frame(dlg, bg=T.BLANCO, relief="solid", bd=1)
        frame.pack(pady=10, padx=30, fill="x")

        tk.Label(frame, text="N Operador:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO).grid(row=0, column=0, padx=10, pady=8, sticky="e")
        entry_num = tk.Entry(frame, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                             relief="solid", bd=1, width=15)
        entry_num.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(frame, text="Clave:", font=T.FONT_LABEL, bg=T.BLANCO, 
                 fg=T.TEXTO).grid(row=1, column=0, padx=10, pady=8, sticky="e")
        entry_pass = tk.Entry(frame, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, 
                              relief="solid", bd=1, width=15, show="*")
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
            self._editar(tipo)

        tk.Button(btns, text="Autorizar", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=autorizar).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_BOTON, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=dlg.destroy).pack(side="left", padx=10)

        entry_num.focus()
        entry_num.bind("<Return>", lambda e: entry_pass.focus())
        entry_pass.bind("<Return>", lambda e: autorizar())

    def _editar(self, tipo):
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

        tk.Label(dlg, text=f"Nuevo valor para {tipo.upper()}:", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=20)

        frame = tk.Frame(dlg, bg=T.BLANCO, relief="solid", bd=1)
        frame.pack(padx=30, fill="x")

        entry = tk.Entry(frame, font=T.FONT_MONO, bg=T.GRIS_CLARO, fg=T.TEXTO, 
                         width=15, justify="right")
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

                self._update_preview()
                dlg.destroy()
                messagebox.showinfo("Exito", f"Ticket de {tipo} actualizado")

            except ValueError as e:
                messagebox.showerror("Error", f"Valor invalido: {e}", parent=dlg)

        tk.Button(btns, text="Guardar", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=guardar).pack(side="left", padx=10)
        tk.Button(btns, text="Cancelar", font=T.FONT_BOTON, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=dlg.destroy).pack(side="left", padx=10)

        entry.focus()
        entry.select_range(0, tk.END)

    def _update_preview(self):
        anio = datetime.now().year
        try:
            ing = int(self.entry_ingreso.get())
            eg = int(self.entry_egreso.get())
            self.lbl_preview_in.configure(text=f"Ingreso: TI-{anio}-{ing:06d}")
            self.lbl_preview_out.configure(text=f"Egreso: TE-{anio}-{eg:06d}")
        except:
            pass
