import tkinter as tk
import threading
import time
from models.usuario import UsuarioModel


# ── Paleta de colores ──────────────────────────────────────────────────────────
COLORS = {
    "bg_top":      "#8b2a2a",
    "bg_bottom":   "#d4847a",
    "card_bg":     "#b04848",
    "card_border": "#c96060",
    "text_white":  "#ffffff",
    "text_muted":  "#f0d0d0",
    "entry_bg":    "#9e3b3b",
    "entry_fg":    "#ffffff",
    "btn_bg":      "#7a2020",
    "btn_hover":   "#9b3030",
    "bar_bg":      "#7a2020",
    "bar_fill":    "#f0c0c0",
    "error_fg":    "#ffb3b3",
    "success_fg":  "#b3ffd1",
}

FONT_TITLE    = ("Impact", 32, "bold")
FONT_SUBTITLE = ("Georgia", 12, "italic")
FONT_LABEL    = ("Segoe UI", 10, "bold")
FONT_ENTRY    = ("Segoe UI", 11)
FONT_BTN      = ("Segoe UI", 12, "bold")
FONT_STATUS   = ("Segoe UI", 9)


class VentanaLogin:
    def __init__(self, root: tk.Tk, callback_success):
        self.root = root
        self.callback_success = callback_success
        self._loading = False

        self._configurar_ventana()
        self._construir_ui()
        self._animar_entrada()

    # ── Configuración de la ventana ────────────────────────────────────────────
    def _configurar_ventana(self):
        self.root.title("SmartSales – Inicio de Sesión")
        self.root.geometry("480x620")      # tamaño inicial antes de maximizar
        self.root.resizable(True, True)    # habilita los 3 botones normales
        self.root.state("zoomed")          # abre maximizado (Windows)
        self.root.configure(bg=COLORS["bg_top"])
        self.root.minsize(380, 520)        # tamaño mínimo para que no se rompa

    # ── Construcción de la UI ──────────────────────────────────────────────────
    def _construir_ui(self):
        # Canvas para el fondo degradado, se expande con la ventana
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Redibujar fondo cada vez que cambie el tamaño
        self.root.bind("<Configure>", lambda e: self._redibujar_fondo())

        # ── Card central ──────────────────────────────────────────────────────
        self.card = tk.Frame(
            self.canvas,
            bg=COLORS["card_bg"],
            highlightthickness=1,
            highlightbackground=COLORS["card_border"]
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=340, height=460)

        # Logo / título
        tk.Label(
            self.card, text="SMART SALES",
            font=FONT_TITLE, fg=COLORS["text_white"],
            bg=COLORS["card_bg"]
        ).pack(pady=(30, 2))

        tk.Label(
            self.card, text="Sistema de Gestión de Ventas",
            font=FONT_SUBTITLE, fg=COLORS["text_muted"],
            bg=COLORS["card_bg"]
        ).pack(pady=(0, 22))

        # ── Campos ────────────────────────────────────────────────────────────
        self.entries = {}
        self._crear_campo(self.card, "USUARIO",    "usuario")
        self._crear_campo(self.card, "CONTRASEÑA", "password", show="*")

        # ── Botón ─────────────────────────────────────────────────────────────
        self.btn = tk.Button(
            self.card, text="ENTRAR",
            font=FONT_BTN, fg=COLORS["text_white"],
            bg=COLORS["btn_bg"],
            activebackground=COLORS["btn_hover"],
            activeforeground=COLORS["text_white"],
            relief="flat", cursor="hand2",
            command=self._validar
        )
        self.btn.pack(fill="x", padx=30, pady=(12, 0), ipady=10)
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=COLORS["btn_hover"]))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=COLORS["btn_bg"]))

        # ── Barra de progreso ─────────────────────────────────────────────────
        bar_frame = tk.Frame(self.card, bg=COLORS["card_bg"])
        bar_frame.pack(fill="x", padx=30, pady=(16, 0))

        self.bar_bg = tk.Frame(bar_frame, bg=COLORS["bar_bg"], height=8)
        self.bar_bg.pack(fill="x")

        self.bar_fill = tk.Frame(self.bar_bg, bg=COLORS["bar_fill"], height=8)
        self.bar_fill.place(relwidth=0, rely=0, anchor="nw")

        self.lbl_status = tk.Label(
            self.card, text="",
            font=FONT_STATUS, fg=COLORS["text_muted"],
            bg=COLORS["card_bg"]
        )
        self.lbl_status.pack(pady=(5, 0))

        # ── Mensaje error / éxito ─────────────────────────────────────────────
        self.lbl_msg = tk.Label(
            self.card, text="",
            font=FONT_STATUS, fg=COLORS["error_fg"],
            bg=COLORS["card_bg"]
        )
        self.lbl_msg.pack(pady=(2, 0))

        # Teclas Enter
        self.entries["password"].bind("<Return>", lambda e: self._validar())
        self.entries["usuario"].bind("<Return>",
            lambda e: self.entries["password"].focus())

    def _crear_campo(self, parent, label_text, key, show=None):
        tk.Label(
            parent, text=label_text,
            font=FONT_LABEL, fg=COLORS["text_muted"],
            bg=COLORS["card_bg"], anchor="w"
        ).pack(fill="x", padx=30, pady=(0, 3))

        entry = tk.Entry(
            parent, font=FONT_ENTRY,
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["entry_fg"],
            relief="flat", bd=0, show=show
        )
        entry.pack(fill="x", padx=30, pady=(0, 4), ipady=8)

        tk.Frame(parent, bg=COLORS["card_border"], height=1).pack(
            fill="x", padx=30, pady=(0, 12)
        )

        self.entries[key] = entry

    # ── Fondo degradado (se redibuja al cambiar tamaño) ───────────────────────
    def _redibujar_fondo(self):
        self.canvas.delete("fondo")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 2 or h < 2:
            return
        steps = 60
        r1, g1, b1 = 0x8b, 0x2a, 0x2a
        r2, g2, b2 = 0xd4, 0x84, 0x7a
        step_h = max(1, h // steps)
        for i in range(steps):
            t = i / steps
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_rectangle(
                0, i * step_h, w, (i + 1) * step_h,
                fill=color, outline=color, tags="fondo"
            )
        # El fondo siempre detrás de la card
        self.canvas.tag_lower("fondo")

    # ── Animación de entrada ───────────────────────────────────────────────────
    def _animar_entrada(self):
        self.root.attributes("-alpha", 0.0)
        self._fade_in(0.0)

    def _fade_in(self, alpha):
        if alpha < 1.0:
            alpha = min(alpha + 0.07, 1.0)
            self.root.attributes("-alpha", alpha)
            self.root.after(20, lambda: self._fade_in(alpha))

    # ── Barra de progreso animada ──────────────────────────────────────────────
    def _animar_barra(self, pasos):
        def _paso(idx):
            if idx >= len(pasos):
                return
            pct, texto, delay = pasos[idx]
            self.bar_fill.place(relwidth=pct)
            self.lbl_status.config(text=texto)
            self.root.after(delay, lambda: _paso(idx + 1))
        _paso(0)

    # ── Validación ────────────────────────────────────────────────────────────
    def _validar(self):
        if self._loading:
            return

        usuario  = self.entries["usuario"].get().strip()
        password = self.entries["password"].get().strip()

        self.lbl_msg.config(text="", fg=COLORS["error_fg"])

        if not usuario:
            self.lbl_msg.config(text="⚠  Ingresa tu nombre de usuario")
            self.entries["usuario"].focus()
            return
        if not password:
            self.lbl_msg.config(text="⚠  Ingresa tu contraseña")
            self.entries["password"].focus()
            return

        self._loading = True
        self.btn.config(state="disabled", text="VERIFICANDO...")

        pasos = [
            (0.2, "Verificando credenciales...",   300),
            (0.5, "Consultando base de datos...",  350),
            (0.8, "Cargando perfil de usuario...", 350),
            (1.0, "Procesando...",                 300),
        ]
        self._animar_barra(pasos)

        threading.Thread(
            target=self._consultar_usuario,
            args=(usuario, password),
            daemon=True
        ).start()

    def _consultar_usuario(self, usuario, password):
        time.sleep(1.4)
        datos = UsuarioModel.validar_usuario(usuario, password)
        self.root.after(0, lambda: self._resultado(datos))

    def _resultado(self, datos):
        self._loading = False
        self.btn.config(state="normal", text="ENTRAR")

        if datos:
            self.lbl_status.config(text="✓ Acceso concedido")
            nombre = datos.get("nombre", "Usuario")
            self.lbl_msg.config(
                text=f"Bienvenido, {nombre}",
                fg=COLORS["success_fg"]
            )
            self.root.after(600, lambda: self.callback_success(datos))
        else:
            self.bar_fill.place(relwidth=0)
            self.lbl_status.config(text="")
            self.lbl_msg.config(
                text="✖  Usuario o contraseña incorrectos",
                fg=COLORS["error_fg"]
            )
            self.entries["password"].delete(0, "end")
            self.entries["password"].focus()
            self._sacudir_ventana()

    def _sacudir_ventana(self):
        x0 = self.root.winfo_x()
        y0 = self.root.winfo_y()
        movs = [(-8, 0), (8, 0), (-6, 0), (6, 0), (-4, 0), (4, 0), (0, 0)]

        def _mv(i):
            if i >= len(movs):
                return
            dx, dy = movs[i]
            self.root.geometry(f"+{x0+dx}+{y0+dy}")
            self.root.after(40, lambda: _mv(i + 1))

        _mv(0)