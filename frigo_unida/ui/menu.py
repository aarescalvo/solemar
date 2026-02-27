"""
Menu Principal v3.1.2
Estructura: Pesaje | Ciclo I | Ciclo II | Configuracion General
"""
import tkinter as tk
import os
from core import theme as T
from core.session import Sesion

class MenuScreen(tk.Frame):
    def __init__(self, master, on_logout):
        super().__init__(master, bg=T.FONDO)
        self.on_logout = on_logout
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=T.AZUL, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo
        logo_path = self._buscar_logo()
        if logo_path:
            try:
                self.logo_img = tk.PhotoImage(file=logo_path)
                tk.Label(header, image=self.logo_img, bg=T.AZUL).pack(side="left", padx=10, pady=10)
            except:
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(logo_path)
                    img.thumbnail((40, 40), Image.Resampling.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(img)
                    tk.Label(header, image=self.logo_img, bg=T.AZUL).pack(side="left", padx=10, pady=10)
                except:
                    tk.Label(header, text="F", font=("Arial", 24, "bold"), bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)
        else:
            tk.Label(header, text="F", font=("Arial", 24, "bold"), bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=15, pady=10)

        tk.Label(header, text="FRIGORIFICO SOLEMAR", font=T.FONT_SUBTITULO, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=10, pady=15)

        info = tk.Frame(header, bg=T.AZUL)
        info.pack(side="right", padx=20)
        tk.Label(info, text=f"{Sesion.nombre_usuario()} ({Sesion.rol()})", font=T.FONT_NORMAL, 
                 bg=T.AZUL, fg=T.TEXTO_CLARO).pack(side="left", padx=10)
        tk.Button(info, text="Salir", font=T.FONT_LABEL, bg=T.ROJO, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", command=self._logout).pack(side="left", padx=10)

        content = tk.Frame(self, bg=T.FONDO)
        content.pack(expand=True, fill="both", padx=50, pady=30)

        tk.Label(content, text="MODULOS DEL SISTEMA", font=T.FONT_SUBTITULO, 
                 bg=T.FONDO, fg=T.TEXTO).pack(pady=20)

        grid = tk.Frame(content, bg=T.FONDO)
        grid.pack(expand=True)

        # Estructura de modulos principal
        modulos = [
            ("PESAJE", "Pesaje de camiones", T.VERDE, "pesaje"),
            ("CICLO I", "Recepcion, Faena, Stock", T.AZUL, "ciclo1"),
            ("CICLO II", "Desposte, Stock, Reportes", T.ROJO, "ciclo2"),
            ("CONFIGURACION GENERAL", "Operadores, usuarios, equipos y establecimiento", T.GRIS_OSCURO, "config"),
        ]

        for i, (titulo, desc, color, modulo) in enumerate(modulos):
            # Distribuir en 2 filas para 4 modulos
            row, col = divmod(i, 2)
            self._make_card(grid, titulo, desc, color, modulo, row, col)

    def _buscar_logo(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_names = ["logo.png", "logo.jpg", "logo.jpeg", "logo.gif", "logo.ico", 
                      "Logo.png", "Logo.jpg", "Logo.jpeg", "Logo.gif", "Logo.ico",
                      "LOGO.png", "LOGO.jpg", "LOGO.jpeg", "LOGO.gif"]
        
        for name in logo_names:
            path = os.path.join(base_dir, name)
            if os.path.exists(path):
                return path
        return None

    def _make_card(self, parent, titulo, desc, color, modulo, row, col):
        outer = tk.Frame(parent, bg=T.FONDO, width=240, height=130)
        outer.grid(row=row, column=col, padx=15, pady=15)
        outer.grid_propagate(False)

        card = tk.Frame(outer, bg=T.BLANCO, relief="solid", bd=1, cursor="hand2")
        card.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(card, text=titulo, font=T.FONT_TITULO, bg=T.BLANCO, fg=color).pack(pady=(22, 4))
        tk.Label(card, text=desc, font=T.FONT_LABEL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=4)

        bottom = tk.Frame(card, bg=color, height=5)
        bottom.pack(fill="x", side="bottom")

        def on_click(e):
            self.master._go_modulo(modulo)

        def on_enter(e):
            card.configure(bg=T.GRIS_CLARO)

        def on_leave(e):
            card.configure(bg=T.BLANCO)

        card.bind("<Button-1>", on_click)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        for child in card.winfo_children():
            child.bind("<Button-1>", on_click)

        parent.columnconfigure(col, weight=1)
        parent.rowconfigure(row, weight=1)

    def _logout(self):
        Sesion.cerrar()
        self.on_logout()
