"""
Módulo de Stock y Despachos
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core import theme as T
from core.session import Sesion
from core.database import get_proximo_despacho, guardar_despacho, listar_despachos
import os

class StockMenu(tk.Frame):
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
        tk.Label(header, text="📦 STOCK Y DESPACHOS", font=T.FONT_SUBTITULO, bg=T.ROJO, fg=T.TEXTO_CLARO).pack(side="left", padx=20, pady=15)

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
            ("📦 STOCK CORRALES", "Tropas en corral", self._show_stock_corrales, T.AZUL),
            ("🥩 STOCK CUARTOS", "Cuartos en cámaras", self._show_stock_cuartos, T.AZUL),
            ("📤 NUEVO DESPACHO", "Registrar despacho", self._show_nuevo_despacho, T.VERDE),
            ("📋 VER DESPACHOS", "Historial de despachos", self._show_historial, T.AZUL),
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

    def _show_nuevo_despacho(self):
        self._clear_current()
        NuevoDespacho(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_historial(self):
        self._clear_current()
        HistorialDespachos(self._current, self._show_main_menu).pack(expand=True, fill="both")

    def _show_stock_corrales(self):
        self._clear_current()
        StockCorrales(self._current, self._show_main_menu).pack(expand=True, fill="both")
    
    def _show_stock_cuartos(self):
        self._clear_current()
        StockCuartos(self._current, self._show_main_menu).pack(expand=True, fill="both")
    def _back(self):
        self.master._show_menu()


class NuevoDespacho(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.VERDE, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📤 NUEVO DESPACHO", font=T.FONT_SUBTITULO, bg=T.VERDE, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        # Número de remito
        remito_num = get_proximo_despacho()
        self.remito_num = remito_num

        info_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=10)

        tk.Label(info_frame, text=f"Remito: {remito_num}", font=T.FONT_BOTON, bg=T.BLANCO, fg=T.AZUL).pack(side="left", padx=15, pady=10)
        tk.Label(info_frame, text=f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(side="right", padx=15, pady=10)

        # Formulario
        form = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        form.pack(fill="x", pady=10)

        row1 = tk.Frame(form, bg=T.BLANCO)
        row1.pack(fill="x", padx=15, pady=10)

        tk.Label(row1, text="Cliente:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_cliente = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=30, relief="solid", bd=1)
        self.entry_cliente.pack(side="left", padx=5)

        tk.Label(row1, text="CUIT:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=(20, 5))
        self.entry_cuit = tk.Entry(row1, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=15, relief="solid", bd=1)
        self.entry_cuit.pack(side="left", padx=5)

        row2 = tk.Frame(form, bg=T.BLANCO)
        row2.pack(fill="x", padx=15, pady=10)

        tk.Label(row2, text="Destino:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_destino = tk.Entry(row2, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=30, relief="solid", bd=1)
        self.entry_destino.pack(side="left", padx=5)

        row3 = tk.Frame(form, bg=T.BLANCO)
        row3.pack(fill="x", padx=15, pady=10)

        tk.Label(row3, text="Patente:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_patente = tk.Entry(row3, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=10, relief="solid", bd=1)
        self.entry_patente.pack(side="left", padx=5)

        tk.Label(row3, text="Transportista:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=(20, 5))
        self.entry_transportista = tk.Entry(row3, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=25, relief="solid", bd=1)
        self.entry_transportista.pack(side="left", padx=5)

        row4 = tk.Frame(form, bg=T.BLANCO)
        row4.pack(fill="x", padx=15, pady=10)

        tk.Label(row4, text="Peso Total (kg):", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=5)
        self.entry_peso = tk.Entry(row4, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=10, relief="solid", bd=1)
        self.entry_peso.pack(side="left", padx=5)

        tk.Label(row4, text="Observaciones:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(side="left", padx=(20, 5))
        self.entry_obs = tk.Entry(row4, font=T.FONT_NORMAL, bg=T.GRIS_CLARO, width=30, relief="solid", bd=1)
        self.entry_obs.pack(side="left", padx=5)

        # Botones
        btn_frame = tk.Frame(content, bg=T.FONDO)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="✅ GUARDAR DESPACHO", font=T.FONT_BOTON, bg=T.VERDE, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=30, pady=10, command=self._guardar).pack(side="left", padx=15)
        tk.Button(btn_frame, text="❌ Cancelar", font=T.FONT_BOTON, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", padx=20, pady=10, command=self.on_back).pack(side="left", padx=15)

    def _guardar(self):
        cliente = self.entry_cliente.get().strip()
        if not cliente:
            messagebox.showwarning("Validación", "Ingrese el cliente")
            return

        datos = {
            "numero_remito": self.remito_num,
            "cliente": cliente,
            "cuit_cliente": self.entry_cuit.get().strip(),
            "destino": self.entry_destino.get().strip(),
            "patente": self.entry_patente.get().strip().upper(),
            "transportista": self.entry_transportista.get().strip(),
            "peso_total": float(self.entry_peso.get() or 0),
            "observaciones": self.entry_obs.get().strip(),
            "operador": Sesion.nombre_usuario(),
        }

        try:
            guardar_despacho(datos)
            messagebox.showinfo("Éxito", f"Despacho {self.remito_num} registrado correctamente")
            self.on_back()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")


class HistorialDespachos(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()


class StockCorrales(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📦 STOCK EN CORRALES", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        tabla_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        tabla_frame.pack(expand=True, fill="both")

        scroll = ttk.Scrollbar(tabla_frame)
        scroll.pack(side="right", fill="y")

        cols = ("tropa", "especie", "proveedor", "fecha", "corral", "esperados", "registrados", "estado")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", yscrollcommand=scroll.set, height=20)
        headers = [("tropa", "Tropa", 120), ("especie", "Especie", 70), ("proveedor", "Proveedor", 150),
                   ("fecha", "Fecha", 100), ("corral", "Corral", 80), ("esperados", "Esp.", 60),
                   ("registrados", "Reg.", 60), ("estado", "Estado", 80)]
        for cid, text, w in headers:
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=w, minwidth=50)

        scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        self._cargar()

    def _cargar(self):
        from core.database import listar_tropas, contar_animales_tropa
        for item in self.tree.get_children():
            self.tree.delete(item)
        tropas = listar_tropas({"estado": "en_corral"})
        for t in tropas:
            registrados = contar_animales_tropa(t['id'])
            self.tree.insert("", "end", values=(
                t['numero_tropa'],
                t['especie'].upper(),
                t.get('proveedor', '-') or '-',
                t.get('fecha_ingreso', '-'),
                t.get('corral_num', '-') or '-',
                t.get('cantidad_esperada', 0),
                registrados,
                t.get('estado', '-')
            ))


class StockCuartos(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=T.FONDO)
        self.on_back = on_back
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="🥩 STOCK DE CUARTOS EN CÁMARAS", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        frame.pack(expand=True, fill="both")

        scroll = ttk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")

        cols = ("codigo", "tipo", "peso", "camara", "posicion", "fecha")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", yscrollcommand=scroll.set, height=20)
        for cid, text, w in [("codigo", "Código", 160), ("tipo", "Tipo", 100), ("peso", "Peso", 80), ("camara", "Cámara", 100), ("posicion", "Posición", 100), ("fecha", "Fecha", 100)]:
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=w, minwidth=50)
        scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)
        self._cargar()

    def _cargar(self):
        from core.database import listar_cuartos_en_camaras, listar_camaras
        cams = {c['id']: c for c in listar_camaras()}
        for item in self.tree.get_children():
            self.tree.delete(item)
        for q in listar_cuartos_en_camaras():
            cam = cams.get(q.get('camara_id') or 0)
            camlbl = f"{cam['numero']} - {cam['nombre']}" if cam else "-"
            self.tree.insert("", "end", values=(q.get('codigo', ''), q.get('tipo', ''), f"{q.get('peso', 0):,.0f}", camlbl, q.get('posicion', '-') or '-', q.get('fecha_ingreso', '') or ''))

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="← Volver", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, relief="flat", cursor="hand2", command=self.on_back).pack(side="left", padx=10, pady=8)
        tk.Label(header, text="📋 HISTORIAL DE DESPACHOS", font=T.FONT_SUBTITULO, bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=20, pady=15)

        tabla_frame = tk.Frame(content, bg=T.BLANCO, relief="solid", bd=1)
        tabla_frame.pack(expand=True, fill="both")

        scroll = ttk.Scrollbar(tabla_frame)
        scroll.pack(side="right", fill="y")

        cols = ("remito", "fecha", "cliente", "destino", "patente", "peso", "operador")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", yscrollcommand=scroll.set, height=20)

        headers = [("remito", "Remito", 120), ("fecha", "Fecha", 100), ("cliente", "Cliente", 150),
                   ("destino", "Destino", 120), ("patente", "Patente", 80), ("peso", "Peso kg", 80), ("operador", "Operador", 100)]

        for col_id, text, width in headers:
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, minwidth=50)

        scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        self._cargar()

    def _cargar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        despachos = listar_despachos()
        for d in despachos:
            self.tree.insert("", "end", values=(
                d.get('numero_remito', ''),
                d.get('fecha', ''),
                d.get('cliente', ''),
                d.get('destino', ''),
                d.get('patente', ''),
                f"{d.get('peso_total', 0):,.0f}",
                d.get('operador', ''),
            ))
