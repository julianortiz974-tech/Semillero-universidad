import tkinter as tk
from views.portada import VentanaPortada
from views.menu_principal import MenuPrincipal
from config.db_conexion import ConexionDB

class SmartSalesApp:
    def __init__(self):
        self.root = tk.Tk()
        # Agregamos el protocolo de cierre que mencionamos antes
        self.root.protocol("WM_DELETE_WINDOW", self.al_cerrar)
        
        # Corregido: 'mostrar_portada' con la 'r'
        self.mostrar_portada()

    def mostrar_portada(self):
        """Muestra la pantalla de portada"""
        VentanaPortada(self.root, self.mostrar_menu_principal)

    def mostrar_menu_principal(self):
        """Muestra el menú principal"""
        MenuPrincipal(self.root)

    def al_cerrar(self):
        """Cierre limpio de la base de datos"""
        db = ConexionDB()
        db.cerrar()
        self.root.destroy()

    def ejecutar(self):
        """Inicia el loop principal de la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SmartSalesApp()
    app.ejecutar()