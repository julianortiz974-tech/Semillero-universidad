import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from models.modelos import Usuario

# ── Paleta (igual que el resto del sistema) ─────────────────────────────────
BG        = "#F4F6F9"
BG_CARD   = "#FFFFFF"
BORDER    = "#E2E8F0"
ACCENT    = "#4361EE"
ACCENT_H  = "#2b4fd4"
DANGER    = "#E63946"
SUCCESS   = "#10B981"
TEXT_DARK = "#1E293B"
TEXT_MID  = "#64748B"
TEXT_LITE = "#94A3B8"


def _hash(password: str) -> str:
    return hashlib.sha256(password.strip().encode()).hexdigest()


class VentanaUsuarios:
    def __init__(self, root, usuario_actual):
        self.root          = root
        self.usuario_actual = usuario_actual   # dict con datos del admin logueado

        for w in root.winfo_children():
            w.destroy()

        root.configure(bg=BG)
        self._construir_ui()
        self.cargar_usuarios()

    # ──────────────────────────────────────────────────────────────────────
    # UI PRINCIPAL
    # ──────────────────────────────────────────────────────────────────────

    def _construir_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=30, pady=(30, 10))

        tk.Label(header, text="Gestión de Usuarios",
                 font=("Segoe UI", 20, "bold"), bg=BG, fg=TEXT_DARK).pack(side="left")

        tk.Button(header, text="＋  Nuevo Usuario",
                  command=self.form_nuevo_usuario,
                  bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  padx=16, pady=8,
                  activebackground=ACCENT_H, activeforeground="white"
                  ).pack(side="right")

        tk.Label(header,
                 text="Solo los administradores pueden gestionar usuarios.",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT_MID).pack(side="left", padx=20)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(0, 15))

        # TARJETA DE LA TABLA
        card = tk.Frame(self.root, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Barra de acciones sobre la tabla
        action_bar = tk.Frame(card, bg=BG_CARD)
        action_bar.pack(fill="x", padx=20, pady=(15, 5))

        for texto, cmd, color in [
            ("✏️  Editar",            self.form_editar_usuario,   ACCENT),
            ("🔑  Cambiar Contraseña", self.form_cambiar_password, "#F59E0B"),
            ("🔁  Activar / Desactivar", self.toggle_estado,      "#6B7280"),
        ]:
            tk.Button(action_bar, text=texto, command=cmd,
                      bg=color, fg="white", relief="flat",
                      font=("Segoe UI", 9, "bold"), cursor="hand2",
                      padx=12, pady=6,
                      activebackground=ACCENT_H, activeforeground="white"
                      ).pack(side="left", padx=(0, 8))

        # TABLA
        cols = ("ID", "Nombre", "Usuario", "Rol", "Estado")
        self.tabla = ttk.Treeview(card, columns=cols, show="headings",
                                  selectmode="browse")

        anchos = {"ID": 50, "Nombre": 220, "Usuario": 160, "Rol": 130, "Estado": 100}
        for c in cols:
            self.tabla.heading(c, text=c)
            self.tabla.column(c, anchor="center", width=anchos[c])

        self.tabla.tag_configure("activo",   background="#F0FDF4", foreground="#166534")
        self.tabla.tag_configure("inactivo", background="#FEF2F2", foreground="#991B1B")

        scroll = ttk.Scrollbar(card, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.tabla.pack(fill="both", expand=True, padx=(10, 0), pady=10)

        self.tabla.bind("<Double-1>", lambda e: self.form_editar_usuario())

    
    # CARGAR DATOS

    def cargar_usuarios(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        for u in Usuario.obtener_todos():
            estado_txt = "✅ Activo" if u["estado"] else "❌ Inactivo"
            tag        = "activo"   if u["estado"] else "inactivo"
            self.tabla.insert("", "end", values=(
                u["id_usuario"], u["nombre"], u["username"],
                u["rol"], estado_txt
            ), tags=(tag,))

    def _fila_seleccionada(self):
        item = self.tabla.selection()
        if not item:
            messagebox.showwarning("Selección requerida",
                                   "Selecciona un usuario de la lista.")
            return None
        return self.tabla.item(item)["values"]

    # FORMULARIOS (modales)

    def _modal(self, titulo, ancho=420, alto=480):
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry(f"{ancho}x{alto}")
        win.resizable(False, False)
        win.grab_set()
        win.configure(bg=BG_CARD)

        tk.Label(win, text=titulo, font=("Segoe UI", 14, "bold"),
                 bg=BG_CARD, fg=TEXT_DARK).pack(pady=(20, 5), padx=24, anchor="w")
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 10))
        return win

    def _entry(self, parent, label, placeholder="", show=""):
        tk.Label(parent, text=label, font=("Segoe UI", 9, "bold"),
                 bg=BG_CARD, fg=TEXT_MID).pack(anchor="w", padx=24, pady=(8, 2))
        e = tk.Entry(parent, font=("Segoe UI", 11), show=show, bd=0, relief="flat",
                     fg=TEXT_LITE if placeholder else TEXT_DARK,
                     highlightbackground=BORDER, highlightthickness=1,
                     highlightcolor=ACCENT)
        e.pack(fill="x", padx=24, ipady=8)
        if placeholder:
            e.insert(0, placeholder)
            e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder:
                   (en.delete(0, tk.END), en.config(fg=TEXT_DARK)) if en.get() == ph else None)
            e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder:
                   (en.insert(0, ph), en.config(fg=TEXT_LITE)) if en.get().strip() == "" else None)
        return e

    def _boton_guardar(self, parent, texto, comando):
        tk.Button(parent, text=texto, command=comando,
                  bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), cursor="hand2",
                  padx=20, pady=10,
                  activebackground=ACCENT_H, activeforeground="white"
                  ).pack(fill="x", padx=24, pady=(20, 8))

    # ── NUEVO USUARIO ──────────────────────────────────────────────────────

    def form_nuevo_usuario(self):
        win = self._modal("Nuevo Usuario", alto=520)

        en_nombre = self._entry(win, "Nombre completo *", "Ej: Juan Pérez")
        en_user   = self._entry(win, "Nombre de usuario *", "Ej: jperez")
        en_pass   = self._entry(win, "Contraseña *", show="●")
        en_pass2  = self._entry(win, "Confirmar contraseña *", show="●")

        tk.Label(win, text="Rol *", font=("Segoe UI", 9, "bold"),
                 bg=BG_CARD, fg=TEXT_MID).pack(anchor="w", padx=24, pady=(8, 2))
        cb_rol = ttk.Combobox(win, values=["ADMIN", "CAJERO"],
                              state="readonly", font=("Segoe UI", 11))
        cb_rol.set("CAJERO")
        cb_rol.pack(fill="x", padx=24, ipady=4)

        tk.Label(win, text="(*) Campos obligatorios",
                 font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_LITE).pack(padx=24, anchor="w")

        def guardar():
            nombre = en_nombre.get().strip()
            user   = en_user.get().strip()
            pwd    = en_pass.get()
            pwd2   = en_pass2.get()
            rol    = cb_rol.get()

            if not nombre or nombre.startswith("Ej:"):
                messagebox.showwarning("Campo requerido", "El nombre es obligatorio.", parent=win); return
            if not user or user.startswith("Ej:"):
                messagebox.showwarning("Campo requerido", "El usuario es obligatorio.", parent=win); return
            if len(pwd) < 4:
                messagebox.showwarning("Contraseña débil",
                    "La contraseña debe tener al menos 4 caracteres.", parent=win); return
            if pwd != pwd2:
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=win); return

            exito, msg = Usuario.insertar(nombre, user, pwd, rol)
            if exito:
                messagebox.showinfo("✅ Listo", "Usuario creado correctamente.", parent=win)
                win.destroy()
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", msg, parent=win)

        self._boton_guardar(win, "  💾  Crear Usuario", guardar)

    # ── EDITAR USUARIO ─────────────────────────────────────────────────────

    def form_editar_usuario(self):
        vals = self._fila_seleccionada()
        if not vals: return

        id_u, nombre, username, rol, _ = vals

        # No dejar editar el propio admin logueado desde aquí (solo desde perfil)
        win = self._modal("Editar Usuario", alto=440)

        en_nombre = self._entry(win, "Nombre completo *")
        en_nombre.insert(0, nombre)
        en_nombre.config(fg=TEXT_DARK)

        en_user = self._entry(win, "Nombre de usuario *")
        en_user.insert(0, username)
        en_user.config(fg=TEXT_DARK)

        tk.Label(win, text="Rol *", font=("Segoe UI", 9, "bold"),
                 bg=BG_CARD, fg=TEXT_MID).pack(anchor="w", padx=24, pady=(8, 2))
        cb_rol = ttk.Combobox(win, values=["ADMIN", "CAJERO"],
                              state="readonly", font=("Segoe UI", 11))
        cb_rol.set(rol)
        cb_rol.pack(fill="x", padx=24, ipady=4)

        def guardar():
            nuevo_nombre = en_nombre.get().strip()
            nuevo_user   = en_user.get().strip()
            nuevo_rol    = cb_rol.get()

            if not nuevo_nombre:
                messagebox.showwarning("Campo requerido", "El nombre es obligatorio.", parent=win); return
            if not nuevo_user:
                messagebox.showwarning("Campo requerido", "El usuario es obligatorio.", parent=win); return

            exito, msg = Usuario.actualizar(id_u, nuevo_nombre, nuevo_user, nuevo_rol)
            if exito:
                messagebox.showinfo("✅ Listo", "Usuario actualizado.", parent=win)
                win.destroy()
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", msg, parent=win)

        self._boton_guardar(win, "  💾  Guardar Cambios", guardar)

    # ── CAMBIAR CONTRASEÑA ─────────────────────────────────────────────────

    def form_cambiar_password(self):
        vals = self._fila_seleccionada()
        if not vals: return

        id_u, nombre, *_ = vals
        win = self._modal(f"Cambiar Contraseña — {nombre}", alto=360)

        en_nueva    = self._entry(win, "Nueva contraseña *",    show="●")
        en_confirmar = self._entry(win, "Confirmar contraseña *", show="●")

        tk.Label(win,
                 text="⚠️  La contraseña se guardará cifrada (SHA-256).",
                 font=("Segoe UI", 8), bg=BG_CARD, fg="#F59E0B"
                 ).pack(padx=24, anchor="w", pady=(6, 0))

        def guardar():
            nueva = en_nueva.get()
            conf  = en_confirmar.get()

            if len(nueva) < 4:
                messagebox.showwarning("Contraseña débil",
                    "Mínimo 4 caracteres.", parent=win); return
            if nueva != conf:
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=win); return

            exito, msg = Usuario.cambiar_password(id_u, nueva)
            if exito:
                messagebox.showinfo("✅ Listo", "Contraseña actualizada.", parent=win)
                win.destroy()
            else:
                messagebox.showerror("Error", msg, parent=win)

        self._boton_guardar(win, "  🔑  Actualizar Contraseña", guardar)

    # ── ACTIVAR / DESACTIVAR ───────────────────────────────────────────────

    def toggle_estado(self):
        vals = self._fila_seleccionada()
        if not vals: return

        id_u, nombre, username, rol, estado_txt = vals

        # Proteger al admin logueado
        if username == self.usuario_actual.get("username"):
            messagebox.showwarning("Operación no permitida",
                "No puedes desactivar tu propio usuario."); return

        activo_ahora = "Activo" in estado_txt
        accion       = "desactivar" if activo_ahora else "activar"

        if messagebox.askyesno("Confirmar",
                               f"¿Deseas {accion} al usuario '{nombre}'?"):
            nuevo_estado = 0 if activo_ahora else 1
            exito, msg   = Usuario.cambiar_estado(id_u, nuevo_estado)
            if exito:
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", msg)