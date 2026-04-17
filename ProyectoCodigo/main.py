import tkinter as tk
from tkinter import messagebox

from views.portada import VentanaPortada
from views.login_view import VentanaLogin
from views.menu_principal import MenuPrincipal
from config.db_conexion import ConexionDB


class SmartSalesApp:
    def __init__(self):
        self.root = tk.Tk()
        self.usuario_actual = None
        self.db = None

        self._configurar_ventana()
        self._conectar_db()
        self.root.protocol("WM_DELETE_WINDOW", self._al_cerrar)
        self.mostrar_portada()

    # ── Configuración inicial ──────────────────────────────────────────────────
    def _configurar_ventana(self):
        self.root.title("SmartSales")
        self.root.geometry("480x620")
        self.root.resizable(True, True)
        self.root.minsize(380, 520)
        self.root.state("zoomed")

    def _conectar_db(self):
        """Intenta conectar a la base de datos al arrancar."""
        try:
            self.db = ConexionDB()
        except Exception as e:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar a la base de datos:\n{e}\n\n"
                "La aplicación se cerrará."
            )
            self.root.destroy()

    # ── Navegación entre vistas ────────────────────────────────────────────────
    def _limpiar_ventana(self):
        """Destruye todos los widgets de la ventana actual."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_portada(self):
        self._limpiar_ventana()
        VentanaPortada(self.root, self.mostrar_login)

    def mostrar_login(self):
        self._limpiar_ventana()
        self.usuario_actual = None
        VentanaLogin(self.root, self._login_exitoso)

    def _login_exitoso(self, datos_usuario):
        self.usuario_actual = datos_usuario
        nombre = datos_usuario.get("nombre", "Usuario")
        rol    = datos_usuario.get("rol", "")
        self.root.title(f"SmartSales  —  {nombre}  ({rol})")
        self.mostrar_menu_principal()

    def mostrar_menu_principal(self):
        self._limpiar_ventana()
        MenuPrincipal(self.root, self.usuario_actual, self._cerrar_sesion)

    def _cerrar_sesion(self):
        """Cierra sesión y vuelve al login."""
        confirmado = messagebox.askyesno(
            "Cerrar sesión",
            "¿Seguro que deseas cerrar sesión?"
        )
        if confirmado:
            self.root.title("SmartSales")
            self.mostrar_login()

    # ── Cierre limpio ─────────────────────────────────────────────────────────
    def _al_cerrar(self):
        """Pregunta confirmación y cierra la app limpiamente."""
        confirmado = messagebox.askyesno(
            "Salir",
            "¿Deseas salir de SmartSales?"
        )
        if not confirmado:
            return

        try:
            if self.db:
                self.db.cerrar()
        except Exception:
            pass

        self.root.destroy()

    # ── Loop principal ─────────────────────────────────────────────────────────
    def ejecutar(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SmartSalesApp()
    app.ejecutar()