import tkinter as tk
from tkinter import messagebox

class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        
        # Limpiar ventana para la transición
        for widget in root.winfo_children():
            widget.destroy()
        
        self.root.title("Smart Sales - Sistema de Gestión")
        self.root.geometry("1100x700")
        
        # Canvas para el fondo
        self.canvas = tk.Canvas(root, width=1100, height=700, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # LLAMADA AL DEGRADADO (Aquí es donde daba el error)
        self.dibujar_degradado("#712828", "#ff9d9d")
        
        # Título SMART SALES (Color crema e0e0d5)
        self.canvas.create_text(150, 320, text="SMART", font=("Impact", 110), fill="#e0e0d5", anchor="w")
        self.canvas.create_text(150, 450, text="SALES", font=("Impact", 110), fill="#e0e0d5", anchor="w")
        
        # Botones de módulos con colores del mockup
        self.crear_boton_modulo("INVENTARIO", 800, 200, "#C48B7A", self.abrir_inventario)
        self.crear_boton_modulo("VENTAS", 800, 310, "#CA9788", self.abrir_ventas)
        self.crear_boton_modulo("CLIENTES", 800, 420, "#D8B6AC", self.abrir_clientes)
        self.crear_boton_modulo("CONFIGURACION", 800, 530, "#D8B6AC", self.abrir_configuracion)

    # --- MÉTODO FALTANTE QUE DEBES AGREGAR ---
    def dibujar_degradado(self, color_inicio, color_fin):
        """Crea el efecto de fondo degradado del diseño"""
        r1, g1, b1 = self.root.winfo_rgb(color_inicio)
        r2, g2, b2 = self.root.winfo_rgb(color_fin)
        r1, g1, b1 = r1//256, g1//256, b1//256
        r2, g2, b2 = r2//256, g2//256, b2//256
        
        for i in range(700):
            r = int(r1 + (r2 - r1) * (i / 700))
            g = int(g1 + (g2 - g1) * (i / 700))
            b = int(b1 + (b2 - b1) * (i / 700))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 1100, i, fill=color)

    def crear_boton_modulo(self, texto, x, y, color, comando):
        btn = tk.Button(self.root, text=texto, command=comando, font=("Arial", 16, "bold"), 
                        bg=color, fg="white", width=22, height=2, relief="flat", cursor="hand2")
        self.canvas.create_window(x, y, window=btn)
        btn.bind("<Enter>", lambda e: btn.config(bg="#e0e0d5", fg=color))
        btn.bind("<Leave>", lambda e: btn.config(bg=color, fg="white"))

    def abrir_inventario(self):
        from views.productos_view import VentanaProductos
        VentanaProductos(self.root, self.volver_menu)

    def volver_menu(self):
        self.__init__(self.root)

    def abrir_ventas(self):
        try:
            from views.ventas_view import VentanaVentas
            VentanaVentas(self.root, self.volver_menu)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir Ventas: {e}")
    def abrir_clientes(self):
        try:
            from views.clientes_view import VentanaClientes
            VentanaClientes(self.root, self.volver_menu)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al abrir Clientes: {e}")
    def abrir_configuracion(self):
        """Importa y abre la ventana de configuración de la empresa"""
        try:
            from views.config_view import VentanaConfig
            # Pasamos self.root para que use la misma ventana y self.volver_menu para el botón atrás
            VentanaConfig(self.root, self.volver_menu)
        except ImportError:
            messagebox.showerror("Error", "No se encontró el archivo 'views/config_view.py'")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al abrir configuración: {e}")