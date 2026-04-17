import tkinter as tk
from tkinter import messagebox

# ── Paleta de colores ──────────────────────────────────────────────────────────
COLORS = {
    "bg_top":       "#712828",
    "bg_bottom":    "#d4847a",
    "text_light":   "#e0e0d5",
    "btn_1":        "#C48B7A",
    "btn_2":        "#CA9788",
    "btn_3":        "#D8B6AC",
    "btn_4":        "#D8B6AC",
    "btn_hover_bg": "#e0e0d5",
    "logout_bg":    "#5a1e1e",
    "logout_hover": "#7a2828",
}

FONT_LOGO    = ("Impact", 110)
FONT_INFO    = ("Segoe UI", 11, "bold")
FONT_BTN     = ("Segoe UI", 14, "bold")
FONT_LOGOUT  = ("Segoe UI", 10, "bold")

class MenuPrincipal:
    def __init__(self, root: tk.Tk, usuario_actual: dict, logout_callback):
        self.root = root
        self.usuario = usuario_actual
        self.logout_callback = logout_callback
        self.nombre_usuario = usuario_actual["nombre"]
        self.rol_usuario    = usuario_actual["rol"]
        
        self._limpiar_ventana()
        self.root.title(f"Smart Sales – {self.nombre_usuario} ({self.rol_usuario})")
        self.root.geometry("1100x700")

        # Contenedor de botones para no recrearlos
        self.botones_modulos = []
        self.btn_logout = None
        
        self._construir_ui()
        
    def _redibujar(self):
        """Método ÚNICO para actualizar todo el diseño al redimensionar."""
        
        # 1. Escudo de seguridad: Si el canvas ya no existe, no hacemos nada
        if not self.canvas.winfo_exists():
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Evitar cálculos si la ventana es demasiado pequeña (como al minimizar)
        if w < 10 or h < 10: 
            return

        # 2. LIMPIEZA: Borramos solo los dibujos, NO los botones (widgets)
        self.canvas.delete("fondo_diseno")

        # 3. DIBUJO DEL FONDO (Degradado)
        self._dibujar_degradado(w, h)

        # 4. DIBUJO DE LA BARRA SUPERIOR
        self.canvas.create_rectangle(
            0, 0, w, 55, 
            fill="#4a1818", outline="", tags="fondo_diseno"
        )

        # 5. ACTUALIZACIÓN DE TEXTOS (Info de sesión y Logo)
        info = f"Usuario: {self.nombre_usuario}  |  Rol: {self.rol_usuario}"
        self.canvas.create_text(
            20, 27, text=info, font=FONT_INFO, 
            fill=COLORS["text_light"], anchor="w", tags="fondo_diseno"
        )
        
        cy = h // 2
        self.canvas.create_text(
            w * 0.08, cy - 80, text="SMART", 
            font=FONT_LOGO, fill=COLORS["text_light"], anchor="w", tags="fondo_diseno"
        )
        self.canvas.create_text(
            w * 0.08, cy + 60, text="SALES", 
            font=FONT_LOGO, fill=COLORS["text_light"], anchor="w", tags="fondo_diseno"
        )

        # 6. REPOSICIONAMIENTO DE BOTONES (Sin volver a crearlos)
        # Mover Botón Logout
        self.canvas.coords(self.logout_id, w - 20, 27)
        self.canvas.itemconfigure(self.logout_id, state='normal')

        # Mover Botones de Módulos
        bx = w * 0.72
        gap = 115
        # Calculamos el inicio para que el grupo de botones siempre esté centrado verticalmente
        by_start = cy - (len(self.botones_modulos) * gap) // 2 + 50
        
        for i, window_id in enumerate(self.botones_modulos):
            self.canvas.coords(window_id, bx, by_start + i * gap)
            self.canvas.itemconfigure(window_id, state='normal')
        

    def _limpiar_ventana(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _construir_ui(self):
        
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 1. CREAR los widgets una sola vez
        self._inicializar_widgets()

        # 2. VINCULAR el evento AL CANVAS directamente
        # Al hacerlo al canvas, evitamos que el root intente redibujar 
        # cuando el menú ya no existe.
        self.canvas.bind("<Configure>", lambda e: self._redibujar())
        
        # Pequeño delay para el primer dibujado
        self.root.after(100, self._redibujar)

    def _inicializar_widgets(self):
        """Crea los objetos de botón pero no los posiciona aún."""
        # Botón Logout
        self.btn_logout = tk.Button(
            self.canvas, text="Cerrar Sesión",
            command=self._confirmar_logout,
            font=FONT_LOGOUT, bg=COLORS["logout_bg"], fg=COLORS["text_light"],
            activebackground=COLORS["logout_hover"], activeforeground=COLORS["text_light"],
            relief="flat", cursor="hand2", padx=12, pady=4
        )
        self.btn_logout.bind("<Enter>", lambda e: self.btn_logout.config(bg=COLORS["logout_hover"]))
        self.btn_logout.bind("<Leave>", lambda e: self.btn_logout.config(bg=COLORS["logout_bg"]))

        # Botones de módulos
        modulos = [
            ("INVENTARIO",   COLORS["btn_1"], self.abrir_inventario),
            ("VENTAS",       COLORS["btn_2"], self.abrir_ventas),
            ("CLIENTES",     COLORS["btn_3"], self.abrir_clientes),
        ]
        
        if self.rol_usuario == "ADMIN":
            modulos.append(("CONFIGURACIÓN", COLORS["btn_4"], self.abrir_configuracion))

        for texto, color, cmd in modulos:
            btn = tk.Button(
                self.canvas, text=texto, command=cmd,
                font=FONT_BTN, bg=color, fg="white",
                activebackground=COLORS["btn_hover_bg"], activeforeground=color,
                width=20, height=2, relief="flat", cursor="hand2"
            )
            # Efecto hover corregido (usando clausura para mantener el color)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=COLORS["btn_hover_bg"], fg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c, fg="white"))
            
            # Guardamos el ID de la ventana del canvas para moverlo luego
            window_id = self.canvas.create_window(0, 0, window=btn, state='hidden')
            self.botones_modulos.append(window_id)

        # ID del botón logout
        self.logout_id = self.canvas.create_window(0, 0, window=self.btn_logout, anchor="e", state='hidden')

    def _dibujar_degradado(self, w, h):
        r1, g1, b1 = 0x71, 0x28, 0x28
        r2, g2, b2 = 0xd4, 0x84, 0x7a
        steps = 30 # Reducido para mejor rendimiento
        step_h = h / steps
        for i in range(steps):
            t = i / steps
            color = f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"
            self.canvas.create_rectangle(0, i*step_h, w, (i+1)*step_h, fill=color, outline=color, tags="fondo_diseno")

    def _confirmar_logout(self):
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar la sesión actual?"):
            # IMPORTANTE: Desvincular el evento antes de salir para evitar errores de memoria
            self.root.unbind("<Configure>", self._bind_id)
            self.logout_callback()

    # --- Navegación ---
    def abrir_inventario(self):
        try:
            # Antes de irnos, ocultamos los widgets para evitar parpadeos
            self.canvas.pack_forget() 
            
            from views.productos_view import VentanaProductos
            VentanaProductos(self.root, self.volver_menu)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Inventario: {e}")

    def volver_menu(self):
        """Regresa al menú refrescando la vista."""
        # Al usar __init__ de nuevo, se recrea todo el objeto limpiamente
        self.__init__(self.root, self.usuario, self.logout_callback)

    def abrir_ventas(self):
        try:
            from views.ventas_view import VentanaVentas
            VentanaVentas(self.root, self.volver_menu)
        except Exception as e: messagebox.showerror("Error", f"No disponible: {e}")

    def abrir_clientes(self):
        try:
            from views.clientes_view import VentanaClientes
            VentanaClientes(self.root, self.volver_menu)
        except Exception as e: messagebox.showerror("Error", f"No disponible: {e}")

    def abrir_configuracion(self):
        try:
            from views.config_view import VentanaConfig
            VentanaConfig(self.root, self.volver_menu)
        except Exception as e: messagebox.showerror("Error", f"No disponible: {e}")

    def volver_menu(self):
        # Desvinculamos el evento anterior para que no se duplique al reiniciar
        self.root.unbind("<Configure>", self._bind_id)
        self.__init__(self.root, self.usuario, self.logout_callback)