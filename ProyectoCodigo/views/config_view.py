import os
import tkinter as tk
from tkinter import filedialog, messagebox
from models.empresa import Empresa
from PIL import Image, ImageTk

class VentanaConfig:
    def __init__(self, root, callback_volver):
        self.root = root
        self.callback_volver = callback_volver
        self.ruta_logo = ""

        # Limpiar ventana para la transición
        for widget in root.winfo_children(): 
            widget.destroy()
            
        self.root.title("Smart Sales - Configuración de Empresa")
        self.root.geometry("1100x700")
        self.root.configure(bg="#F2E8E4")

        # --- BARRA SUPERIOR GUINDA ---
        top_bar = tk.Frame(root, bg="#712828", height=50)
        top_bar.pack(fill="x")
        
        tk.Button(top_bar, text="⬅", command=self.callback_volver, 
                  bg="#712828", fg="white", relief="flat", 
                  font=("Arial", 18, "bold"), cursor="hand2").pack(side="left", padx=10)
        
        tk.Label(top_bar, text="PANEL DE CONFIGURACIÓN", font=("Arial", 14, "bold"), 
                 bg="#712828", fg="white").pack(side="left", padx=5)

        # --- CONTENEDOR CENTRAL (Sin bordes extra en los lados) ---
        main_container = tk.Frame(root, bg="#F2E8E4")
        main_container.pack(padx=50, pady=40, fill="both", expand=True)

        # 1. SECCIÓN IZQUIERDA: FORMULARIO
        left_panel = tk.Frame(main_container, bg="#F2E8E4")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 30))

        tk.Label(left_panel, text="REGISTRO DE EMPRESA", font=("Arial", 22, "bold"), 
                 bg="#F2E8E4", fg="#A5525A").pack(anchor="w", pady=(0, 15))

        # Campos de texto
        self.en_nom = self.crear_campo(left_panel, "Nombre de la Empresa")
        self.en_nit = self.crear_campo(left_panel, "NIT / RUT")
        self.en_dir = self.crear_campo(left_panel, "Dirección y Ciudad")
        self.en_tel = self.crear_campo(left_panel, "Teléfono")
        self.en_cor = self.crear_campo(left_panel, "Correo Electrónico")

        # --- BOTÓN DE GUARDADO (Recuperado) ---
        tk.Button(left_panel, text="EDITAR INFORMACIÓN", command=self.guardar, 
                  bg="#A5525A", fg="white", font=("Arial", 14, "bold"), 
                  padx=40, pady=10, cursor="hand2").pack(pady=30, anchor="w")

        # 2. SECCIÓN DERECHA: LOGO (Diseño limpio y grande)
        right_panel = tk.Frame(main_container, bg="#F2E8E4", width=380, height=450)
        right_panel.pack(side="right", padx=10, fill="y")
        right_panel.pack_propagate(False) # Evita que el cuadro se encoja

        tk.Label(right_panel, text="LOGO", font=("Arial", 14, "bold"), 
                 bg="#F2E8E4", fg="#A5525A").pack(pady=(15, 0))

        # Cuadro blanco de previsualización
        self.lbl_logo = tk.Label(right_panel, bg="white", relief="groove", bd=2)
        # ipady/ipadx le dan aire por dentro para que la imagen no toque los bordes
        self.lbl_logo.pack(pady=(10, 5), padx=20, expand=True)

        # Etiqueta de texto "Previsualización del Logo" (Nueva)
        tk.Label(right_panel, text="Previsualización del Logo", font=("Arial", 9), 
                 bg="#F2E8E4", fg="#A5525A").pack(pady=(0, 10))

        # Botón "Cargar Imagen" (Mauve con texto blanco, grande)
        tk.Button(right_panel, text="Cargar Imagen", command=self.seleccionar_logo, 
                  bg="#A5525A", fg="white", font=("Arial", 12, "bold"), 
                  padx=30, pady=8, cursor="hand2").pack(side="bottom", pady=(10, 25))
        # Cargar datos e imagen inicial desde la BD
        self.cargar_datos_actuales()

    def crear_campo(self, master, texto):
        """Helper para crear etiquetas y entradas rápidamente"""
        tk.Label(master, text=texto, bg="#F2E8E4", fg="#712828", 
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
        e = tk.Entry(master, font=("Arial", 12), bd=1, relief="solid")
        e.pack(fill="x", pady=5)
        return e

    def mostrar_imagen(self, ruta):
        """Dibuja la imagen en tamaño grande y centrado"""
        if os.path.exists(ruta):
            try:
                pil_img = Image.open(ruta)
                pil_img = pil_img.resize((250, 250), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                
                self.lbl_logo.config(image=tk_img, text="")
                self.lbl_logo.image = tk_img 
            except Exception as e:
                self.lbl_logo.config(text=f"Error:\n{e}", image="", fg="red")
        else:
            self.lbl_logo.config(text=f"No se encontró:\n{ruta}", fg="red")

    def seleccionar_logo(self):
        """Abre el buscador de archivos y actualiza la vista"""
        ruta = filedialog.askopenfilename(
            title="Seleccionar Logo",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")]
        )
        if ruta:
            self.ruta_logo = ruta
            self.mostrar_imagen(ruta)

    def cargar_datos_actuales(self):
        """Llama a la BD para llenar los campos y el logo"""
        d = Empresa.obtener_datos()
        if d:
            # Llenar campos de texto
            self.en_nom.insert(0, d['nombre'])
            self.en_nit.insert(0, d['nit'])
            self.en_dir.insert(0, d['direccion'])
            self.en_tel.insert(0, d['telefono'])
            self.en_cor.insert(0, d['correo'])
            
            # Cargar ruta del logo
            self.ruta_logo = d['ruta_logo']
            if not self.ruta_logo or not os.path.exists(self.ruta_logo):
                self.ruta_logo = "assets/cargarlogo.jpg" 
            
            self.mostrar_imagen(self.ruta_logo)

    def guardar(self):
        """Guarda los cambios en la Base de Datos"""
        try:
            exito = Empresa.actualizar(
                self.en_nom.get(), self.en_nit.get(), self.en_dir.get(), 
                self.en_tel.get(), self.en_cor.get(), self.ruta_logo
            )
            if exito:
                messagebox.showinfo("Éxito", "¡Información actualizada correctamente!")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")