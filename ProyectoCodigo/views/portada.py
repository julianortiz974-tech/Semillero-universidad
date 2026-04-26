import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time

# 🎨 Nueva paleta alineada con tu sistema
COLORS = {
    "bg_main": "#F4F6F9",
    "primary": "#4361EE",
    "primary_soft": "#E0E7FF",
    "text_main": "#1E293B",
    "text_muted": "#64748B",
    "border": "#E2E8F0"
}

class VentanaPortada:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        self.root.title("Smart Sales - Bienvenido")
        self.root.state("zoomed")
        self.root.configure(bg=COLORS["bg_main"])
        
        # Canvas limpio (sin degradado)
        self.canvas = tk.Canvas(root, bg=COLORS["bg_main"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # --- CONTENEDOR CENTRAL (tipo card moderna) ---
        self.card = tk.Frame(
            self.canvas,
            bg="white",
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )

        self.card_window = self.canvas.create_window(0, 0, window=self.card)

        # LOGO
        self.logo_img = None
        self._cargar_imagen_logo()

        if self.logo_img:
            tk.Label(self.card, image=self.logo_img, bg="white").pack(pady=(40,10))
        else:
            tk.Label(
                self.card,
                text="SMART SALES",
                font=("Segoe UI", 28, "bold"),
                fg=COLORS["primary"],
                bg="white"
            ).pack(pady=(40,10))

        # SUBTÍTULO
        tk.Label(
            self.card,
            text="Sistema de Gestión de Inventario y Ventas",
            font=("Segoe UI", 11),
            fg=COLORS["text_muted"],
            bg="white"
        ).pack(pady=(0,20))

        # PROGRESS BAR MODERNA
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=COLORS["primary_soft"],
            background=COLORS["primary"],
            thickness=10,
            bordercolor=COLORS["primary_soft"]
        )

        self.progress = ttk.Progressbar(
            self.card,
            length=300,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=(10,10))

        # TEXTO DE CARGA
        self.lbl = tk.Label(
            self.card,
            text="Iniciando sistema...",
            font=("Segoe UI", 10),
            fg=COLORS["text_muted"],
            bg="white"
        )
        self.lbl.pack(pady=(0,40))

        # CENTRAR DINÁMICO
        self.canvas.bind("<Configure>", self._centrar_card)

        # INICIAR
        self.root.after(500, self.iniciar_carga)

    def _cargar_imagen_logo(self):
        try:
            logo_path = os.path.join("assets", "portadaProyecto.jpg")
            if os.path.exists(logo_path):
                imagen = Image.open(logo_path)
                imagen = imagen.resize((180, 180), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(imagen)
        except:
            pass

    def _centrar_card(self, event):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.canvas.coords(self.card_window, w/2, h/2)

        # tamaño fijo tipo login
        self.card.config(width=420, height=420)

    def iniciar_carga(self):
        for i in range(101):
            if not self.canvas.winfo_exists():
                return

            self.progress['value'] = i
            self.lbl.config(text=f"Cargando sistema... {i}%")
            self.root.update_idletasks()
            time.sleep(0.015)

        if self.canvas.winfo_exists():
            self.root.after(400, self.callback)

