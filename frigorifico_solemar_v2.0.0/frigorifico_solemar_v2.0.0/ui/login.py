"""
Pantalla de Login - Operadores del Sistema
"""
import tkinter as tk
from tkinter import messagebox
import os
from core import theme as T
from core.database import autenticar_operador
from core.session import Sesion


class LoginScreen(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, bg=T.FONDO)
        self.on_success = on_success
        self._build()

    def _build(self):
        container = tk.Frame(self, bg=T.BLANCO, relief="solid", bd=2)
        container.pack(expand=True, pady=80, padx=300)

        # Intentar cargar logo
        logo_label = None
        logo_path = self._buscar_logo()
        
        if logo_path:
            try:
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(logo_path)
                    img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    logo_img = ImageTk.PhotoImage(img)
                    logo_label = tk.Label(container, image=logo_img, bg=T.BLANCO)
                    logo_label.image = logo_img
                    logo_label.pack(pady=(30, 10))
                except ImportError:
                    logo_img = tk.PhotoImage(file=logo_path)
                    logo_label = tk.Label(container, image=logo_img, bg=T.BLANCO)
                    logo_label.image = logo_img
                    logo_label.pack(pady=(30, 10))
            except Exception as e:
                print(f"Error cargando logo: {e}")
                logo_label = None

        if not logo_label:
            tk.Label(container, text="F", font=("Arial", 48), bg=T.BLANCO, fg=T.AZUL).pack(pady=(30, 10))

        tk.Label(container, text="FRIGORIFICO SOLEMAR", font=T.FONT_TITULO, bg=T.BLANCO, fg=T.AZUL).pack(pady=(5, 5))
        tk.Label(container, text="Sistema de Trazabilidad v2.0.0", font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack(pady=(0, 30))

        fields_frame = tk.Frame(container, bg=T.BLANCO)
        fields_frame.pack(padx=40, pady=10)

        # N Operador (solo numeros)
        tk.Label(fields_frame, text="N Operador:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w")
        self.entry_operador = tk.Entry(fields_frame, font=T.FONT_MONO_LARGE, width=15, bg=T.GRIS_CLARO, 
                                        fg=T.TEXTO, relief="solid", bd=1, justify="center")
        self.entry_operador.pack(pady=(2, 15), ipady=5)
        # Validar que solo se ingresen numeros y Enter pasa al siguiente campo
        self.entry_operador.bind("<Key>", self._validar_numero)
        self.entry_operador.bind("<Return>", lambda e: self.entry_clave.focus())
        self.entry_operador.bind("<KP_Enter>", lambda e: self.entry_clave.focus())

        # Clave (solo numeros, oculta)
        tk.Label(fields_frame, text="Clave:", font=T.FONT_LABEL, bg=T.BLANCO, fg=T.TEXTO).pack(anchor="w")
        self.entry_clave = tk.Entry(fields_frame, font=T.FONT_MONO_LARGE, width=15, bg=T.GRIS_CLARO, 
                                     fg=T.TEXTO, relief="solid", bd=1, show="*", justify="center")
        self.entry_clave.pack(pady=(2, 20), ipady=5)
        self.entry_clave.bind("<Key>", self._validar_numero)
        self.entry_clave.bind("<Return>", lambda e: self._login())
        self.entry_clave.bind("<KP_Enter>", lambda e: self._login())

        tk.Button(container, text="INGRESAR", font=T.FONT_BOTON, bg=T.AZUL, fg=T.TEXTO_CLARO, 
                  relief="flat", cursor="hand2", width=20, command=self._login).pack(pady=(0, 30), ipady=8)

        self.entry_operador.focus()

        # Info de operadores por defecto
        info_frame = tk.Frame(container, bg=T.BLANCO)
        info_frame.pack(pady=(0, 20))
        tk.Label(info_frame, text="Operador: 0001  Clave: 1234 (Admin)", 
                 font=T.FONT_NORMAL, bg=T.BLANCO, fg=T.GRIS_OSCURO).pack()

    def _validar_numero(self, event):
        """Solo permite ingresar numeros"""
        if event.keysym in ("BackSpace", "Delete", "Tab", "Return", "Left", "Right"):
            return
        if event.char and not event.char.isdigit():
            return "break"

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

    def _login(self):
        num_op = self.entry_operador.get().strip()
        clave = self.entry_clave.get()
        
        if not num_op or not clave:
            messagebox.showwarning("Atencion", "Complete todos los campos")
            return
        
        if not num_op.isdigit():
            messagebox.showwarning("Atencion", "N Operador debe ser solo numeros")
            return
        
        if not clave.isdigit():
            messagebox.showwarning("Atencion", "La clave debe ser solo numeros")
            return
        
        auth = autenticar_operador(int(num_op), clave)
        if auth:
            Sesion.iniciar(auth)
            self.on_success()
        else:
            messagebox.showerror("Error", "N Operador o clave incorrectos")
            self.entry_clave.delete(0, tk.END)
            self.entry_clave.focus()
