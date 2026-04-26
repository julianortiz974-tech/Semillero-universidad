import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from models.modelos import SistemaConfiguracion
from PIL import Image, ImageTk

BG_APP    = "#F4F6F8"
BG_CARD   = "#FFFFFF"
BORDER    = "#E0E0E0"
ACCENT    = "#4361EE"
ACCENT_H  = "#2b4fd4"
TEXT_DARK = "#1A1A2E"
TEXT_MID  = "#555770"
TEXT_LITE = "#9E9EB0"
DANGER    = "#E53935"


class VentanaConfig:
    def __init__(self, root, callback_volver):
        self.root            = root
        self.callback_volver = callback_volver
        self.ruta_logo       = ""
        self._tk_img         = None
        self._id_config      = None

        for widget in root.winfo_children():
            widget.destroy()

        root.configure(bg=BG_APP)
        self._construir_ui()
        self.cargar_datos_actuales()

    def _construir_ui(self):
        topbar = tk.Frame(self.root, bg="#1A1A2E", height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Button(topbar, text="<=  Volver", command=self.callback_volver,
                  bg="#1A1A2E", fg="white", relief="flat",
                  font=("Segoe UI", 11), cursor="hand2").pack(side="left", padx=20, pady=10)
        tk.Label(topbar, text="Configuracion del Sistema",
                 font=("Segoe UI", 14, "bold"), bg="#1A1A2E", fg="white").pack(side="left")

        canvas    = tk.Canvas(self.root, bg=BG_APP, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.page = tk.Frame(canvas, bg=BG_APP)
        win_id    = canvas.create_window((0, 0), window=self.page, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        self.page.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        header = tk.Frame(self.page, bg=BG_APP)
        header.pack(fill="x", padx=40, pady=(30, 10))
        tk.Label(header, text="Configuracion del Sistema",
                 font=("Segoe UI", 18, "bold"), bg=BG_APP, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(header, text="Datos de tu organizacion, contacto y logo comercial.",
                 font=("Segoe UI", 10), bg=BG_APP, fg=TEXT_MID).pack(anchor="w", pady=(2, 0))
        tk.Frame(self.page, bg=BORDER, height=1).pack(fill="x", padx=40, pady=(10, 20))

        body = tk.Frame(self.page, bg=BG_APP)
        body.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        self._card_formulario(body)
        self._card_logo(body)
        self._card_backup()

    def _card_formulario(self, parent):
        card = tk.Frame(parent, bg=BG_CARD, bd=0,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=(0, 16))

        ch = tk.Frame(card, bg=BG_CARD)
        ch.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(ch, text="Datos de la Organizacion",
                 font=("Segoe UI", 12, "bold"), bg=BG_CARD, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(ch, text="Aparecen en reportes y documentos.",
                 font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_LITE).pack(anchor="w", pady=(2, 0))
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        form = tk.Frame(card, bg=BG_CARD)
        form.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self.en_nombre = self._campo(form, "Nombre de la Empresa *", "Ej: Mi Negocio S.A.S.")
        self.en_pais   = self._campo(form, "Pais",                    "Ej: Colombia")
        self.en_nit    = self._campo(form, "NIT / RUT",               "Ej: 900.123.456-7")
        self.en_tel    = self._campo(form, "Telefono de Contacto",    "Ej: +57 300 000 0000")
        self.en_correo = self._campo(form, "Correo Electronico",      "Ej: contacto@miempresa.com")

        tk.Label(form, text="(*) Campo obligatorio",
                 font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_LITE).pack(anchor="w", pady=(4, 0))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(fill="x", padx=24, pady=(8, 24))
        self.btn_guardar = tk.Button(
            btn_frame, text="  Guardar Configuracion",
            command=self.guardar, bg=ACCENT, fg="white", relief="flat",
            font=("Segoe UI", 11, "bold"), cursor="hand2", padx=24, pady=10,
            activebackground=ACCENT_H, activeforeground="white")
        self.btn_guardar.pack(side="left")
        self.btn_guardar.bind("<Enter>", lambda e: self.btn_guardar.config(bg=ACCENT_H))
        self.btn_guardar.bind("<Leave>", lambda e: self.btn_guardar.config(bg=ACCENT))

    def _card_logo(self, parent):
        card = tk.Frame(parent, bg=BG_CARD, bd=0,
                        highlightbackground=BORDER, highlightthickness=1, width=300)
        card.pack(side="right", fill="y")
        card.pack_propagate(False)

        ch = tk.Frame(card, bg=BG_CARD)
        ch.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(ch, text="Logo Comercial", font=("Segoe UI", 12, "bold"),
                 bg=BG_CARD, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(ch, text="PNG, JPG o BMP recomendado",
                 font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_LITE).pack(anchor="w")
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        self.lbl_logo = tk.Label(card, text="Sin imagen\nPresiona Cargar Logo",
                                  font=("Segoe UI", 10), fg=TEXT_LITE,
                                  bg="#F9FAFB", relief="groove", bd=1,
                                  width=20, height=11, wraplength=180, justify="center")
        self.lbl_logo.pack(expand=True, fill="both", padx=24)

        self.lbl_ruta = tk.Label(card, text="Ningun archivo seleccionado",
                                  font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_LITE,
                                  wraplength=240, justify="center")
        self.lbl_ruta.pack(pady=(6, 0), padx=24)

        tk.Button(card, text="Cargar Logo", command=self.seleccionar_logo,
                  bg="#F4F6F8", fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  padx=20, pady=8, highlightbackground=BORDER, highlightthickness=1
                  ).pack(pady=(12, 24), padx=24, fill="x")

    def _card_backup(self):
        card = tk.Frame(self.page, bg=BG_CARD, bd=0,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=40, pady=(0, 40))

        ch = tk.Frame(card, bg=BG_CARD)
        ch.pack(fill="x", padx=24, pady=(20, 0))
        info = tk.Frame(ch, bg=BG_CARD)
        info.pack(side="left")
        tk.Label(info, text="Respaldo de Base de Datos",
                 font=("Segoe UI", 12, "bold"), bg=BG_CARD, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(info, text="Exporta todas las tablas a un archivo .sql para restaurar cuando necesites.",
                 font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_LITE).pack(anchor="w", pady=(2, 0))

        tk.Button(ch, text="Generar Backup (.sql)", command=self._hacer_backup,
                  bg="#10B981", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  padx=20, pady=8, activebackground="#059669"
                  ).pack(side="right", padx=(20, 0))

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)
        tk.Label(card,
                 text="El archivo generado incluye estructura y datos completos. "
                      "Guardalo en USB o Google Drive.",
                 font=("Segoe UI", 9), bg=BG_CARD, fg="#64748B",
                 wraplength=700, justify="left").pack(anchor="w", padx=24, pady=(0, 16))

    def _campo(self, master, etiqueta, placeholder=""):
        tk.Label(master, text=etiqueta, font=("Segoe UI", 9, "bold"),
                 bg=BG_CARD, fg=TEXT_MID).pack(anchor="w", pady=(12, 2))
        entry = tk.Entry(master, font=("Segoe UI", 11), bd=0, relief="flat",
                         fg=TEXT_LITE, highlightbackground=BORDER,
                         highlightthickness=1, highlightcolor=ACCENT)
        entry.pack(fill="x", ipady=8, pady=(0, 2))
        if placeholder:
            entry.insert(0, placeholder)
            self._bind_placeholder(entry, placeholder)
        return entry

    def _bind_placeholder(self, entry, placeholder):
        entry.bind("<FocusIn>",  lambda e, en=entry, ph=placeholder:
                   (en.delete(0, tk.END), en.config(fg=TEXT_DARK)) if en.get() == ph else None)
        entry.bind("<FocusOut>", lambda e, en=entry, ph=placeholder:
                   (en.insert(0, ph), en.config(fg=TEXT_LITE)) if en.get().strip() == "" else None)

    def _get(self, entry, placeholder):
        val = entry.get().strip()
        return "" if val == placeholder else val

    def _set(self, entry, valor, placeholder):
        entry.delete(0, tk.END)
        if valor:
            entry.insert(0, str(valor))
            entry.config(fg=TEXT_DARK)
        else:
            entry.insert(0, placeholder)
            entry.config(fg=TEXT_LITE)

    def mostrar_imagen(self, ruta):
        if ruta and os.path.exists(ruta):
            try:
                img = Image.open(ruta).resize((220, 220), Image.Resampling.LANCZOS)
                self._tk_img = ImageTk.PhotoImage(img)
                self.lbl_logo.config(image=self._tk_img, text="")
                self.lbl_ruta.config(text=os.path.basename(ruta), fg="#2E7D32")
            except Exception as e:
                self.lbl_logo.config(text=f"Error:\n{e}", image="", fg=DANGER)
        else:
            self.lbl_logo.config(text="Sin imagen\nPresiona Cargar Logo", image="", fg=TEXT_LITE)
            self.lbl_ruta.config(text="Ningun archivo seleccionado", fg=TEXT_LITE)

    def seleccionar_logo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar Logo",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.bmp")])
        if ruta:
            self.ruta_logo = ruta
            self.mostrar_imagen(ruta)

    def cargar_datos_actuales(self):
        d = SistemaConfiguracion.obtener()
        if d:
            self._id_config = d.get("id")
            self._set(self.en_nombre, d.get("nombre_organizacion", ""), "Ej: Mi Negocio S.A.S.")
            self._set(self.en_pais,   d.get("pais", ""),                "Ej: Colombia")
            self._set(self.en_nit,    d.get("codigo_area", ""),         "Ej: 900.123.456-7")
            self._set(self.en_tel,    d.get("moneda", ""),              "Ej: +57 300 000 0000")
            self._set(self.en_correo, d.get("simbolo_moneda", ""),      "Ej: contacto@miempresa.com")
            ruta = d.get("logo_path", "") or "assets/cargarlogo.jpg"
            self.ruta_logo = ruta
            self.mostrar_imagen(ruta)

    def guardar(self):
        nombre = self._get(self.en_nombre, "Ej: Mi Negocio S.A.S.")
        if not nombre:
            messagebox.showwarning("Campo requerido", "El nombre de la empresa es obligatorio.")
            self.en_nombre.focus_set()
            return
        try:
            config = SistemaConfiguracion(
                nombre_org = nombre,
                pais       = self._get(self.en_pais,   "Ej: Colombia"),
                codigo     = self._get(self.en_nit,    "Ej: 900.123.456-7"),
                moneda     = self._get(self.en_tel,    "Ej: +57 300 000 0000"),
                simbolo    = self._get(self.en_correo, "Ej: contacto@miempresa.com"),
                logo_path  = self.ruta_logo,
                id_config  = self._id_config
            )
            if config.actualizar():
                messagebox.showinfo("Guardado", "Configuracion guardada correctamente!")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar:\n{e}")

    def _hacer_backup(self):
        from reportes import hacer_backup_bd
        hacer_backup_bd()