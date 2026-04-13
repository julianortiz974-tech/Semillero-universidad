import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time

class VentanaPortada:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        # Configuración de ventana
        self.root.title("Smart Sales - Bienvenido")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Usamos un Canvas para permitir el degradado de fondo
        self.canvas = tk.Canvas(root, width=700, height=500, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Dibujar degradado (Usando los colores de tu mockup: #712828 a #ff9d9d)
        self.dibujar_degradado("#712828", "#ff9d9d")
        
        # Cargar logo de portada
        self.mostrar_logo()
        
        # Subtítulo (Usando el color crema e0e0d5 para consistencia)
        self.canvas.create_text(
            350, 380, 
            text="Sistema de Gestión de Ventas", 
            font=("Arial", 14, "italic"), 
            fill="#e0e0d5"
        )
        
        # Barra de progreso estilizada
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background='#C48B7A', # Color de tus botones
            troughcolor='#712828',
            bordercolor='#712828',
            lightcolor='#C48B7A',
            darkcolor='#C48B7A'
        )
        
        self.progress = ttk.Progressbar(
            self.root,
            length=400,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.canvas.create_window(350, 420, window=self.progress)
        
        self.label_carga = tk.Label(
            self.root, text="Iniciando...", font=("Arial", 10), 
            fg="white", bg="#A35E5E" # Color aproximado del degradado en esa zona
        )
        self.canvas.create_window(350, 450, window=self.label_carga)
        
        # Iniciar carga
        self.root.after(500, self.iniciar_carga)

    def dibujar_degradado(self, color_inicio, color_fin):
        """Crea el fondo visual del mockup"""
        r1, g1, b1 = self.root.winfo_rgb(color_inicio)
        r2, g2, b2 = self.root.winfo_rgb(color_fin)
        r1, g1, b1 = r1//256, g1//256, b1//256
        r2, g2, b2 = r2//256, g2//256, b2//256
        
        for i in range(500):
            r = int(r1 + (r2 - r1) * (i / 500))
            g = int(g1 + (g2 - g1) * (i / 500))
            b = int(b1 + (b2 - b1) * (i / 500))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 700, i, fill=color)

    def mostrar_logo(self):
        try:
            logo_path = os.path.join("assets", "portadaProyecto.jpg")
            if os.path.exists(logo_path):
                imagen = Image.open(logo_path)
                imagen = imagen.resize((300, 300), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(imagen)
                self.canvas.create_image(350, 200, image=self.logo_img)
            else:
                self.canvas.create_text(
                    350, 200, text="SMART SALES", 
                    font=("Impact", 60), fill="#e0e0d5"
                )
        except:
            pass

    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho, alto = 700, 500
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')

    def iniciar_carga(self):
        for i in range(101):
            self.progress['value'] = i
            self.label_carga.config(text=f"Cargando componentes... {i}%")
            self.root.update_idletasks()
            time.sleep(0.02)
        self.root.after(300, self.callback)