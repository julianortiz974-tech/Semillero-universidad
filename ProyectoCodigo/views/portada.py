import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time

class VentanaPortada:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        # 1. Ajuste de dimensiones a 1100x700 (igual que el menú)
        self.ancho = 1100
        self.alto = 700
        
        self.root.title("Smart Sales - Bienvenido")
        self.root.resizable(True, True)
        
        # Centrar ventana con las nuevas medidas
        self.centrar_ventana()
        
        # Canvas pantalla completa
        self.canvas = tk.Canvas(root, width=self.ancho, height=self.alto, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 2. Dibujar degradado extendido a 700px de altura
        self.dibujar_degradado("#712828", "#ff9d9d")
        
        # 3. Posicionamiento centrado (X = 550)
        self.mostrar_logo()
        
        # Subtítulo (Bajamos la posición Y para el nuevo tamaño)
        self.canvas.create_text(
            550, 520, 
            text="Sistema de Gestión de Inventarios y Ventas", 
            font=("Arial", 18, "italic"), 
            fill="#e0e0d5"
        )
        
        # 4. Barra de progreso estilizada
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background='#C48B7A', 
            troughcolor='#712828',
            bordercolor='#712828',
            thickness=20
        )
        
        self.progress = ttk.Progressbar(
            self.root,
            length=600, # Más larga para el nuevo ancho
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.canvas.create_window(550, 580, window=self.progress)
        
        self.label_carga = tk.Label(
            self.root, text="Iniciando sistema...", font=("Arial", 11, "bold"), 
            fg="#e0e0d5", bg="#9b5656" # Color ajustado al fondo
        )
        self.canvas.create_window(550, 620, window=self.label_carga)
        
        # Iniciar carga
        self.root.after(500, self.iniciar_carga)

    def dibujar_degradado(self, color_inicio, color_fin):
        """Crea el fondo visual adaptado al nuevo alto de 700px"""
        r1, g1, b1 = self.root.winfo_rgb(color_inicio)
        r2, g2, b2 = self.root.winfo_rgb(color_fin)
        r1, g1, b1 = r1//256, g1//256, b1//256
        r2, g2, b2 = r2//256, g2//256, b2//256
        
        for i in range(self.alto):
            r = int(r1 + (r2 - r1) * (i / self.alto))
            g = int(g1 + (g2 - g1) * (i / self.alto))
            b = int(b1 + (b2 - b1) * (i / self.alto))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, self.ancho, i, fill=color)

    def mostrar_logo(self):
        """Carga y centra el logo en la nueva resolución"""
        try:
            logo_path = os.path.join("assets", "portadaProyecto.jpg")
            if os.path.exists(logo_path):
                imagen = Image.open(logo_path)
                # Logo un poco más grande para la pantalla de 1100px
                imagen = imagen.resize((350, 350), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(imagen)
                self.canvas.create_image(550, 280, image=self.logo_img)
            else:
                self.canvas.create_text(
                    550, 280, text="SMART SALES", 
                    font=("Impact", 100), fill="#e0e0d5"
                )
        except:
            pass

    def centrar_ventana(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.alto // 2)
        self.root.geometry(f'{self.ancho}x{self.alto}+{x}+{y}')

    def iniciar_carga(self):
        """Simulación de carga fluida"""
        for i in range(101):
            self.progress['value'] = i
            self.label_carga.config(text=f"Cargando módulos de inventario... {i}%")
            self.root.update_idletasks()
            time.sleep(0.015) # Un poco más rápido
        
        # Pequeña pausa al final para elegancia
        self.root.after(400, self.callback)