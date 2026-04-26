import tkinter as tk
import threading
import time
from models.modelos import Usuario

COLORS = {
    "bg_main":        "#F1F5F9",  # Fondo general un poco más suave
    "card_bg":        "#FFFFFF",
    "border":         "#E2E8F0",
    "primary":        "#4361EE",
    "primary_hover":  "#3A56D4",
    "primary_light":  "#EEF2FF",  # Color para el focus
    "text_main":      "#1E293B",
    "text_muted":     "#64748B",
    "text_light":     "#F8FAFC",
    "entry_bg":       "#F8FAFC",
    "entry_border":   "#CBD5E1",
    "entry_focus":    "#4361EE",  # Borde al hacer clic
    "success":        "#10B981",
    "error":          "#EF4444"
}

class VentanaLogin:
    def __init__(self, root: tk.Tk, callback_success):
        self.root = root
        self.callback_success = callback_success
        self._loading = False
        self.mostrar_password = False

        self._configurar_ventana()
        self._construir_ui()

    def _configurar_ventana(self):
        self.root.title("Smart Sales – Acceso al Sistema")
        self.root.geometry("1024x600")
        self.root.state("zoomed")
        self.root.configure(bg=COLORS["bg_main"])

    def _construir_ui(self):
        # Contenedor principal (La Tarjeta Grande)
        self.card = tk.Frame(self.root, bg=COLORS["card_bg"], highlightbackground=COLORS["border"], highlightthickness=1)
        # Tamaño más ancho para el diseño de panel dividido
        self.card_width = 850
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=self.card_width, height=500)

        # ==========================================
        # PANEL IZQUIERDO (BRANDING)
        # ==========================================
        left_panel = tk.Frame(self.card, bg=COLORS["primary"])
        left_panel.place(relx=0, rely=0, relwidth=0.45, relheight=1)

        tk.Label(left_panel, text="📦", font=("Segoe UI", 60), bg=COLORS["primary"], fg="white").pack(pady=(120, 10))
        tk.Label(left_panel, text="SMART SALES", font=("Segoe UI", 24, "bold"), bg=COLORS["primary"], fg="white").pack()
        tk.Label(left_panel, text="Tu inventario bajo control,\nen tiempo real.", font=("Segoe UI", 11), bg=COLORS["primary"], fg=COLORS["primary_light"], justify="center").pack(pady=10)

        # ==========================================
        # PANEL DERECHO (FORMULARIO)
        # ==========================================
        right_panel = tk.Frame(self.card, bg=COLORS["card_bg"])
        right_panel.place(relx=0.45, rely=0, relwidth=0.55, relheight=1)

        # Contenedor interno para centrar el formulario
        form_container = tk.Frame(right_panel, bg=COLORS["card_bg"])
        form_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)

        tk.Label(form_container, text="¡Bienvenido de nuevo!", font=("Segoe UI", 20, "bold"), fg=COLORS["text_main"], bg=COLORS["card_bg"]).pack(anchor="w", pady=(0, 5))
        tk.Label(form_container, text="Ingresa tus credenciales para continuar.", font=("Segoe UI", 10), fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(anchor="w", pady=(0, 30))

        self.entries = {}
        self.borders = {} # Para manejar el cambio de color al hacer clic

        # Campo Usuario
        self._crear_campo(form_container, "USUARIO", "usuario", "👤")

        # Campo Contraseña
        tk.Label(form_container, text="CONTRASEÑA", font=("Segoe UI", 9, "bold"), fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(fill="x", pady=(10, 5))

        border_pw = tk.Frame(form_container, bg=COLORS["entry_border"])
        border_pw.pack(fill="x", pady=(0, 15))
        self.borders["password"] = border_pw

        pw_container = tk.Frame(border_pw, bg=COLORS["entry_bg"])
        pw_container.pack(fill="x", padx=1, pady=1) # El padx/pady 1 crea el efecto de borde

        tk.Label(pw_container, text="🔒", bg=COLORS["entry_bg"], fg=COLORS["text_muted"], font=("Segoe UI", 11)).pack(side="left", padx=(10, 0))

        self.entry_password = tk.Entry(pw_container, font=("Segoe UI", 11), bg=COLORS["entry_bg"], fg=COLORS["text_main"], relief="flat", bd=0, show="*")
        self.entry_password.pack(side="left", fill="x", expand=True, ipady=10, padx=(5, 0))

        btn_eye = tk.Button(pw_container, text="👁", bg=COLORS["entry_bg"], fg=COLORS["text_muted"], relief="flat", bd=0, cursor="hand2", command=self._toggle_password)
        btn_eye.pack(side="right", padx=10)

        self.entries["password"] = self.entry_password

        # Eventos Focus Contraseña
        self.entry_password.bind("<FocusIn>", lambda e: border_pw.config(bg=COLORS["entry_focus"]))
        self.entry_password.bind("<FocusOut>", lambda e: border_pw.config(bg=COLORS["entry_border"]))

        # Botón Login
        self.btn = tk.Button(form_container, text="Iniciar Sesión", font=("Segoe UI", 11, "bold"), fg="white", bg=COLORS["primary"], activebackground=COLORS["primary_hover"], activeforeground="white", relief="flat", cursor="hand2", command=self._validar)
        self.btn.pack(fill="x", pady=(15, 0), ipady=10)

        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=COLORS["primary_hover"]))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=COLORS["primary"]))

        # Mensajes de Estado
        self.lbl_status = tk.Label(form_container, text="", font=("Segoe UI", 9), fg=COLORS["text_muted"], bg=COLORS["card_bg"])
        self.lbl_status.pack(pady=(15, 0))

        self.lbl_msg = tk.Label(form_container, text="", font=("Segoe UI", 9, "bold"), fg=COLORS["error"], bg=COLORS["card_bg"])
        self.lbl_msg.pack(pady=(0, 0))

        self.entries["password"].bind("<Return>", lambda e: self._validar())
        self.entries["usuario"].bind("<Return>", lambda e: self.entries["password"].focus())

    def _crear_campo(self, parent, label_text, key, icon):
        tk.Label(parent, text=label_text, font=("Segoe UI", 9, "bold"), fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(fill="x", pady=(0, 5))

        border = tk.Frame(parent, bg=COLORS["entry_border"])
        border.pack(fill="x", pady=(0, 10))
        self.borders[key] = border

        inner_frame = tk.Frame(border, bg=COLORS["entry_bg"])
        inner_frame.pack(fill="x", padx=1, pady=1)

        tk.Label(inner_frame, text=icon, bg=COLORS["entry_bg"], fg=COLORS["text_muted"], font=("Segoe UI", 11)).pack(side="left", padx=(10, 0))

        entry = tk.Entry(inner_frame, font=("Segoe UI", 11), bg=COLORS["entry_bg"], fg=COLORS["text_main"], relief="flat", bd=0)
        entry.pack(fill="x", expand=True, ipady=10, padx=(5, 10))

        # Efecto Focus
        entry.bind("<FocusIn>", lambda e, b=border: b.config(bg=COLORS["entry_focus"]))
        entry.bind("<FocusOut>", lambda e, b=border: b.config(bg=COLORS["entry_border"]))

        self.entries[key] = entry

    def _toggle_password(self):
        self.mostrar_password = not self.mostrar_password
        self.entry_password.config(show="" if self.mostrar_password else "*")

    def _validar(self):
        if self._loading:
            return

        usuario = self.entries["usuario"].get().strip()
        password = self.entries["password"].get().strip()
        self.lbl_msg.config(text="")

        if len(usuario) < 3:
            self.lbl_msg.config(text="⚠️ El usuario es muy corto")
            self._sacudir_card()
            return

        if len(password) < 3:
            self.lbl_msg.config(text="⚠️ La contraseña es muy corta")
            self._sacudir_card()
            return

        self._loading = True
        self.btn.config(state="disabled", text="Verificando...")
        self.lbl_status.config(text="Validando credenciales en la base de datos...")

        threading.Thread(target=self._consultar_usuario, args=(usuario, password), daemon=True).start()

    def _consultar_usuario(self, usuario, password):
        time.sleep(1.0)
        datos = Usuario.autenticar(usuario, password)
        self.root.after(0, lambda: self._resultado(datos))

    def _resultado(self, datos):
        self._loading = False
        self.btn.config(state="normal", text="Iniciar Sesión")

        if datos:
            self.lbl_status.config(text="✅ Acceso concedido", fg=COLORS["success"])
            self.lbl_msg.config(text=f"¡Bienvenido, {datos.get('nombre', 'Usuario')}!", fg=COLORS["success"])
            self.root.after(800, lambda: self.callback_success(datos))
        else:
            self.lbl_status.config(text="", fg=COLORS["text_muted"])
            self.lbl_msg.config(text="❌ Credenciales incorrectas", fg=COLORS["error"])
            self.entries["password"].delete(0, "end")
            self.entries["password"].focus()
            self._sacudir_card()

    def _sacudir_card(self):
        # En lugar de sacudir el monitor completo, sacudimos solo el formulario
        original_x = 0.5 
        
        def animate(step=0):
            offsets = [-0.01, 0.01, -0.005, 0.005, -0.002, 0.002, 0]
            if step < len(offsets):
                self.card.place_configure(relx=original_x + offsets[step])
                self.root.after(40, animate, step + 1)
                
        animate()